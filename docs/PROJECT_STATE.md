# EnergyHub Project State

Last Updated: 2026-07-09

---

# Project Vision

EnergyHub is an autonomous home energy management system built on top of Home Assistant.

Its goal is not only to monitor energy, but to make intelligent decisions about battery usage, heating, EV charging and household energy consumption.

EnergyHub should remain:

- local first;
- calm;
- explainable;
- modular;
- reliable;
- suitable for real daily family use.

---

# Current Architecture

```text
Homeowner
   ↓
Dashboards
   ↓
Home Assistant
   ↓
MQTT
   ↓
EnergyHub Core
   ↓
Services / Engines
   ↓
Devices

# Current Dashboard Architecture

The EnergyHub Developer Dashboard separates current operational state from information used for analysis and future decisions.

## EnergyHub Status

Purpose:

```text
What is happening now?

Is the system healthy?
```

Current information:

- Communication Status
- Battery SOC
- Battery Charging Current
- Battery Discharge Current
- House Load
- PV1 Power
- Grid Voltage

New health information available for future dashboard integration:

- Battery Health
- Telemetry Freshness
- Inverter Health
- System Health

Future:

- Current Operating Mode
- prominent Operating Mode visualization
- consistent Operating Mode colors
- System Health visualization
- Battery Health status
- Telemetry Freshness status
- Inverter Health status
- unified signed Battery Current sensor if useful

---

## EnergyHub Intelligence

Purpose:

```text
What does EnergyHub know?

What information is available for decisions?
```

Current information:

- Grid Confidence
- Grid Available 24h
- Grid Available 48h
- Consumption Yesterday
- Solar Surplus Yesterday
- Solar Forecast Today
- Solar Forecast Tomorrow

Grid Confidence is displayed prominently using:

```text
🟢 NORMAL
🟡 UNSTABLE
🟠 RISK
🔴 PANIC
```

Future:

- Recommended Mode
- Recommendation
- Reason
- Recommended Action
- Battery Reserve Forecast
- expected ability to operate until the next charging opportunity

When Current Mode and Recommended Mode differ, EnergyHub Intelligence should clearly explain why.

---

# Current Dashboard

## Developer Dashboard

Contains technical, operational and decision-support information:

- PowMr telemetry
- Battery state
- Grid state
- Communication status
- EnergyHub Status
- EnergyHub Intelligence
- Grid Confidence
- Grid Availability
- Daily energy statistics
- Smart plug / heat pump visibility

Future additions:

- System Health
- Battery Health
- Telemetry Freshness
- Inverter Health
- Current Operating Mode
- Current Setting 01 state
- Current Setting 16 state
- Daily Grid Import
- Decision Engine recommendations and explanations

## Family Dashboard

Contains calm operational information for household members:

- inverter/grid status;
- battery state;
- current house load;
- floor temperatures;
- smart plug controls;
- heat pump controls;
- operational warnings only when needed.

Future additions:

- Current Operating Mode
- simplified System Health information
- Panic Mode control where appropriate

The Family Dashboard should not expose unnecessary engineering details.

---

# Known Hardware Limitations

PowMr PI30MAX currently exposes:

- Battery information
- Grid voltage
- Grid frequency
- Load
- PV1 telemetry only

Not available from the inverter:

- PV2 telemetry
- second output status
- reliable grid import/export counters
- reliable total PV generation when both PV inputs are involved

Because of this:

- inverter PV telemetry is treated primarily as operational and diagnostic information;
- daily solar surplus is based on Solcast forecast, not inverter PV production;
- total Grid Import must be calculated or estimated by EnergyHub;
- Grid Import statistics will initially be informational rather than meter-accurate.

---

# Current Inverter Control Knowledge

EnergyHub has successfully tested programmatic control of Setting 16.

Verified mapping:

```text
Setting 16 — Charger Source Priority

PCP02 → OSO
PCP03 → CSO
PCP01 → SNU
```

The inverter may expose command names and display names differently.

The real inverter display was used to verify actual Setting 16 behavior.

---

# Setting 01

Setting 01 controls output source priority.

The future EnergyHub operating strategy requires programmatic switching between:

```text
SBU
↕
SUB
```

This has not yet been tested programmatically.

Testing Setting 01 control is the next critical inverter-control milestone.

Automatic Operating Mode execution must not begin until EnergyHub can safely:

- switch SBU → SUB;
- verify the resulting inverter state;
- switch SUB → SBU;
- verify restoration of the expected inverter state.

---

# Current Inverter Charging-Source Modes

The current PowMr firmware exposes three usable Setting 16 charging-source modes:

```text
OSO
CSO
SNU
```

`CUB` is not available on the current inverter firmware.

## OSO

Only Solar.

Current intended use:

```text
Solar Mode
```

Battery charging is performed from solar energy only.

---

## CSO

Solar First.

Real-system testing showed that CSO is not suitable for planned continuous grid charging.

Observed behavior:

```text
Night
PV = 0
Utility charging active

↓

PV generation begins

↓

Utility charging current significantly decreases
```

Because of this behavior, CSO is no longer the primary candidate for controlled Hybrid or Panic charging.

---

## SNU

SNU is the selected candidate for controlled utility and solar charging.

Current intended use:

```text
Hybrid charging
Panic charging
```

Important real-system finding:

Changing Setting 16 from OSO to SNU alone does not necessarily force immediate grid charging.

The inverter still follows Setting 01 output-source behavior and the configured low-battery transfer thresholds.

Because of this, controlled EnergyHub charging requires coordinated Setting 01 and Setting 16 changes.

---

# Current Operating Mode Strategy

The previous mode names:

```text
Summer
Winter
```

were abandoned.

They did not accurately describe the real operating strategy.

Current mode names:

```text
Solar
Hybrid
Panic
Away
```

The modes describe how the house obtains and manages energy rather than the current season.

---

## Solar Mode

Purpose:

Prefer solar generation and battery energy.

Expected inverter configuration:

```text
Setting 01 → SBU
Setting 16 → OSO
```

Behavior:

- house prefers solar and battery operation;
- battery charging is solar-only;
- normal inverter low-battery fallback behavior remains available.

Current inverter thresholds:

```text
Battery SOC reaches 15%
→ inverter switches house load to grid

Battery charges from solar to 30%
→ inverter switches house back to SBU operation
```

This behavior may be acceptable when Grid Confidence is good.

During the fallback period, house consumption supplied by the grid must eventually be included in Daily Grid Import.

---

## Hybrid Mode

Purpose:

Use controlled grid charging when expected solar generation is insufficient to maintain an appropriate battery reserve.

Expected charging configuration:

```text
Setting 01 → SUB
Setting 16 → SNU
```

Initial charging target:

```text
Battery SOC → 80%
```

After the target is reached:

```text
Restore:

Setting 01 → SBU
Setting 16 → OSO
```

Initial expected use:

```text
Controlled night-tariff battery charging
```

Hybrid Mode should eventually consider:

- Grid Confidence;
- Solar Forecast;
- expected House Consumption;
- current Battery SOC;
- expected battery reserve.

Hybrid Mode is not simply a fixed seasonal mode.

It is an energy strategy that may be activated when solar energy alone is unlikely to provide sufficient battery reserve.

---

## Panic Mode

Purpose:

Protect battery reserve when grid availability is unreliable.

Expected charging configuration:

```text
Setting 01 → SUB
Setting 16 → SNU
```

Initial charging target:

```text
Battery SOC → 95%
```

After the target is reached:

```text
Restore:

Setting 01 → SBU
Setting 16 → OSO
```

Unlike Hybrid Mode, Panic charging may occur at any time of day.

Possible triggers include:

- poor Grid Confidence;
- rapidly falling Battery SOC;
- low remaining solar generation;
- high expected House Consumption;
- insufficient projected battery reserve.

Panic Mode should eventually become proactive.

EnergyHub should not always wait until the battery reaches the inverter's 15% low-battery fallback threshold.

---

## Away Mode

Status:

```text
Requires additional design
```

Current concept:

- prioritize safe autonomous house operation;
- protect battery reserve;
- use excess solar energy for flexible heating loads;
- reduce unnecessary grid import.

Possible future behavior:

```text
SOC high
+
sufficient solar generation
→ enable flexible heating loads

SOC falls to reserve threshold
→ disable flexible heating loads
```

Exact Away Mode behavior will be designed later.

---

# Proactive Battery Reserve Protection

A key future Decision Engine responsibility is predicting whether the house can safely operate until the next expected charging opportunity.

Example scenario:

```text
Night
        ↓
Hybrid charging to 80%
        ↓
Day
        ↓
Low solar generation
+
High house consumption
        ↓
Battery SOC falls toward 30%
        ↓
Grid Confidence is poor
        ↓
Risk of battery depletion
        ↓
Grid may be unavailable when the battery reaches critical SOC
```

In this situation, waiting for the normal inverter 15% fallback threshold may be unsafe.

Future EnergyHub behavior may be:

```text
Grid Confidence poor
+
SOC falling
+
Remaining Solar Forecast low
+
Expected House Consumption high
+
Projected Battery Reserve insufficient
        ↓
Temporary daytime Panic charging while grid is available
```

The central future Decision Engine question is:

```text
Can the house safely survive until the next expected charging opportunity?
```

This requires future battery reserve forecasting based on:

- current Battery SOC;
- Battery SOC trend;
- remaining solar production;
- expected House Consumption;
- Grid Confidence;
- time until the next expected charging opportunity.

---

# Current Daily Summary Model

Daily Summary Engine v1 is implemented inside EnergyHub.

Home Assistant provides selected daily values through retained MQTT input topics.

EnergyHub consumes these inputs, stores a daily snapshot, and republishes EnergyHub-owned MQTT sensors for dashboards and future engines.

## Home Assistant Source Values

- Daily House Consumption
- Solcast Forecast Today
- Daily Solar Surplus Estimated

## Snapshot Timing

Home Assistant owns the daily snapshot timing.

At 23:50 local time:

- Home Assistant calculates and stores Daily Solar Surplus Estimated before daily source sensors reset at midnight.

At 23:51 local time:

- Home Assistant publishes the Daily Summary input values to MQTT.

EnergyHub receives the retained MQTT messages and creates or updates the daily snapshot when all required values are available.

## MQTT Input Topics

```text
energyhub/input/ha/daily_house_consumption
energyhub/input/ha/solar_forecast_today
energyhub/input/ha/daily_solar_surplus_estimated
```

## EnergyHub Daily Sensors

```text
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_forecast
sensor.energyhub_daily_solar_surplus_estimated
sensor.energyhub_daily_grid_availability
```

## Persistence

Daily summaries are stored in:

```text
/data/daily_summary.json
```

The service is idempotent.

Retained MQTT messages received after an EnergyHub restart do not create unnecessary snapshot updates when the stored values are unchanged.

---

# Daily Summary Architecture

```text
Home Assistant Daily Sensors
            │
            │ 23:50 snapshot
            ▼
Daily Solar Surplus Estimated
            │
            │ 23:51 MQTT publish
            ▼
energyhub/input/ha/*
            │
            ▼
DailySummaryService
            │
            ├── Persistent Daily History
            │      /data/daily_summary.json
            │
            └── EnergyHub MQTT Sensors
                        │
                        ▼
               Home Assistant Dashboards
                        │
                        ▼
              Future Decision Engine
```

The architectural responsibility is intentionally separated:

```text
Home Assistant
    │
    └── provides integration data and snapshot timing

EnergyHub Daily Summary Engine
    │
    ├── owns the daily summary data model
    ├── stores historical daily snapshots
    └── publishes EnergyHub-owned daily sensors

Decision Engine
    │
    └── consumes summarized facts
```

The Decision Engine must consume Daily Summary data rather than create historical facts itself.

---

# Solar Surplus Terminology

The old term:

```text
Daily Energy Balance
```

has been replaced with:

```text
Daily Solar Surplus Estimated
```

Meaning:

```text
Estimated solar energy that was probably not used today.
```

Formula:

```text
max(0, Solcast Forecast Today - Daily House Consumption)
```

The value is intentionally based on Solcast forecast rather than inverter PV telemetry.

The PowMr inverter exposes PV1 telemetry only.

PV2 telemetry is not available, and PV2 may remain unused when PV1 generation is sufficient for current house load and battery charging demand.

Because of this, inverter PV telemetry cannot currently provide a reliable estimate of total daily solar generation.

Daily Solar Surplus Estimated is used for:

- historical statistics;
- understanding unused solar potential;
- future energy optimization;
- future Decision Engine context.

It should not be interpreted as meter-accurate unused solar energy.

---

# Daily Grid Import

Status:

```text
Planned
```

The PowMr inverter does not expose a reliable accumulated Grid Import counter.

EnergyHub must therefore calculate or estimate Daily Grid Import.

Grid Import may occur in several different operating scenarios.

---

## Solar Mode Fallback Grid Import

Normal Solar Mode configuration:

```text
Setting 01 → SBU
Setting 16 → OSO
```

Possible inverter behavior:

```text
Battery SOC reaches 15%
        ↓
Inverter switches house load to grid
        ↓
Solar charges battery
        ↓
Battery SOC reaches 30%
        ↓
Inverter switches house back to SBU operation
```

During the period between switching to grid and returning to SBU operation, house consumption is Grid Import.

This situation may be completely acceptable when Grid Confidence is good.

Future work:

- reliably detect when house load is supplied by the grid;
- accumulate imported house energy;
- store Daily Grid Import;
- publish Daily Grid Import through MQTT;
- add Grid Import to the Energy Statistics dashboard.

Planned entity:

```text
sensor.energyhub_daily_grid_import
```

---

## Hybrid and Panic Grid Import

Grid Import must also include electricity imported during controlled charging sessions.

Examples:

```text
Hybrid charging
→ house consumption supplied by grid
→ battery charging supplied by grid

Panic charging
→ house consumption supplied by grid
→ battery charging supplied by grid
```

Future estimation model:

```text
Daily Grid Import
=
House Load supplied by grid
+
Estimated Battery Charging Energy supplied by grid
```

The exact estimation method requires validation against real-system behavior.

Daily Grid Import is initially intended for historical and informational purposes.

It must not be treated as authoritative Decision Engine input until the estimation method is validated.

---

# Future Energy Statistics

The current 7-day Energy Statistics chart should eventually include:

```text
House Consumption
Unused Solar
Grid Import
Grid Availability
```

The exact chart title and final visual design may be adjusted when Daily Grid Import is implemented.

---

# Grid Confidence

Grid Confidence is calculated from rolling 48-hour grid availability.

Current thresholds:

```text
90–100%  → normal
60–90%   → unstable
30–60%   → risk
0–30%    → panic
```

Grid Confidence is an operational metric.

Daily Grid Availability is a historical metric.

They are related but separate concepts.

The architecture is:

```text
Grid Monitor
      │
      ▼
Grid History Service
      │
      ├── Daily Availability
      │        │
      │        ▼
      │   Daily Summary Engine
      │
      └── Rolling 48h Availability
               │
               ▼
        Grid Stability Engine
               │
               ▼
          Grid Confidence
```

Future Decision Engine behavior should use Grid Confidence to determine how aggressively EnergyHub protects battery reserve.

Example:

```text
Grid Confidence good
→ normal inverter fallback to grid may be acceptable

Grid Confidence poor
→ preserve battery reserve proactively
→ consider Hybrid or Panic charging before critical SOC
```

---

# Recovery Strategy

Status:

```text
Initial design complete
Implementation intentionally deferred
```

The current Recovery Strategy is conservative.

EnergyHub must first detect and classify failures before attempting recovery.

Core principle:

```text
Detection
    ↓
Classification
    ↓
Safe bounded recovery where appropriate
```

EnergyHub must not use universal restart logic.

---

## Inverter Recovery

Policy:

```text
EnergyHub must never automatically restart the inverter.
```

Reasons:

- the inverter owns its internal protection behavior;
- the inverter already has internal restart and recovery settings;
- different inverter faults require different responses;
- automatic restart may be unsafe for faults such as over-temperature, overload or battery problems.

Inverter warnings and faults are detection and reporting events only in Recovery v1.

---

## Battery Recovery

Policy:

```text
Battery Health anomalies
→ detect
→ report
→ no automatic recovery action
```

Battery SOC anomalies may indicate:

- BMS behavior;
- protection events;
- SOC calculation problems;
- battery communication problems.

EnergyHub must not attempt automatic battery recovery based only on these warnings.

---

## EnergyHub Recovery

Future EnergyHub self-recovery may be allowed where the failure type is understood and software recovery is considered safe.

Automatic recovery must be bounded.

Initial concept:

```text
Failure detected
        ↓
Retry and verify
        ↓
First automatic recovery attempt
        ↓
Verify result
        ↓
If still failed
        ↓
Cooldown approximately 30 minutes
        ↓
Second automatic recovery attempt
        ↓
Verify result
        ↓
If still failed
        ↓
Stop automatic recovery
        ↓
Require human attention
```

Infinite restart loops are prohibited.

The exact implementation remains future work.

---

## Home Assistant Failure Limitation

EnergyHub and Home Assistant cannot reliably report their own failure if the entire Home Assistant platform is frozen or unavailable.

Example:

```text
Home Assistant frozen
        ↓
EnergyHub unavailable
        ↓
MQTT notifications unavailable
        ↓
Home Assistant cannot report its own failure
```

Because of this, future infrastructure should include an external heartbeat or watchdog.

Possible future architecture:

```text
Home Assistant / EnergyHub
        ↓
External Heartbeat
        ↓
Independent Monitor
        ↓
External Notification
```

This remains a future infrastructure task.

---

# Current Real-System Findings

## JK BMS SOC Anomaly

Observed abnormal SOC behavior included:

```text
53% → 1%
33% → 100%
```

Further investigation identified a probable relationship with battery over-current protection.

The battery BMS maximum configured current was approximately:

```text
150 A
```

while the inverter maximum charging current was configured to:

```text
160 A
```

When solar charging exceeded the BMS protection threshold, the BMS activated protection and abnormal SOC behavior was observed.

EnergyHub now detects abnormal SOC changes through Battery Health Monitor v1.

---

## Battery Charging Current Discrepancy

During grid charging:

```text
Inverter configured charging current → 30 A

JK BMS observed current → approximately 30 A

PowMr telemetry → approximately 23–24 A
```

The approximately 20–25% discrepancy is larger than expected.

This is not currently critical for EnergyHub operation but requires future investigation.

Possible causes may include:

- different current measurement points;
- inverter telemetry interpretation;
- conversion losses;
- protocol field meaning;
- measurement calibration differences.

No conclusion has yet been reached.

---

## Persistent EEPROM Fault

Real-system QPIWS testing returned:

```text
eeprom_fault = 1
```

All other observed warning and fault flags were zero.

The inverter continued normal operation.

The meaning of this persistent flag remains unknown.

Possible explanations requiring investigation include:

- real active fault;
- historical or sticky fault;
- firmware behavior;
- protocol interpretation issue.

The warning is intentionally not hidden.

Current result:

```text
Inverter Health → warning
System Health → warning
```

until the fault is understood.

---