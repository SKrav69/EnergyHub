# Home Assistant Configuration

## Responsibility

Home Assistant owns the user-facing and household-automation layer. EnergyHub owns energy intelligence and inverter strategy execution.

## Repository layout

```text
homeassistant/
  README.md
  live/
    config/
      configuration.yaml
      automations.yaml
      scripts.yaml
      scenes.yaml
    storage/
      input_boolean
      input_number
      timer
      lovelace.dashboard_powmr1
      lovelace_dashboards
      lovelace_resources
```

Only selected `.storage` files are versioned. Do not commit the entity registry, recorder database, credentials, tokens, or unrelated runtime storage.

## Helpers

### Autopilot

```text
input_boolean.energyhub_autopilot
```

Master permission for automatic inverter strategy changes and manual Panic.

### Daily Solar Surplus snapshot

```text
input_number.energyhub_daily_solar_surplus_estimated
```

Stores the 23:50 estimate before daily source sensors reset.

### Third-floor auto-off duration

```text
input_number.input_number_floor3_heat_pump_timer_hours
```

Range: 0–9 hours. Zero means manual mode and cancels an active countdown without turning the plug off.

### Third-floor timer

```text
timer.floor_3_heat_pump_auto_off
```

## Scripts

### `script.energyhub_start_panic`

- requires Autopilot on;
- publishes `panic` to `energyhub/input/ha/inverter_mode`;
- otherwise creates a persistent notification explaining why Panic was not started.

## Automations

### EnergyHub Beacon

Visual household indicator:

- colour represents SOC range;
- breathing indicates grid outage;
- 100% brightness indicates intentional grid use/SUB;
- solid white indicates unavailable/stale telemetry.

### Daily Solar Surplus Estimated Snapshot

At 23:50:

```text
max(0, forecast today - daily house consumption)
```

is stored in the helper.

### Floor 3 Heat Pump Auto Off

- plug on or duration changed to non-zero → start/restart timer;
- duration changed to zero → cancel timer, leave plug unchanged;
- plug off → cancel timer and reset duration;
- timer finished → switch off plug and reset duration.

### Publish Daily Summary Inputs

At 23:49 and 23:51, the automation refreshes the retained individual inputs.

At 23:51, it additionally publishes one retained atomic JSON object to:

```text
energyhub/input/ha/daily_summary_snapshot
```

The JSON contains date, timestamp, consumption, forecasts, and estimated surplus.

### Publish Live Solcast Forecasts

On Solcast changes and HA startup, after a short delay, publishes:

```text
energyhub/input/ha/solar_forecast_today_live
energyhub/input/ha/solar_forecast_tomorrow_live
```

These update decision inputs without creating Daily Summary records.

### Publish Autopilot State

Publishes the retained helper state to:

```text
energyhub/input/ha/autopilot
```

### Hybrid Schedule

- 23:50 → publish `evaluate_hybrid`;
- 07:00 → publish `solar` only when Autopilot is on.

### Mode Notifications

Consumes `energyhub/event/notification` and creates persistent notifications for:

- Hybrid activation;
- Panic activation;
- Hybrid transition failure;
- Panic transition failure.

Activation messages occur only after EnergyHub reports transition success.

## MQTT contracts

### Inputs from HA

```text
energyhub/input/ha/...
```

### Notification events

```text
energyhub/event/notification
```

### EnergyHub state

Current state is published below `powmr/.../state` for historical compatibility.

### Availability

```text
energyhub/status
powmr/status
```

## Stable Grid Import entities

| Entity | Meaning |
|---|---|
| `sensor.energyhub_grid_import_power_estimated` | current estimated grid-supplied house power |
| `sensor.energyhub_daily_grid_import_estimated` | current-day accumulated estimated import |
| `sensor.energyhub_grid_import_yesterday_estimated` | previous completed day |
| `sensor.energyhub_daily_summary_grid_import` | finalized historical Daily Summary value |

The live current-day and finalized historical entities are intentionally separate.

## Dashboard structure

### Charts

#### Solar, Load & Battery — 24h

- rolling previous 24 hours;
- five-minute average PV and house load;
- five-minute last SOC;
- orange/blue/green visual language.

#### Energy Balance — 7 days

- House Consumption;
- Solar Surplus Estimated;
- Grid Import;
- header: Consumption Today, Solar Today, Solar Tomorrow.

#### Inverter Load & Temperature — 24h

- five-minute average inverter load and temperature;
- technical diagnostic chart.

### Modes & Controls

- current strategy and reason;
- Autopilot tile;
- Start Panic action;
- Smart Thermal planned 1.5 card.

No active Smart Thermal helper exists in 1.0.

### EnergyHub Status

- Menu priority explanation;
- communication;
- battery and generation;
- one conditional Grid Online/Grid Offline tile;
- Grid Import Now and Today.

Conditional cards display all branches in dashboard edit mode. Outside edit mode, only the matching online or offline tile is shown.

### Decision Logic

Summary:

- Grid Confidence;
- Current Mode;
- Night Plan.

Details:

- Grid Confidence and 24-hour availability;
- Hybrid inputs and reason;
- Panic status and reason.

### Floor cards

- 1st Floor: temperature, humidity, heat pump, power;
- 2nd Floor · Kids Room: temperature and humidity;
- 3rd Floor: temperature, humidity, heat pump, power, auto-off duration, remaining time.

## Visual language

- orange: solar;
- blue: consumption and humidity;
- green: battery, online, enabled, healthy;
- purple: grid import/technical load;
- red: emergency, failure, risk;
- orange thermometer and blue humidity across floor cards.

## Dashboard dependencies

The chart cards require the ApexCharts custom card resource currently registered in Home Assistant.

## Synchronization workflow

### Pull live HA changes to Git

```powershell
.\tools\dev\sync-from-ha.ps1
```

Review in GitHub Desktop before committing.

### Push repository configuration to HA

```powershell
.\tools\dev\sync-to-ha.ps1
```

Follow the script output and reload/restart the appropriate HA component.

### Add-on deployment

```powershell
.\tools\dev\deploy-to-ha.ps1
```

Then rebuild/restart the local add-on.

## Editing rules

- Prefer the HA UI for helpers and dashboard storage.
- Never overwrite a live `.storage` file while Home Assistant is running.
- YAML automations may be replaced as complete files, then reloaded through Developer Tools.
- After UI changes, synchronize back to Git.
- Do not commit temporary entity-registry exports.
