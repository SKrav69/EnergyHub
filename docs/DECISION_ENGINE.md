# EnergyHub Decision Engine

## Purpose

The Decision Engine converts household context into a requested operating strategy. It never writes inverter settings directly.

![Autopilot logic](Images/Infographic%231_logic.png)

## Inputs

### Physical state

- battery SOC;
- confirmed operating mode;
- grid availability history;
- Grid Confidence.

### Energy context

- live Solcast forecast today;
- live Solcast forecast tomorrow;
- scheduled daily house consumption;
- battery capacity fixed at 16 kWh in 1.0.

### Permission and time

- Autopilot state;
- Hybrid trigger at 23:50;
- Panic window 12:00–23:50;
- Solar restoration at 07:00.

## Outputs

A decision result contains:

- status;
- reason;
- optional requested mode;
- optional target SOC;
- optional energy calculation values.

The request is queued by `main.py` and executed by Inverter Controller.

## Operating modes

### Solar

Default and recovery state.

```text
SBU + OSO
```

### Hybrid Charging

```text
SUB + SNU
Target = 80%
```

### Hybrid Grid Hold

```text
SUB + OSO
Exit = 07:00
```

### Panic

```text
SUB + SNU
Target = 80% or 95%
```

## Hybrid decision

### Preconditions

Hybrid is skipped when:

- Autopilot is disabled;
- operating mode is not Solar or Unknown;
- SOC is unavailable;
- tomorrow forecast is unavailable;
- current daily consumption is unavailable.

### Formula

```text
missing battery energy
= 16 kWh × (100 - SOC) / 100
```

```text
required energy
= today's house consumption + missing battery energy
```

### Rule

```text
if tomorrow forecast < required energy
    request Hybrid
else
    remain Solar
```

The decision formula evaluates energy required to refill the battery to 100%, while the actual night charging target is currently 80%. This is the implemented conservative rule and should be reviewed when strategy parameters become configurable.

### Execution

1. Enter Hybrid Charging.
2. Monitor SOC in the main loop.
3. At SOC ≥ 80%, enter Hybrid Grid Hold.
4. At 07:00, HA requests Solar when Autopilot is enabled.

## Panic decision

### Evaluation window

```text
12:00 inclusive → 23:50 exclusive
```

Evaluation occurs every 15 minutes and after selected strategy transitions.

### Preconditions

Panic is skipped when:

- Autopilot is disabled;
- outside the time window;
- Hybrid is active;
- Panic is already active;
- transition is in progress;
- operating mode is not Solar;
- SOC, forecast today, or yesterday consumption is unavailable.

### Conservative consumption

```text
required forecast = yesterday consumption × 1.20
```

### Risk/panic Grid Confidence

```text
if SOC >= 80%
    no action
else if forecast today >= required forecast
    no action
else
    request Panic target 95%
```

### Unstable Grid Confidence

```text
if SOC >= 50%
    no action
else if forecast today >= required forecast
    no action
else
    request Panic target 80%
```

### Normal Grid Confidence

No automatic Panic.

### Current policy note

The current implementation does **not** use live PV power as a Panic prerequisite. Earlier design discussions included a low-PV threshold. Whether to restore such a gate is an explicit 1.1 test-drive item rather than an undocumented assumption.

## Manual Panic

- user presses Start Panic;
- HA requires Autopilot on;
- request is `panic`;
- EnergyHub uses 95% target;
- blocked requests create a clear HA notification.

## Autopilot

Autopilot is not an operating mode. It is permission to execute requested strategy changes.

With Autopilot off:

- ordinary mode requests are ignored;
- Hybrid and Panic decisions are skipped;
- disabling it during an active/unknown automatic state queues one safe Solar recovery.

## Request priority

`safe_solar` has queue priority. It cannot be overwritten by Hybrid, Panic, or manual requests.

## Transition results

The decision engine distinguishes:

```text
decision selected
request queued
transition executed
transition confirmed or failed
```

Only the last step produces activation or failure events.

## Explainability entities

### Hybrid

- `sensor.energyhub_hybrid_decision`;
- `sensor.energyhub_hybrid_decision_reason`;
- evaluated SOC;
- evaluated consumption;
- evaluated forecast;
- battery refill required;
- total energy required.

### Panic

- `sensor.energyhub_panic_decision`;
- `sensor.energyhub_panic_decision_reason`.

### Strategy

- `sensor.energyhub_operating_mode`;
- `sensor.energyhub_operating_mode_reason`;
- output source priority;
- charger source priority.

## Failure behavior

### Decision failure

Missing inputs produce `skipped` with a reason. They do not cause a hardware write.

### Execution failure

Inverter Controller attempts bounded recovery where defined. The mode becomes Solar after successful recovery or `transition_failed` if recovery is incomplete.

### Notification failure semantics

No activation event is sent when a transition fails. HA receives an explicit failed-activation event with current mode, controller error, and original decision reason.

## Future decision work

- configurable targets and time windows;
- uncertainty-aware forecasts;
- live PV/net-power policy review;
- telemetry quality gates;
- Smart Thermal decisions;
- EV/flexible-load decisions;
- dynamic tariffs;
- multi-day reserve planning.
