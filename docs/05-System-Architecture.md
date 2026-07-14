# EnergyHub System Architecture

> A modern home should behave as one coordinated system, not as a collection of independent devices.

---

# Overview

EnergyHub is a local-first home energy management system built as a set of small, cooperating services.

The architecture separates:

- physical devices and protocols;
- telemetry and state;
- historical knowledge;
- health and reliability;
- decisions;
- control execution;
- Home Assistant integration;
- homeowner interaction.

The current implementation is optimized for one real PowMr installation, while the long-term architecture is intended to support additional hardware vendors and complete home energy management.

---

# Current System Architecture

```text
                         Homeowner
                             │
                             ▼
                  Home Assistant Dashboards
                             │
                  Automations / Helpers / UI
                             │
                             ▼
                            MQTT
                             │
                             ▼
                       EnergyHub Core
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
   Telemetry             Intelligence          Control
        │                    │                    │
        ▼                    ▼                    ▼
 InverterState       Decision Engines     Inverter Controller
        │                    │                    │
        ▼                    ▼                    ▼
    Event Bus          Operating Mode       PowMr Adapter
        │                    │                    │
        ▼                    ▼                    ▼
 Health / History     Notifications       Physical Inverter
```

EnergyHub currently runs as a Home Assistant add-on.

Home Assistant and EnergyHub have separate responsibilities.

EnergyHub owns:

- inverter communication;
- telemetry processing;
- historical grid knowledge;
- health evaluation;
- decision logic;
- operating-mode state;
- inverter control;
- Grid Import estimation.

Home Assistant owns:

- dashboards;
- helpers;
- selected household automations;
- user controls;
- mobile and persistent notifications;
- external integrations such as Solcast.

---

# Current EnergyHub Core

Current implemented services and subsystems include:

- PowMr Local Adapter;
- `InverterState`;
- Telemetry Service;
- Event Bus;
- MQTT Publisher;
- Communication Watchdog;
- Grid Monitor;
- Grid History Service;
- Grid Stability / Confidence Engine;
- Daily Summary Service;
- Battery Health Monitor;
- Telemetry Freshness Monitor;
- Inverter Health Monitor;
- System Health aggregation;
- Hybrid Decision Engine;
- Panic Decision Engine;
- Inverter Controller;
- Operating Mode state;
- Autopilot state;
- Grid Import Estimator;
- notification event publishing.

Current high-level data flow:

```text
PowMr Inverter
      │
      ▼
PowMr Local Adapter
      │
      ▼
Raw Telemetry
      │
      ▼
Telemetry Service
      │
      ▼
InverterState
      │
      ├──────────────► MQTT Telemetry
      │
      ├──────────────► Health Services
      │
      ├──────────────► Grid Monitor
      │
      ├──────────────► Grid Import Estimator
      │
      └──────────────► Decision Engines
                              │
                              ▼
                       Operating Decision
                              │
                              ▼
                      Inverter Controller
                              │
                              ▼
                        PowMr Commands
```

---

# Layer 1 — User Experience

The homeowner interacts with simple concepts.

Current concepts:

- Solar;
- Hybrid;
- Panic;
- Autopilot;
- System Health;
- Grid Confidence.

Users should not need to understand:

- `POP01`;
- `POP02`;
- `PCP01`;
- `PCP02`;
- PI30MAX;
- MQTT topics;
- serial communication details.

The family-facing interface should explain:

- what EnergyHub is doing;
- why it made a decision;
- whether the house is healthy;
- whether user action is required.

Detailed technical information remains available in engineering and testing views.

---

# Layer 2 — Home Assistant Integration

Home Assistant is the user-facing integration and automation platform.

Current responsibilities:

- dashboards;
- entity model;
- helpers;
- timers;
- selected household automations;
- Solcast integration;
- MQTT integration;
- persistent notifications;
- future mobile and Telegram notifications.

EnergyHub extends Home Assistant rather than replacing it.

The integration is bidirectional:

```text
Home Assistant
      │
      │ inputs / commands
      ▼
     MQTT
      │
      ▼
EnergyHub Core
      │
      │ telemetry / state / decisions
      ▼
     MQTT
      │
      ▼
Home Assistant
```

Examples of Home Assistant inputs:

- daily house consumption;
- solar forecast today;
- solar forecast tomorrow;
- daily solar surplus;
- Autopilot state;
- inverter-mode requests.

Examples of EnergyHub outputs:

- telemetry;
- Grid Confidence;
- System Health;
- Operating Mode;
- Hybrid Decision and evaluation data;
- Panic Decision;
- Grid Import;
- notification events.

---

# Layer 3 — Telemetry and State

The Telemetry Service converts raw inverter data into validated EnergyHub state.

Current required telemetry includes:

- Battery SOC;
- House Load;
- PV Power.

Additional telemetry includes:

- Grid Voltage;
- Battery Voltage;
- Battery Charging Current;
- Battery Discharge Current;
- inverter temperature;
- output voltage and frequency.

The central state object is:

```text
InverterState
```

It provides a normalized representation of current inverter conditions.

The Decision Engine should consume normalized state rather than raw protocol output.

---

# Layer 4 — Historical Knowledge

EnergyHub stores historical information that cannot be understood from one telemetry sample.

Current services include:

## Grid History

Stores grid availability events.

Produces:

- 24-hour availability;
- 48-hour availability;
- Grid Confidence.

## Daily Summary

Stores daily historical values.

Current values include:

- House Consumption;
- Solar Forecast;
- Solar Surplus Estimated;
- Grid Availability;
- Grid Import Estimated.

## Grid Import Estimation

Estimates current and accumulated grid import because the PowMr inverter does not provide a reliable import counter.

Historical knowledge principle:

> Calculate reusable historical knowledge once and allow dashboards and decision services to consume it.

---

# Layer 5 — Health and Reliability

EnergyHub treats system health as a first-class subsystem.

Current architecture:

```text
Communication Health
        +
Battery Health
        +
Telemetry Freshness
        +
Inverter Health
        ↓
System Health
```

## Communication Health

Detects inverter communication state.

## Battery Health

Current v1 checks:

- low SOC;
- abnormal SOC jumps.

## Telemetry Freshness

Current v1 checks:

- missing valid telemetry;
- suspiciously unchanged House Load.

## Inverter Health

Polls `QPIWS` and interprets warning and fault flags.

## System Health

Aggregates subsystem health into one overall state and reason.

Recovery remains deliberately separate from detection.

EnergyHub must never automatically restart the inverter.

---

# Layer 6 — Decision Intelligence

The Decision Engine converts current state, historical knowledge, forecasts, and strategy into explainable decisions.

Current implemented decision services:

- Hybrid Decision Engine;
- Panic Decision Engine.

Future decision services may include:

- proactive battery reserve prediction;
- consumption prediction;
- advanced solar forecasting;
- tariff optimization;
- export optimization;
- EV charging strategy.

Every important decision should provide:

```text
Decision
+
Reason
+
Relevant Inputs
```

Explainability is a core architectural requirement.

Hybrid evaluations currently retain:

- final decision;
- decision reason;
- Battery SOC used;
- House Consumption used;
- Battery Refill Required;
- Total Energy Required;
- Solar Forecast Tomorrow used.

---

# Hybrid Decision Architecture

Hybrid is evaluated at 23:50.

Inputs:

```text
Current Battery SOC
+
Today's House Consumption
+
Tomorrow's Solar Forecast
+
Nominal Battery Capacity
```

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

Hybrid sequence:

```text
Hybrid Decision
      │
      ▼
Hybrid Charging
SUB + SNU
      │
      ▼
SOC reaches 80%
      │
      ▼
Hybrid Grid Hold
SUB + OSO
      │
      ▼
07:00
      │
      ▼
Solar
SBU + OSO
```

---

# Panic Decision Architecture

Panic protects battery reserve when current conditions indicate increased energy risk.

Automatic evaluation occurs every 15 minutes between 12:00 and 23:50.

Evaluation is active only in Solar mode.

Evaluation order:

```text
1. Autopilot enabled
2. Inside the 12:00–23:50 evaluation window
3. Current Operating Mode is Solar
4. Evaluate Grid Confidence
5. Evaluate Battery SOC threshold
6. Compare Solar Forecast Today with Previous Daily Consumption × 1.20
```

Instantaneous PV power is intentionally not used.

Unstable-grid strategy:

```text
Grid Confidence = unstable
AND
SOC < 50%
AND
Forecast Today < Previous Daily Consumption × 1.20
→ Panic target 80%
```

Higher-risk strategy:

```text
Grid Confidence = risk or panic
AND
SOC < 80%
AND
Forecast Today < Previous Daily Consumption × 1.20
→ Panic target 95%
```

Panic sequence:

```text
Panic Decision
      │
      ▼
SUB + SNU
      │
      ▼
Target SOC reached
      │
      ▼
Restore Solar
      │
      ▼
Reevaluate Panic
```

---

# Layer 7 — Control Execution

Decision logic and hardware execution are separate responsibilities.

The Decision Engine requests an operating strategy.

The Inverter Controller executes the required hardware commands.

Example:

```text
Decision:
Enter Hybrid
```

becomes:

```text
Setting 01 → SUB
Setting 16 → SNU
```

Current verified PowMr commands:

```text
POP01 → SUB
POP02 → SBU

PCP01 → SNU
PCP02 → OSO
PCP03 → CSO
```

Control execution includes:

- command sending;
- ACK validation;
- QPIRI verification where supported;
- bounded retries;
- transition state;
- transition failure state;
- inverter settling time.

The Decision Engine should never directly send PI30MAX commands.

---

# Operating Modes

Current operating strategies:

## Solar

```text
Setting 01 → SBU
Setting 16 → OSO
```

## Hybrid Charging

```text
Setting 01 → SUB
Setting 16 → SNU
```

## Hybrid Grid Hold

```text
Setting 01 → SUB
Setting 16 → OSO
```

## Panic

```text
Setting 01 → SUB
Setting 16 → SNU
```

# Autopilot

Autopilot determines whether EnergyHub may execute automatic inverter strategy changes.

When enabled:

- automatic Hybrid decisions may execute;
- automatic Panic decisions may execute;
- scheduled Solar restoration may execute.

When disabled:

- EnergyHub should return to or preserve the safe Solar strategy;
- automatic decision execution is disabled.


---

# Notifications

EnergyHub owns the event that a significant automatic decision occurred.

Home Assistant owns user-facing delivery.

Architecture:

```text
EnergyHub Decision
        │
        ▼
MQTT Notification Event
        │
        ▼
Home Assistant Automation
        │
        ▼
Persistent Notification
Mobile Notification
Future Telegram Notification
```

Current notification topic:

```text
energyhub/event/notification
```

Current automatic events:

- Hybrid activated;
- Panic activated.

This keeps decision ownership inside EnergyHub while allowing Home Assistant to manage delivery channels.

---

# Grid Import Architecture

The PowMr inverter does not provide a reliable accumulated Grid Import counter.

EnergyHub therefore estimates Grid Import during verified SUB operating intervals.

Accounting starts when EnergyHub enters:

- Hybrid Charging;
- Hybrid Grid Hold;
- Panic.

Accounting stops when EnergyHub returns to Solar/SBU.

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

Battery contribution uses positive SOC gain relative to the start of the SUB interval.

Temporary SOC drops do not inflate the estimate.

The service:

- accumulates house energy during SUB;
- estimates battery refill energy from SOC gain;
- persists current-day state;
- survives EnergyHub restarts;
- supports day-boundary finalization;
- publishes yesterday and Daily Summary history;
- uses a versioned persistence schema.

Grid Import is informational rather than billing-grade.

---

# Home Assistant Configuration Architecture

The repository now stores reviewed Home Assistant configuration.

Structure:

```text
homeassistant/
└── live/
    ├── config/
    └── storage/
```

`live/` contains current synchronized Home Assistant files.

The old manually maintained `homeassistant/legacy/` structure was removed from Git.

Synchronization workflow:

```text
Edit Home Assistant
        │
        ▼
tools/dev/sync-from-ha.ps1
        │
        ▼
homeassistant/live/
        │
        ▼
Review Git Changes
        │
        ▼
Commit
```

Only explicitly approved `.storage` files are synchronized.

The complete Home Assistant `.storage` directory must never be committed.

---

# Current Hardware Boundary

The current implementation directly supports:

- PowMr 10.2M;
- PI30MAX;
- Home Assistant;
- MQTT;
- Solcast inputs;
- selected Xiaomi smart-home devices through Home Assistant.

This is the current implementation boundary, not the final architectural boundary.

EnergyHub 1.x may contain practical PowMr-specific code where necessary.

Future versions should progressively introduce capability abstractions when multiple hardware vendors are supported.

---

# Capability-Based Future Architecture

Long-term EnergyHub architecture should be based on capabilities rather than device brands.

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

The Decision Engine should eventually request capabilities:

```text
charge_battery(target_soc=80)
```

rather than vendor commands:

```text
POP01
PCP01
```

Hardware adapters will translate generic requests into vendor-specific implementations.

---

# EnergyHub 1.x Architecture

## EnergyHub 1.0 — Autonomous Home

Status:

```text
Feature development complete
Test-drive and cleanup phase
```

Focus:

- reliable operation of the current house;
- explainable Solar, Hybrid, and Panic autonomy;
- Autopilot;
- Grid Intelligence;
- health monitoring;
- Daily Summary;
- Grid Import accounting;
- Home Assistant integration.

## EnergyHub 1.1 — Smart Loads & Test-Drive Improvements

Focus:

- bugs discovered during real Autopilot operation;
- dashboard and chart improvements;
- Smart Heating architecture;
- Away rethink;
- flexible loads;
- EV charging template.

## EnergyHub 1.2 — Configurable EnergyHub

Focus:

- configurable tariff windows;
- nominal battery capacity;
- grid charging current;
- Hybrid target;
- Panic profiles;
- other safe strategy variables.

## EnergyHub 1.3 — Recovery & Resilience

Focus:

- MQTT recovery;
- network recovery;
- serial and `mpp-solar` recovery;
- Home Assistant connectivity failures;
- bounded retries;
- safe-state reconstruction;
- external watchdog strategy.

Goal:

> Build a house that operates by itself as much as possible while remaining safe, understandable, and cost-effective.

---

# EnergyHub 2.x Architecture

Focus:

- multiple inverter vendors;
- device capability abstraction;
- dynamic tariffs;
- import optimization;
- export optimization;
- Net Billing;
- battery degradation modeling.

Core question:

> Is it better to consume, store, import, or export energy now?

---

# EnergyHub 3.x Architecture

EnergyHub evolves into a complete Home Energy Management System.

```text
Weather
+
Solar Forecast
+
House Consumption
+
Battery State
+
Grid Reliability
+
Electricity Prices
+
EV Requirements
+
Heating Requirements
        │
        ▼
EnergyHub Intelligence
        │
        ▼
Explainable Whole-Home Energy Strategy
        │
        ▼
Device Capability Layer
        │
        ▼
Inverters / Batteries / EV / Heating / Flexible Loads
```

---

# Architectural Principles

EnergyHub should remain:

- local-first;
- modular;
- explainable;
- progressively automated;
- safe by design;
- resilient to communication failures;
- independent of cloud availability for core operation.

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

Each subsystem should have a clear responsibility.

---

# Architectural Goal

EnergyHub should become the operating-system layer that transforms independent energy and smart-home devices into one coordinated autonomous home.

The system should optimize:

- resilience;
- comfort;
- operating cost;
- renewable energy utilization;
- battery lifetime;
- future import and export value.

The homeowner should interact with understandable strategies and outcomes rather than hardware protocols.