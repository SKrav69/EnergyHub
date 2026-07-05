# EnergyHub Decision Engine

> The Decision Engine is the brain of EnergyHub.

Its purpose is to determine how the house should operate while maximizing comfort, minimizing energy cost and maintaining resilience during uncertain grid conditions.

The Decision Engine does not create historical facts.

It consumes reliable facts and operational state produced by other EnergyHub services.

---

# Core Philosophy

EnergyHub should not react only to current events.

Instead, it should continuously determine the most appropriate operating strategy using:

- current system state;
- historical data;
- weather and solar forecasts;
- household behaviour;
- user preferences.

EnergyHub should always answer one question:

> "What is the best decision for the house right now?"

Every important decision should also answer:

> "Why did EnergyHub make this decision?"

---

# Architecture

The Decision Engine is built on top of EnergyHub services.

```text
PowMr
  │
  ▼
Telemetry Service
  │
  ▼
Grid Monitor
  │
  ├──────────────► Grid History
  │                       │
  │                       ├──► Grid Stability Engine
  │                       │          │
  │                       │          ▼
  │                       │    Grid Confidence
  │                       │
  │                       └──► Daily Summary Engine
  │
Home Assistant
  │
  │ Daily Summary MQTT Inputs
  ▼
Daily Summary Engine
  │
  ▼
Decision Engine
  │
  ▼
Intentions / Recommendations
  │
  ▼
Device Control Layer
```

The architectural responsibility is intentionally separated:

```text
Telemetry and Services
        │
        └── create reliable facts

Daily Summary Engine
        │
        └── creates historical daily facts

Decision Engine
        │
        └── evaluates facts and produces intentions

Device Control Layer
        │
        └── translates intentions into actions
```

---

# Decision Layers

The Decision Engine is composed of independent decision layers.

Each layer has a single responsibility.

Example:

```text
Grid Confidence

↓

Season Strategy

↓

Energy Forecast

↓

Battery Strategy

↓

Load Priorities

↓

Device Intentions
```

Each layer contributes information to the final decision.

The Decision Engine should remain modular.

A new decision input or strategy should not require redesigning the entire engine.

---

# Decision Inputs

Initial Decision Engine inputs may include:

- Battery SOC;
- Grid Confidence;
- rolling 48-hour Grid Availability;
- Daily Summary history;
- Daily House Consumption;
- Daily Solar Forecast;
- Daily Solar Surplus Estimated;
- Solar Forecast Today;
- Solar Forecast Tomorrow;
- Indoor temperatures;
- Outdoor temperature;
- Electricity tariff;
- current operating mode;
- manual overrides.

Future inputs may include:

- Daily Grid Import Estimated;
- Battery Grid Charge Estimated;
- EV battery SOC;
- calendar information;
- occupancy prediction;
- historical household behaviour;
- dynamic electricity pricing.

Not every available metric should automatically become a Decision Engine input.

Metrics with low confidence or informational-only purpose must remain outside authoritative decision logic.

---

# Decision Evaluation

The Decision Engine should support two types of evaluation.

## Scheduled Evaluation

A complete strategy evaluation is performed at a defined daily time.

The exact schedule will be determined during Decision Engine implementation.

The Daily Summary Engine already creates the previous day's historical facts before Home Assistant daily sensors reset.

The Decision Engine consumes those facts.

## Event-Driven Evaluation

Significant events may trigger an additional evaluation.

Examples:

- Grid Confidence changes;
- battery SOC crosses a critical threshold;
- grid becomes unavailable;
- grid returns;
- operating mode is changed manually;
- solar forecast changes significantly;
- occupancy state changes.

The selected strategy remains active until the next scheduled or significant event-driven evaluation.

---

# Initial Implementation Strategy

Decision Engine v1 should be recommendation-only.

It should:

- evaluate current conditions;
- determine the recommended operating mode;
- determine recommended battery strategy;
- determine recommended flexible-load strategy;
- explain the reason for each recommendation;
- publish the recommendation through MQTT.

It should not initially:

- change inverter settings automatically;
- switch heat pumps automatically based on complex energy logic;
- control EV charging;
- execute high-impact actions without validation.

Automatic execution should be introduced progressively after recommendations have been observed and validated against real household behaviour.

---

# Operating Modes

## Summer

Primary objective:

Maximize useful solar energy consumption while maintaining household comfort.

Priority:

```text
PV

↓

House

↓

Battery

↓

Heat Pumps

↓

EV

↓

Export / Unused Solar Potential
```

Typical behaviour:

- Battery used normally.
- Flexible loads encouraged when solar surplus is expected.
- Grid charging disabled under normal conditions.
- Household comfort has priority over maximizing statistics.

---

## Winter

Primary objective:

Guarantee comfort and resilience while minimizing electricity cost.

Priority:

```text
PV

↓

House

↓

Battery Reserve

↓

Night Tariff Charging

↓

Heat Pumps

↓

Comfort Optimization
```

Typical behaviour:

- Night tariff charging may be enabled.
- Battery reserve may be increased.
- Heating strategy may use weather and energy forecasts.
- Grid Confidence influences battery strategy.

---

## Away

Primary objective:

Protect the house with minimum unnecessary energy consumption.

Typical behaviour:

- Reduced heating where safe.
- Battery strategy optimized for resilience.
- Flexible loads reduced or disabled.
- Smart plugs may be controlled according to house requirements.
- Solar energy may be used to prepare the house before expected occupancy.

Future inputs may include:

- motion sensors;
- calendar information;
- user override;
- time of day;
- occupancy prediction.

---

## Panic

Primary objective:

Maximize resilience during exceptional conditions.

Typical behaviour:

- Battery maintained at a high state of charge.
- Grid charging may be allowed immediately.
- Non-critical loads may be disabled.
- Flexible loads are disabled unless explicitly permitted.
- EnergyHub prioritizes house protection and outage preparation.

Panic Mode may be activated manually or recommended because of severe system conditions.

If Panic Mode is activated manually, EnergyHub must never exit it automatically.

Instead, it may provide a recommendation.

Example:

> Recommended mode: Winter

The homeowner decides when normal automation resumes.

---

# Automatic vs Manual Decisions

EnergyHub distinguishes between recommended, automatic and manual decisions.

## Recommendation

EnergyHub determines what it believes should happen but does not execute the action.

Example:

```text
Recommended Mode: Winter

Reason:
Grid Confidence is unstable.
Solar Forecast Tomorrow is low.
Battery SOC is 42%.

Recommendation:
Charge battery during the night tariff.
```

## Automatic Decision

EnergyHub may eventually execute validated low-risk actions automatically.

Automatic control should be introduced progressively.

## Manual Override

The homeowner may override automatic behaviour.

Manual overrides must be visible to the Decision Engine and must not be silently reversed.

Panic Mode activated manually is a persistent manual override until explicitly cancelled.

---

# Grid Confidence

Grid Confidence is independent from operating modes.

It evaluates recent grid behaviour using rolling 48-hour Grid Availability history.

Current levels:

```text
90–100%  → normal
60–90%   → unstable
30–60%   → risk
0–30%    → panic
```

Grid Confidence influences Decision Engine recommendations and battery strategy.

It does not directly change the operating mode.

Example:

```text
Operating Mode: Winter

Grid Confidence: unstable

Battery Strategy:
Increase reserve and consider night tariff charging.
```

Daily Grid Availability and Grid Confidence are separate concepts.

Daily Grid Availability is a historical daily fact stored by the Daily Summary Engine.

Grid Confidence is a current operational assessment produced by the Grid Stability Engine.

---

# Decision Priorities

When objectives conflict, EnergyHub follows these priorities:

1. Safety
2. House protection
3. Occupant comfort
4. Grid resilience
5. Energy independence
6. Cost optimization
7. Solar utilization

These priorities are intentionally ordered.

EnergyHub should never sacrifice safety, house protection or reasonable occupant comfort only to improve energy statistics.

---

# Flexible Loads

Flexible loads may include:

- Heat pumps;
- boiler;
- EV charging;
- smart plugs.

EnergyHub determines when these loads should be recommended or permitted to operate.

Flexible-load decisions may consider:

- current operating mode;
- Battery SOC;
- Grid Confidence;
- Solar Forecast;
- Daily Solar Surplus history;
- electricity tariff;
- household occupancy;
- user preferences.

The Decision Engine produces intentions.

The device control layer executes device-specific actions.

---

# Daily Summary Engine

The Daily Summary Engine is a separate EnergyHub service.

Status:

```text
v1 Complete
```

Its purpose is to create stable historical daily facts for:

- dashboards;
- historical analysis;
- future Decision Engine evaluations.

Current responsibilities:

- store Daily House Consumption;
- store Daily Solar Forecast;
- store Daily Solar Surplus Estimated;
- store Daily Grid Availability;
- persist daily history;
- publish EnergyHub Daily Summary MQTT sensors.

Current persistence:

```text
/data/daily_summary.json
```

Current EnergyHub entities:

```text
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_forecast
sensor.energyhub_daily_solar_surplus_estimated
sensor.energyhub_daily_grid_availability
```

The Daily Summary Engine receives selected Home Assistant values through retained MQTT messages.

Current input topics:

```text
energyhub/input/ha/daily_house_consumption
energyhub/input/ha/solar_forecast_today
energyhub/input/ha/daily_solar_surplus_estimated
```

The Daily Summary Engine is idempotent.

Retained MQTT messages received after EnergyHub restart do not cause unnecessary snapshot writes when stored values are unchanged.

---

# Daily Solar Surplus Estimated

Daily Solar Surplus Estimated represents solar energy that was probably available but not used during the day.

Formula:

```text
max(0, Solcast Forecast Today - Daily House Consumption)
```

The value is intentionally based on Solcast forecast rather than inverter PV telemetry.

The PowMr inverter exposes PV1 telemetry only and does not provide reliable total PV1 + PV2 generation.

Daily Solar Surplus Estimated is useful for:

- historical analysis;
- identifying unused solar potential;
- future flexible-load planning;
- future EV charging strategy;
- Decision Engine context.

It is an estimate and should not be interpreted as meter-accurate unused solar energy.

---

# Daily Grid Import Estimated

Daily Grid Import Estimated is deferred.

The PowMr inverter does not expose a reliable accumulated grid import counter.

A future EnergyHub version may estimate grid import during controlled grid-charging sessions.

The initial estimation model may assume:

- grid charging is intentionally enabled;
- charging normally occurs at night;
- PV generation during the charging period is zero;
- Battery SOC change is known;
- house consumption during the charging period is known.

Daytime Grid Import during Panic Mode may not be included.

Daily Grid Import Estimated is intended for:

- historical statistics;
- cost analysis;
- informational dashboards.

It must not be used as an authoritative Decision Engine input.

---

# Explainable Decisions

Explainability is a core EnergyHub requirement.

The Decision Engine should never publish only:

```text
Mode: Winter
```

It should provide context.

Example:

```text
Operating Mode:
Winter

Reason:

Solar Forecast Tomorrow: 6.2 kWh
Battery SOC: 42%
Grid Confidence: unstable
Night Tariff begins in 3 hours

Decision:

Charge battery tonight.

Target:

80% SOC
```

Every significant recommendation should include:

- relevant inputs;
- evaluated conditions;
- selected strategy;
- recommended action;
- reason for the recommendation.

The homeowner should be able to understand EnergyHub behaviour without reading logs or source code.

---

# Notifications

EnergyHub communicates important decisions.

Examples:

- Operating mode changed.
- Grid Confidence decreased.
- Battery reserve increased.
- Night charging recommended.
- Panic Mode recommended.
- Manual action recommended.
- Recovery action performed.

Notifications should explain the reason behind important decisions.

The notification system may initially use Home Assistant.

A future Telegram Bot may provide:

- status;
- alerts;
- notifications;
- Decision Engine recommendations;
- explanations.

---

# Future Inputs

Future versions may incorporate:

- weather forecast;
- additional Solcast forecast data;
- dynamic electricity pricing;
- EV battery SOC;
- calendar information;
- occupancy prediction;
- historical household behaviour.

The Decision Engine should remain extensible without requiring architectural redesign.

New inputs should be added through services or defined interfaces rather than direct dependencies on Home Assistant entities or hardware-specific protocols.

---

# Architectural Principle

EnergyHub does not control devices directly from the Decision Engine.

The Decision Engine produces intentions.

Example:

```text
Maintain battery above 80%
```

rather than:

```text
Execute inverter command XYZ
```

Hardware adapters and future device control services translate intentions into device-specific commands.

This separation allows:

- hardware replacement;
- easier testing;
- explainable behaviour;
- progressive automation;
- safer failure handling.

---

# Development Strategy

Decision Engine development should follow the standard EnergyHub workflow:

```text
Architecture

↓

Implement

↓

Deploy

↓

Test on Real System

↓

Document

↓

Commit
```

Decision Engine v1 should begin only after the Recovery Strategy investigation.

The initial implementation should remain recommendation-only.

Recommendations should be observed and validated against real household behaviour before automatic execution is introduced.

---

# Current Status

```text
Foundation             Complete

Daily Summary Engine   v1 Complete

Recovery Strategy      Next

Decision Engine        Planned
```

The next milestone is to investigate recovery behaviour for:

- MQTT failures;
- network failures;
- serial communication failures;
- `mpp-solar` timeouts or blocking;
- Home Assistant connectivity failures.

Only after the recovery architecture is understood should Decision Engine v1 implementation begin.

---

# Vision

EnergyHub should behave like an experienced energy manager.

It should continuously balance:

- comfort;
- cost;
- resilience;
- sustainability.

It should remain:

- transparent;
- predictable;
- understandable;
- modular;
- explainable.

The homeowner should always be able to answer:

> "Why did EnergyHub make this decision?"