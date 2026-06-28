# EnergyHub Developer Architecture

> This document describes how EnergyHub should be structured internally for developers.

---

# Purpose

EnergyHub should hide hardware complexity behind clean software abstractions.

Application code should work with concepts such as:

* inverter mode
* battery state
* home mode
* energy surplus
* panic mode
* charging policy

It should not work directly with vendor-specific commands, MQTT topic strings or raw protocol responses.

---

# Core Layers

```text
EnergyHub Application
        |
EnergyHub Core
        |
Device Abstraction Layer
        |
Vendor Adapters
        |
Protocols
        |
Physical Devices
```

---

# EnergyHub Core

The Core contains business logic.

Examples:

* Decide when to charge the battery
* Decide when to enable Panic Mode
* Decide when to start the heat pump
* Decide when to notify the homeowner
* Decide when to use solar surplus

The Core should not know whether the inverter is PowMr, Deye or Victron.

---

# Device Abstraction Layer

This layer exposes generic device capabilities.

Example:

```python
inverter.set_output_source("solar_battery_utility")
inverter.set_charger_source("solar_and_utility")
battery.get_soc()
battery.get_power()
```

The rest of EnergyHub should use these abstractions instead of vendor commands.

# Vendor Adapters

Vendor adapters translate generic EnergyHub commands into hardware-specific commands.

Example:

```python
set_home_mode("panic")
```

may internally become:

```text
PowMr command → SNU
AC charging current → 100A
```

This translation must remain inside the PowMr adapter.

The rest of EnergyHub should never know vendor-specific commands.

---

# Protocol Layer

Protocols are transport mechanisms.

Examples:

* Serial
* USB-RS232
* Modbus
* MQTT
* Bluetooth
* REST API

Protocols move data and commands.

They should never contain business logic.

---

# MQTT

MQTT is the integration layer between EnergyHub and Home Assistant.

MQTT should expose stable, predictable and documented entities.

Application logic should never depend on hardcoded MQTT topic names scattered throughout the code.

---

# Home Assistant

Home Assistant is currently the primary runtime environment.

It provides:

* Entity Registry
* Dashboards
* Automations
* Add-on framework
* MQTT broker
* User interface

Home Assistant is infrastructure.

EnergyHub is the product.

The EnergyHub Core should remain portable so that future versions could support additional platforms if required.

# Configuration

Configuration should remain simple and human-readable.

Good example:

```yaml
inverter:
  type: powmr
  protocol: PI30MAX
  port: /dev/ttyUSB0
```

Bad example:

```yaml
command_qpigs: QPIGS
command_pop02: POP02
battery_soc_field: battery_capacity
```

Vendor-specific details belong inside adapters—not inside user configuration.

---

# Error Handling

EnergyHub should always fail safely.

Examples:

* If the BMS is unavailable, use inverter battery data.
* If weather forecasts are unavailable, switch to conservative automation.
* If MQTT disconnects, reconnect automatically.
* If an inverter command fails, verify the state before retrying.

Graceful degradation is preferred over complete failure.

---

# Logging

Logs should describe system behaviour rather than protocol details.

Good:

```text
[EnergyHub] Panic Mode enabled.
Reason: Grid outage detected.
Battery SOC: 42%.
```

Bad:

```text
POP02 OK
```

Every important log should answer:

* What happened?
* Why did it happen?
* Is user action required?

---

# Testing Strategy

Write operations should always be verified.

Recommended workflow:

1. Read current state.
2. Execute command.
3. Read state again.
4. Verify expected result.
5. Roll back if required.

Potentially dangerous operations should always be reversible.

# Repository Structure

Recommended project structure:

```text
EnergyHub/
│
├── addon/
│   └── app/
│       ├── core/
│       ├── devices/
│       ├── adapters/
│       ├── protocols/
│       ├── mqtt/
│       └── config/
│
├── homeassistant/
│   ├── dashboards/
│   ├── automations/
│   ├── templates/
│   └── examples/
│
├── tools/
│   ├── diagnostics/
│   ├── migration/
│   └── experiments/
│
└── docs/
```

The repository should clearly separate:

* Product code
* Home Assistant configuration
* Developer tools
* Documentation

---

# Development Rules

High-level EnergyHub code should never contain:

* Vendor commands
* MQTT topic strings
* Serial commands
* Hardware-specific logic

Instead, it should use EnergyHub abstractions.

Example:

Good:

```python
energyhub.inverter.set_mode("panic")
```

Bad:

```python
send_command("POP02")
```

---

# Long-Term Goal

EnergyHub should become a platform—not a collection of scripts.

Business logic, hardware integrations and communication protocols should evolve independently.

This architecture enables:

* vendor independence
* modular development
* easier testing
* cleaner code
* long-term maintainability

---

# Architecture Principle

High-level code speaks **EnergyHub language**.

Adapters speak **device language**.

Protocols speak **transport language**.

Each layer has a single responsibility.

This separation is the foundation that allows EnergyHub to grow from a Home Assistant project into an Operating System for Autonomous Homes.
 й