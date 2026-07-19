# EnergyHub Roadmap

The roadmap is organized by product capability, not by speculative code layers.

## EnergyHub 1.0 — Autonomous Home

### Goal

A tested autonomous strategy layer for one house, one PowMr inverter, one battery, and Home Assistant.

### Delivered

- local PI30MAX telemetry and control;
- stable MQTT Discovery entities;
- Solar, Hybrid Charging, Hybrid Grid Hold, and Panic;
- Autopilot permission gate;
- live Solcast decision inputs;
- Grid History and Grid Confidence;
- Grid Import estimation;
- atomic Daily Summary;
- midnight Grid Import reconciliation;
- communication, battery, telemetry, inverter, and system health;
- transition verification and bounded Solar recovery;
- restart-safe strategy reconstruction;
- confirmed transition notifications;
- family and technical infographics;
- redesigned charts, status, decision, mode, and floor dashboards.

### Remaining release closure

- executable automated tests;
- pin tested dependencies;
- secure MQTT default configuration;
- complete installation, upgrade, and rollback instructions;
- remove remaining UI placeholders and repository artifacts;
- validate real daytime Panic Grid Import behavior;
- package and tag the release.

## EnergyHub 1.1 — Test-Drive and Telemetry Robustness

### Goal

Improve behavior from real-world operation without changing the core architecture.

### Planned

- general telemetry plausibility layer;
- distinguish valid rapid SOC changes from impossible jumps;
- protect energy calculations from anomalous telemetry;
- evaluate whether Panic should use a live PV threshold;
- validate and refine daytime SUB Grid Import estimation;
- improve decision and transition test coverage;
- add the second-floor heat-pump smart plug when hardware is available;
- preserve manual load ownership semantics;
- small UI and notification corrections discovered during test drive.

## EnergyHub 1.2 — Configurable EnergyHub

### Goal

Move trusted strategy policy from code constants into validated user configuration.

### Planned settings

- cheap-tariff start and end;
- battery capacity;
- Hybrid target SOC;
- Panic trigger and target SOCs;
- forecast safety factor;
- grid-confidence thresholds;
- charging current policy;
- strategy profiles;
- notification preferences.

Technical safety limits and household policy settings must be clearly separated.

## EnergyHub 1.3 — Recovery & Resilience

### Goal

Make recovery responsibilities explicit across MQTT, network, serial, `mpp-solar`, Home Assistant, and process lifecycle failures.

### Planned

- bounded reconnect policies;
- serial and command timeout classification;
- state-aware retries;
- internal fallback for missed 07:00 restoration;
- startup reconstruction after delayed HA/MQTT availability;
- external heartbeat/watchdog;
- safe process restart policy;
- clear recovery notifications;
- no automatic inverter reboot.

## EnergyHub 1.4 — Remote Access & Telegram

### Goal

Securely administer and understand the home from another network.

### Planned

- secure remote Home Assistant access;
- Cloudflare Tunnel primary path;
- WireGuard backup path;
- Telegram status command;
- important health and strategy alerts;
- optional approved commands;
- auditable command ownership and permission checks.

## EnergyHub 1.5 — Smart Thermal Energy

### Goal

Convert surplus solar or cheap-tariff electricity into useful heating or cooling through Home Assistant-controlled heat pumps.

This replaces the narrow experimental Away Mode concept.

### Principles

- works whether anyone is home or away;
- uses selected heat-pump smart plugs;
- starts only when energy, reserve, and comfort conditions allow;
- stops around a configurable reserve boundary;
- prevents short cycling;
- respects minimum run and cooldown times;
- respects comfort limits;
- stops only loads that EnergyHub started;
- supports multiple prioritized thermal loads.

### Initial concept

A possible first policy is:

```text
SOC approximately 95% or higher
+ useful solar surplus or cheap tariff
+ room comfort permits
→ start selected heat pump
```

```text
SOC approximately 80% or lower
or reserve/comfort/safety rule reached
→ stop EnergyHub-owned load
```

Exact thresholds remain design parameters, not final requirements.

## EnergyHub 2.x — Energy Optimization Platform

- capability-based inverter and battery adapters;
- economic optimization across tariffs;
- better forecast uncertainty;
- EV charging templates;
- flexible-load prioritization;
- multi-day reserve planning;
- measured import/export integration where hardware supports it.

## EnergyHub 3.x — Full Home Energy Management System

- whole-home energy orchestration;
- multiple generation and storage assets;
- comfort, cost, resilience, and lifecycle optimization;
- vendor-independent capability model;
- explainable policy engine;
- household and installer product modes.

## Roadmap rule

A roadmap item moves into implementation only when:

- the household outcome is clear;
- responsibility ownership is defined;
- safe exits and failure behavior are designed;
- required telemetry is available;
- the change can be validated.
