# EnergyHub Project State

Last Updated: 2026-07-05

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
- Notification Engine
- Forecast Engine
- Device Manager
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
✅ Floor 3 Heat Pump Auto-Off
✅ House Model
✅ Daily Solar Surplus Estimated
✅ Daily Summary MQTT input path
✅ Daily Summary Engine v1

---

# Current Dashboard

## Developer Dashboard

Contains technical and operational diagnostics:

- PowMr telemetry
- Battery state
- Grid state
- Communication status
- Grid confidence
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

# Current Daily Summary Model

Daily Summary Engine v1 is implemented inside EnergyHub.

Home Assistant provides selected daily values through retained MQTT input topics.

EnergyHub consumes these inputs, stores a daily snapshot, and republishes EnergyHub-owned MQTT sensors for dashboards and future engines.

## Home Assistant source values

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

# Current Priorities

1. Reliability
2. Recovery strategy
3. Decision Engine v1
4. Explainable decisions
5. Telegram notifications

---

# Immediate Roadmap

- Complete Daily Summary Engine documentation.
- Investigate recovery strategy for network, MQTT and serial communication failures.
- Determine why EnergyHub telemetry previously stopped after a network connectivity problem.
- Design recovery behavior instead of blindly restarting services.
- Begin Decision Engine v1.
- Add recommendation-only operating modes:
  - Summer
  - Winter
  - Away
  - Panic

---

# Long-Term Vision

EnergyHub becomes the operating system of the house.

Home Assistant remains the integration platform.

Devices become interchangeable hardware adapters.

EnergyHub services create reliable facts and operational state.

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

## Next Milestone

Investigate recovery strategy for MQTT, network and serial communication failures.

After the recovery architecture is understood, begin Decision Engine v1.

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

After investigation:

- document the recovery architecture;
- implement only justified recovery mechanisms;
- deploy;
- test on the real system;
- commit.

After the Recovery Strategy milestone, begin Decision Engine v1.