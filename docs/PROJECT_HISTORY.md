# EnergyHub Changelog

This document summarizes major features, architectural milestones, and capabilities added to EnergyHub.

It intentionally focuses on functionality rather than bug fixes.

---

# 2026-06-16

## Initial EnergyHub foundation

### Added

- PowMr inverter communication
- PI30MAX protocol support
- Raspberry Pi integration
- Home Assistant integration
- MQTT communication
- Basic telemetry publishing

---

# 2026-06-17

## MQTT Device Integration

### Added

- MQTT Discovery
- Automatic Home Assistant entity creation
- Standard MQTT device model
- Availability topics

### Architecture

EnergyHub becomes MQTT-first.

---

# 2026-06-18

## Telemetry Engine

### Added

Real-time publishing of:

- Battery SOC
- Battery Voltage
- Battery Current
- PV Voltage
- PV Current
- PV Power
- Output Power
- Grid Voltage
- Grid Frequency
- Load Percentage
- Inverter Status

---

# 2026-06-20

## Repository & Documentation

### Added

- GitHub repository
- Documentation structure
- Development philosophy
- Design principles
- Architecture documentation
- Decision log

### Architecture

Documentation becomes part of development.

---

# 2026-06-22

## Grid Intelligence

### Added

Grid monitoring

Grid History

Grid Confidence

24-hour availability calculation

48-hour availability calculation

Grid outage history

### Architecture

Grid events become historical rather than instantaneous.

---

# 2026-06-24

## Developer Dashboard

### Added

Developer Dashboard

Real-time inverter diagnostics

Health visualization

Grid visualization

---

# 2026-06-25

## Family Dashboard

### Added

Family Dashboard

House status

Floor cards

Temperature monitoring

Heat pump controls

Simple homeowner interface

### Philosophy

Separate homeowner UI from engineering UI.

---

# 2026-06-26

## Communication Reliability

### Added

Communication Watchdog

Health Monitor

Communication state machine

Health MQTT entities

Communication diagnostics

### States

Starting

Online

Recovering

Offline

### Architecture

System health becomes a first-class subsystem.

---

# 2026-06-27

## Home Model

### Added

House Model

Floor documentation

Room documentation

Device inventory

Automation planning

### Architecture

Documentation now represents the physical house.

---

# 2026-06-28

## Dashboard Evolution

### Added

Daily Energy Statistics

7-day historical charts

Forecast integration

House Consumption chart

Grid Availability visualization

Dual-axis charts

### Removed

PV1 generation chart
(replaced because only one MPPT is available)

---

# 2026-06-29

## Heat Pump Automation

### Added

Floor 3 Heat Pump Auto-Off

Remaining countdown timer

Timer helper

Daily Energy Balance helper

Daily Energy Balance automation

### Architecture

Manual user actions can now have automatic expiration.

---

# 2026-07-03

## Project Architecture v2

### Added

Home Assistant Configuration documentation

Dashboard source files

Automation source files

Roadmap redesign

Daily Summary Engine design

Decision Engine design

### Architecture

EnergyHub architecture now consists of:

Telemetry Engine

Health Monitor

MQTT Publisher

Dashboards

Daily Summary Engine

Decision Engine

### Philosophy

Historical knowledge should be generated once.

Dashboards consume historical knowledge rather than calculating it.

Automation decisions should be explainable.

Documentation is treated as the source of truth.

---

# Upcoming

## Daily Summary Engine

Daily historical statistics

Daily Energy Balance

Daily Grid Availability

Daily Grid Import

Historical MQTT sensors

---

## Decision Engine

Summer Mode

Winter Mode

Away Mode

Panic Mode

Battery optimization

Heat pump optimization

EV charging

Smart plug scheduling

Explainable decisions

---

## Telegram Integration

Notifications

Warnings

Status

Remote mode switching

---

## Platform Expansion

Additional inverter vendors

Additional BMS vendors

EV chargers

Heat pumps

Matter

Vendor-independent architecture

# 2026-07-09

## Inverter Setting 01 control confirmed

### Added
- Verified programmatic control of Output Source Priority.
- Confirmed POP01 → SUB.
- Confirmed POP02 → SBU.
- Confirmed safe restore back to SBU.

### Architecture
EnergyHub can now control both key inverter strategy settings:
- Setting 01: output source priority
- Setting 16: charger source priority