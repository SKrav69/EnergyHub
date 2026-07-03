# EnergyHub Decision Engine

> The Decision Engine is the brain of EnergyHub.

Its purpose is to determine how the house should operate over the next 24 hours while maximizing comfort, minimizing energy cost and maintaining resilience during uncertain grid conditions.

---

# Core Philosophy

EnergyHub should not react only to current events.

Instead, it should continuously predict the most appropriate operating strategy using:

- current system state
- historical data
- weather forecasts
- household behaviour
- user preferences

EnergyHub should always answer one question:

> "What is the best decision for the house right now?"

---

# Decision Layers

The Decision Engine is composed of independent decision layers.

Each layer has a single responsibility.

Example:

```
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

Device Actions
```

Each layer contributes information to the final decision.

---

# Daily Decision Cycle

Every day at 00:00 EnergyHub performs a complete evaluation.

Inputs include:

- Battery SOC
- Grid Reliability
- Solar Forecast (today)
- Solar Forecast (tomorrow)
- House Consumption (previous day)
- Indoor temperatures
- Outdoor temperature
- Electricity tariff
- Manual overrides

The Decision Engine then determines:

- Operating Mode
- Battery Strategy
- Heating Strategy
- Flexible Load Strategy

The selected strategy remains active until the next evaluation unless overridden by significant events.

---

# Operating Modes

## Summer

Primary objective:

Use available solar energy.

Typical behaviour:

- Battery used normally.
- Flexible loads encouraged.
- Grid charging disabled.

---

## Winter

Primary objective:

Guarantee comfort while minimizing cost.

Typical behaviour:

- Night tariff charging may be enabled.
- Battery reserve increased.
- Heating optimized.

---

## Away

Primary objective:

Protect the house with minimum energy consumption.

Typical behaviour:

- Reduced heating.
- High battery reserve.
- Flexible loads disabled.

---

## Panic

Primary objective:

Maximize resilience.

Typical behaviour:

- Battery maintained close to 100%.
- Grid charging allowed immediately.
- Only essential loads guaranteed.
- Flexible loads disabled unless explicitly permitted.

---

# Automatic vs Manual Decisions

EnergyHub distinguishes between automatic and manual decisions.

## Automatic Modes

Summer

Winter

Away

These modes may be changed automatically.

---

## Manual Mode

Panic

If Panic Mode is activated manually:

EnergyHub never exits Panic automatically.

Instead it provides recommendations.

Example:

> Recommended mode: Winter

The homeowner decides when normal automation resumes.

---

# Grid Reliability

Grid Reliability is independent from operating modes.

It evaluates recent grid behaviour.

Examples:

Normal

Unstable

Risk

Blackout

Panic

Grid Reliability influences battery strategy but does not directly change operating mode.

---

# Decision Priorities

When objectives conflict, EnergyHub follows these priorities.

1. Safety

2. House protection

3. Occupant comfort

4. Grid resilience

5. Energy independence

6. Cost optimization

7. Solar utilization

---

# Flexible Loads

Flexible loads may include:

- Heat pumps
- Boiler
- EV charging
- Smart plugs

EnergyHub determines when these loads may operate.

---

# Daily Energy Summary

Every midnight EnergyHub stores:

- House consumption
- Solar forecast
- Grid availability
- Energy opportunity
- Operating mode

Historical summaries are used to improve future decisions.

---

# Notifications

EnergyHub communicates important decisions.

Examples:

Operating mode changed.

Grid reliability decreased.

Battery reserve increased.

Night charging scheduled.

Manual action recommended.

Notifications explain the reason behind every decision.

---

# Future Inputs

Future versions may incorporate:

- Weather forecast
- Solcast forecast
- Dynamic electricity pricing
- EV battery SOC
- Calendar information
- Occupancy prediction
- Historical household behaviour

The Decision Engine should remain extensible without requiring architectural changes.

---

# Architectural Principle

EnergyHub does not control devices directly.

The Decision Engine produces intentions.

Example:

```
Maintain battery above 80%
```

rather than

```
Execute inverter command XYZ
```

Hardware adapters translate intentions into device-specific commands.

---

# Vision

EnergyHub should behave like an experienced energy manager.

It should continuously balance:

- comfort
- cost
- resilience
- sustainability

while remaining transparent, predictable and understandable to the homeowner.

The homeowner should always be able to answer:

> "Why did EnergyHub make this decision?"

## Daily Summary Engine

Runs once per day before daily sensors reset.

Responsibilities:

- Store House Consumption
- Store Solar Balance
- Store Grid Availability
- Store Grid Import
- Store Battery Grid Charge
- Publish historical MQTT sensors

Purpose:

Provide stable daily historical values for dashboards and future Decision Engine analytics.