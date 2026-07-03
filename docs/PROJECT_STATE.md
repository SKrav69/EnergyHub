# EnergyHub Project State

Last Updated: 2026-07-03

---

# Project Vision

EnergyHub is an autonomous home energy management system built on top of Home Assistant.

Its goal is not only to monitor energy, but to make intelligent decisions about battery usage, heating, EV charging and household energy consumption.

---

# Current Architecture

Homeowner

↓

Dashboards

↓

EnergyHub Core

↓

Home Assistant

↓

MQTT / Modbus / Bluetooth

↓

Devices

Current EnergyHub Core modules:

- Telemetry Service
- Event Bus
- Grid Monitor
- Grid History
- Grid Stability Engine
- Communication Watchdog
- Health Monitor

Future modules:

- Decision Engine
- Notification Engine
- Forecast Engine
- Device Manager

---

# Current Features

Implemented

✅ PowMr telemetry

✅ MQTT Discovery

✅ Telemetry validation

✅ Communication Watchdog

✅ Health Monitor

✅ Grid History

✅ Grid Availability

✅ Grid Stability Engine

---

# Current Dashboard

Developer Dashboard

- PowMr telemetry
- Energy graphs
- Smart lamp status

Family Dashboard

Planning started.

---

# Known Hardware Limitations

PowMr PI30MAX currently exposes:

- Battery information
- Grid voltage
- Grid frequency
- Load
- PV1 only

Not available:

- PV2 telemetry
- Second output status
- Energy import/export counters

---

# Current Priorities

1. Reliability
2. Dashboard
3. Decision Engine

---

# Immediate Roadmap

- Communication Health Card
- Family Dashboard v1
- Daily Energy Summary
- Decision Engine v1

---

# Long-Term Vision

EnergyHub becomes the operating system of the house.

Home Assistant becomes the integration platform.

Devices become interchangeable hardware adapters.