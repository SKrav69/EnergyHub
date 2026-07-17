# EnergyHub 1.0 Full Project Review

## Executive assessment

EnergyHub 1.0 has a **sound overall architecture**:

- decisions are separated from inverter execution;
- serial access is serialized;
- Setting 01 commands are acknowledged and read back;
- Grid History, Daily Summary and Grid Import have persistence;
- Hybrid and Panic decisions are explainable;
- Home Assistant and EnergyHub have generally understandable ownership boundaries.

The project does **not** require a broad rewrite.

However, the review found several real functional defects that should be corrected before dashboard polishing and release closure.

There are no confirmed Critical findings that appear likely to damage the inverter or battery directly. There are, however, several **High-priority correctness issues**:

1. Automatic Panic normally uses the previous day’s solar forecast.
2. System Health does not actually include Communication Health.
3. Restart recovery reconstructs strategy from clock time rather than inverter state.
4. A failed transition to Grid Hold can leave grid charging active without target monitoring.
5. Disabling Autopilot can lose its queued Solar recovery request.
6. Daily Summary updates are not atomic and can contaminate historical charts.
7. EnergyHub’s remembered operating mode can diverge from the real inverter state.
8. Away Mode remains active in HA despite being outside EnergyHub 1.0.
9. SOC anomalies can corrupt Grid Import accounting.
10. Runtime entity registry state is not synchronized, preventing safe diagnosis of the current `*_2` conflict from the repository alone.

---

# 1. Current architecture

## Core data and control path

```text
PowMr inverter
    ↓
PowMrLocalAdapter
    ↓
TelemetryService
    ↓
InverterState
    ├── health monitors
    ├── Grid Monitor / Grid History / Grid Confidence
    ├── Grid Import estimator
    ├── Hybrid Decision Engine
    └── Panic Decision Engine
             ↓
        mode request queue
             ↓
       InverterController
             ↓
       verified inverter commands
```

Home Assistant provides:

```text
Autopilot helper
Daily house consumption
Solcast forecasts
Daily solar-surplus helper
Schedules
Manual controls
Notifications
Dashboards
```

These are transferred through retained MQTT inputs:

```text
energyhub/input/ha/#
```

EnergyHub publishes telemetry and intelligence primarily under:

```text
powmr/#
```

Notifications use:

```text
energyhub/event/notification
```

## Architectural strengths

- `PowMrLocalAdapter` owns physical communication and protects the serial port with a lock: `addon/app/adapters/powmr.py:12–35`.
- `InverterController` owns inverter writes rather than allowing decision engines to write directly.
- Hybrid and Panic engines return a decision, explanation and requested action.
- Menu 01 has bounded write attempts and QPIRI verification: `addon/app/services/inverter_controller.py:172–254`.
- Partial Hybrid and Panic entry failures attempt Solar recovery.
- Grid Import persistence is schema-versioned.
- HA remains the user-facing control and notification surface.
- No code automatically restarts the inverter.

The basic service-oriented architecture should be retained.

---

# 2. Startup, runtime and shutdown map

## Startup

```text
main()
  ↓
load add-on options
  ↓
create PowMr adapter and InverterController
  ↓
create MQTT client
  ↓
construct services
  ├── GridHistoryService loads /data/grid_history.json
  ├── GridImportService loads /data/grid_import.json
  └── DailySummaryService loads /data/daily_summary.json
  ↓
register MQTT callbacks
  ↓
retry MQTT connection indefinitely
  ↓
start MQTT network thread
  ↓
publish all Discovery definitions
  ↓
publish persisted or initial states
  ├── Autopilot = off until retained HA input arrives
  ├── Operating Mode = unknown
  ├── Grid Import persisted values
  └── Daily Summary last snapshot
  ↓
publish powmr/status = online
```

Relevant code: `addon/app/main.py:84–142`, `406–551`.

## Main runtime loop

```text
process one queued mode request
  ↓
read QPIGS telemetry
  ↓
parse and publish telemetry
  ↓
update Telemetry Freshness
  ↓
periodically read QPIWS
  ↓
periodically read QPIRI
  ↓
update health
  ↓
update Grid Import
  ↓
perform requested Hybrid evaluation
  ↓
check Hybrid target
  ↓
check Panic target
  ↓
evaluate automatic Panic every 15 minutes
  ↓
update Grid History and Grid Confidence
  ↓
sleep for poll interval
```

Relevant code: `addon/app/main.py:553–821`.

## External HA schedule

```text
23:49
→ publish Daily Summary / decision inputs

23:50
→ calculate solar surplus helper
→ request Hybrid evaluation

23:51
→ republish final Daily Summary inputs

07:00
→ request Solar when Autopilot is enabled
```

Relevant code: `homeassistant/live/config/automations.yaml:155–173`, `247–342`.

## Command path

```text
HA MQTT command
    ↓
MQTT callback thread
    ↓
single-item mode request queue
    ↓
main loop
    ↓
InverterController
    ↓
mpp-solar command
    ↓
ACK and, for Menu 01, QPIRI verification
```

## Persistence ownership

| File | Owner | Contents |
|---|---|---|
| `/data/grid_history.json` | `GridHistoryService` | Grid transitions and current grid state |
| `/data/grid_import.json` | `GridImportService` | Current/day-before import estimate and active SUB interval |
| `/data/daily_summary.json` | `DailySummaryService` | Daily snapshots and history |
| `/data/energy_hub_powmr_last.json` | `TelemetryService` | Last raw telemetry response |

## Shutdown

There is no explicit shutdown lifecycle:

- no signal handlers;
- no `finally` block;
- no `client.loop_stop()`;
- no explicit final persistence flush;
- no deliberate MQTT offline publication.

The add-on currently depends on process/container termination and MQTT Last Will behavior.

This is not the first problem to fix, but it should be addressed before final release or during Recovery & Resilience.

---

# 3. Service responsibility assessment

| Component | Current responsibility | Assessment |
|---|---|---|
| `PowMrLocalAdapter` | Runs `mpp-solar` commands and serializes access | Clear and appropriately focused |
| `InverterController` | Writes settings, verifies Menu 01, tracks expected strategy | Correct owner, but lacks startup and ongoing reconciliation |
| `TelemetryService` | Converts telemetry, publishes raw sensors, writes last response | Mostly clear; disk write does not belong on every poll |
| `AutopilotState` | Parses and stores current Autopilot status | Clear, but non-persistent inside EnergyHub |
| `HybridDecisionEngine` | Computes nightly energy decision | Clear and testable |
| `PanicDecisionEngine` | Evaluates daytime reserve risk | Clear, but receives stale HA forecast data |
| `GridMonitor` | Stores latest valid grid state | Clear |
| `GridHistoryService` | Persists grid transitions and calculates availability | Clear |
| `GridStabilityEngine` | Converts 24/48-hour history into confidence | Clear |
| `GridImportService` | Estimates import and persists active intervals | Correct owner; needs anomaly handling and rollover refinement |
| `DailySummaryService` | Stores and publishes daily values | Correct concept, but snapshot triggering is flawed |
| `CommunicationWatchdog` | Tracks successful and failed telemetry | Clear |
| `HealthMonitor` | Converts watchdog state into communication status | Clear |
| `BatteryHealthMonitor` | Detects low SOC and SOC jumps | Too permissive around jumps to high SOC |
| `TelemetryFreshnessMonitor` | Detects stale telemetry and unchanged load | Mixes freshness with signal plausibility |
| `InverterHealthMonitor` | Interprets QPIWS | Clear |
| `SystemHealthMonitor` | Aggregates subsystem health | Contains a confirmed communication aggregation bug |
| `EventBus` | Delivers telemetry to `GridMonitor` | Currently unnecessary but harmless |
| `main.py` | Construction, MQTT callbacks, orchestration, transitions, targets and notifications | Still recognizably an orchestrator, but has accumulated too much strategy coordination |

`main.py` should not be rewritten wholesale. A targeted extraction of strategy lifecycle coordination may eventually be justified, but only after the functional defects are fixed and covered by tests.

---

# 4. MQTT and Home Assistant ownership

## EnergyHub-owned state

EnergyHub publishes:

- raw PowMr telemetry;
- Grid History and Grid Confidence;
- operating strategy and reason;
- inverter source priorities;
- Hybrid decision and inputs;
- Panic decision and reason;
- health sensors;
- Grid Import estimates;
- Daily Summary values;
- Autopilot acknowledgement/status.

## HA-owned state

Home Assistant owns:

- `input_boolean.energyhub_autopilot`;
- schedule triggers;
- Solcast entities;
- house consumption sensor;
- daily solar-surplus helper;
- manual Panic UI;
- persistent notifications;
- household smart-plug controls;
- dashboards.

## Boundary issue

EnergyHub intelligence sensors use the `powmr/#` state namespace even though their MQTT device is `energyhub_core`.

For example, `_publish_sensor_discovery()` points every EnergyHub state to:

```text
powmr/<key>/state
```

See `addon/app/mqtt/publisher.py:550–583`.

Meanwhile, HA inputs and notifications use `energyhub/#`.

This is not an immediate 1.0 defect, but it is inconsistent and will complicate future multi-inverter or multi-vendor work. Renaming topics now could destroy history and create more duplicate entities, so it should be documented rather than casually changed.

---

# 5. Functional findings

## F-01 — Automatic Panic uses a stale solar forecast

**Severity:** High  
**Status:** Confirmed defect

The HA automation publishes `solar_forecast_today` only at 23:49 and 23:51:

- `homeassistant/live/config/automations.yaml:247–280`

EnergyHub uses that retained value for automatic Panic every 15 minutes:

- `addon/app/main.py:349–367`
- `addon/app/services/panic_decision.py:21–32`

After midnight, the retained `solar_forecast_today` still represents the previous day. It is not refreshed for the new day until 23:49.

Therefore, throughout almost the entire Panic window from 12:00 to 23:49, Panic normally evaluates using **yesterday’s forecast**, not today’s forecast.

### Consequence

Panic can be incorrectly activated or incorrectly rejected.

### Required direction

Separate the two temporal use cases:

- nightly Daily Summary snapshot inputs;
- live Panic decision inputs.

At minimum, publish the current-day forecast before the Panic window and whenever materially updated. Preferably attach a source timestamp or date.

---

## F-02 — System Health ignores Communication Health

**Severity:** High  
**Status:** Confirmed defect

`HealthMonitor` exposes communication status through the `state` property:

- `addon/app/services/health_monitor.py:18–24`

`SystemHealthMonitor` attempts to read:

```python
getattr(health, "status", "unknown")
```

- `addon/app/services/system_health.py:6–15`

`HealthMonitor` has no `status` attribute. Communication is therefore always read as `unknown`.

A direct test showed:

```text
Communication Health = offline
System Health = normal / ok
```

### Consequence

The high-level System Health sensor may remain normal while inverter communication is offline.

### Required direction

Use the actual `state` property or expose a consistent health interface across monitors. Also define how `starting`, `recovering` and `stale` map into aggregate health.

---

## F-03 — Restart recovery uses clock time instead of actual inverter state

**Severity:** High  
**Status:** Confirmed defect

On startup, EnergyHub publishes:

```text
Operating Mode = unknown
```

- `addon/app/main.py:542–545`

The HA restart automation waits ten seconds and then:

- requests Hybrid at night;
- requests Solar during the day.

- `homeassistant/live/config/automations.yaml:343–375`

It does not inspect Setting 01, Setting 16, persisted strategy context or the pre-restart target.

### Examples

At night:

```text
Real state before restart = Hybrid Grid Hold
Automation result = Hybrid Charging
```

The battery begins charging again.

```text
Nightly decision was Solar
EnergyHub restarts at 01:00
Automation result = Hybrid Charging
```

An unnecessary grid charge begins.

During daytime Panic:

```text
Real state before restart = Panic
Automation result = Solar
```

The protective strategy is abandoned.

### Required direction

Reconstruct from verified settings and persisted context:

```text
SBU + OSO → Solar
SUB + OSO → Hybrid Grid Hold
SUB + SNU → Hybrid Charging or Panic; persisted context required
```

The current clock-based automation should not be described as “restoring the correct strategy.”

---

## F-04 — Failed Grid Hold transition can leave charging active without target handling

**Severity:** High  
**Status:** Confirmed defect

`enter_hybrid_grid_hold()`:

1. confirms Menu 01 = SUB;
2. attempts Menu 16 = OSO;
3. sets `transition_failed` if Menu 16 fails;
4. does not attempt Solar recovery or preserve `hybrid_charging`.

- `addon/app/services/inverter_controller.py:311–336`

If the system was previously Hybrid Charging, a failed OSO command can leave the inverter physically at:

```text
SUB + SNU
```

but EnergyHub changes its logical mode to:

```text
transition_failed
```

The Hybrid target check only runs when mode is exactly `hybrid_charging`:

- `addon/app/main.py:685–700`

### Consequence

Grid charging may continue after reaching 80%, while EnergyHub no longer runs the 80% target transition.

The 07:00 HA automation may eventually restore Solar, but that is not sufficient protection.

### Required direction

Define a safe partial-transition policy. Likely options:

- preserve `hybrid_charging` if Grid Hold entry failed and physical charging remains confirmed;
- or attempt bounded Solar recovery;
- publish the actual partial physical state and a failure notification.

---

## F-05 — Autopilot Solar recovery can be overwritten in the mode queue

**Severity:** High  
**Status:** Confirmed race condition

The mode queue holds one entry. Every new request first removes the existing entry:

- `addon/app/main.py:169–177`

When Autopilot changes from on to off, `safe_solar` is queued:

- `addon/app/main.py:436–450`

A second MQTT command arriving before the next main-loop iteration replaces `safe_solar`.

Because later commands are ignored when Autopilot is disabled, the result can be:

```text
Autopilot OFF
+
active Hybrid/Panic strategy
+
safe_solar request lost
```

### Required direction

Safety requests must have priority and must not be replaceable by ordinary commands.

A simple priority or explicit pending-safe-recovery flag is preferable to a large command framework.

---

## F-06 — Daily Summary is updated non-atomically

**Severity:** High  
**Status:** Confirmed defect

Every individual input message calls `snapshot()` as soon as the three required keys exist:

- `addon/app/services/daily_summary.py:64–87`

HA publishes four inputs sequentially:

- `homeassistant/live/config/automations.yaml:247–280`

At 23:49, the service can create several snapshots combining:

- new house consumption;
- old forecast;
- old solar surplus;
- current Grid Import.

The chart groups daily values using `max`, including solar surplus:

- `homeassistant/live/storage/lovelace.dashboard_powmr1:142–238`

If yesterday’s surplus was larger than today’s, the temporary stale value can remain the maximum for today even after the correct final snapshot arrives.

### Restart consequence

After an add-on restart, retained previous-day values arrive one at a time. The service can store those values under the current date:

```text
today's date
+
yesterday's retained consumption/forecast/surplus
+
today's Grid Import = 0
```

This was reproduced directly from the current service behavior.

### Required direction

Input updates and snapshot creation must be separate operations.

Preferred sequence:

```text
update all inputs
→ explicit snapshot/finalize request
→ validate source date/freshness
→ publish one coherent snapshot
```

A single JSON input payload would also solve the partial-update problem.

---

## F-07 — EnergyHub does not reconcile remembered mode with the real inverter

**Severity:** High  
**Status:** Confirmed architecture gap

Every 60 seconds, EnergyHub reads QPIRI and publishes Setting 01:

- `addon/app/main.py:595–633`

It does not update `InverterController.mode`.

`known_charger_priority` is only updated after EnergyHub itself receives an ACK for a Menu 16 write:

- `addon/app/services/inverter_controller.py:128–170`

### Consequence

If:

- the user changes settings on the inverter;
- another tool sends a command;
- the add-on restarts;
- a command is acknowledged but the final hardware state differs;

then:

- operating mode can be stale;
- Grid Import may account using the wrong strategy;
- target logic can run against the wrong physical mode;
- dashboards may show contradictory mode and source settings.

### Required direction

At minimum, detect mismatch and mark the strategy `unknown` or `inconsistent`.

Full reconstruction belongs partly to 1.3, but basic mismatch detection is a 1.0 reliability requirement.

---

## F-08 — Away Mode remains active in the live 1.0 configuration

**Severity:** High  
**Status:** Confirmed scope and behavior defect

The live automation still controls the first-floor heat pump:

- `homeassistant/live/config/automations.yaml:431–514`

The helpers still exist:

- `homeassistant/live/storage/input_boolean:12–17`

The dashboard still exposes Away Mode:

- `homeassistant/live/storage/lovelace.dashboard_powmr1:430–437`

Yet the current architecture says Away Mode is not part of EnergyHub 1.0.

### Consequence

An explicitly deferred strategy can still control real household hardware.

### Required direction

Remove it only after confirming runtime references. Repository references currently exist in:

- `automations.yaml`;
- `input_boolean` storage;
- Lovelace dashboard;
- several documentation files.

The ownership idea—only stop a load that EnergyHub started—should be retained for future 1.5 Smart Thermal Energy.

---

## F-09 — SOC anomalies can corrupt Grid Import

**Severity:** High for accounting accuracy  
**Status:** Confirmed risk in current logic

Grid Import converts the maximum SOC increase during a SUB interval directly into battery energy:

- `addon/app/services/grid_import.py:306–346`

It does not consult Battery Health or reject suspicious jumps.

Battery Health also ignores any jump where the new or prior SOC is above 95%:

- `addon/app/services/battery_health.py:34–41`

A jump such as:

```text
33% → 100%
```

is not reported as a SOC jump and may add approximately:

```text
16 kWh × 67% = 10.72 kWh
```

to Grid Import.

### Required direction

- detect very large jumps even when the destination is 100%;
- reject or quarantine suspicious SOC changes in Grid Import;
- log that accounting was skipped because SOC was unreliable.

---

## F-10 — Telemetry Freshness generates false warnings for stable load

**Severity:** Medium  
**Status:** Confirmed design defect

Telemetry Freshness reports a warning if house load remains exactly unchanged for five minutes:

- `addon/app/services/telemetry_freshness.py:49–55`

The beacon treats anything other than `fresh` as telemetry failure and turns white:

- `homeassistant/live/config/automations.yaml:37–61`

A valid integer load value can naturally remain unchanged for five minutes.

### Consequence

The white lamp can appear briefly even though fresh telemetry continues to arrive. This matches the previously observed behavior.

### Required direction

Do not classify an unchanged load as stale telemetry.

Freshness should primarily use valid-message age. An unchanged-value diagnostic can remain separate and should require stronger evidence across several fields.

---

## F-11 — “Activated” notifications are sent before activation succeeds

**Severity:** Medium  
**Status:** Confirmed defect

Hybrid and Panic notifications are published immediately after a decision requests a mode:

- `addon/app/main.py:322–347`
- `addon/app/main.py:380–404`

The real inverter transition happens later, when the queued request is processed.

### Consequence

HA can display “Hybrid activated” or “Panic activated” even when the write or verification later fails.

### Required direction

Distinguish:

```text
decision_triggered
transition_started
transition_succeeded
transition_failed
```

The user-facing “activated” notification should follow successful transition verification.

---

## F-12 — The 23:51 Daily Summary is not the final daily Grid Import value

**Severity:** Medium  
**Status:** Confirmed accounting mismatch

The final Daily Summary refresh runs at 23:51.

Grid Import continues accumulating until midnight, especially during Grid Hold.

Therefore, Daily Summary’s `grid_import_estimated_kwh` can omit the final nine minutes of the day.

The separate Grid Import service correctly finalizes its own yesterday value on the first update after midnight, but that value is not copied into the previous Daily Summary record.

### Required direction

Either:

- finalize the complete daily record after midnight;
- or update yesterday’s Daily Summary from `grid_import.yesterday_energy_kwh`.

The current 23:51 snapshot can remain useful for consumption/forecast data, but it is not final for Grid Import.

---

# 6. Code findings

## C-01 — `main.py` has accumulated strategy lifecycle responsibilities

**Severity:** Medium  
**Status:** Confirmed technical debt

`main.py` currently owns:

- mode queue replacement policy;
- safe recovery;
- Hybrid and Panic input gathering;
- notification generation;
- Panic target state;
- Hybrid and Panic target monitoring;
- periodic evaluation;
- health aggregation publication;
- startup publication and MQTT callbacks.

It remains understandable, but 824 lines is now a warning signal.

The correct response is not a wholesale rewrite. First fix the functional findings and add tests. Then evaluate extracting only the strategy lifecycle coordination.

---

## C-02 — Policy values and mappings are duplicated

**Severity:** Medium

Examples:

- battery capacity in both Hybrid and Grid Import;
- Panic targets in `main.py` and `panic_decision.py`;
- Setting 01 mappings in `main.py`, `publisher.py` and `inverter_controller.py`.

Files:

- `addon/app/main.py:66–72`
- `addon/app/services/hybrid_decision.py:1–3`
- `addon/app/services/grid_import.py:9–17`
- `addon/app/services/panic_decision.py:9–13`
- `addon/app/mqtt/publisher.py:9–12`
- `addon/app/services/inverter_controller.py:6–20`

This creates hidden coupling, especially for future configurable profiles.

---

## C-03 — Menu 16 is acknowledged but not independently verified

**Severity:** Medium  
**Status:** Known limitation / possible risk

Menu 01 is checked with QPIRI. Menu 16 trusts the command ACK and updates `known_charger_priority`.

If the hardware protocol cannot query Menu 16, this may be the best available implementation, but documentation should say “ACK-confirmed,” not imply full setting verification.

---

## C-04 — Persistence writes are not atomic

**Severity:** Medium

The services directly overwrite JSON files:

- `grid_import.py:198–205`
- `daily_summary.py:49–56`
- `grid_history.py:33–43`
- `telemetry.py:64`

A power loss during a write can leave invalid JSON.

Grid Import can also write every 0.001 kWh, often every poll during meaningful import:

- `grid_import.py:413–422`

Telemetry writes the entire last response every valid polling cycle.

### Consequences

- unnecessary storage writes;
- possible SD-card wear;
- corruption risk;
- telemetry can be marked failed merely because the debug file write failed.

Use temporary-file replacement and a time-based persistence cadence, with a forced save on important transitions.

---

## C-05 — No executable automated tests

**Severity:** High for release confidence  
**Status:** Confirmed repository gap

There are no unit or integration tests for:

- Hybrid decisions;
- Panic windows and thresholds;
- Grid Import intervals;
- midnight rollover;
- stale retained inputs;
- restart reconstruction;
- partial inverter transitions;
- queue priority;
- health aggregation.

The identified defects are exactly the kinds of problems small deterministic tests catch.

Tests should be added before substantial refactoring, not after.

---

## C-06 — Dependencies are unpinned

**Severity:** Medium

`addon/requirements.txt` contains only:

```text
paho-mqtt
mppsolar
```

A future rebuild may install behaviorally different versions.

Pin currently tested versions before release closure.

---

## C-07 — Default MQTT credentials are committed

**Severity:** High for public release security

`addon/config.yaml:17–20` contains a default MQTT username and a matching weak default password.

Even when users can change these options, a public release should not encourage shared default credentials.

---

# 7. Entity and MQTT audit

## Current intentional Grid Import entities

The current code creates two conceptually different daily entities:

### Live current-day accumulator

```text
unique_id: energyhub_daily_grid_import_estimated
state topic: powmr/daily_grid_import_estimated/state
state class: total_increasing
```

### Daily Summary snapshot

```text
unique_id: energyhub_daily_grid_import
state topic: powmr/daily_grid_import/state
state class: measurement
```

Files:

- `addon/app/mqtt/publisher.py:183–213`
- `addon/app/mqtt/publisher.py:255–297`

These are not technically the same entity, but their names are very similar:

- Grid Import Today Estimated
- Daily Grid Import Estimated

That similarity causes understandable UI confusion.

## Exact `*_2` root cause

The repository does not contain an entity ending in `_2`.

It also does not include:

- the live MQTT broker’s retained topic inventory;
- `.storage/core.entity_registry`;
- `.storage/core.device_registry`.

Therefore, the precise runtime source of:

```text
sensor.energyhub_daily_grid_import_estimated_2
```

cannot be proven from this ZIP alone.

The likely causes are external to the synchronized repository:

- an old retained MQTT Discovery payload;
- an entity registry entry using the desired entity ID with another unique ID;
- a previous manual entity rename;
- an obsolete Discovery entity created before the current Git history.

## Reproducibility issue

The dashboard references entity IDs such as:

```text
sensor.energyhub_grid_confidence
sensor.energyhub_grid_available_24h
sensor.energyhub_grid_available_48h
```

- `lovelace.dashboard_powmr1:543–566`

Current Discovery keys are:

```text
grid_confidence_level
grid_available_hours_24h
grid_available_hours_48h
```

- `addon/app/mqtt/publisher.py:129–169`

The live HA entity registry likely contains manual renames that make the dashboard work. However, the sync script deliberately does not copy the entity registry:

- `tools/dev/sync-from-ha.ps1:74–81`

### Consequence

A fresh Home Assistant installation may not reproduce the entity IDs expected by the committed dashboard.

### Required audit data before cleanup

Export or inspect:

```text
homeassistant/sensor/energyhub_+/config
```

and registry entries whose unique IDs begin with:

```text
energyhub_
```

Then prepare a keep/migrate/delete table. Do not publish empty payloads broadly.

## Shared availability issue

All EnergyHub core sensors use:

```text
powmr/status
```

as their availability topic:

- `addon/app/mqtt/publisher.py:557–563`

When telemetry is invalid, EnergyHub sets that topic offline:

- `addon/app/main.py:635–650`

This makes System Health, Daily Summary, decision reasons and Grid History unavailable at the exact moment they are most useful for diagnosis.

A separate process/core availability topic and inverter telemetry availability topic would be cleaner, though migration must preserve entity history.

---

# 8. Dashboard and chart assessment

## Current structure

The current Solar dashboard contains:

- one view;
- nine sections;
- three major charts;
- EnergyHub controls;
- detailed system status;
- decision logic;
- three household-floor sections.

Several headings remain literally:

```text
New section
```

Examples: `lovelace.dashboard_powmr1:409–465`, `530–646`.

## Strengths

- The 24-hour PV/load/SOC chart is genuinely useful.
- The 7-day chart combines the main daily energy story.
- Hybrid and Panic reasons are visible.
- Current Setting 01 and Setting 16 have human-readable explanations.
- Manual Panic and Autopilot controls are easy to find.
- Household floor controls are already integrated.

## Problems

### Family and developer information are mixed

Raw currents, inverter source priorities, health diagnostics, decision equations and household controls all live in one long page.

### Information is repeated

Current strategy appears in:

- a dedicated markdown mode card;
- Decision Logic markdown;
- entities;
- source-priority explanation.

Grid Confidence and other decision inputs are also repeated.

### The dashboard is not truly context-aware

Hybrid input details remain visible when Solar is operating normally. Panic reasons remain permanently displayed. There are no conditional cards focused on the active strategy.

### Chart semantics are overloaded

The 7-day chart combines:

- three kWh bar series;
- one percentage line;
- three additional header-only live values.

The label “Grid Import Today” is attached to a seven-day historical series.

### Unnecessary nesting

The first chart is wrapped in several single-column grid cards, adding storage JSON complexity without visual benefit.

### Away Mode remains visible

The deferred feature is still a primary control tile.

### Mobile length

A single view with nine sections and extensive diagnostics creates excessive scrolling.

## Proposed UI structure

### View 1 — Home / Family

1. **EnergyHub hero card**
   - current strategy;
   - Autopilot;
   - System Health;
   - concise current explanation.

2. **Current energy**
   - PV;
   - house load;
   - battery SOC;
   - grid state/import.

3. **Active strategy context**
   - Solar: next expected decision;
   - Hybrid Charging: target and progress;
   - Grid Hold: “Grid Hold until 07:00”;
   - Panic: reason and target.

4. **Compact 24-hour chart**

5. **Compact 7-day energy summary**

6. **House comfort and floor controls**

### View 2 — Energy Intelligence

- Grid Confidence and history;
- Hybrid decision inputs;
- Panic decision inputs;
- forecast and consumption;
- Daily Summary;
- Grid Import accounting.

### View 3 — Developer / Diagnostics

- Setting 01 and Setting 16;
- raw operating state;
- all health components;
- QPIWS details;
- telemetry freshness;
- transition status and last error;
- persistence/accounting diagnostics.

This separation should happen after entity naming is stabilized.

---

# 9. Documentation findings

## D-01 — Away Mode documentation contradicts live configuration

`docs/12-HomeAssistant-Configuration.md:110–114` says the Away helpers and automation were removed.

They remain active in the synchronized HA files.

Other documents still describe Away as current:

- `docs/10-Developer-Architecture.md:602–640`
- `docs/DECISION_ENGINE.md:793–807`

Meanwhile, Project State and the latest planning say it is deferred.

This is a confirmed contradiction.

## D-02 — Roadmap does not contain the agreed 1.4 and 1.5 milestones

`docs/06-Roadmap.md` moves directly from:

```text
1.3 Recovery & Resilience
```

to:

```text
2.x Energy Optimization Platform
```

The agreed roadmap is missing:

```text
1.4 — Remote Access & Telegram
1.5 — Smart Thermal Energy
```

Smart Heating is still assigned largely to 1.1 at `docs/06-Roadmap.md:58–103`.

The updated direction is:

- 1.1 collects test-drive improvements and requirements;
- 1.4 adds Cloudflare/remote HA access and Telegram;
- 1.5 implements universal surplus/cheap-tariff thermal control.

## D-03 — README repository structure is partly stale

README lists:

```text
addon/app/inverter/
```

but the actual folder is:

```text
addon/app/adapters/
```

See `README.md:321–342`.

## D-04 — “Correct restart restoration” is overstated

HA documentation describes restart mode handling as restoring/requesting the mode, while the automation itself uses time alone.

This must be rewritten as a temporary fallback until genuine reconstruction exists.

## D-05 — Documentation has substantial duplication

The same operating logic is repeated extensively across:

- `PROJECT_STATE.md`;
- `DECISION_ENGINE.md`;
- `05-System-Architecture.md`;
- `09-Decision-Log.md`;
- `10-Developer-Architecture.md`;
- `12-HomeAssistant-Configuration.md`;
- README.

Duplication has already produced contradictions.

A future documentation audit should assign clear ownership:

| Document | Should own |
|---|---|
| README | Product overview and quick start |
| PROJECT_STATE | Current factual state only |
| Roadmap | Future milestones only |
| Backlog | Unfinished actionable work |
| DECISION_ENGINE | Current strategy logic |
| System Architecture | Components and boundaries |
| Developer Architecture | Internal code structure |
| Decision Log | Why major decisions were made |
| HA Configuration | HA-specific integration |
| Project History | Historical milestones |

## D-06 — Operational and deployment documentation is incomplete for an external user

A stranger still lacks a complete path covering:

- prerequisites;
- MQTT credentials;
- required HA integrations and custom cards;
- expected entity naming;
- entity registry renames;
- initial helper setup;
- deployment validation;
- safe rollback;
- known hardware assumptions.

This is a release-preparation item, not an immediate functional blocker.

---

# 10. Restart, midnight and 07:00 risk assessment

| Boundary | Current behavior | Risk |
|---|---|---|
| Add-on restart during Solar day | HA requests Solar after ten seconds | Mostly safe but unnecessary write |
| Restart during Solar night after a Solar decision | HA requests Hybrid | Unnecessary grid charging |
| Restart during Hybrid Charging | HA requests Hybrid again | Target context resets but charging continues |
| Restart during Grid Hold | HA requests Hybrid Charging | Battery can recharge unnecessarily |
| Restart during daytime Panic | HA requests Solar | Panic reserve strategy is lost |
| Midnight during SUB | Grid Import finalizes previous day on first new-day update | Estimator rollover is reasonable |
| Midnight Daily Summary | No exact finalization using Grid Import’s completed total | Summary may miss final import |
| Restart after midnight | Retained old inputs can be stored under new date | Historical contamination |
| 07:00 with HA operational | HA requests Solar | Expected |
| 07:00 with HA unavailable | No internal fallback | Grid Hold/charging may continue |
| 07:00 Solar command failure | Mode becomes transition failed | No dedicated retry/alert path beyond logs |

The first corrections should focus on restart reconstruction and atomic day finalization.

---

# 11. Findings by severity

## Critical

No confirmed Critical defects were found.

## High

1. Panic uses stale previous-day forecast.
2. System Health ignores Communication Health.
3. Clock-only restart reconstruction.
4. Failed Grid Hold transition can leave charging active without target control.
5. Safe Solar recovery request can be overwritten.
6. Daily Summary partial/stale snapshots contaminate history.
7. Controller mode can diverge from physical inverter state.
8. Away Mode remains active outside the 1.0 scope.
9. SOC jumps can corrupt Grid Import.
10. No automated tests for safety- and time-sensitive logic.
11. Weak committed default MQTT credentials.
12. Runtime entity naming is not reproducible from the repository.

## Medium

1. Telemetry Freshness false positives on unchanged load.
2. Notifications claim activation before transition success.
3. 23:51 is not final for Grid Import.
4. Menu 16 is ACK-confirmed but not independently read back.
5. Shared availability hides diagnostic entities during communication failure.
6. Non-atomic and frequent persistence writes.
7. Grid Import counts full house load during daytime SUB even when PV may contribute.
8. `main.py` has accumulated lifecycle complexity.
9. Hardcoded strategy constants and duplicated protocol mappings.
10. Unpinned dependencies.
11. 07:00 restoration depends exclusively on HA.
12. Manual Panic silently depends on Autopilot being enabled.

## Low

1. `TelemetryService.previous` is maintained but not used to suppress publications.
2. `EventBus` currently has only one subscriber.
3. Several dashboard card wrappers are redundant.
4. Add-on description mentions future JK BMS and EV functionality as though part of the product.
5. Version already reports `1.0.0` while release cleanup remains open.

## Observations

1. The weighted Grid Confidence calculation does implement the requested relative weighting: one outage hour in the latest 24 hours has approximately three times the impact of an hour in the older 24–48-hour segment.
2. Hybrid’s battery-refill calculation deliberately estimates refill to 100%, although actual cheap-tariff charging stops at 80%. This matches current documentation but should be evaluated economically during test driving.
3. Grid Import is necessarily informational because the inverter lacks a reliable accumulated import counter.
4. The architecture is strong enough to improve incrementally; a platform rewrite is unwarranted.

---

# 12. Proposed order of changes

## Batch 1 — Functional correctness

Use **High**.

1. Fix live Panic input publication and freshness.
2. Fix System Health communication aggregation.
3. Make Daily Summary snapshots atomic.
4. Fix Grid Hold partial-failure behavior.
5. Protect `safe_solar` from queue replacement.
6. Add focused tests for all five corrections.

Do not begin dashboard work before these are stable.

## Batch 2 — Restart and state truth

Use **High**.

1. Read and classify actual startup settings.
2. Persist enough strategy context to distinguish Hybrid Charging and Panic.
3. Detect runtime inverter-setting mismatch.
4. replace or disable the clock-only HA restart automation.
5. add explicit transition-success/failure events.

## Batch 3 — Grid Import validation

Mostly **Instant**, with High for design decisions.

1. Validate Hybrid Charging.
2. Validate Grid Hold.
3. Validate Panic with daytime PV.
4. validate restart persistence.
5. validate midnight rollover.
6. protect against SOC anomalies.
7. reconcile final Grid Import with Daily Summary.
8. reduce and atomically write persistence.

## Batch 4 — Away removal and entity/MQTT cleanup

Use **High**.

1. Remove active Away automation and UI after final reference verification.
2. export retained Discovery topics and HA entity registry entries.
3. define canonical entity names.
4. preserve desired historical entity IDs where possible.
5. delete only confirmed obsolete Discovery topics.
6. update dashboard references.
7. verify no `_2` entity remains.

## Batch 5 — Dashboard and chart redesign

Use **High**.

1. Separate Family, Intelligence and Developer views.
2. create context-aware strategy cards.
3. simplify the 24-hour chart.
4. split or simplify the overloaded seven-day chart.
5. standardize names, icons, spacing and section headings.
6. validate mobile layout.

## Batch 6 — Documentation audit

Use **High**.

1. Update every document against final code.
2. remove current/future contradictions.
3. add roadmap 1.4 and 1.5.
4. remove active Away wording from 1.0.
5. document entity ownership and migration.
6. reduce duplication.

## Batch 7 — Infographics and release preparation

Use **High**.

1. How EnergyHub works.
2. Runtime architecture.
3. Solar/Hybrid/Panic decision flow.
4. Home Assistant and MQTT boundary.
5. final screenshots.
6. README deployment guide.
7. known limitations.
8. pinned dependencies.
9. safe configuration defaults.
10. release notes and Git tag.

---

# 13. Expected files for each correction

| Change | Expected files |
|---|---|
| Live Panic forecast and freshness | `homeassistant/live/config/automations.yaml`, `addon/app/main.py`, possibly `daily_summary.py` and `panic_decision.py` |
| System Health communication | `services/system_health.py` and/or `services/health_monitor.py` |
| Atomic Daily Summary | `services/daily_summary.py`, `main.py`, `automations.yaml`, possibly `mqtt/publisher.py` |
| Grid Hold failure handling | `services/inverter_controller.py`, `main.py` |
| Safe recovery queue priority | `main.py` |
| Startup reconstruction | `main.py`, `inverter_controller.py`, `adapters/powmr.py`, `automations.yaml`, possibly `mqtt/publisher.py` |
| Transition notifications | `main.py`, `mqtt/publisher.py`, HA notification automation |
| SOC anomaly handling | `battery_health.py`, `grid_import.py`, possibly `main.py` |
| Grid Import finalization | `grid_import.py`, `daily_summary.py`, `main.py` |
| Persistence reliability | `grid_import.py`, `daily_summary.py`, `grid_history.py`, `telemetry.py`, shared utility if justified |
| Away removal | `automations.yaml`, storage `input_boolean`, Lovelace dashboard, affected docs |
| Entity cleanup | `mqtt/publisher.py`, Lovelace dashboard, runtime MQTT retained topics, runtime HA entity registry |
| Dashboard redesign | `lovelace.dashboard_powmr1`, possibly Lovelace resources |
| Roadmap update | `docs/06-Roadmap.md`, `07-Backlog.md`, `PROJECT_STATE.md`, README, changelog/history where appropriate |
| Documentation audit | all primary docs listed in the handover |
| Release security | `addon/config.yaml`, `requirements.txt`, README |
| Test coverage | new `tests/` files and minimal test configuration |

# Conclusion

EnergyHub 1.0 is not architecturally broken. Its core design is good and worth preserving.

The immediate priority should not be a stylistic code refactor. It should be a focused **functional-stability correction batch**, beginning with:

1. stale Panic forecast;
2. broken System Health aggregation;
3. Daily Summary atomicity;
4. Grid Hold failure safety;
5. safe-Solar queue priority.

After those are corrected and tested, restart reconstruction becomes the next major architectural task. Entity cleanup, dashboard polish, documentation, infographics and release closure should follow in that order.