# EnergyHub Developer Architecture

> This document describes the current internal structure of EnergyHub 1.0 and the architectural direction for future versions.

---

# Purpose

EnergyHub should remain understandable as it grows.

The current project is no longer a collection of scripts. It contains:

- inverter communication;
- telemetry processing;
- MQTT integration;
- historical services;
- health monitoring;
- decision engines;
- inverter control;
- operating-mode management;
- Grid Import estimation;
- Home Assistant integration.

This document distinguishes between:

1. the architecture that exists now;
2. development rules for EnergyHub 1.x;
3. future abstractions that should be introduced only when required.

---

# Current EnergyHub 1.0 Structure

The current application is organized around a small orchestration layer and focused services.

```text
addon/
└── app/
    ├── main.py
    ├── config.py
    ├── models/
    ├── mqtt/
    ├── services/
    └── utils/
```

The exact file list will evolve, but the responsibility boundaries should remain clear.

---

# `main.py`

`main.py` is the application orchestrator.

Its responsibilities include:

- loading configuration;
- initializing MQTT;
- initializing services;
- connecting callbacks;
- subscribing to Home Assistant inputs;
- running the telemetry loop;
- processing mode requests;
- scheduling periodic service work;
- coordinating application startup and shutdown.

`main.py` may coordinate services.

It should not become the permanent home of:

- decision formulas;
- Grid Import calculations;
- health rules;
- PowMr command mappings;
- MQTT Discovery definitions.

Rule:

> If a block of logic develops its own state, rules, persistence, or tests, it probably belongs in a service.

---

# Configuration

`config.py` contains shared runtime configuration and persistent file paths.

Configuration should remain simple and human-readable.

Good user-facing configuration:

```yaml
serial_port: /dev/ttyUSB0
protocol: PI30MAX
poll_interval: 10
```

Bad user-facing configuration:

```yaml
command_qpigs: QPIGS
command_pop02: POP02
battery_soc_field: battery_capacity
```

Protocol-specific implementation details should remain inside EnergyHub code.

Future EnergyHub 1.2 strategy parameters should also have clear ownership and safe bounds.

Examples:

- Hybrid target SOC;
- Hybrid evaluation time;
- morning exit time;
- Panic thresholds;

Technical hardware limits must remain separate from household strategy parameters.

---

# Models

The `models/` package contains shared data models.

The central current model is:

```text
InverterState
```

Its purpose is to convert raw inverter telemetry into normalized EnergyHub state.

Current examples:

- telemetry validity;
- Grid Availability;
- Battery SOC;
- Battery Voltage;
- Battery Current;
- PV Power;
- House Load;
- raw telemetry.

Decision and health services should prefer normalized state over raw protocol dictionaries.

---

# Telemetry Service

The Telemetry Service converts raw PowMr data into `InverterState`.

Responsibilities:

- validate required telemetry fields;
- normalize numeric values;
- determine basic Grid Availability;
- publish telemetry through MQTT;
- preserve the latest raw telemetry;
- produce concise operational logs.

Current required fields include:

```text
battery_capacity
ac_output_active_power
pv1_charging_power
```

Invalid telemetry must not be treated as valid current state.

---

# MQTT Package

The `mqtt/` package owns Home Assistant and MQTT integration.

Responsibilities include:

- connection handling;
- MQTT Discovery;
- stable topic definitions;
- telemetry publishing;
- retained state publishing;
- Home Assistant input subscriptions;
- notification events.

Application logic should not scatter MQTT topic strings throughout unrelated services.

Where practical, MQTT ownership should remain centralized.

---

# MQTT Publisher

The MQTT Publisher translates EnergyHub values into MQTT entities.

Current responsibilities include publishing:

- inverter telemetry;
- Grid information;
- health information;
- operating mode;
- inverter settings;
- Hybrid Decision and evaluation data;
- Panic Decision;
- Autopilot state;
- Daily Summary;
- Grid Import.

The publisher should remain an integration component.

It should not contain:

- Hybrid formulas;
- Panic rules;
- recovery decisions;
- inverter command execution.

---

# Services

The `services/` package contains focused stateful application behavior.

A service may own:

- rules;
- state;
- persistence;
- periodic evaluation;
- event handling;
- a specific subsystem.

Current service categories include:

- telemetry;
- grid monitoring and history;
- Grid Confidence;
- Daily Summary;
- health monitoring;
- Hybrid decisions;
- Panic decisions;
- inverter control;
- operating mode;
- Autopilot;
- Grid Import estimation.

---

# Grid Services

Grid-related services own historical Grid Availability and Grid Confidence.

Responsibilities include:

- observing Grid Availability;
- storing outage history;
- calculating 24-hour availability;
- calculating 48-hour availability;
- deriving Grid Confidence.

Decision services consume Grid Confidence.

They should not reimplement grid-history calculations.

---

# Daily Summary Service

The Daily Summary Service owns reusable daily historical knowledge.

Current inputs include:

- Daily House Consumption;
- Solar Forecast Today;
- Solar Forecast Tomorrow;
- Daily Solar Surplus Estimated.

Current stored values include:

- House Consumption;
- Solar Forecast;
- Solar Surplus Estimated;
- Grid Availability;
- Grid Import Estimated.

The service owns:

- persistence;
- daily snapshots;
- historical loading;
- MQTT publication.

Dashboards should consume Daily Summary values instead of reproducing historical calculations.

---

# Health Services

Health monitoring is divided by responsibility.

Current subsystems:

```text
Communication Health
Battery Health
Telemetry Freshness
Inverter Health
        ↓
System Health
```

Each health service should provide:

```text
state
+
reason
```

Health detection should remain separate from recovery execution.

A health service may report a problem without attempting to fix it.

---

# Hybrid Decision Engine

`hybrid_decision.py` owns the daily Hybrid decision.

Inputs:

- current Battery SOC;
- current-day House Consumption;
- next-day Solar Forecast;
- nominal battery capacity.

Calculation:

```text
Battery Refill Required
=
Battery Capacity × Missing SOC Percentage
```

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

The service should return an explainable result.

It should not directly send PowMr commands.

---

# Panic Decision Engine

The Panic Decision Engine owns automatic daytime risk evaluation.

Inputs include:

- Operating Mode;
- Grid Confidence;
- current SOC;
- current solar forecast;
- previous Daily House Consumption.

Current evaluation window:

```text
12:00–23:50
```

Current evaluation order:

```text
1. Autopilot enabled
2. Current time is inside the evaluation window
3. Operating Mode is Solar
4. Evaluate Grid Confidence
5. Evaluate Battery SOC threshold
6. Compare Forecast Today with Previous Daily Consumption × 1.20
```

Instantaneous PV power is intentionally not used.

The service should produce:

```text
decision
+
reason
+
target SOC when applicable
```

It should not directly send inverter commands.

---

# Inverter Controller

The Inverter Controller owns execution of operating strategies on the physical inverter.

Responsibilities include:

- Setting 01 changes;
- Setting 16 changes;
- command order;
- ACK handling;
- QPIRI verification;
- bounded retries;
- transition state;
- transition failure state;
- settling delays.

Current verified mappings:

```text
POP01 → SUB
POP02 → SBU

PCP01 → SNU
PCP02 → OSO
PCP03 → CSO
```

High-level code requests:

```text
Solar
Hybrid
Panic
```

The controller performs the required PowMr-specific execution.

---

# Operating Mode Service

Operating Mode represents the confirmed EnergyHub strategy.

Current states include:

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

A requested mode and a confirmed physical mode are not the same thing.

EnergyHub should publish a confirmed mode only after appropriate execution and verification.

---

# Autopilot

Autopilot controls whether automatic inverter strategy execution is allowed.

Autopilot is separate from:

- Operating Mode;
- manual Panic control.

When disabled, automatic decision execution should stop and EnergyHub should preserve or restore the defined safe strategy according to policy.

---

# Grid Import Service

`grid_import.py` estimates Grid Import because the current PowMr interface does not provide a reliable accumulated import counter.

The service owns:

- SUB-interval accounting;
- house-energy accumulation;
- battery refill estimation from positive SOC gain;
- daily accumulation;
- persistence;
- day-boundary finalization;
- yesterday history;
- MQTT publication inputs.

Accounting starts when EnergyHub enters:

- Hybrid Charging;
- Hybrid Grid Hold;
- Panic.

Accounting stops after EnergyHub returns to Solar/SBU.

Current calculation:

```text
Grid Import
=
House Energy Supplied During SUB
+
Positive Battery SOC Gain × Nominal Battery Capacity
```

Current nominal battery capacity:

```text
16 kWh
```

Temporary SOC drops do not inflate the estimate.

The persistence format is schema-versioned so incompatible estimator state is not silently reused after architecture changes.

The service must avoid accounting from invalid telemetry.

Grid Import is informational rather than billing-grade.

---

# Notification Flow

EnergyHub owns significant automatic decision events.

Home Assistant owns delivery.

```text
Decision Service
      ↓
EnergyHub Notification Event
      ↓
MQTT
      ↓
Home Assistant Automation
      ↓
Persistent / Mobile / Future Telegram Notification
```

Current MQTT topic:

```text
energyhub/event/notification
```

This keeps decision context inside EnergyHub while avoiding notification-channel logic in the Core.

---

# Home Assistant Responsibilities

Home Assistant currently owns:

- dashboards;
- helpers;
- timers;
- selected household automations;
- Solcast integration;
- user controls;
- notification delivery.

EnergyHub currently owns:

- inverter telemetry;
- energy intelligence;
- historical Grid knowledge;
- health evaluation;
- Hybrid and Panic decisions;
- inverter strategy execution;
- Grid Import estimation.

The responsibility boundary should remain explicit.

---

# Smart Heating and Flexible Loads

The original Away Mode v1 implementation is not part of the final EnergyHub 1.0 architecture.

Design review showed that occupancy, comfort, solar-surplus use, cheap-tariff opportunities, battery reserve, and flexible-load control require a broader architecture.

This work is deferred to EnergyHub 1.1.

The ownership principle remains:

> An automation should automatically stop a load only when that automation previously started it.

This principle should be reused for future Smart Heating, EV charging, and other flexible loads.

---

# Home Assistant Repository Structure

Current repository structure:

```text
homeassistant/
└── live/
    ├── config/
    │   ├── automations.yaml
    │   ├── configuration.yaml
    │   ├── scenes.yaml
    │   └── scripts.yaml
    └── storage/
        ├── input_boolean
        ├── input_number
        ├── timer
        ├── lovelace.dashboard_powmr1
        ├── lovelace_dashboards
        └── lovelace_resources
```

`live/` contains selected current Home Assistant configuration synchronized from the real installation.

The old manually maintained `homeassistant/legacy/` tree was removed from Git.

---

# Deployment Workflow

EnergyHub application code is deployed from Git to Home Assistant.

Current workflow:

```text
Edit Code
    ↓
Review Locally
    ↓
tools/dev/deploy-to-ha.ps1
    ↓
sync-to-ha.ps1
    ↓
robocopy addon/ → Home Assistant add-on directory
    ↓
Restart EnergyHub Add-on Manually
    ↓
Inspect Logs
    ↓
Test Behavior
    ↓
Commit
```

Manual add-on restart is intentionally preserved in the current workflow.

It provides a clear checkpoint before the changed runtime is activated.

---

# Home Assistant Synchronization Workflow

Selected Home Assistant configuration is synchronized back to Git.

Current workflow:

```text
Edit Home Assistant
    ↓
Test in Home Assistant
    ↓
tools/dev/sync-from-ha.ps1
    ↓
Copy approved files into homeassistant/live/
    ↓
Review Git Changes
    ↓
Commit
```

The complete Home Assistant `.storage` directory must never be copied into Git.

Only explicitly approved files should be synchronized.

---

# Git Workflow

Recommended current workflow:

```text
Make One Logical Change
    ↓
Deploy / Sync
    ↓
Test
    ↓
Inspect Logs and Home Assistant
    ↓
git status
    ↓
Review Diff
    ↓
Commit
```

Large development sessions may contain several related changes, but commits should still describe coherent milestones.

Generated runtime data should not be committed unless intentionally used as fixtures or documentation examples.

---

# Logging

Logs should describe system behavior.

Good:

```text
Automatic Panic evaluation:
status=no_action
reason=Grid confidence=normal; automatic Panic is not required
```

Good:

```text
Starting transition to Solar:
Menu 01=SBU
Menu 16=OSO
```

Less useful alone:

```text
POP02 OK
```

Protocol-level details may appear in debug information, but normal logs should answer:

- What happened?
- Why did it happen?
- Did it succeed?
- Is user action required?

---

# Error Handling

EnergyHub should fail safely.

Examples:

- invalid telemetry is rejected;
- communication failure does not terminate the complete process;
- MQTT reconnects;
- failed inverter commands are retried only within bounded limits;
- mode success is not claimed before verification;
- Grid Import is not integrated from invalid data;
- inverter faults are detected but do not trigger automatic inverter restart.

Graceful degradation is preferred over uncontrolled recovery.

---

# Recovery Architecture

Recovery is a separate architectural concern.

Current recovery-related behavior includes:

- communication retries;
- MQTT reconnect;
- telemetry failure handling;
- bounded inverter-command verification;
- transition failure state;
- safe Solar restoration.

EnergyHub 1.3 recovery services should own:

- failure classification;
- bounded recovery attempts;
- cooldown;
- verification;
- escalation;
- persistence of recovery state.

Recovery design is documented separately in:

```text
13-Recovery-Strategy.md
```

---

# Restart Strategy Reconstruction

A high-priority future improvement is reconstructing EnergyHub strategy from verified inverter settings after restart.

Intended mapping:

```text
SUB + SNU → Hybrid Charging or Panic; additional context is required
SUB + OSO → Hybrid Grid Hold
SBU + OSO → Solar
```

This logic should live in an operating-state or recovery service.

It should not become another large conditional block inside `main.py`.

---

# EnergyHub 1.2 Configurable Parameters

Future strategy parameters should be centralized.

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
- Panic targets;
- selectable Panic profiles.

Recommended direction:

```text
Configuration Source
        ↓
Validation / Safe Bounds
        ↓
Strategy Configuration Model
        ↓
Decision Services
```

Decision services should receive validated configuration.

They should not independently read arbitrary Home Assistant helpers throughout the codebase.

Technical hardware limits must remain separate from household strategy parameters.

---

# Testing Strategy

Every service should be testable independently where practical.

## Telemetry Tests

Test:

- valid telemetry;
- missing required fields;
- invalid numeric values;
- Grid Availability detection.

## Decision Tests

Test:

- Hybrid Solar branch;
- Hybrid charging branch;
- Panic no-action reasons;
- unstable-grid target;
- risk target;
- mode restrictions.

## Grid Import Tests

Test:

- SUB interval start;
- Hybrid Charging;
- Panic;
- Hybrid Grid Hold;
- return to Solar;
- house-energy accumulation;
- positive SOC gain;
- temporary SOC decrease;
- day-boundary finalization;
- yesterday history;
- restart persistence;
- persistence schema migration;
- invalid telemetry.

## Inverter Controller Tests

Test:

- ACK success;
- ACK failure;
- verification success;
- verification mismatch;
- bounded retries;
- transition failure;
- safe Solar restoration.

## Recovery Tests

Test:

- MQTT failure;
- serial failure;
- timeout;
- restart during every operating mode;
- inconsistent inverter settings.

---

# Current Development Rules

## Rule 1 — Keep `main.py` as an orchestrator

Do not allow new subsystem logic to accumulate permanently in `main.py`.

## Rule 2 — One service, one clear responsibility

A service should have a clear reason to exist.

## Rule 3 — Decisions do not send protocol commands

Decision services produce strategy decisions.

The Inverter Controller executes them.

## Rule 4 — Do not duplicate historical calculations

Calculate reusable historical knowledge once.

## Rule 5 — Publish reasons, not only states

Important states should include human-readable reasons.

## Rule 6 — Recovery must be bounded

No infinite retry loops.

## Rule 7 — Never automatically restart the inverter

The inverter owns its internal protection.

## Rule 8 — Verify physical state after writes

ACK alone is not sufficient when read-back verification is available.

## Rule 9 — Do not prematurely generalize EnergyHub 1.0

Make the current installation reliable first.

Introduce abstractions when real requirements justify them.

## Rule 10 — Keep Home Assistant configuration reviewable

Synchronize selected current HA configuration into Git and review changes before committing.

---

# Future Device Abstraction Layer

A complete device abstraction layer is a future architecture goal, not the current codebase structure.

Future example:

```python
inverter.set_output_source("solar_battery_utility")
inverter.set_charger_source("solar_and_utility")
battery.get_soc()
battery.get_power()
```

Future vendor adapters may support:

- PowMr;
- Deye;
- GoodWe;
- Victron;
- additional inverter and BMS vendors.

The abstraction should emerge from real multi-vendor requirements.

---

# Future Capability Architecture

Long-term EnergyHub code should reason about capabilities.

Examples:

```text
Battery Storage
Solar Generation
Grid Supply
House Heating
Water Heating
EV Charging
Energy Export
```

Future decision code may request:

```text
charge_battery(target_soc=80)
```

A hardware adapter would translate that request into vendor-specific commands.

---

# Long-Term Repository Direction

Possible future structure:

```text
EnergyHub/
├── addon/
│   └── app/
│       ├── models/
│       ├── services/
│       ├── mqtt/
│       ├── adapters/
│       ├── capabilities/
│       ├── recovery/
│       └── utils/
├── homeassistant/
│   └── live/
├── tools/
│   ├── dev/
│   ├── diagnostics/
│   └── experiments/
└── docs/
```

This is a direction, not a required immediate refactor.

---

# Architecture Principle

Current EnergyHub 1.0:

```text
main.py
speaks orchestration language

Decision Services
speak strategy language

Inverter Controller
speaks control language

PowMr integration
speaks device language

MQTT
speaks integration language

Home Assistant
speaks user and automation language
```

Future EnergyHub:

```text
High-level code
speaks EnergyHub language

Capability Layer
speaks energy-system language

Adapters
speak device language

Protocols
speak transport language
```

---

# Goal

EnergyHub should become a platform, not a collection of scripts.

The path to that goal is not maximum abstraction today.

The path is:

```text
Clear Responsibilities
        ↓
Reliable Real-World Behavior
        ↓
Explainable Decisions
        ↓
Safe Autonomous Control
        ↓
Reusable Services
        ↓
Validated Abstractions
        ↓
Multi-Vendor Energy Platform
```

The current priority is to make EnergyHub 1.0 reliable, understandable, and maintainable while preserving a clean path toward the larger architecture.