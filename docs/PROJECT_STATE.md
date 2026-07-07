# EnergyHub Project State

Last Updated: 2026-07-06

---

# Project Vision

EnergyHub is an autonomous home energy management system built on top of Home Assistant.

Its goal is not only to monitor energy, but to make intelligent decisions about battery usage, heating, EV charging and household energy consumption.

EnergyHub should remain:

- local first;
- calm;
- explainable;
- modular;
- reliable;
- suitable for real daily family use.

---

# Current Architecture

```text
Homeowner
   ↓
Dashboards
   ↓
Home Assistant
   ↓
MQTT
   ↓
EnergyHub Core
   ↓
Services / Engines
   ↓
Devices
```

Current EnergyHub Core modules:

- Telemetry Service
- Event Bus
- Grid Monitor
- Grid History
- Grid Stability Engine
- Communication Watchdog
- Health Monitor
- Daily Summary Engine

Future modules:

- Decision Engine
- Battery Health Monitor
- Notification Engine
- Forecast Engine
- Device Manager
- BMS Adapter
- Telegram Bot

---

# Current Features Implemented

✅ PowMr telemetry  
✅ MQTT Discovery  
✅ Telemetry validation  
✅ Communication Watchdog  
✅ Health Monitor  
✅ Grid History  
✅ Grid Availability  
✅ Grid Stability Engine  
✅ Family Dashboard v1  
✅ Developer Dashboard improvements  
✅ Daily Energy Statistics dashboard  
✅ EnergyHub Status dashboard card  
✅ EnergyHub Intelligence dashboard card  
✅ Floor 3 Heat Pump Auto-Off  
✅ House Model  
✅ Daily Solar Surplus Estimated  
✅ Daily Summary MQTT input path  
✅ Daily Summary Engine v1  

---

# Current Dashboard Architecture

The EnergyHub Developer Dashboard now separates current operational state from information used for analysis and future decisions.

## EnergyHub Status

Purpose:

```text
What is happening now?

Is the system healthy?
```

Current information:

- Communication Status
- Battery SOC
- Battery Charging Current
- Battery Discharge Current
- House Load
- PV1 Power
- Grid Voltage

Future:

- Current Operating Mode
- prominent Operating Mode visualization
- consistent Operating Mode colors
- unified signed Battery Current sensor if useful
- Battery Health status
- Inverter Health status

---

## EnergyHub Intelligence

Purpose:

```text
What does EnergyHub know?

What information is available for decisions?
```

Current information:

- Grid Confidence
- Grid Available 24h
- Grid Available 48h
- Consumption Yesterday
- Solar Surplus Yesterday
- Solar Forecast Today
- Solar Forecast Tomorrow

Grid Confidence is displayed prominently using:

```text
🟢 NORMAL
🟡 UNSTABLE
🟠 RISK
🔴 PANIC
```

Future:

- Recommended Mode
- Recommendation
- Reason
- Recommended Action

When Current Mode and Recommended Mode differ, EnergyHub Intelligence should clearly explain why.

---

# Current Dashboard

## Developer Dashboard

Contains technical, operational and decision-support information:

- PowMr telemetry
- Battery state
- Grid state
- Communication status
- EnergyHub Status
- EnergyHub Intelligence
- Grid Confidence
- Grid Availability
- Daily energy statistics
- Smart plug / heat pump visibility

## Family Dashboard

Contains calm operational information for household members:

- Inverter/grid status
- Battery state
- Current house load
- Floor temperatures
- Smart plug controls
- Heat pump controls
- Operational warnings only when needed

---

# Known Hardware Limitations

PowMr PI30MAX currently exposes:

- Battery information
- Grid voltage
- Grid frequency
- Load
- PV1 telemetry only

Not available from the inverter:

- PV2 telemetry
- second output status
- reliable grid import/export counters
- reliable total PV generation when both PV inputs are involved

Because of this:

- inverter PV telemetry is treated as diagnostic;
- daily solar surplus is based on Solcast forecast, not inverter PV production;
- grid import is informational only and deferred until a later estimation model exists.

---

# Current Inverter Charging-Source Modes

The current PowMr firmware exposes three usable charging-source modes:

```text
OSO
CSO
SNU
```

`CUB` is not available on the current inverter firmware.

## OSO

Only Solar.

Current intended use:

```text
Summer Mode
```

Battery charging is performed from solar energy only.

## CSO

Solar First.

Real-system testing showed that CSO is not suitable for planned continuous grid charging.

Observed behavior:

```text
Night
PV = 0
Utility charging active

↓

PV generation begins

↓

Utility charging current significantly decreases
```

Because of this behavior, CSO is no longer the primary candidate for Winter scheduled charging or Panic charging.

## SNU

SNU is the current candidate for simultaneous utility and solar charging.

Possible future use:

```text
Winter scheduled grid charging
Panic charging
```

Expected strategy:

```text
Summer
→ OSO

Winter scheduled grid charging
→ SNU

Panic charging
→ SNU
```

SNU behavior must be validated through additional real-system testing before this strategy is considered final.

The planned charging-source strategy is therefore currently:

```text
OSO ↔ SNU
```

rather than the previously considered:

```text
OSO ↔ CSO
```

This remains pending completion of SNU real-system testing.

---

# Current Daily Summary Model

Daily Summary Engine v1 is implemented inside EnergyHub.

Home Assistant provides selected daily values through retained MQTT input topics.

EnergyHub consumes these inputs, stores a daily snapshot, and republishes EnergyHub-owned MQTT sensors for dashboards and future engines.

## Home Assistant Source Values

- Daily House Consumption
- Solcast Forecast Today
- Daily Solar Surplus Estimated

## Snapshot Timing

Home Assistant owns the daily snapshot timing.

At 23:50 local time:

- Home Assistant calculates and stores Daily Solar Surplus Estimated before daily source sensors reset at midnight.

At 23:51 local time:

- Home Assistant publishes the Daily Summary input values to MQTT.

EnergyHub receives the retained MQTT messages and creates or updates the daily snapshot when all required values are available.

## MQTT Input Topics

```text
energyhub/input/ha/daily_house_consumption
energyhub/input/ha/solar_forecast_today
energyhub/input/ha/daily_solar_surplus_estimated
```

## EnergyHub Daily Sensors

```text
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_forecast
sensor.energyhub_daily_solar_surplus_estimated
sensor.energyhub_daily_grid_availability
```

## Persistence

Daily summaries are stored in:

```text
/data/daily_summary.json
```

The service is idempotent.

Retained MQTT messages received after an EnergyHub restart do not create unnecessary snapshot updates when the stored values are unchanged.

---

# Daily Summary Architecture

```text
Home Assistant Daily Sensors
            │
            │ 23:50 snapshot
            ▼
Daily Solar Surplus Estimated
            │
            │ 23:51 MQTT publish
            ▼
energyhub/input/ha/*
            │
            ▼
DailySummaryService
            │
            ├── Persistent Daily History
            │      /data/daily_summary.json
            │
            └── EnergyHub MQTT Sensors
                        │
                        ▼
               Home Assistant Dashboards
                        │
                        ▼
              Future Decision Engine
```

The architectural responsibility is intentionally separated:

```text
Home Assistant
    │
    └── provides integration data and snapshot timing

EnergyHub Daily Summary Engine
    │
    ├── owns the daily summary data model
    ├── stores historical daily snapshots
    └── publishes EnergyHub-owned daily sensors

Decision Engine
    │
    └── consumes summarized facts
```

The Decision Engine must consume Daily Summary data rather than create historical facts itself.

---

# Solar Surplus Terminology

The old term:

```text
Daily Energy Balance
```

has been replaced with:

```text
Daily Solar Surplus Estimated
```

Meaning:

```text
Estimated solar energy that was probably not used today.
```

Formula:

```text
max(0, Solcast Forecast Today - Daily House Consumption)
```

The value is intentionally based on Solcast forecast rather than inverter PV telemetry.

The PowMr inverter exposes PV1 telemetry only. PV2 telemetry is not available, and PV2 may remain unused when PV1 generation is sufficient for current house load and battery charging demand.

Because of this, inverter PV telemetry cannot currently provide a reliable estimate of total daily solar generation.

Daily Solar Surplus Estimated is used for:

- historical statistics;
- understanding unused solar potential;
- future energy optimization;
- future Decision Engine context.

It should not be interpreted as meter-accurate unused solar energy.

---

# Grid Import

Daily Grid Import is not implemented in Daily Summary Engine v1.

The PowMr inverter does not expose a reliable accumulated grid import counter.

Future EnergyHub versions may estimate grid import during controlled grid-charging sessions.

The intended initial estimation model assumes:

- grid charging is intentionally enabled;
- charging normally occurs at night;
- PV generation during the charging period is assumed to be zero;
- battery SOC change is known;
- house consumption during the charging period is known.

Daytime grid import during Panic Mode may not be included in the estimate.

This is acceptable because Daily Grid Import Estimated is intended for informational and historical purposes only.

It must not be used as an authoritative input by the Decision Engine.

---

# Grid Confidence

Grid Confidence is calculated from rolling 48-hour grid availability.

Current thresholds:

```text
90–100%  → normal
60–90%   → unstable
30–60%   → risk
0–30%    → panic
```

Grid Confidence is an operational metric.

Daily Grid Availability is a historical metric.

They are related but separate concepts.

The architecture is:

```text
Grid Monitor
      │
      ▼
Grid History Service
      │
      ├── Daily Availability
      │        │
      │        ▼
      │   Daily Summary Engine
      │
      └── Rolling 48h Availability
               │
               ▼
        Grid Stability Engine
               │
               ▼
          Grid Confidence
```

---

# Battery Health Monitoring

Status:

```text
Planned
```

Recent real-system battery behavior demonstrated the need for dedicated Battery Health monitoring.

Observed abnormal SOC changes included:

```text
53% → 1%
33% → 100%
```

The first Battery Health feature should detect abnormal SOC changes between telemetry updates.

Initial detection concept:

```text
SOC change >= 3%
→ warning

SOC change >= 10%
→ critical
```

These thresholds require validation against real battery behavior.

Future Battery Health responsibilities may include:

- SOC jump detection;
- Battery Health status;
- latest SOC anomaly information;
- anomaly persistence;
- Battery Health MQTT sensors;
- notifications;
- direct BMS data integration.

Possible future architecture:

```text
PowMr Telemetry ────────┐
                        │
                        ▼
                Battery Health Monitor
                        │
                        ├── Health State
                        ├── MQTT Sensors
                        ├── Alerts
                        └── Decision Engine Inputs

JK BMS Adapter ─────────┘
```

The Battery Health Monitor should not depend directly on JK BMS protocol implementation.

Hardware communication and Battery Health analysis should remain separate responsibilities.

---

# JK BMS Integration

Status:

```text
Paused
```

Priority:

```text
Medium
```

A previous attempt to integrate JK BMS telemetry directly into EnergyHub was paused after communication issues.

The integration should be revisited after the current reliability and Decision Engine foundation work.

Target timeframe:

```text
Approximately 1–2 weeks
```

Required data:

- individual cell voltages;
- minimum cell voltage;
- maximum cell voltage;
- cell voltage delta;
- Battery Current;
- Battery Voltage;
- Battery SOC;
- battery temperatures;
- BMS alarms and protection states;
- balancing status.

Purpose:

- detect cell imbalance;
- detect abnormal SOC behavior;
- monitor battery health;
- improve battery diagnostics;
- generate Battery Health alerts;
- provide reliable battery information for the future Decision Engine.

Target architecture:

```text
JK BMS
    │
    ▼
BMS Adapter
    │
    ▼
Battery Health Monitor
    │
    ├── MQTT Sensors
    ├── Health Alerts
    └── Decision Engine Inputs
```

JK BMS protocol handling must remain separate from Battery Health analysis.

The BMS Adapter should translate hardware-specific data into a stable EnergyHub battery data model.

---

# Inverter Health Monitoring

Status:

```text
Research Required
```

An unexpected inverter restart demonstrated the need to investigate available inverter warning and fault information.

Future investigation should include:

- PI30MAX warning information;
- `QPIWS`;
- additional supported warning or fault commands;
- detection of unexpected inverter restarts where possible;
- persistence of latest warning or fault information;
- MQTT health entities;
- notifications.

Possible future entities:

```text
sensor.energyhub_inverter_warning_status
sensor.energyhub_inverter_last_warning
binary_sensor.energyhub_inverter_fault
```

Inverter Health Monitoring belongs to the EnergyHub reliability and health architecture.

---

# Current Priorities

1. Reliability and Recovery Strategy
2. Battery Health / SOC Jump Detection
3. Decision Engine v1
4. Explainable decisions
5. JK BMS Integration
6. Inverter Health Monitoring
7. Telegram notifications

---

# Immediate Roadmap

- Complete documentation updates for 2026-07-06.
- Complete real-system SNU charging behavior testing.
- Investigate Recovery Strategy for network, MQTT and serial communication failures.
- Determine why EnergyHub telemetry previously stopped after a network connectivity problem.
- Design targeted recovery behavior instead of blindly restarting services.
- Implement initial Battery SOC jump detection.
- Begin Decision Engine v1.
- Add recommendation-only operating modes:
  - Summer
  - Winter
  - Away
  - Panic
- Revisit JK BMS integration after the current reliability and Decision Engine foundation work.
- Investigate inverter warning and fault telemetry.

---

# Long-Term Vision

EnergyHub becomes the operating system of the house.

Home Assistant remains the integration platform.

Devices become interchangeable hardware adapters.

EnergyHub services create reliable facts and operational state.

Health services detect abnormal system and battery behavior.

The Decision Engine consumes those facts and produces explainable recommendations and, later, automated actions.

---

# 2026-07-03

## Completed

- Communication Health Monitor implemented.
- MQTT Health discovery added.
- Grid Availability sensors completed.
- Grid Confidence implemented.
- Family Dashboard v1 created.
- Developer Dashboard improved.
- Floor cards implemented:
  - 1st Floor
  - 2nd Floor
  - 3rd Floor
- 3rd Floor Heat Pump Auto-Off helper implemented.
- Daily Energy Statistics chart redesigned.
- House Consumption replaces PV1 generation.
- Secondary Grid Availability axis added.
- Daily Energy Balance concept implemented.
- Daily Energy Balance helper and automation created.

## Decisions

- Historical values must be generated by EnergyHub rather than calculated continuously in Home Assistant.
- Daily summaries are generated once per day.
- Family Dashboard should expose only operational information.
- Technical diagnostics belong to the Developer Dashboard.

---

# 2026-07-05

## Completed

- Daily Energy Balance renamed to Daily Solar Surplus Estimated.
- Daily Solar Surplus Estimated helper and automation updated.
- Daily Solar Surplus calculation changed to never go below zero.
- Daily Summary MQTT input automation added in Home Assistant.
- Home Assistant now publishes daily summary inputs to MQTT at 23:51.
- Daily Summary Engine v1 implemented in EnergyHub.
- `DailySummaryService` added to the EnergyHub service architecture.
- EnergyHub subscribes to retained Home Assistant Daily Summary input topics.
- EnergyHub stores daily snapshots in `/data/daily_summary.json`.
- EnergyHub publishes Daily Summary sensors through MQTT Discovery.
- Energy Statistics chart migrated to EnergyHub-owned Daily Summary sensors.
- Retained MQTT restart behavior made idempotent.
- Grid Confidence calculation changed to rolling 48-hour availability percentage thresholds.

## Daily Summary Sensors Added

```text
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_forecast
sensor.energyhub_daily_solar_surplus_estimated
sensor.energyhub_daily_grid_availability
```

## Decisions

- Home Assistant owns Daily Summary snapshot timing for now.
- The Daily Solar Surplus Estimated helper is captured at 23:50 before daily source sensors reset.
- Home Assistant publishes Daily Summary inputs at 23:51.
- EnergyHub owns the Daily Summary data model, persistence and published daily sensors.
- Daily Solar Surplus Estimated is based on Solcast forecast rather than inverter PV telemetry.
- Daily Grid Import Estimated is deferred.
- Daily Grid Import Estimated will be informational only.
- Daily Grid Import Estimated must not be used as an authoritative Decision Engine input.
- Grid Confidence is based on rolling 48-hour availability.
- Daily Grid Availability and Grid Confidence remain separate concepts.
- Decision Engine should consume Daily Summary Engine data rather than create historical facts.

---

# 2026-07-06

## Completed

- Energy Statistics dashboard card updated.
- Historical Daily Summary values remain in the 7-day chart.
- Live `Consumption Today` added to the Energy Statistics header.
- Developer Dashboard monitoring split into two distinct cards:
  - EnergyHub Status
  - EnergyHub Intelligence
- EnergyHub Status card updated with:
  - Communication Status
  - Battery SOC
  - Battery Charging Current
  - Battery Discharge Current
  - House Load
  - PV1 Power
  - Grid Voltage
- EnergyHub Intelligence card updated with:
  - prominent dynamic Grid Confidence status;
  - Grid Available 24h;
  - Grid Available 48h;
  - Consumption Yesterday;
  - Solar Surplus Yesterday;
  - Solar Forecast Today;
  - Solar Forecast Tomorrow.
- Historical Solar Forecast Yesterday removed from EnergyHub Intelligence.
- Dynamic Grid Confidence visualization added:

```text
🟢 NORMAL
🟡 UNSTABLE
🟠 RISK
🔴 PANIC
```

## Real-System Findings

### Battery SOC Behavior

Abnormal Battery SOC changes were observed:

```text
53% → 1%
33% → 100%
```

This identified the need for dedicated Battery Health monitoring and SOC jump detection.

### Inverter Charging-Source Modes

The current PowMr firmware exposes:

```text
OSO
CSO
SNU
```

`CUB` is not available.

Real-system CSO testing showed:

```text
PV = 0
→ utility charging active

PV generation begins
→ utility charging current significantly decreases
```

Because of this behavior, CSO is no longer the primary candidate for planned Winter or Panic grid charging.

SNU is now the candidate charging-source mode for:

```text
Winter scheduled grid charging
Panic charging
```

SNU behavior remains pending additional real-system testing.

### Unexpected Inverter Restart

An unexpected inverter restart identified the need to investigate available inverter warning and fault information.

Future investigation should include PI30MAX warning and fault commands, including `QPIWS`.

## Decisions

- Developer Dashboard information is separated into two responsibilities:

```text
EnergyHub Status
→ current operational state
→ system health

EnergyHub Intelligence
→ information available for decisions
→ future recommendations and explanations
```

- Current Operating Mode should eventually be displayed prominently in EnergyHub Status.
- Future Operating Mode colors should remain consistent:
  - Summer → orange;
  - Winter → dark blue;
  - Panic → warning pink/red;
  - Away → gray.
- Recommended Mode, Reason and Recommended Action should eventually be displayed in EnergyHub Intelligence.
- Separate Battery Charging Current and Battery Discharge Current sensors remain on the Status card for now.
- A unified signed Battery Current sensor is deferred as a future improvement.
- Battery SOC jump detection should be added to Battery Health monitoring.
- Direct JK BMS integration should be revisited in approximately 1–2 weeks.
- JK BMS protocol handling and Battery Health analysis must remain separate architectural responsibilities.
- Inverter warning and fault monitoring requires investigation.
- The planned inverter charging-source strategy is being reconsidered from:

```text
OSO ↔ CSO
```

to:

```text
OSO ↔ SNU
```

pending completion of SNU real-system testing.

## Validation

- Verified updated Energy Statistics dashboard behavior.
- Verified live Consumption Today display.
- Verified separation of EnergyHub Status and EnergyHub Intelligence.
- Verified dynamic Grid Confidence visualization.
- Verified Battery Charging Current and Battery Discharge Current display.
- Performed initial real-system CSO charging behavior test.

---

# Current Milestone Status

## Foundation

Status: Complete

Implemented:

- PowMr integration
- Telemetry Engine
- MQTT Discovery
- Communication Watchdog
- Health Monitor
- Grid Monitor
- Grid History
- Grid Confidence
- Family Dashboard
- Developer Dashboard
- House Model

## Daily Summary Engine

Status: v1 Complete

Implemented:

- Home Assistant daily source integration through MQTT
- retained MQTT input topics
- `DailySummaryService`
- persistent daily history
- MQTT Discovery
- EnergyHub-owned daily sensors
- dashboard migration
- restart idempotency

Deferred:

- Daily Grid Import Estimated
- Battery Grid Charge Estimated
- advanced historical analysis

## Recovery Strategy

Status: Next

Goals:

- investigate MQTT disconnection behavior;
- investigate serial communication failures;
- investigate `mpp-solar` blocking and timeout behavior;
- investigate Home Assistant and network connectivity failures;
- determine why service restart previously restored telemetry;
- design targeted recovery mechanisms;
- avoid unnecessary blind restarts;
- add recovery grace periods where appropriate.

## Battery Health Monitoring

Status: Planned

Initial goal:

```text
Detect abnormal Battery SOC jumps between telemetry updates.
```

Future goals:

- Battery Health state;
- anomaly persistence;
- MQTT sensors;
- notifications;
- JK BMS data integration.

## Decision Engine

Status: Planned

Initial modes:

```text
Summer
Winter
Away
Panic
```

Initial implementation should be recommendation-only.

Automatic control should be introduced progressively after recommendations are validated against real household behavior.

## JK BMS Integration

Status: Paused / Revisit

Target:

```text
Approximately 1–2 weeks
```

Goal:

Provide direct cell-level battery information to the future Battery Health Monitor.

## Inverter Health Monitoring

Status: Research Required

Goal:

Investigate inverter warning, fault and unexpected restart information available through PI30MAX.

---

# Development Workflow

EnergyHub development follows this cycle:

```text
Architecture
    ↓
Implement
    ↓
Deploy
    ↓
Test on Real System
    ↓
Document
    ↓
Commit
```

Every runtime change must be deployed and tested on the real EnergyHub system before commit.

Documentation must be updated whenever architecture or system behavior changes.

Git and project documentation remain the source of truth.

If code and documentation differ, they must be reconciled rather than creating a new undocumented architecture.

---

# Next Session

Start with the EnergyHub Recovery Strategy investigation.

Do not begin by implementing automatic restart logic.

First determine:

1. What failed during the previous telemetry interruption?
2. Was MQTT disconnected?
3. Was `mpp-solar` blocked?
4. Did serial communication stop?
5. Did Home Assistant lose connectivity?
6. Why did restarting EnergyHub restore operation?
7. Which failures can EnergyHub detect automatically?
8. Which failures can EnergyHub recover from safely?

After the Recovery Strategy investigation:

- document the recovery architecture;
- implement only justified recovery mechanisms;
- deploy;
- test on the real system;
- commit.

In parallel with the next development milestones:

- complete real-system SNU charging behavior testing;
- implement initial Battery SOC jump detection;
- investigate inverter warning and fault telemetry;
- revisit JK BMS integration in approximately 1–2 weeks.

After the Recovery Strategy milestone, begin Decision Engine v1.

The initial Decision Engine should remain recommendation-only.

Future automatic inverter control should be introduced progressively only after:

- Decision Engine recommendations have been validated;
- SNU charging behavior has been confirmed;
- inverter control commands have been tested safely;
- recovery behavior is understood.

---

# Immediate Next Actions

```text
1. Complete documentation updates
2. Commit dashboard and documentation changes
3. Test SNU charging behavior on the real inverter
4. Investigate Recovery Strategy
5. Implement Battery SOC jump detection
6. Begin Decision Engine v1
7. Revisit JK BMS integration
8. Investigate Inverter Health telemetry
```

---

# Project Principle

EnergyHub should evolve from:

```text
Monitoring
    ↓
Reliable Facts
    ↓
Health Awareness
    ↓
Recommendations
    ↓
Explainable Decisions
    ↓
Carefully Validated Automation
```

The system should not automate behavior simply because automation is technically possible.

Every automated decision should be based on reliable facts, observable system behavior and validated real-world experience.