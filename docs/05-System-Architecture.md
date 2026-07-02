# EnergyHub System Architecture

> A modern home should behave as one coordinated system, not as a collection of independent devices.

---

# Overview

EnergyHub is designed as a layered architecture.

Each layer has a clear responsibility.

Higher layers never depend on specific hardware.

Lower layers never contain business logic.

This separation allows EnergyHub to remain modular, maintainable and vendor-independent.

---

# Architecture Layers

```
                 Homeowner

                      │

         Dashboards & Mobile App

                      │

────────────────────────────────────────

                EnergyHub Core

      Decision Engine
      Automation Engine
      Notification Engine
      Forecast Engine
      Device Manager

────────────────────────────────────────

             Home Assistant

────────────────────────────────────────

 MQTT   Modbus   Bluetooth   REST   Matter

────────────────────────────────────────

 PowMr   BMS   Shelly   ESPHome

 EV Charger   Heat Pump

 Sensors   Smart Plugs
```

---

# Current EnergyHub Core

The current implementation is built around small independent services.

```
                    PowMr Local Adapter
                            │
                            ▼
                     InverterState
                            │
                            ▼
                       Event Bus
                            │
          ┌─────────────────┴─────────────────┐
          ▼                                   ▼
  TelemetryService                    GridMonitor
                                              │
                                              ▼
                                     GridHistoryService
                                              │
                                              ▼
                                   Grid Confidence Engine
                                              │
                                              ▼
                                      Decision Engine
                                              │
                                              ▼
                                     Automation Engine
```

Current implemented services:

- PowMr Local Adapter
- InverterState
- Event Bus
- Telemetry Service
- Communication Watchdog
- Grid Monitor
- Grid History Service
- Grid Confidence Engine (initial implementation)

Future services:

- Decision Engine
- Automation Engine
- Forecast Engine
- Notification Engine
- Device Manager

---

# Layer 1 — User Experience

The homeowner interacts with simple concepts.

Examples:

- Summer Mode
- Winter Mode
- Away Mode
- Panic Mode

Users should never need to understand inverter commands, MQTT topics or hardware protocols.

---

# Layer 2 — EnergyHub Core

This layer contains all business logic.

Responsibilities include:

- Energy management decisions
- Automation execution
- Grid confidence evaluation
- Forecast processing
- Notification delivery
- Device abstraction
- Strategy selection

The EnergyHub Core remains independent from specific hardware vendors.

---

# Layer 3 — Home Assistant Platform

Home Assistant acts as the integration platform.

It provides:

- Entity model
- Automation framework
- MQTT integration
- Dashboard infrastructure
- Device discovery

EnergyHub extends Home Assistant rather than replacing it.

---

# Layer 4 — Communication

Communication remains independent from business logic.

Supported technologies include:

- MQTT
- Modbus
- Bluetooth
- REST APIs
- Matter
- Zigbee

New protocols should be added without changing the upper layers.

---

# Layer 5 — Devices

Devices represent the physical infrastructure.

Examples include:

- Inverters
- Batteries
- Solar controllers
- EV chargers
- Heat pumps
- Smart plugs
- Sensors

Devices should be replaceable without affecting the EnergyHub Core.

---

# Design Principles

Business logic must never depend directly on hardware.

Instead of:

```
PCP03
```

EnergyHub uses:

```
set_mode("panic")
```

Hardware adapters translate generic commands into vendor-specific implementations.

---

# Design Philosophy

EnergyHub is designed around **capabilities**, not devices.

The Decision Engine should never know whether a heat pump is controlled by:

- Xiaomi
- Shelly
- Zigbee
- Matter

Instead, it operates on abstract capabilities such as:

- House Heating
- Battery Charging
- EV Charging
- Grid Supply
- Solar Generation

Hardware adapters translate these capabilities into device-specific implementations.

This abstraction allows hardware to evolve without changing the EnergyHub decision logic.

---

# Mode Ownership

EnergyHub automatically manages normal operating modes.

```
Summer
Owner: EnergyHub

Winter
Owner: EnergyHub

Away
Owner: EnergyHub
```

Panic Mode is treated differently.

If Panic Mode is activated manually:

```
Owner: User
```

EnergyHub remains in Panic Mode until the user manually selects another mode.

During this period EnergyHub only provides recommendations.

If Panic Mode is activated automatically by EnergyHub:

```
Owner: EnergyHub
```

EnergyHub may automatically return to another operating mode according to its decision logic.

This guarantees that manual emergency decisions always take priority over automatic optimization.

---

# Future Architecture

Current implementation focuses on Home Assistant.

Future versions may support additional backends while preserving the same EnergyHub Core.

Planned future integrations include:

- PowMr Cloud Adapter
- JK BMS
- Smart meters
- Solcast
- Weather forecasts
- Dynamic electricity pricing
- Net Billing
- EV charging management

---

# Architectural Goal

EnergyHub should become the operating system layer that transforms independent smart devices into one autonomous home.

The long-term objective is an autonomous energy management platform capable of optimizing:

- Energy resilience
- Household comfort
- Operating costs
- Renewable energy utilization
- Future Net Billing profitability

while remaining independent from any particular hardware vendor or home automation platform.