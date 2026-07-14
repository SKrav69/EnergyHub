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
Grid Confidence is normal; automatic Panic is not required.
```

---

# Operating Strategies

Current EnergyHub 1.0 operating strategies are:

```text
Solar
Hybrid Charging
Hybrid Grid Hold
Panic
```

Away Mode is not part of the final EnergyHub 1.0 operating strategy model. Its original concept is deferred to EnergyHub 1.1 for redesign as part of Smart Heating and flexible-load architecture.

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

Grid Import accounting is active during this SUB interval.

The current estimator combines:

```text
House Energy Supplied During SUB
+
Positive Battery SOC Gain × Nominal Battery Capacity
```

The current nominal battery capacity is 16 kWh.

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

Grid Import accounting remains active during Grid Hold because Setting 01 remains SUB.

House energy accumulated during the SUB interval is combined with positive battery SOC gain when calculating the estimated Grid Import total.

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

Evaluation order:

```text
1. Autopilot enabled
2. Current time is between 12:00 and 23:50
3. Current Operating Mode is Solar
4. Evaluate Grid Confidence
5. Evaluate Battery SOC threshold
6. Compare Solar Forecast Today with Previous Daily Consumption × 1.20
```

Current Grid Confidence branches:

## Risk or Panic

```text
Grid Confidence = risk or panic
SOC < 80%
Forecast Today < Previous Consumption × 1.20
```

Result:

```text
Panic Target → 95%
```

## Unstable

```text
Grid Confidence = unstable
SOC < 50%
Forecast Today < Previous Consumption × 1.20
```

Result:

```text
Panic Target → 80%
```

If conditions are not met, the service returns no action and an explanation.

Example:

```text
status=no_action
reason=Grid confidence=normal; automatic Panic is not required
```

---

# Away and Smart Heating

Away Mode is not part of the final EnergyHub 1.0 Decision Engine.

The original concept mixed:

- occupancy;
- solar-surplus heating;
- battery reserve;
- cheap-tariff opportunities;
- flexible-load control.

This work is deferred to EnergyHub 1.1.

The future goal is a broader Smart Heating and flexible-load architecture rather than a simple Away state.

The ownership principle remains valid:

> EnergyHub automatically stops a household load only when EnergyHub previously started it.

---

# Autopilot

Autopilot controls whether EnergyHub may automatically execute strategy decisions.

Current user control:

```text
input_boolean.energyhub_autopilot
```

Autopilot is separate from:

- Operating Mode;
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
- Grid Availability;
- Grid Import Estimated.

Hybrid evaluation data is also retained for explainability:

- final Hybrid decision;
- decision reason;
- Battery SOC used;
- House Consumption used;
- Battery Refill Required;
- Total Energy Required;
- Solar Forecast Tomorrow used.

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
→ Hybrid Charging or Panic; additional context is required

SUB + OSO
→ Hybrid Grid Hold
```

Additional context may be required to distinguish strategies that use identical inverter settings.

Restart reconstruction should live in Operating Mode or Recovery architecture.

It should not become another large conditional block in `main.py`.

---

# Configurable Strategy Parameters

EnergyHub 1.2 should centralize trusted strategy parameters.

Candidates include:

- cheap-tariff start and end times;
- Hybrid evaluation time;
- Hybrid target SOC;
- Hybrid morning exit time;
- nominal battery capacity;
- grid charging current;
- Panic evaluation window;
- Panic forecast margin;
- Panic SOC thresholds;
- Panic target SOC values.

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

EnergyHub 1.0 Decision Engine feature development is complete.

Current priorities are:

1. run the system in Autopilot under real household conditions;
2. perform a full post-1.0 code review;
3. clean duplicate and obsolete MQTT Discovery entities;
4. resolve entity naming conflicts such as `*_2`;
5. verify Grid Import midnight rollover and historical continuity;
6. validate Hybrid and Panic behavior with real data;
7. improve restart strategy reconstruction;
8. redesign and standardize dashboards and charts;
9. fix bugs discovered during the 1.0 test-drive period.

Future milestone ownership:

```text
1.1
→ Smart Loads, Smart Heating / Away rethink, EV charging template, test-drive improvements

1.2
→ Configurable strategy parameters

1.3
→ Recovery & Resilience
```

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