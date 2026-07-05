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

The new name better reflects the actual meaning of the value.

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

# Energy Statistics Dashboard

The 7-day Energy Statistics chart uses:

```text
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_surplus_estimated
sensor.energyhub_daily_grid_availability
```

Current Solcast forecasts remain visible in the dashboard header:

```text
sensor.solcast_pv_forecast_forecast_today
sensor.solcast_pv_forecast_forecast_tomorrow
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