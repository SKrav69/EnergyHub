# EnergyHub Decision Log

This document records the major architectural and design decisions made during the EnergyHub project.

The purpose is not to document implementation details, but to explain **why** specific decisions were made.

Detailed implementation history belongs in `CHANGELOG.md`.

---

# Decision 001

## Home Assistant is the integration and user-experience platform

### Decision

EnergyHub uses Home Assistant as its primary integration, automation, and user-experience platform.

### Reason

Home Assistant already provides:

- MQTT integration;
- dashboards;
- device discovery;
- helpers;
- automations;
- notifications;
- a large integration ecosystem.

EnergyHub should focus on energy intelligence, historical knowledge, health evaluation, and coordinated energy strategy rather than replacing Home Assistant.

---

# Decision 002

## Prefer local communication

### Decision

Whenever possible, EnergyHub communicates with devices locally.

### Reason

The system must continue operating during:

- Internet outages;
- cloud service failures;
- vendor service interruptions.

Local control is the primary implementation.

Cloud integrations may be added as optional data sources or adapters.

---

# Decision 003

## PI30MAX is the primary PowMr interface

### Decision

The first EnergyHub implementation uses the local PI30MAX protocol.

### Reason

PI30MAX provides sufficient access to:

- Battery SOC;
- Grid Voltage;
- House Load;
- PV production;
- charging configuration;
- output-source configuration;
- operating state;
- warning information.

Some information is unavailable through PI30MAX, including reliable accumulated Grid Import data and PV2 telemetry.

EnergyHub may derive missing operational knowledge where technically reasonable.

---

# Decision 004

## Separate decision logic from hardware execution

### Decision

Decision services must not directly send hardware protocol commands.

### Reason

Energy strategy and hardware execution are different responsibilities.

Example:

```text
Decision:
Enter Hybrid
```

The Inverter Controller translates that strategy into:

```text
Setting 01 → SUB
Setting 16 → SNU
```

The PowMr implementation then translates those settings into PI30MAX commands.

This separation improves:

- testability;
- explainability;
- future hardware support;
- control safety.

---

# Decision 005

## Progress toward capability-based architecture

### Decision

The long-term EnergyHub architecture should operate on capabilities rather than device brands.

### Examples

Instead of:

- Xiaomi Plug;
- Shelly Relay;
- PowMr Command.

EnergyHub should eventually reason about:

- House Heating;
- EV Charging;
- Battery Charging;
- Grid Supply;
- Solar Generation.

### Reason

Devices may change.

Capabilities remain conceptually stable.

### Current Limitation

EnergyHub 1.x may contain practical device-specific integration where required for the current house.

Capability abstraction should be introduced progressively rather than prematurely.

---

# Decision 006

## Grid Confidence replaces Grid Stability

### Decision

EnergyHub evaluates **Grid Confidence** rather than Grid Stability.

### Reason

The objective is not to measure electrical grid quality.

The objective is to estimate how much EnergyHub should trust the grid when making energy-management decisions.

Current inputs include recent grid availability.

Future inputs may include:

- weighted recent outages;
- weather forecast;
- planned outages;
- historical reliability.

---

# Decision 007

## Operating strategies are Solar, Hybrid, Panic, and Away

### Decision

The original Summer / Winter / Away concept is replaced by explicit EnergyHub operating strategies:

- Solar;
- Hybrid;
- Panic;
- Away.

### Reason

Summer and Winter describe seasons rather than actual energy strategies.

The new names describe what EnergyHub is doing.

### Current Meaning

```text
Solar
→ normal solar-first operation

Hybrid
→ planned grid charging and battery preservation

Panic
→ protective charging caused by increased energy risk

Away
→ autonomous flexible-load operation while the house is unoccupied
```

---

# Decision 008

## Manual Panic and automatic Panic are different intents

### Decision

EnergyHub distinguishes between user-requested Panic and automatically triggered Panic.

### Reason

Automatic Panic is an EnergyHub decision based on known system inputs.

Manual Panic represents direct homeowner intent.

The system should preserve this distinction in future control and recovery logic.

### Current Implementation

Automatic Panic may:

- start automatically;
- charge to a calculated target;
- restore Solar automatically.

Manual Panic is available as a direct user control.

Further manual-override policy will be refined during stabilization.

---

# Decision 009

## Automatic decisions should be reversible

### Decision

When EnergyHub automatically changes operating strategy, it may automatically leave that strategy when its completion or exit conditions are reached.

### Reason

Autonomous decisions require autonomous lifecycle management.

Examples:

```text
Automatic Panic
→ target SOC reached
→ restore Solar
```

```text
Hybrid Charging
→ 80% SOC reached
→ Hybrid Grid Hold
→ 07:00
→ restore Solar
```

---

# Decision 010

## Hybrid strategy is evaluated once per day

### Decision

EnergyHub evaluates the need for Hybrid operation at 23:50.

### Inputs

- current Battery SOC;
- today's House Consumption;
- tomorrow's Solar Forecast;
- nominal battery capacity.

### Reason

The decision should estimate whether tomorrow's solar energy is sufficient both to operate the house and restore missing battery energy.

### Calculation

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

### Result

```text
Forecast Tomorrow >= Required Energy
→ remain Solar

Forecast Tomorrow < Required Energy
→ enter Hybrid
```

---

# Decision 011

## Event-driven architecture

### Decision

EnergyHub uses an Event Bus for internal event distribution.

### Reason

Services should remain independent where practical.

New inverter telemetry can be published once and consumed by interested services.

Current and evolving consumers include:

- Grid Monitor;
- health services;
- historical services;
- decision services.

The Event Bus should reduce unnecessary direct coupling between services.

---

# Decision 012

## Layered and responsibility-based architecture

### Decision

EnergyHub separates major responsibilities.

```text
Hardware
    ↓
Communication / Adapters
    ↓
Telemetry and State
    ↓
Historical Knowledge / Health
    ↓
Decision Intelligence
    ↓
Control Execution
    ↓
Home Assistant Integration
    ↓
User Interface
```

### Reason

Each subsystem should have a clear responsibility.

Core separation:

```text
Telemetry
≠
Historical Knowledge
≠
Health
≠
Decision
≠
Control
≠
User Interface
```

---

# Decision 013

## EnergyHub owns inverter strategy execution

### Decision

EnergyHub, not Home Assistant, owns execution of inverter operating strategies.

### Reason

EnergyHub now contains:

- decision logic;
- operating-mode state;
- command sequencing;
- acknowledgement handling;
- verification;
- bounded retries;
- transition state.

Home Assistant remains responsible for:

- dashboards;
- helpers;
- user controls;
- selected household automations;
- notification delivery;
- external integrations.

### Impact

The previous statement that Home Assistant is the sole execution platform is no longer accurate.

Responsibility is divided according to system role.

---

# Decision 014

## EnergyHub optimizes policies, not individual devices

### Decision

EnergyHub is designed to optimize operating policies.

Examples include:

- resilience;
- comfort;
- economy;
- renewable-energy utilization;
- future Net Billing profitability.

### Reason

Hardware may change.

Optimization goals may evolve.

The Decision Engine should remain flexible enough to support different strategies without redesigning the entire architecture.

---

# Decision 015

## Inverter Setting 01 control is approved for autonomous use

### Decision

EnergyHub may use POP commands to control inverter Setting 01.

### Confirmed Mapping

```text
POP01 → SUB
POP02 → SBU
```

### Reason

The mapping was verified on the real inverter using:

- ACK responses;
- QPIRI;
- QMOD;
- physical inverter display.

### Impact

This enabled autonomous Solar, Hybrid, and Panic strategy execution.

---

# Decision 016

## Inverter Setting 16 control is approved for autonomous use

### Decision

EnergyHub may use PCP commands to control inverter Setting 16.

### Confirmed Mapping

```text
PCP01 → SNU
PCP02 → OSO
PCP03 → CSO
```

### Reason

The mapping was verified on the real inverter.

### Impact

EnergyHub can coordinate charger-source strategy with output-source strategy.

---

# Decision 017

## Hybrid uses a two-stage strategy

### Decision

Hybrid operation consists of:

1. Hybrid Charging;
2. Hybrid Grid Hold.

### Sequence

```text
Hybrid Charging
SUB + SNU
      ↓
SOC reaches 80%
      ↓
Hybrid Grid Hold
SUB + OSO
      ↓
07:00
      ↓
Solar
SBU + OSO
```

### Reason

After the battery reaches the target SOC, continuing utility charging is unnecessary.

However, immediately returning to battery operation would consume the stored reserve during the cheap night-tariff period.

Grid Hold preserves the battery until morning.

---

# Decision 018

## Panic is evaluated repeatedly during the day

### Decision

Automatic Panic evaluation occurs every 15 minutes between 12:00 and 23:50.

### Reason

Unlike the daily Hybrid decision, Panic responds to changing daytime energy risk.

### Current Common Conditions

```text
PV < 200 W
AND
Forecast Today < Previous Daily Consumption × 1.20
```

### Current Strategies

Unstable grid:

```text
SOC < 50%
→ target 80%
```

Higher-risk grid:

```text
SOC < 80%
→ target 95%
```

### Constraint

Automatic Panic evaluation is active only when the current operating strategy is Solar.

---

# Decision 019

## Automatic decision notifications originate in EnergyHub

### Decision

EnergyHub publishes significant automatic decision events.

Home Assistant delivers the user-facing notification.

### Architecture

```text
EnergyHub Decision
        ↓
MQTT Notification Event
        ↓
Home Assistant Automation
        ↓
Persistent / Mobile / Future Telegram Notification
```

### Reason

EnergyHub knows why the decision occurred.

Home Assistant is better suited to notification channels and presentation.

### Current Topic

```text
energyhub/event/notification
```

---

# Decision 020

## Grid Import is estimated inside EnergyHub

### Decision

EnergyHub estimates Grid Import because the current PowMr interface does not provide a reliable accumulated Grid Import counter.

### Reason

Grid Import is important for:

- historical energy understanding;
- Hybrid testing;
- future economic optimization.

### Current Mode-Aware Logic

Solar:

```text
Grid Import
=
House Load
+ Battery Charging Power
- Battery Discharging Power
- PV Power
```

Hybrid Charging / Panic:

```text
Grid Import
=
House Load
+
Battery Charging Power
```

Hybrid Grid Hold:

```text
Grid Import
=
House Load
```

### Constraint

Estimated Grid Import is informational and not billing-grade.

---

# Decision 021

## Solar-mode Grid Import uses a noise floor

### Decision

Estimated Solar-mode Grid Import below 50 W is treated as zero.

### Reason

Telemetry values are not perfectly synchronized.

Small positive balance errors can appear even when the inverter is not meaningfully importing energy from the grid.

Without a noise floor, these errors would accumulate into false daily Grid Import.

---

# Decision 022

## Grid Import state is persistent

### Decision

Daily estimated Grid Import is stored persistently.

### Reason

EnergyHub restarts must not reset accumulated daily energy.

### Current Storage

```text
/data/grid_import.json
```

The service also resets daily accumulation at the day boundary.

---

# Decision 023

## Away Mode controls flexible loads using ownership

### Decision

EnergyHub tracks whether Away Mode started a controlled load.

### Reason

When Away Mode ends or stop conditions are reached, EnergyHub must not blindly switch off a device that was started manually or by another automation.

### Current Helper

```text
input_boolean.energyhub_away_heat_pump_active
```

### Rule

```text
EnergyHub may automatically stop the heat pump
only when EnergyHub previously started it.
```

This ownership principle should be reused for future flexible-load control.

---

# Decision 024

## Away Mode v1 prioritizes useful solar consumption

### Decision

Away Mode v1 may start the first-floor heat pump when surplus energy and battery reserve are available.

### Current Start Conditions

```text
Away Mode ON
Temperature < 18°C
SOC > 95%
PV > 200 W
```

### Current Stop Conditions

```text
Temperature >= 23°C
OR
SOC <= 81%
```

### Reason

The house can convert otherwise-unused solar energy into useful thermal energy while protecting battery reserve.

Temporary PV fluctuations are ignored after the load starts.

---

# Decision 025

## Home Assistant configuration is versioned selectively

### Decision

Selected Home Assistant configuration is synchronized into the EnergyHub Git repository.

### Structure

```text
homeassistant/
├── live/
└── legacy/
```

### Reason

The repository should represent the complete reviewed EnergyHub system, including the Home Assistant configuration that participates in operation.

### Constraint

The complete Home Assistant `.storage` directory must never be committed.

Only explicitly approved files are synchronized.

---

# Decision 026

## Home Assistant synchronization is bidirectional at the workflow level

### Decision

EnergyHub code is deployed from Git to Home Assistant, while selected Home Assistant configuration is synchronized from Home Assistant back to Git.

### Workflow

```text
EnergyHub Code
Git → Home Assistant
```

```text
Home Assistant Configuration
Home Assistant → Git
```

### Reason

Python code and Home Assistant configuration are edited in different environments.

Both must still be reviewable and versioned in one project repository.

---

# Decision 027

## Technical hardware limits and household strategy parameters are different concepts

### Decision

Future configurable parameters must distinguish between:

- technical hardware limits;
- household operating strategy.

### Examples

Technical:

- maximum battery charging current;
- inverter-supported current limits;
- battery manufacturer limits.

Strategy:

- Hybrid target SOC;
- Panic target SOC;
- Away Mode temperature thresholds;
- Away Mode PV threshold.

### Reason

Technical limits depend on installed hardware.

Strategy settings depend on homeowner preferences and operating goals.

EnergyHub 1.1 will progressively make trusted strategy parameters configurable.

---

# Decision 028

## Recovery must be bounded and responsibility-specific

### Decision

EnergyHub should automatically recover only from failures where safe recovery actions are known and bounded.

### Reason

Detection and recovery are different responsibilities.

Examples:

- MQTT reconnect may be automatic;
- transient serial retry may be automatic;
- service restart may be considered;
- inverter restart must never be automatic.

Recovery architecture must define:

- what failed;
- which subsystem owns recovery;
- which actions are allowed;
- retry limits;
- escalation behavior.

---

# Decision 029

## Restart recovery should reconstruct strategy from verified inverter state

### Decision

EnergyHub should evolve toward reconstructing the current operating strategy after restart from verified inverter settings.

### Intended Mapping

```text
SUB + SNU → Hybrid Charging
SUB + OSO → Hybrid Grid Hold
SBU + OSO → Solar
```

### Reason

Time alone is not sufficient to determine the real operating strategy after a restart.

The physical inverter state is the authoritative execution state.

### Status

Planned high-priority stabilization work.

---

# Decision 030

## EnergyHub 1.0 prioritizes one reliable real installation over premature generalization

### Decision

EnergyHub 1.0 focuses on making the current house operate reliably and autonomously.

### Reason

Real-world validation is more valuable than introducing abstractions before their requirements are understood.

The current implementation may remain PowMr-specific where practical.

Multi-vendor abstractions belong to later EnergyHub versions.

---

# Decision 031

## EnergyHub evolves progressively

### Decision

EnergyHub development follows this progression:

```text
Monitoring
    ↓
Reliable Facts
    ↓
Health Awareness
    ↓
Historical Knowledge
    ↓
Explainable Decisions
    ↓
Validated Automation
    ↓
Autonomous Home Operation
    ↓
Whole-Home Energy Optimization
```

### Reason

Autonomy should be earned through validated system knowledge and safe control behavior.

---

# Future Decisions

This document will continue to evolve as EnergyHub grows.

Likely future architectural decisions include:

- configurable EnergyHub 1.1 parameters;
- advanced Grid Confidence weighting;
- direct BMS integration;
- EV charging strategy;
- multi-inverter capability abstraction;
- dynamic tariff optimization;
- Net Billing and export optimization;
- battery degradation modeling.

Major architectural decisions should be recorded here when they become sufficiently concrete to guide implementation.