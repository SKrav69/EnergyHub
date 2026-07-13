# EnergyHub Decision Engine

> The Decision Engine determines what EnergyHub should do, explains why, and delegates physical execution to the appropriate control service.

---

# Purpose

EnergyHub should not react only to individual sensor changes.

It should evaluate the current energy situation using:

- current system state;
- historical energy data;
- solar forecasts;
- Grid Confidence;
- Battery SOC;
- Battery Health;
- Inverter Health;
- current Operating Mode;
- Autopilot state;
- user controls;
- household strategy.

The Decision Engine should answer:

```text
What should EnergyHub do?
Why should EnergyHub do it?
What information caused the decision?
What should happen next?
```

---

# Current EnergyHub 1.0 Decision Architecture

EnergyHub 1.0 has moved beyond recommendation-only behavior.

Current architecture:

```text
System Facts
      ↓
Decision Services
      ↓
Decision + Reason + Target
      ↓
Autopilot / User Request
      ↓
Operating Mode Service
      ↓
Inverter Controller
      ↓
PowMr Commands
      ↓
Verification
      ↓
Confirmed Operating Mode
```

Decision services do not directly send inverter commands.

The Inverter Controller owns physical execution.

---

# Current Decision Services

EnergyHub currently separates decision logic by responsibility.

```text
Hybrid Decision Engine
        +
Panic Decision Engine
        +
Operating Mode Logic
        +
Autopilot
```

Future decision services may manage:

- flexible loads;
- heating strategy;
- EV charging;
- battery reserve optimization;
- dynamic tariffs;
- occupancy-aware behavior.

A single large universal Decision Engine should not replace focused services.

---

# Decision Inputs

Current decision inputs include:

- Battery SOC;
- Grid Confidence;
- Grid Availability history;
- PV Power;
- Solar Forecast Today;
- Solar Forecast Tomorrow;
- Daily House Consumption;
- current Operating Mode;
- Autopilot state;
- current time.

Additional system facts include:

- Battery Health;
- Telemetry Freshness;
- Inverter Health;
- System Health;
- Grid Import Estimated.

Not every fact is currently used by every decision service.

Decision services should consume only the information they need.

---

# Decision Outputs

A decision should provide enough information to understand and execute it.

Typical output:

```text
Decision
+
Reason
+
Target SOC when applicable
```

Examples:

```text
Decision:
Solar

Reason:
Tomorrow's solar forecast is sufficient to restore expected energy use.
```

```text
Decision:
Hybrid

Reason:
Tomorrow's forecast is insufficient for expected house consumption and battery refill.

Target SOC:
80%
```

```text
Decision:
No Action

Reason:
PV power is still sufficient: 453 W >= 200 W.
```

---

# Operating Strategies

Current EnergyHub operating strategies are:

```text
Solar
Hybrid Charging
Hybrid Grid Hold
Panic
Away
```

Additional temporary states include:

```text
Transitioning
Transition Failed
Unknown
```

These strategies replace the old Summer/Winter operating-mode model.

---

# Solar

Solar is the default operating strategy.

Current inverter configuration:

```text
Setting 01 → SBU
Setting 16 → OSO
```

Purpose:

- prioritize normal solar/battery operation;
- avoid unnecessary Grid Import;
- use the battery according to normal inverter behavior;
- provide the default state after controlled strategies end.

Solar is the normal starting point for automatic Panic evaluation.

---

# Hybrid Strategy

Hybrid is the planned night-energy strategy.

Its purpose is to use cheap night grid power when the next day's solar forecast is insufficient for expected household energy needs.

Hybrid contains two operating phases:

```text
Hybrid Charging
        ↓
Hybrid Grid Hold
        ↓
Solar
```

---

# Hybrid Decision Engine

`hybrid_decision.py` owns the daily Hybrid decision.

The decision is evaluated using:

- current Battery SOC;
- nominal battery capacity;
- current-day House Consumption;
- Solar Forecast Tomorrow.

Battery refill requirement:

```text
Battery Refill Required
=
Battery Capacity × Missing SOC Percentage
```

Required energy:

```text
Required Energy
=
Today's House Consumption
+
Battery Refill Required
```

Decision:

```text
Forecast Tomorrow >= Required Energy
→ Solar

Forecast Tomorrow < Required Energy
→ Hybrid
```

The Hybrid Decision Engine returns an explainable decision.

It does not directly change inverter settings.

---

# Hybrid Charging

When Hybrid is selected, EnergyHub enters Hybrid Charging.

Current inverter strategy:

```text
Setting 01 → SUB
Setting 16 → SNU
```

Current target:

```text
Battery SOC → 80%
```

Purpose:

- power the house from the grid;
- charge the battery from available charging sources;
- use cheap night tariff energy;
- build sufficient battery reserve for the following day.

Grid Import during this phase is estimated as:

```text
House Load
+
Battery Charging Power
```

---

# Hybrid Grid Hold

When the Hybrid charging target is reached before morning, EnergyHub enters Hybrid Grid Hold.

Current inverter strategy:

```text
Setting 01 → SUB
Setting 16 → OSO
```

Purpose:

- stop planned utility battery charging;
- keep the house on cheap night grid power;
- preserve the charged battery;
- wait until the morning Solar transition.

Current morning exit time:

```text
07:00
```

At the end of Hybrid Grid Hold:

```text
Hybrid Grid Hold
        ↓
Solar
```

Grid Import during Grid Hold is estimated as:

```text
House Load
```

---

# Panic Strategy

Panic is a daytime protective charging strategy.

Its purpose is to increase battery reserve when EnergyHub detects increased energy risk.

Panic may be:

- automatically requested by the Panic Decision Engine;
- manually requested by the user.

Current inverter strategy:

```text
Setting 01 → SUB
Setting 16 → SNU
```

When the target SOC is reached:

```text
Panic
    ↓
Solar
```

If Panic remains active at the daily Hybrid evaluation time, the system may transition into the planned Hybrid strategy according to current operating policy.

---

# Panic Decision Engine

Automatic Panic evaluation currently runs:

```text
Every 15 minutes
Between 12:00 and 23:50
```

Evaluation is skipped when the current strategy is not appropriate for automatic Panic entry.

Common prerequisites:

```text
PV < 200 W

AND

Forecast Today
<
Previous Daily House Consumption × 1.20
```

Current Grid Confidence branches:

## Risk

```text
Grid Confidence = risk
PV < 200 W
Forecast Today < Previous Consumption × 1.20
SOC < 80%
```

Result:

```text
Panic Target → 95%
```

## Unstable

```text
Grid Confidence = unstable
PV < 200 W
Forecast Today < Previous Consumption × 1.20
SOC < 50%
```

Result:

```text
Panic Target → 80%
```

If conditions are not met, the service returns no action and an explanation.

Example:

```text
status=no_action
reason=PV power is still sufficient: 453 W >= 200 W
```

---

# Away Strategy

Away Mode allows EnergyHub to use flexible household loads while the house is unoccupied.

Current v1 behavior controls the first-floor heat pump.

Start conditions:

```text
Away Mode ON
Temperature < 18°C
SOC > 95%
PV > 200 W
```

Stop conditions:

```text
Temperature >= 23°C
OR
SOC <= 81%
```

After EnergyHub starts the heat pump, temporary PV fluctuations do not stop it.

Current ownership helper:

```text
input_boolean.energyhub_away_heat_pump_active
```

Rule:

> EnergyHub automatically stops a household load only when EnergyHub previously started it.

Away Mode v1 currently uses Home Assistant automation.

Future versions may move more flexible-load strategy into dedicated EnergyHub decision services.

---

# Autopilot

Autopilot controls whether EnergyHub may automatically execute strategy decisions.

Current user control:

```text
input_boolean.energyhub_autopilot
```

Autopilot is separate from:

- Operating Mode;
- Away Mode;
- manual Panic requests.

Architecture:

```text
Decision
    ↓
Autopilot Enabled?
    ↓
Yes → Execute Through Control Services

No → Do Not Automatically Execute
```

Disabling Autopilot does not remove monitoring, telemetry, history, or explainability.

---

# Automatic and Manual Decisions

EnergyHub distinguishes between decision origin and physical execution.

## Automatic Decisions

Examples:

- daily Hybrid decision;
- automatic Panic evaluation;
- target completion;
- morning return to Solar.

Automatic execution requires the appropriate policy and Autopilot state.

## Manual Requests

Examples:

- Start Panic;
- request Solar;
- enable Away Mode;
- disable Autopilot.

Manual requests still use the normal control architecture.

They should not bypass the Inverter Controller.

---

# Operating Mode

Operating Mode represents the confirmed EnergyHub strategy.

Current states:

```text
solar
hybrid_charging
hybrid_grid_hold
panic
away
transitioning
transition_failed
unknown
```

Operating Mode should include:

```text
mode
+
reason
```

A requested strategy is not automatically a confirmed Operating Mode.

Architecture:

```text
Request
    ↓
Transitioning
    ↓
Inverter Commands
    ↓
Verification
    ↓
Confirmed Mode
```

If execution or verification fails:

```text
Transition Failed
```

---

# Inverter Controller

The Inverter Controller translates high-level strategy requests into PowMr-specific execution.

Current verified mappings:

```text
POP01 → SUB
POP02 → SBU

PCP01 → SNU
PCP02 → OSO
PCP03 → CSO
```

Responsibilities:

- command ordering;
- Setting 01 changes;
- Setting 16 changes;
- ACK handling;
- bounded retries;
- QPIRI verification where available;
- transition status;
- transition failure;
- settling delays.

Decision services must not duplicate this behavior.

---

# Grid Reliability

Grid Reliability is independent from Operating Mode.

EnergyHub maintains:

- Grid History;
- Grid Availability;
- Grid Confidence.

Current Grid Confidence levels:

```text
normal
unstable
risk
panic
```

Current thresholds are derived from rolling Grid Availability history.

Grid Confidence influences decisions.

It does not directly send inverter commands.

Architecture:

```text
Grid Monitor
      ↓
Grid History
      ↓
Grid Stability Engine
      ↓
Grid Confidence
      ↓
Decision Services
```

Recent outages should have greater strategic importance than older outages.

The exact weighting model may evolve as real-world data accumulates.

---

# Daily Summary

The Daily Summary Service creates stable historical facts for decisions and dashboards.

Current inputs include:

- Daily House Consumption;
- Solar Forecast Today;
- Solar Forecast Tomorrow;
- Daily Solar Surplus Estimated.

Current stored daily facts include:

- House Consumption;
- Solar Forecast;
- Solar Surplus Estimated;
- Grid Availability.

The Hybrid Decision Engine consumes current and historical energy facts.

The Panic Decision Engine consumes forecast and previous-consumption facts.

Decision services do not own Daily Summary persistence.

---

# Battery Health

Battery Health is independent from Battery Strategy.

Current Battery Health monitoring includes SOC jump detection.

Current concept:

```text
SOC jump >= 2%
within the monitored SOC range
→ warning
```

The exact technical thresholds should remain configurable or code-owned according to hardware requirements.

Recent abnormal real-system behavior included:

```text
53% → 1%
33% → 100%
```

Future Battery Health inputs may include:

- individual cell voltages;
- minimum cell voltage;
- maximum cell voltage;
- cell delta;
- battery temperatures;
- BMS alarms;
- protection states;
- balancing status.

Decision services should consume normalized Battery Health.

They should not interpret JK BMS protocol data directly.

---

# Inverter Health

Current Inverter Health monitoring uses inverter warning information.

The Decision Engine should consume normalized health information where needed.

It should not directly query protocol warning commands.

Architecture:

```text
PowMr Integration
      ↓
Inverter Health Monitor
      ↓
Inverter Health
      ↓
Decision Services
```

Health detection and recovery execution remain separate responsibilities.

---

# System Health

System Health aggregates subsystem health.

Current health architecture includes:

```text
Communication Health
Battery Health
Telemetry Freshness
Inverter Health
        ↓
System Health
```

Future decisions may use System Health as a prerequisite or safety gate.

A health warning should not silently cause an unrelated strategy transition.

---

# Decision Priorities

When objectives conflict, EnergyHub follows these priorities:

1. Safety.
2. House protection.
3. Occupant comfort.
4. System reliability.
5. Grid resilience.
6. Battery health.
7. Energy independence.
8. Cost optimization.
9. Solar utilization.

Optimization must not override safe and reliable operation.

---

# Flexible Loads

Current and future flexible loads include:

- heat pumps;
- boiler;
- EV charging;
- smart plugs.

Current implementation:

```text
Away Mode
→ First-Floor Heat Pump
```

Future decision services may produce intentions such as:

```text
Allow Water Heating
```

```text
Prioritize EV Charging
```

```text
Preserve Solar Energy for House Comfort
```

Device-specific automation or control services should execute these intentions.

---

# Notifications

EnergyHub owns significant decision events.

Home Assistant owns delivery.

Current architecture:

```text
Decision / Transition Event
        ↓
energyhub/event/notification
        ↓
Home Assistant Automation
        ↓
Persistent Notification
Mobile Notification
Future Telegram Notification
```

Notifications should explain significant automatic behavior.

Useful notification content:

```text
What happened?
Why?
What is the target?
What happens next?
```

Routine telemetry and expected no-action evaluations should remain primarily in logs rather than generating user notifications.

---

# Explainability

Every significant decision should preserve enough information to explain:

```text
What is EnergyHub doing?
Why is EnergyHub doing it?
Which facts caused the decision?
What target is being pursued?
What will happen next?
```

Current examples:

```text
Operating Mode
+
Operating Mode Reason
```

```text
Panic Decision
+
Panic Decision Reason
```

Future decision services should follow the same pattern.

---

# Logging

Decision logs should describe behavior rather than only implementation details.

Good:

```text
Automatic Panic evaluation:
status=no_action
reason=PV power is still sufficient: 453 W >= 200 W
```

Good:

```text
Starting transition to Solar:
Setting 01=SBU
Setting 16=OSO
```

Good:

```text
Hybrid selected:
forecast tomorrow is insufficient for expected consumption and battery refill
```

Less useful alone:

```text
POP02 ACK
```

Protocol details may be logged when useful, but normal logs should preserve decision context.

---

# Real-System Validation

Real-system observations have priority over assumptions.

Development cycle:

```text
Hypothesis
    ↓
Manual Test or Implementation
    ↓
Real-System Observation
    ↓
Validation
    ↓
Architecture Decision
    ↓
Documentation
```

Examples already validated on the real inverter include:

- Setting 01 switching;
- Setting 16 switching;
- SBU/SUB transitions;
- OSO/SNU behavior used by current strategies;
- QPIRI verification behavior.

Unvalidated assumptions should remain clearly identified as future work.

---

# Failure Behavior

Decision failure and execution failure are different.

## Decision Failure

Examples:

- missing input;
- stale telemetry;
- unknown Operating Mode;
- unavailable forecast.

Expected behavior:

```text
Do Not Execute Unsafe Decision
+
Publish or Log Reason
```

## Execution Failure

Examples:

- command rejected;
- verification mismatch;
- communication failure;
- transition timeout.

Expected behavior:

```text
Bounded Retry
    ↓
Verification
    ↓
Success or Transition Failed
```

Recovery behavior belongs to the Recovery architecture.

---

# Restart Strategy Reconstruction

A high-priority future improvement is reconstructing EnergyHub strategy after restart from verified inverter settings.

Intended mapping:

```text
SBU + OSO
→ Solar

SUB + SNU
→ Hybrid Charging

SUB + OSO
→ Hybrid Grid Hold
```

Additional context may be required to distinguish strategies that use identical inverter settings.

Restart reconstruction should live in Operating Mode or Recovery architecture.

It should not become another large conditional block in `main.py`.

---

# Configurable Strategy Parameters

EnergyHub 1.1 should centralize trusted strategy parameters.

Candidates include:

- Hybrid evaluation time;
- Hybrid target SOC;
- Hybrid morning exit time;
- Panic PV threshold;
- Panic forecast margin;
- Panic SOC thresholds;
- Panic target SOC values;
- Away Mode SOC thresholds;
- Away Mode temperature thresholds;
- Away Mode PV threshold.

Architecture:

```text
Configuration Source
        ↓
Validation and Safe Bounds
        ↓
Strategy Configuration
        ↓
Decision Services
```

Technical hardware limits must remain separate from household strategy preferences.

---

# Future Decision Development

Future development should build on the current focused-service architecture.

Likely areas:

## Better Hybrid Decisions

Possible future inputs:

- multi-day forecasts;
- recent consumption averages;
- forecast uncertainty;
- Grid Confidence weighting;
- seasonal consumption behavior.

## Flexible Load Decisions

Possible outputs:

- heat now;
- heat later;
- heat only from surplus;
- charge EV;
- delay EV charging;
- heat water;
- preserve battery.

## Occupancy-Aware Decisions

Possible inputs:

- Away Mode;
- motion history;
- calendar information;
- expected arrival time.

## Dynamic Tariffs

Possible inputs:

- hourly energy prices;
- export prices;
- tariff windows.

## Advanced Battery Strategy

Possible inputs:

- Battery Health;
- BMS data;
- temperature;
- degradation considerations;
- expected outage risk.

New decision capabilities should be introduced only when they solve real household problems.

---

# Architectural Principle

EnergyHub decision code speaks strategy language.

Example:

```text
Enter Hybrid with target SOC 80%.
```

The Inverter Controller speaks control language.

Example:

```text
Set Setting 16 to SNU.
Set Setting 01 to SUB.
Verify configuration.
```

The PowMr integration speaks device language.

Example:

```text
PCP01
POP01
QPIRI
```

Architecture:

```text
System Facts
      ↓
Decision Services
      ↓
Strategy Intentions
      ↓
Operating Mode / Control Services
      ↓
Inverter Controller
      ↓
PowMr Integration
      ↓
Physical Inverter
```

This separation provides:

- explainable decisions;
- safer testing;
- clear ownership;
- easier recovery design;
- a path toward future hardware support.

---

# Current Development Priorities

The Decision Engine is no longer a future recommendation-only subsystem.

Current priorities are:

1. test Grid Import in Solar, Hybrid Charging, and Hybrid Grid Hold;
2. complete real-world validation of Hybrid behavior;
3. stabilize Hybrid Decision execution;
4. reconstruct strategy correctly after restart;
5. implement Recovery Strategy responsibilities;
6. improve notification quality;
7. continue Away Mode development;
8. centralize configurable strategy parameters for EnergyHub 1.1;
9. polish dashboards and logs after behavior is stable.

---

# Decision Engine Principle

EnergyHub should behave like an experienced energy manager.

It should:

```text
Observe
    ↓
Remember
    ↓
Evaluate
    ↓
Decide
    ↓
Explain
    ↓
Execute Safely
    ↓
Verify
    ↓
Recover When Appropriate
    ↓
Learn from Real-System Behavior
```

The goal is not maximum automation.

The goal is reliable, explainable automation that reduces homeowner decisions while preserving safety, control, and understanding.