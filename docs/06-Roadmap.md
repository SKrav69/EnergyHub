# EnergyHub Roadmap

> Build the foundation first. Add intelligence second. Scale third.

## EnergyHub 1.0 — Autonomous Home

Goal:

Create a reliable local-first energy system that monitors the house, understands current conditions, makes explainable decisions, and safely controls the real inverter.

Status:

**Release-ready as EnergyHub 1.0.2.**

Delivered:

- PowMr PI30MAX telemetry and control;
- MQTT communication and Discovery;
- verified Menu 01 control and ACK-confirmed Menu 16 control;
- Solar, Hybrid Charging, Hybrid Grid Hold, and Panic;
- Autopilot and explainable decision reasons;
- Grid History, Grid Availability, and weighted Grid Confidence;
- Communication, Battery, Telemetry, Inverter, and System Health;
- QPIWS monitoring;
- persistent Daily Summary and estimated Grid Import;
- Home Assistant schedules, controls, notifications, dashboards, and selected configuration synchronization;
- atomic persistence and restart strategy reconstruction;
- persistent FTDI serial identity;
- pinned dependencies and public-safe defaults;
- executable Docker-build release tests;
- installation, upgrade, and release documentation.

Success criterion:

> The house operates safely and economically with minimal homeowner intervention, while every important automated decision remains understandable.

---

## EnergyHub 1.1 — Test-drive and Telemetry Robustness

Goal:

Use sustained real-world operation to improve correctness, observability, and confidence without broad architectural expansion.

Planned work:

- fix defects found during real Autopilot operation;
- refine daytime SUB and Grid Import behavior;
- improve logs and diagnostic context;
- capture meaningful pre-event and post-event telemetry around anomalies;
- detect suspicious SOC changes using both simple thresholds and current-integrated plausibility;
- distinguish raw SOC from trusted SOC where justified;
- preserve anomaly history and recurrence information;
- continue entity, chart, dashboard, and usability cleanup;
- establish flexible-load groundwork without introducing unsafe automatic control.

Status:

Planned after the 1.0.2 release.

---

## EnergyHub 1.2 — Configurable EnergyHub

Goal:

Make trusted household strategy variables adjustable without editing Python or Home Assistant YAML.

Planned parameters:

- cheap-tariff start and end times;
- Hybrid evaluation time;
- Hybrid target SOC;
- morning Solar restoration time;
- nominal battery capacity;
- grid charging current within hardware-safe bounds;
- Panic evaluation window;
- Panic SOC thresholds and targets;
- selectable Panic profiles;
- technical monitoring thresholds where appropriate.

Requirements:

- safe parameter bounds;
- clear descriptions;
- separation between hardware limits and household strategy;
- persistent configuration;
- understandable defaults;
- no need to edit source code.

Status:

Planned.

---

## EnergyHub 1.3 — Recovery & Resilience

Goal:

Recover safely and predictably from real communication and service failures.

Planned work:

- MQTT reconnect ownership and bounded retry;
- network failure detection;
- serial communication recovery;
- inverter communication recovery;
- `mpp-solar` timeout and blocking protection;
- Home Assistant connectivity failure handling;
- service startup, shutdown, and restart behavior;
- safe-state reconstruction;
- bounded retry/backoff policies;
- escalation and notification behavior;
- external heartbeat/watchdog strategy.

Safety rule:

> EnergyHub must never automatically restart the inverter.

Status:

Planned.

---

## EnergyHub 1.4 — Remote Access & Telegram

Goal:

Provide secure remote visibility and structured alert delivery without moving decision logic into cloud services.

Planned work:

- secure remote Home Assistant access;
- Cloudflare Tunnel with WireGuard backup strategy;
- structured EnergyHub notification events;
- Telegram status queries;
- health, outage, anomaly, and strategy-transition alerts;
- carefully bounded remote commands;
- notification policy and rate limiting.

Status:

Planned.

---

## EnergyHub 1.5 — Smart Thermal Energy

Goal:

Use flexible heating and cooling as an energy asset while preserving comfort and battery resilience.

The design replaces the old narrow Away Mode concept.

Planned inputs:

- room temperature and comfort targets;
- occupancy context without making occupancy the only trigger;
- available solar surplus;
- cheap-tariff opportunities;
- battery SOC and reserve;
- solar forecast;
- grid reliability;
- current and projected household demand.

Planned behavior:

- use otherwise curtailed or unused solar for useful heating/cooling;
- preheat or precool during cheap-tariff periods when justified;
- preserve required battery reserve;
- coordinate multiple heat pumps and thermal loads;
- stop only loads that EnergyHub previously started;
- introduce a generic Grid Input / Breaker Guard that can reduce charging current when household demand rises.

Status:

Planned.

---

## EnergyHub 2.x — Energy Optimization Platform

Goal:

Optimize monetary and technical value across broader hardware and tariff ecosystems.

Planned direction:

- multiple inverter support;
- Deye, GoodWe, Victron, and other vendors;
- additional BMS vendors;
- device capability abstraction;
- dynamic electricity tariffs;
- energy price forecasting;
- import and export optimization;
- Net Billing;
- battery degradation models;
- cost-aware reserve management.

Core question:

> Is it better to consume, store, import, or export energy now?

---

## EnergyHub 3.x — Full Home Energy Management System

Goal:

Coordinate the complete household energy ecosystem.

Future scope:

- solar generation;
- weather forecasting;
- dynamic electricity markets;
- battery storage;
- EV charging;
- vehicle-to-home or vehicle-to-grid where supported;
- heat pumps and water heating;
- flexible household loads;
- grid reliability;
- energy trading;
- whole-home optimization.

Vision:

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

## Product principles

EnergyHub should remain:

- local-first;
- human-centric;
- calm;
- explainable;
- modular;
- hardware-aware;
- progressively automated;
- safe by design;
- resilient to communication failures.

Development progression:

```text
Monitoring
    ↓
Reliable Facts
    ↓
Health Awareness
    ↓
Explainable Decisions
    ↓
Validated Automation
    ↓
Autonomous Home Operation
    ↓
Telemetry Robustness
    ↓
Configurable Strategy
    ↓
Recovery & Resilience
    ↓
Smart Household Loads
    ↓
Whole-Home Energy Optimization
```

## Success metric

> How often does the homeowner need to think about the energy system?

**Almost never.**
