# EnergyHub Decision Engine

> The Decision Engine is the brain of EnergyHub.

Its purpose is to determine how the house should operate while maximizing comfort, minimizing energy cost and maintaining resilience during uncertain grid conditions.

---

# Core Philosophy

EnergyHub should not react only to current events.

Instead, it should continuously evaluate the most appropriate operating strategy using:

- current system state;
- historical data;
- weather and solar forecasts;
- household behaviour;
- grid reliability;
- battery health;
- user preferences;
- manual overrides.

EnergyHub should always answer one question:

> "What is the best decision for the house right now?"

Every significant recommendation or decision should also answer:

> "Why did EnergyHub make this decision?"

---

# Decision Engine v1

The first Decision Engine implementation should be recommendation-only.

It may produce:

- Recommended Mode;
- Recommendation;
- Reason;
- Recommended Action.

Example:

```text
Recommended Mode: Winter

Recommendation:
Charge battery during the night tariff.

Reason:
Low solar forecast tomorrow and reduced grid confidence.

Recommended Action:
Enable scheduled grid charging.
```

The first Decision Engine version should not automatically execute inverter commands.

Recommendations should first be observed and validated against real household behaviour.

Automatic control should be introduced progressively only after:

- recommendations have been validated;
- inverter control commands have been tested safely;
- charging-source behaviour has been confirmed;
- recovery behaviour is understood.

---

# Decision Layers

The Decision Engine is composed of independent decision layers.

Each layer has a single responsibility.

Example:

```text
System Health

↓

Battery Health

↓

Grid Reliability

↓

Season Strategy

↓

Energy Forecast

↓

Battery Strategy

↓

Load Priorities

↓

Recommended Actions
```

Each layer contributes information to the final recommendation.

A failure or uncertainty in one layer should not silently produce an unsafe decision.

---

# Decision Inputs

Decision Engine inputs may include:

- Battery SOC;
- Battery Health;
- Grid Confidence;
- Grid Availability;
- Solar Forecast Today;
- Solar Forecast Tomorrow;
- House Consumption Previous Day;
- Solar Surplus Previous Day;
- Indoor temperatures;
- Outdoor temperature;
- Electricity tariff;
- Current Operating Mode;
- Manual overrides.

Future inputs may include:

- individual battery cell voltages;
- cell voltage delta;
- BMS alarms;
- balancing status;
- EV battery SOC;
- occupancy prediction;
- calendar information;
- historical household behaviour.

---

# Dashboard Architecture

The Developer Dashboard separates current system state from information and recommendations.

## EnergyHub Status

Answers:

```text
What is happening now?

Is the system healthy?
```

Current information includes:

- Communication Status;
- Battery SOC;
- Battery Charging Current;
- Battery Discharge Current;
- House Load;
- PV1 Power;
- Grid Voltage.

Future information may include:

- Current Operating Mode;
- Battery Health;
- Inverter Health.

---

## EnergyHub Intelligence

Answers:

```text
What does EnergyHub know?

What does EnergyHub recommend?

Why?
```

Current information includes:

- Grid Confidence;
- Grid Available 24h;
- Grid Available 48h;
- Consumption Yesterday;
- Solar Surplus Yesterday;
- Solar Forecast Today;
- Solar Forecast Tomorrow.

Future information should include:

- Recommended Mode;
- Recommendation;
- Reason;
- Recommended Action.

The intended relationship is:

```text
EnergyHub Status
→ Current Mode

EnergyHub Intelligence
→ Recommended Mode
→ Reason
→ Recommended Action
```

When Current Mode and Recommended Mode differ, EnergyHub should clearly explain why.

---

# Operating Modes

## Summer

Primary objective:

Use available solar energy efficiently.

Typical behaviour:

- Battery used normally.
- Flexible loads encouraged.
- Planned grid charging disabled.
- Solar-only battery charging preferred.

Current candidate charging-source configuration:

```text
OSO
```

---

## Winter

Primary objective:

Guarantee comfort while minimizing cost and maintaining sufficient battery reserve.

Typical behaviour:

- Night tariff charging may be enabled.
- Battery reserve may be increased.
- Heating may be optimized.
- Solar forecast influences charging decisions.
- Grid Confidence influences battery strategy.

Current candidate charging-source configuration during scheduled grid charging:

```text
SNU
```

SNU behavior requires additional real-system validation before automatic control is implemented.

---

## Away

Primary objective:

Protect the house with minimum unnecessary energy consumption.

Typical behaviour:

- Reduced heating.
- Appropriate battery reserve.
- Flexible loads disabled or restricted.
- House protection remains active.

---

## Panic

Primary objective:

Maximize resilience.

Typical behaviour:

- Battery maintained close to 100%.
- Grid charging allowed immediately when appropriate.
- Only essential loads guaranteed.
- Flexible loads disabled unless explicitly permitted.

Current candidate charging-source configuration:

```text
SNU
```

Panic Mode charging behavior must remain conservative and explainable.

---

# Charging-Source Strategy

The current PowMr firmware exposes three usable charging-source modes:

```text
OSO
CSO
SNU
```

`CUB` is not available on the current inverter firmware.

---

## OSO

Meaning:

```text
Only Solar
```

Current intended use:

```text
Normal Summer operation
```

Battery charging is performed from solar energy only.

---

## CSO

Meaning:

```text
Solar First
```

Real-system testing showed that CSO is not suitable for planned continuous grid charging.

Observed behaviour:

```text
Night
PV generation = 0
Utility charging active

↓

PV generation begins

↓

Utility charging current significantly decreases
```

Because of this behaviour, CSO is no longer the primary candidate for Winter scheduled grid charging or Panic charging.

---

## SNU

SNU is the current candidate for charging scenarios where both utility and solar charging should be available.

Current intended use:

```text
Winter scheduled grid charging
Panic charging
```

Expected strategy:

```text
Summer
→ OSO

Winter scheduled grid charging
→ SNU

Panic charging
→ SNU
```

The expected SNU behaviour is:

```text
Utility charging
+
Available solar charging
=
Combined battery charging
```

subject to:

- maximum utility charging current;
- maximum total charging current;
- battery charging limits;
- inverter firmware behaviour.

This behaviour has not yet been fully validated on the real inverter.

EnergyHub must not assume that SNU maintains a fixed utility charging current while adding available PV power until real-system testing confirms the exact behaviour.

The charging-source strategy therefore remains:

```text
OSO ↔ SNU
```

pending final SNU validation.

---

# Automatic vs Manual Decisions

EnergyHub distinguishes between automatic and manual decisions.

## Automatic Modes

```text
Summer
Winter
Away
```

These modes may eventually be changed automatically.

Automatic mode switching should be introduced only after recommendation-only Decision Engine behaviour has been validated.

---

## Manual Mode

```text
Panic
```

If Panic Mode is activated manually:

EnergyHub never exits Panic automatically.

Instead, it provides recommendations.

Example:

```text
Current Mode:
Panic

Recommended Mode:
Winter

Reason:
Grid Confidence has returned to normal and battery reserve is sufficient.
```

The homeowner decides when normal automation resumes.

---

# Grid Reliability

Grid Reliability is independent from Operating Modes.

Current Grid Confidence thresholds:

```text
90–100%  → normal
60–90%   → unstable
30–60%   → risk
0–30%    → panic
```

Grid Confidence is calculated from rolling 48-hour Grid Availability.

Grid Reliability influences:

- Battery Strategy;
- charging recommendations;
- battery reserve recommendations;
- future Operating Mode recommendations.

Grid Reliability does not directly change Operating Mode.

The Decision Engine consumes Grid Confidence as an input.

It does not calculate or own Grid History.

Architecture:

```text
Grid Monitor
      │
      ▼
Grid History
      │
      ▼
Grid Stability Engine
      │
      ▼
Grid Confidence
      │
      ▼
Decision Engine
```

---

# Battery Health

Battery Health is independent from Battery Strategy.

The Battery Health Monitor should detect abnormal battery behaviour and provide stable health information to the Decision Engine.

Initial Battery Health feature:

```text
SOC Jump Detection
```

Initial detection concept:

```text
SOC change >= 3%
→ warning

SOC change >= 10%
→ critical
```

Thresholds require validation against real battery behaviour.

Recent abnormal SOC behaviour included:

```text
53% → 1%
33% → 100%
```

Future Battery Health inputs may include:

- Battery SOC;
- Battery Current;
- Battery Voltage;
- individual cell voltages;
- minimum cell voltage;
- maximum cell voltage;
- cell voltage delta;
- battery temperatures;
- BMS alarms;
- protection states;
- balancing status.

Target architecture:

```text
PowMr Telemetry ────────┐
                        │
                        ▼
                Battery Health Monitor
                        │
                        ▼
                  Battery Health
                        │
                        ▼
                  Decision Engine

JK BMS Adapter ─────────┘
```

The Decision Engine should consume Battery Health information.

It should not directly interpret JK BMS protocol data.

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

Safety and reliable system operation always have priority over optimization.

---

# Flexible Loads

Flexible loads may include:

- Heat pumps;
- Boiler;
- EV charging;
- Smart plugs.

The Decision Engine determines when these loads should be allowed or encouraged to operate.

The Decision Engine should initially produce intentions.

Example:

```text
Recommendation:
Enable flexible loads.

Reason:
Battery SOC is high and significant solar surplus is forecast.
```

Device-specific services translate these intentions into future hardware actions.

---

# Daily Decision Cycle

Every day EnergyHub performs a complete evaluation.

Inputs may include:

- Battery SOC;
- Battery Health;
- Grid Confidence;
- Solar Forecast Today;
- Solar Forecast Tomorrow;
- House Consumption Previous Day;
- Solar Surplus Previous Day;
- Indoor temperatures;
- Outdoor temperature;
- Electricity tariff;
- Current Operating Mode;
- Manual overrides.

The Decision Engine then determines:

- Recommended Operating Mode;
- Battery Strategy;
- Heating Strategy;
- Flexible Load Strategy;
- Recommended Actions.

The selected recommendation remains active until the next evaluation or until significant new information requires reevaluation.

Future versions may support event-driven reevaluation when important system state changes occur.

---

# Daily Summary Engine

The Daily Summary Engine runs once per day before daily source sensors reset.

Responsibilities:

- Store House Consumption.
- Store Solar Forecast.
- Store Solar Surplus Estimated.
- Store Grid Availability.
- Publish historical MQTT sensors.
- Maintain persistent daily history.

Purpose:

Provide stable daily historical facts for dashboards and future Decision Engine analytics.

Architecture:

```text
Home Assistant
      │
      ▼
Daily Summary Inputs
      │
      ▼
Daily Summary Engine
      │
      ├── Persistent History
      │
      └── MQTT Sensors
               │
               ▼
         Decision Engine
```

The Decision Engine consumes Daily Summary facts.

It does not create historical data.

---

# Notifications

EnergyHub communicates important decisions and abnormal system conditions.

Examples:

- Operating Mode recommendation changed.
- Current Mode differs from Recommended Mode.
- Grid Confidence decreased.
- Battery reserve should be increased.
- Night charging is recommended.
- Manual action is recommended.
- Abnormal Battery SOC change detected.
- Battery Health degraded.
- Inverter warning or fault detected.
- Recovery action performed.

Notifications should explain the reason behind every significant recommendation or action.

Example:

```text
Recommendation:
Increase battery reserve.

Reason:
Grid Confidence changed from normal to unstable and tomorrow's solar forecast is low.
```

---

# Inverter Health

Future Decision Engine versions may consume Inverter Health information.

Possible inputs:

- Communication Status;
- inverter warnings;
- inverter faults;
- unexpected inverter restart information.

The Decision Engine should not directly query PI30MAX warning or fault commands.

Architecture:

```text
PowMr Adapter
      │
      ▼
Inverter Health Monitor
      │
      ├── Health State
      ├── MQTT Sensors
      └── Alerts
               │
               ▼
         Decision Engine
```

Hardware communication and health analysis should remain separate from decision logic.

---

# Future Inputs

Future versions may incorporate:

- Weather forecast;
- Solcast forecast;
- Dynamic electricity pricing;
- EV battery SOC;
- Calendar information;
- Occupancy prediction;
- Historical household behaviour;
- direct BMS information through Battery Health Monitor;
- Inverter Health information.

The Decision Engine should remain extensible without requiring architectural changes.

---

# Architectural Principle

EnergyHub does not control devices directly from the Decision Engine.

The Decision Engine produces intentions.

Example:

```text
Maintain battery above 80%.
```

rather than:

```text
Execute inverter command XYZ.
```

Another example:

```text
Enable scheduled grid charging.
```

rather than:

```text
Change PowMr charging-source mode to SNU.
```

Hardware adapters and control services translate intentions into device-specific commands.

Architecture:

```text
System Facts
      │
      ▼
Decision Engine
      │
      ▼
Intentions
      │
      ▼
Control Services
      │
      ▼
Hardware Adapters
      │
      ▼
Devices
```

This separation allows:

- hardware independence;
- safer testing;
- explainable decisions;
- easier future hardware support;
- clear responsibility boundaries.

---

# Explainability Principle

The homeowner should always be able to understand:

```text
What is EnergyHub doing?

Why is EnergyHub doing it?

What information caused the decision?

What will happen next?
```

The intended dashboard relationship is:

```text
EnergyHub Status
      │
      └── Current Mode

EnergyHub Intelligence
      │
      ├── Recommended Mode
      ├── Recommendation
      ├── Reason
      └── Recommended Action
```

EnergyHub should never silently make significant operational changes without maintaining enough information to explain the reason.

---

# Validation Principle

Real-system observations have priority over assumptions about inverter behaviour.

Example:

The initial charging-source strategy considered:

```text
OSO ↔ CSO
```

Real-system CSO testing showed that utility charging significantly decreased when PV generation started.

The strategy was therefore reconsidered as:

```text
OSO ↔ SNU
```

SNU remains pending real-system validation.

The general development principle is:

```text
Hypothesis
    ↓
Implementation or Manual Test
    ↓
Real-System Observation
    ↓
Validation
    ↓
Architecture Decision
    ↓
Documentation
```

Unvalidated assumptions must be clearly identified as hypotheses.

---

# Development Strategy

Decision Engine development should progress through controlled stages.

## Stage 1 — Reliable Facts

EnergyHub services create stable operational and historical facts.

Examples:

- Telemetry;
- Communication Health;
- Grid History;
- Grid Confidence;
- Daily Summary;
- Battery Health;
- Inverter Health.

## Stage 2 — Recommendations

Decision Engine produces:

- Recommended Mode;
- Recommendation;
- Reason;
- Recommended Action.

No automatic execution.

## Stage 3 — Observation and Validation

Recommendations are compared against real household behaviour.

Incorrect or unnecessary recommendations are investigated and improved.

## Stage 4 — Controlled Automation

Selected low-risk decisions may be executed automatically.

Every automatic action must remain explainable and observable.

## Stage 5 — Advanced Optimization

Future capabilities may include:

- predictive battery management;
- heating optimization;
- EV charging optimization;
- dynamic tariffs;
- occupancy prediction;
- historical behaviour analysis.

---

# Vision

EnergyHub should behave like an experienced energy manager.

It should continuously balance:

- safety;
- house protection;
- comfort;
- reliability;
- grid resilience;
- battery health;
- energy independence;
- cost;
- solar utilization.

while remaining transparent, predictable and understandable to the homeowner.

The homeowner should always be able to answer:

> "Why did EnergyHub make this decision?"

EnergyHub should evolve carefully from monitoring to reliable facts, from reliable facts to recommendations, and only then from recommendations to validated automation.