# Home Assistant Configuration

This document describes Home Assistant objects created specifically for EnergyHub.

Home Assistant remains the integration and presentation platform.

EnergyHub owns system intelligence, persistent operational state, historical summaries and future decision logic.

---

# Helpers

## Daily Solar Surplus Estimated

Entity:

```text
input_number.energyhub_daily_solar_surplus_estimated
```

Purpose:

Stores the estimated daily solar energy that was probably not used.

Updated:

23:50 every day by automation:

```text
EnergyHub - Daily Solar Surplus Estimated Snapshot
```

Formula:

```text
max(0, Solcast Forecast Today - Daily House Consumption)
```

Source entities:

```text
sensor.solcast_pv_forecast_forecast_today
sensor.powmr_10_2m_daily_house_consumption
```

The previous concept:

```text
Daily Energy Balance
```

was renamed to:

```text
Daily Solar Surplus Estimated
```

The calculation intentionally uses Solcast forecast rather than inverter PV generation.

The PowMr inverter exposes PV1 telemetry only and does not provide reliable total PV1 + PV2 production.

---

## Floor 3 Heat Pump Auto-Off

Entity:

```text
input_number.input_number_floor3_heat_pump_timer_hours
```

Purpose:

Number of hours before automatic switch-off.

Values:

```text
0 = Manual
1..9 = Auto-Off after N hours
```

---

## Floor 3 Countdown Timer

Entity:

```text
timer.floor_3_heat_pump_auto_off
```

Purpose:

Displays remaining time until automatic switch-off.

---

# Automations

## Daily Solar Surplus Estimated Snapshot

Runs every day at 23:50.

Purpose:

Stores Daily Solar Surplus Estimated before daily source sensors reset at midnight.

Automation:

```yaml
alias: EnergyHub - Daily Solar Surplus Estimated Snapshot
description: Store estimated unused solar energy before daily sensors reset
triggers:
  - at: "23:50:00"
    trigger: time

variables:
  forecast: "{{ states('sensor.solcast_pv_forecast_forecast_today') | float(0) }}"
  consumption: "{{ states('sensor.powmr_10_2m_daily_house_consumption') | float(0) }}"
  surplus: "{{ [0, forecast - consumption] | max | round(1) }}"

actions:
  - target:
      entity_id: input_number.energyhub_daily_solar_surplus_estimated
    data:
      value: "{{ surplus }}"
    action: input_number.set_value

mode: single
```

---

## Publish Daily Summary Inputs

Runs every day at 23:51.

Purpose:

Publishes Home Assistant Daily Summary source values to EnergyHub through retained MQTT messages.

The one-minute separation ensures that the 23:50 Daily Solar Surplus Estimated snapshot has completed before the values are published.

Automation:

```yaml
alias: EnergyHub - Publish Daily Summary Inputs
description: Publish HA daily summary values to EnergyHub via MQTT
triggers:
  - at: "23:51:00"
    trigger: time

actions:
  - action: mqtt.publish
    data:
      topic: energyhub/input/ha/daily_house_consumption
      payload: "{{ states('sensor.powmr_10_2m_daily_house_consumption') }}"
      retain: true

  - action: mqtt.publish
    data:
      topic: energyhub/input/ha/solar_forecast_today
      payload: "{{ states('sensor.solcast_pv_forecast_forecast_today') }}"
      retain: true

  - action: mqtt.publish
    data:
      topic: energyhub/input/ha/daily_solar_surplus_estimated
      payload: "{{ states('input_number.energyhub_daily_solar_surplus_estimated') }}"
      retain: true

mode: single
```

---

## Floor 3 Heat Pump Auto-Off

Responsibilities:

- Starts countdown timer.
- Restarts timer when duration changes.
- Cancels timer when heat pump is switched off.
- Switches heat pump off when timer finishes.
- Resets Auto-Off helper to 0.

---

# Daily Summary Integration

Home Assistant provides selected daily energy values that are not available reliably from the PowMr inverter.

Current source values:

- Daily House Consumption
- Solcast Forecast Today
- Daily Solar Surplus Estimated

These values are transferred to EnergyHub through retained MQTT messages.

EnergyHub then owns:

- the Daily Summary data model;
- persistent daily snapshots;
- EnergyHub Daily Summary MQTT sensors;
- the data interface used by dashboards;
- the data interface for the future Decision Engine.

The architecture is:

```text
Home Assistant Sensors
        │
        ▼
23:50 Solar Surplus Snapshot
        │
        ▼
23:51 MQTT Publication
        │
        ▼
energyhub/input/ha/*
        │
        ▼
DailySummaryService
        │
        ├── /data/daily_summary.json
        │
        └── EnergyHub MQTT Sensors
                    │
                    ▼
              HA Dashboards
                    │
                    ▼
          Future Decision Engine
```

---

# Daily Summary MQTT Input Topics

EnergyHub subscribes to:

```text
energyhub/input/ha/#
```

Current input topics:

```text
energyhub/input/ha/daily_house_consumption
energyhub/input/ha/solar_forecast_today
energyhub/input/ha/daily_solar_surplus_estimated
```

Messages are retained.

This allows EnergyHub to receive the latest Daily Summary inputs after restart.

`DailySummaryService` prevents unnecessary snapshot writes when retained values are unchanged.

---

# EnergyHub Daily Summary Entities

EnergyHub publishes four Daily Summary sensors through MQTT Discovery:

```text
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_forecast
sensor.energyhub_daily_solar_surplus_estimated
sensor.energyhub_daily_grid_availability
```

These entities are owned by EnergyHub.

Dashboards should prefer EnergyHub Daily Summary entities over the original Home Assistant source entities when displaying historical daily statistics.

---

# Developer Dashboard Architecture

The Developer Dashboard separates current operational state from information used for analysis and future decision-making.

The architecture is:

```text
EnergyHub Status
→ What is happening now?
→ Is the system healthy?

EnergyHub Intelligence
→ What does EnergyHub know?
→ What information is available for decisions?
```

This separation prevents duplication and gives each dashboard card a clear responsibility.

---

# Energy Statistics Dashboard

The 7-day Energy Statistics chart displays completed Daily Summary history.

Historical chart entities:

```text
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_surplus_estimated
sensor.energyhub_daily_grid_availability
```

Live current-day information is displayed in the dashboard header.

Current header entities include:

```text
sensor.powmr_10_2m_daily_house_consumption
sensor.solcast_pv_forecast_forecast_today
sensor.solcast_pv_forecast_forecast_tomorrow
```

The distinction is intentional:

```text
7-day chart
→ completed historical Daily Summary values

Header
→ live current-day values and future forecasts
```

The data flow is:

```text
HA Source Sensors
        │
        ▼
Daily Summary MQTT Inputs
        │
        ▼
EnergyHub DailySummaryService
        │
        ▼
EnergyHub Daily Sensors
        │
        ▼
Energy Statistics Dashboard
```

---

# EnergyHub Status Card

Purpose:

```text
What is happening now?

Is the system healthy?
```

Current entities:

```text
sensor.energyhub_communication_status
sensor.powmr_10_2m_battery_soc
sensor.powmr_10_2m_battery_charging_current
sensor.powmr_10_2m_battery_discharge_current
sensor.powmr_10_2m_output_power
sensor.powmr_10_2m_pv1_power
sensor.powmr_10_2m_grid_voltage
```

Current information:

- Communication Status
- Battery SOC
- Battery Charging Current
- Battery Discharge Current
- House Load
- PV1 Power
- Grid Voltage

Future improvements:

- Current Operating Mode
- prominent Operating Mode visualization
- consistent Operating Mode colors
- Battery Health status
- Inverter Health status
- optional unified signed Battery Current sensor

Planned Operating Mode colors:

```text
Summer → orange
Winter → dark blue
Panic  → warning pink/red
Away   → gray
```

The unified Battery Current sensor is deferred.

For now, separate Battery Charging Current and Battery Discharge Current sensors remain visible.

---

# EnergyHub Intelligence Card

Purpose:

```text
What does EnergyHub know?

What information is available for decisions?
```

Current entities:

```text
sensor.energyhub_grid_confidence
sensor.energyhub_grid_available_24h
sensor.energyhub_grid_available_48h
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_surplus_estimated
sensor.solcast_pv_forecast_forecast_today
sensor.solcast_pv_forecast_forecast_tomorrow
```

Current information:

- Grid Confidence
- Grid Available 24h
- Grid Available 48h
- Consumption Yesterday
- Solar Surplus Yesterday
- Solar Forecast Today
- Solar Forecast Tomorrow

Historical Solar Forecast Yesterday was removed because it is not currently useful for Decision Engine logic or daily operational monitoring.

Grid Confidence is displayed prominently using:

```text
🟢 NORMAL
🟡 UNSTABLE
🟠 RISK
🔴 PANIC
```

Current Grid Confidence thresholds:

```text
90–100% → normal
60–90%  → unstable
30–60%  → risk
0–30%    → panic
```

Future improvements:

- Recommended Mode
- Recommendation
- Reason
- Recommended Action

The intended future relationship is:

```text
EnergyHub Status
→ Current Mode

EnergyHub Intelligence
→ Recommended Mode
→ Recommendation
→ Reason
→ Recommended Action
```

---

# Dashboard Responsibilities

The three main EnergyHub dashboard cards currently have separate responsibilities.

## Energy Statistics

```text
What happened over time?
```

Provides:

- historical energy statistics;
- live Consumption Today;
- current solar forecasts.

## EnergyHub Status

```text
What is happening now?
```

Provides:

- current operational state;
- battery behavior;
- inverter telemetry;
- communication health.

## EnergyHub Intelligence

```text
What does EnergyHub know?
```

Provides:

- Grid Confidence;
- recent Grid Availability;
- previous-day energy facts;
- future solar forecasts.

Future Decision Engine recommendations and explanations will be added to EnergyHub Intelligence.

---

# Daily Grid Import

Daily Grid Import Estimated is not implemented yet.

The PowMr inverter does not provide a reliable accumulated grid import counter.

A future EnergyHub version may estimate grid import during controlled night grid-charging sessions.

The intended initial estimation model assumes:

- grid charging is intentionally enabled;
- charging normally occurs at night;
- PV generation during the charging period is assumed to be zero;
- battery SOC change is known;
- house consumption during the charging period is known.

Daytime grid import during Panic Mode may not be included in the estimate.

This is acceptable because Daily Grid Import Estimated is intended for informational and historical purposes only.

Daily Grid Import Estimated must not be used as an authoritative Decision Engine input.

---

# Home Assistant Responsibility

Home Assistant remains responsible for:

- hardware and service integrations;
- dashboards;
- user controls;
- selected helper entities;
- selected snapshot timing;
- publishing integration data required by EnergyHub.

EnergyHub remains responsible for:

- persistent operational state;
- historical Daily Summary data;
- system health;
- Grid Confidence;
- future Battery Health;
- future Inverter Health;
- future Decision Engine logic;
- future explainable recommendations.

The architectural boundary is:

```text
Home Assistant
→ Integration and Presentation

EnergyHub
→ Intelligence and Persistent System State
```