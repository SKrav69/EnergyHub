# EnergyHub Project History

This document records the major development eras and architectural milestones of EnergyHub.

Detailed implementation changes belong in `CHANGELOG.md`.

---

# June 2026 — Foundation

EnergyHub began as a local integration between a PowMr inverter, Raspberry Pi, Home Assistant, and MQTT.

Major milestones:

- PowMr PI30MAX communication;
- real-time inverter telemetry;
- MQTT publishing;
- MQTT Discovery;
- automatic Home Assistant entities;
- GitHub repository;
- structured project documentation.

Architectural result:

> EnergyHub became a local-first, MQTT-first energy platform rather than a collection of isolated scripts.

---

# Late June 2026 — Grid Intelligence and Health

EnergyHub expanded from telemetry into system awareness.

Major milestones:

- Grid Monitor;
- Grid History;
- 24-hour and 48-hour grid availability;
- Grid Confidence;
- Communication Watchdog;
- Communication Health state machine;
- Developer Dashboard;
- Family Dashboard;
- House Model documentation.

Architectural result:

> EnergyHub began preserving historical context and treating system health as a first-class subsystem.

---

# Late June 2026 — Home Automation and Historical Energy

EnergyHub began connecting energy telemetry with household behavior.

Major milestones:

- Daily Energy Statistics;
- 7-day historical charts;
- solar forecast integration;
- Grid Availability visualization;
- Floor 3 Heat Pump Auto-Off;
- timer helpers;
- Daily Energy Balance helper.

Architectural result:

> Dashboards and automations began consuming reusable energy knowledge rather than repeatedly calculating raw telemetry.

---

# Early July 2026 — Architecture v2

The project was reorganized around modular services and explainable decisions.

Major milestones:

- Daily Summary Engine;
- persistent daily history;
- Battery Health Monitor;
- Telemetry Freshness Monitor;
- Inverter Health Monitor;
- System Health aggregation;
- QPIWS monitoring;
- Recovery Strategy principles;
- Decision Engine design;
- Home Assistant configuration documentation.

Architectural result:

```text
Telemetry
    ↓
Reliable Facts
    ↓
Health Awareness
    ↓
Historical Knowledge
    ↓
Explainable Decisions
```

---

# July 2026 — Real Inverter Control

EnergyHub moved from monitoring and recommendations to verified control of the real inverter.

Major milestones:

- Setting 16 control confirmed:
  - `PCP01 → SNU`;
  - `PCP02 → OSO`;
  - `PCP03 → CSO`.
- Setting 01 control confirmed:
  - `POP01 → SUB`;
  - `POP02 → SBU`.
- command acknowledgement;
- QPIRI verification;
- bounded retries;
- real inverter display verification;
- safe Solar restoration.

Architectural result:

> EnergyHub gained the ability to execute operating strategies rather than only recommend them.

---

# July 2026 — Autonomous Operating Modes

EnergyHub implemented its first complete operating strategies.

## Solar

Default strategy:

```text
SBU + OSO
```

## Hybrid

Night strategy based on tomorrow's forecast, today's consumption, current SOC, and required battery refill energy.

Sequence:

```text
Hybrid Decision
    ↓
Hybrid Charging
SUB + SNU
    ↓
Battery reaches 80%
    ↓
Hybrid Grid Hold
SUB + OSO
    ↓
07:00
    ↓
Solar
```

## Panic

Protective daytime charging based on:

- Grid Confidence;
- current SOC;
- low PV production;
- insufficient solar forecast.

Targets:

- 80% for unstable-grid conditions;
- 95% for higher-risk conditions.

## Away Mode v1

Manual Away Mode with autonomous first-floor heat-pump control based on:

- temperature;
- Battery SOC;
- available PV power.

An ownership helper ensures EnergyHub only switches off loads that it previously started.

Architectural result:

> EnergyHub crossed the boundary from monitoring into explainable autonomous home energy control.

---

# July 2026 — Grid Import Estimation

The PowMr inverter does not provide a reliable accumulated Grid Import counter.

EnergyHub introduced a mode-aware Grid Import Estimator.

Major milestones:

- estimated current Grid Import power;
- estimated Daily Grid Import energy;
- Solar-mode power-balance estimation;
- Hybrid/Panic charging estimation;
- Hybrid Grid Hold estimation;
- persistent daily state;
- midnight reset;
- chart and dashboard integration.

Architectural result:

> EnergyHub learned to derive missing operational knowledge from telemetry and known control state.

---

# July 2026 — Home Assistant as Versioned Project State

The Home Assistant side of EnergyHub was integrated into the repository workflow.

Major milestones:

- `homeassistant/live/` for current synchronized configuration;
- `homeassistant/legacy/` for historical manual exports;
- `tools/dev/sync-from-ha.ps1`;
- selected Home Assistant YAML synchronization;
- selected `.storage` synchronization;
- Lovelace dashboard synchronization;
- helper and timer synchronization.

Development workflow became bidirectional:

```text
EnergyHub code
Git → Home Assistant

Home Assistant configuration
Home Assistant → Git
```

Architectural result:

> The repository now represents both the EnergyHub runtime and the reviewed Home Assistant configuration that surrounds it.

---

# Current Era — EnergyHub 1.0 Stabilization

The current goal is to stabilize and polish the first autonomous EnergyHub release.

Current priorities:

- validate autonomous behavior over real household operation;
- improve restart strategy reconstruction;
- complete bounded recovery behavior;
- expose remaining Hybrid Decision telemetry;
- polish dashboards and naming;
- remove duplicate helpers;
- investigate persistent inverter `eeprom_fault`;
- align all project documentation.

EnergyHub 1.0 success means:

> The house can operate safely and economically with minimal homeowner intervention while every important automated decision remains understandable.

---

# Next Era — EnergyHub 1.1

EnergyHub 1.1 will make household strategy parameters configurable without editing code.

Planned examples:

- Hybrid target SOC;
- Hybrid schedule;
- Panic thresholds and targets;
- Away Mode SOC thresholds;
- Away Mode temperature thresholds;
- Away Mode PV threshold.

Architectural goal:

> Separate hardware technical limits from configurable household strategy.

---

# Future — EnergyHub 2.x

EnergyHub will evolve into a multi-vendor energy optimization platform.

Planned direction:

- Deye, GoodWe, Victron, and other inverter support;
- additional BMS vendors;
- dynamic electricity tariffs;
- import optimization;
- export optimization;
- Net Billing;
- battery degradation modeling.

Core question:

> Is it better to consume, store, import, or export energy now?

---

# Long-Term Vision — EnergyHub 3.x

EnergyHub will evolve into a full Home Energy Management System.

Planned ecosystem:

- solar;
- battery storage;
- weather;
- dynamic electricity markets;
- EV charging;
- heat pumps;
- water heating;
- flexible household loads;
- grid reliability;
- energy trading.

Long-term architecture:

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
        ↓
EnergyHub
        ↓
Explainable Whole-Home Energy Strategy
```

---

# Project Evolution

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