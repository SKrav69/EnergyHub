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

# Layer 1 — User Experience

The homeowner interacts with simple concepts.

Examples:

* Summer Mode
* Winter Mode
* Away Mode
* Panic Mode

Users should never need to understand inverter commands, MQTT topics or hardware protocols.

---

# Layer 2 — EnergyHub Core

This layer contains all business logic.

Examples:

Decision Engine

Makes energy management decisions.

Automation Engine

Executes actions.

Forecast Engine

Uses weather forecasts and historical data.

Notification Engine

Communicates important events.

Device Manager

Provides a unified interface to all supported devices.

---

# Layer 3 — Home Assistant Platform

Home Assistant acts as the integration platform.

It provides:

* Entity model
* Automation framework
* MQTT integration
* Dashboard infrastructure
* Device discovery

EnergyHub extends Home Assistant rather than replacing it.

---

# Layer 4 — Communication

Communication should remain independent from business logic.

Supported technologies include:

* MQTT
* Modbus
* Bluetooth
* REST APIs
* Matter
* Zigbee

New protocols should be added without changing the upper layers.

---

# Layer 5 — Devices

Devices represent the physical infrastructure.

Examples include:

* Inverters
* Batteries
* Solar controllers
* EV chargers
* Heat pumps
* Smart plugs
* Sensors

Devices should be replaceable without affecting the EnergyHub Core.

---

# Design Principles

Business logic must never depend directly on hardware.

Instead of:

```
POP02
```

EnergyHub uses:

```
set_mode("panic")
```

Hardware adapters translate generic commands into vendor-specific implementations.

---

# Future Architecture

Current implementation focuses on Home Assistant.

Future versions may support additional backends while preserving the same EnergyHub Core.

The platform should remain independent from any single home automation ecosystem.

---

# Architectural Goal

EnergyHub should become the operating system layer that transforms independent smart devices into one autonomous home.
