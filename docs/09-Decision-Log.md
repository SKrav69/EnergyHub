# EnergyHub Decision Log

This document records the major architectural and design decisions made during the EnergyHub project.

The purpose is not to document implementation details, but to explain **why** specific decisions were made.

---

# Decision 001

## Home Assistant is the automation platform

### Decision

EnergyHub uses Home Assistant as its primary automation platform.

### Reason

Home Assistant already provides:

- MQTT integration
- Dashboards
- Device discovery
- Automations
- Large integration ecosystem

EnergyHub focuses on energy intelligence rather than replacing Home Assistant.

---

# Decision 002

## Prefer local communication

### Decision

Whenever possible, EnergyHub communicates with devices locally.

### Reason

The system must continue operating during:

- Internet outages
- Cloud service failures
- Vendor service interruptions

Local control is considered the primary implementation.

Cloud integrations may be added as optional adapters.

---

# Decision 003

## PI30MAX is the primary PowMr interface

### Decision

The first EnergyHub implementation uses the local PI30MAX protocol.

### Reason

PI30MAX provides reliable access to:

- Battery SOC
- Grid voltage
- Output power
- Charging configuration
- Operating modes
- Warning information

Although some inverter information is unavailable through PI30MAX, it is sufficient for reliable autonomous energy management.

---

# Decision 004

## Separate business logic from hardware

### Decision

Business logic must never communicate directly with hardware.

### Reason

Hardware changes.

Business rules should not.

Instead of vendor-specific commands such as:

```
PCP03
```

EnergyHub uses:

```
set_mode("panic")
```

Hardware adapters perform the protocol translation.

---

# Decision 005

## EnergyHub operates on capabilities

### Decision

EnergyHub works with abstract capabilities instead of specific devices.

### Examples

Instead of:

- Xiaomi Plug
- Shelly Relay
- PowMr Command

EnergyHub uses:

- House Heating
- EV Charging
- Battery Charging
- Grid Supply
- Solar Generation

### Reason

Devices may change.

Capabilities remain constant.

---

# Decision 006

## Grid Confidence replaces Grid Stability

### Decision

EnergyHub evaluates **Grid Confidence** rather than Grid Stability.

### Reason

The objective is not to measure the electrical grid.

The objective is to estimate how much EnergyHub should trust the grid when making energy management decisions.

Future Grid Confidence may include:

- Recent availability
- Weather forecast
- Planned outages
- Historical reliability

---

# Decision 007

## Automatic operating modes

### Decision

EnergyHub may automatically switch between:

- Summer
- Winter
- Away

### Reason

These represent normal operating conditions and should not require daily user interaction.

---

# Decision 008

## Manual Panic Mode has priority

### Decision

If Panic Mode is activated manually, EnergyHub must never leave Panic Mode automatically.

### Reason

Manual Panic Mode indicates that the user has additional information unavailable to EnergyHub.

Examples:

- Expected missile attacks
- User preference
- Special household requirements

During Manual Panic Mode, EnergyHub only provides recommendations.

---

# Decision 009

## Automatic Panic Mode

### Decision

If Panic Mode was activated automatically by EnergyHub, EnergyHub may later leave Panic Mode automatically.

### Reason

Automatic decisions should also be reversible when conditions improve.

---

# Decision 010

## Daily strategy evaluation

### Decision

EnergyHub evaluates the operating strategy once per day.

The target time is approximately midnight.

### Inputs

- Grid Confidence
- Battery SOC
- Solar forecast
- Weather forecast
- Electricity tariff
- House temperatures
- Manual overrides

### Result

EnergyHub selects the recommended operating strategy for the coming day.

---

# Decision 011

## Event-driven architecture

### Decision

EnergyHub is built around an Event Bus.

### Reason

Services remain independent.

Instead of calling every service directly, new inverter telemetry is published once and consumed by interested services.

Current subscribers include:

- Grid Monitor

Future subscribers may include:

- Battery Monitor
- Forecast Engine
- Decision Engine
- Notification Engine

---

# Decision 012

## Layered architecture

### Decision

EnergyHub follows a layered architecture.

```
Hardware

↓

Communication

↓

Adapters

↓

EnergyHub Core

↓

Decision Engine

↓

Automation

↓

User Interface
```

### Reason

Each layer has one responsibility.

Upper layers never depend on hardware.

Lower layers never contain business logic.

---

# Decision 013

## Home Assistant is an execution platform

### Decision

Home Assistant is responsible for execution.

EnergyHub is responsible for intelligence.

### Reason

Home Assistant already excels at:

- Device integration
- Dashboards
- Automations
- Entity management

EnergyHub should focus exclusively on making good energy management decisions.

---

# Decision 014

## EnergyHub optimizes policies, not devices

### Decision

EnergyHub is designed to optimize different operating policies.

Examples include:

- Resilience
- Comfort
- Economy
- Future Net Billing profitability

### Reason

Hardware may change.

Optimization goals may change.

The Decision Engine should remain flexible enough to support different strategies without redesigning the architecture.


## 2026-07-09 — Inverter output mode control confirmed

Decision:
EnergyHub may use POP commands to control inverter Setting 01.

Confirmed mapping:
- POP01 → SUB
- POP02 → SBU

Reason:
The mapping was verified safely using ACK response, QPIRI, QMOD and the physical inverter display.

Impact:
This unlocks the Inverter Strategy Controller for Solar, Hybrid and Panic modes.

---

# Future Decisions

This document will continue to evolve as EnergyHub grows.

Major architectural decisions should always be recorded here before significant implementation work begins.