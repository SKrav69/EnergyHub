# Home Assistant Configuration

> This document describes the Home Assistant configuration, objects, dashboards, and integration boundaries used by EnergyHub.

---

# Purpose

Home Assistant is the integration, presentation, and user-interaction platform for EnergyHub.

EnergyHub owns energy intelligence, persistent operational state, health evaluation, strategy decisions, inverter control, and historical EnergyHub data.

The architectural boundary is:

```text
Home Assistant
→ Integrations
→ Presentation
→ User Interaction
→ Household Automation
→ Notification Delivery

EnergyHub
→ Energy Intelligence
→ Historical Knowledge
→ Health Evaluation
→ Strategy Decisions
→ Inverter Control
→ Persistent Operational State
```

---

# Current Home Assistant Responsibilities

Home Assistant currently owns:

- hardware and service integrations;
- Solcast integration;
- dashboards;
- user-facing controls;
- helpers;
- timers;
- selected household automations;
- publishing selected Home Assistant data to EnergyHub;
- notification delivery;
- Home Assistant configuration storage.

EnergyHub currently owns:

- inverter telemetry processing;
- Grid Availability history;
- Grid Confidence;
- Daily Summary history;
- Battery Health;
- Telemetry Freshness;
- Inverter Health;
- System Health;
- Hybrid decisions;
- Panic decisions;
- inverter strategy execution;
- Operating Mode;
- Grid Import estimation;
- significant decision events.

---

# Current EnergyHub Helpers

Current EnergyHub-specific Home Assistant helpers include:

```text
input_boolean.energyhub_autopilot
input_number.energyhub_daily_solar_surplus_estimated
input_number.input_number_floor3_heat_pump_timer_hours
timer.floor_3_heat_pump_auto_off
```

---

# Autopilot Helper

Entity:

```text
input_boolean.energyhub_autopilot
```

Purpose:

Provides the user-facing control for automatic EnergyHub strategy execution.

The helper state is published to EnergyHub through retained MQTT.

EnergyHub publishes the resulting status as:

```text
sensor.energyhub_autopilot_status
```

Autopilot is separate from:

- Operating Mode;
- manual strategy requests.

Disabling Autopilot does not disable monitoring, telemetry, history, or health evaluation.

---

# Deferred Smart Load Helpers

The original EnergyHub 1.0 Away Mode helpers and automation were removed from the active 1.0 architecture.

Away / Smart Heating is deferred to EnergyHub 1.1 for redesign as part of a broader flexible-load architecture.

The ownership principle remains valid:

> EnergyHub should automatically stop a household load only when EnergyHub previously started it.

---

# Daily Solar Surplus Estimated Helper

Entity:

```text
input_number.energyhub_daily_solar_surplus_estimated
```

Purpose:

Stores the estimated daily solar energy that was probably not used.

Current formula:

```text
max(0, Solcast Forecast Today - Daily House Consumption)
```

Source entities:

```text
sensor.solcast_pv_forecast_forecast_today
sensor.powmr_10_2m_daily_house_consumption
```

The calculation intentionally uses Solcast forecast rather than inverter PV generation.

The PowMr inverter exposes PV1 telemetry only and does not provide reliable total PV1 + PV2 production.

The previous concept:

```text
Daily Energy Balance
```

was renamed to:

```text
Daily Solar Surplus Estimated
```

---

# Floor 3 Heat Pump Helpers

Auto-Off duration:

```text
input_number.input_number_floor3_heat_pump_timer_hours
```

Values:

```text
0 = Manual
1..9 = Auto-Off after N hours
```

Countdown timer:

```text
timer.floor_3_heat_pump_auto_off
```

Purpose:

Displays the remaining time until automatic switch-off.

---

# Current EnergyHub Automations

The authoritative current automation configuration is stored in:

```text
homeassistant/live/config/automations.yaml
```

Current EnergyHub integration responsibilities include:

- publishing Autopilot state;
- publishing Daily Summary and decision inputs;
- requesting Hybrid evaluation at 23:50;
- restoring Solar at 07:00 when Autopilot is enabled;
- restoring / requesting mode handling after restart;
- delivering EnergyHub notification events;
- selected household automations such as Floor 3 Heat Pump Auto-Off.

This document describes architecture and responsibilities.

It should not duplicate the complete automation YAML.

---

# Daily Summary and Hybrid Schedule

The final nightly sequence is:

```text
23:49
→ Home Assistant publishes fresh decision inputs

23:50
→ Home Assistant requests Hybrid evaluation

23:51
→ Daily Summary refreshes the final daily snapshot
```

This ordering ensures that the Hybrid Decision Engine evaluates current Home Assistant inputs before the final daily history snapshot is completed.

---

# Publish Daily Summary Inputs

Home Assistant publishes selected energy data to EnergyHub through retained MQTT messages.

Current Daily Summary inputs include:

```text
energyhub/input/ha/daily_house_consumption
energyhub/input/ha/solar_forecast_today
energyhub/input/ha/solar_forecast_tomorrow
energyhub/input/ha/daily_solar_surplus_estimated
```

EnergyHub subscribes to:

```text
energyhub/input/ha/#
```

Messages are retained.

This allows EnergyHub to receive the latest Home Assistant inputs after restart.

Architecture:

```text
Home Assistant Sensors
        ↓
Home Assistant Snapshot / Publication
        ↓
Retained MQTT Inputs
        ↓
EnergyHub
        ↓
DailySummaryService
```

---

# Daily Summary Integration

Home Assistant provides selected energy values that are not reliably available from the PowMr inverter.

EnergyHub then owns:

- the Daily Summary data model;
- persistent daily snapshots;
- historical Daily Summary state;
- EnergyHub Daily Summary MQTT sensors;
- the data interface used by dashboards;
- decision-service inputs.

Architecture:

```text
Home Assistant Sensors
        ↓
energyhub/input/ha/*
        ↓
DailySummaryService
        ↓
Persistent Daily History
        +
EnergyHub MQTT Sensors
        ↓
Home Assistant Dashboards
        +
Decision Services
```

---

# EnergyHub Daily Summary Entities

Current EnergyHub Daily Summary entities include:

```text
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_forecast
sensor.energyhub_daily_solar_surplus_estimated
sensor.energyhub_daily_grid_availability
sensor.energyhub_daily_summary_grid_import
```

Dashboards should prefer EnergyHub Daily Summary entities when displaying completed historical daily statistics.

Live current-day information may continue to use the appropriate source entities.

---

# Operating Mode Integration

Current EnergyHub Operating Mode entities:

```text
sensor.energyhub_operating_mode
sensor.energyhub_operating_mode_reason
sensor.energyhub_output_source_priority
sensor.energyhub_charger_source_priority
```

Current mode values include:

```text
solar
hybrid_charging
hybrid_grid_hold
panic
transitioning
transition_failed
unknown
```

Home Assistant displays Operating Mode and its reason.

EnergyHub owns:

- strategy execution;
- inverter command sequencing;
- verification;
- confirmed Operating Mode.

Home Assistant must not infer a confirmed Operating Mode solely from a button press or requested transition.

---

# Manual Panic Control

Current manual control:

```text
script.energyhub_start_panic
```

The Developer Dashboard exposes this script as a button for testing and manual activation.

Automatic Panic evaluation remains owned by EnergyHub.

Current diagnostic entities:

```text
sensor.energyhub_panic_decision
sensor.energyhub_panic_decision_reason
```

Manual requests still use the normal EnergyHub control architecture.

They do not bypass the Inverter Controller.

---

# Hybrid Integration

Home Assistant currently provides schedule and integration support for the Hybrid strategy.

EnergyHub owns:

- Hybrid decision logic;
- target calculation;
- Operating Mode transitions;
- inverter execution.

Current Hybrid phases:

```text
Hybrid Charging
        ↓
Hybrid Grid Hold
        ↓
Solar
```

Home Assistant should not duplicate Hybrid decision formulas.

The authoritative Hybrid decision architecture is documented in:

```text
DECISION_ENGINE.md
```

---

# Hybrid Decision Entities

EnergyHub publishes retained explainable Hybrid evaluation data.

Current entities include:

```text
sensor.energyhub_hybrid_decision
sensor.energyhub_hybrid_decision_reason
sensor.energyhub_hybrid_evaluated_soc
sensor.energyhub_hybrid_evaluated_consumption
sensor.energyhub_hybrid_battery_refill_required
sensor.energyhub_hybrid_total_energy_required
sensor.energyhub_hybrid_evaluated_forecast
```

These entities allow Home Assistant to show both the final decision and the exact values used during the most recent Hybrid evaluation.

Home Assistant displays these values but does not duplicate the Hybrid decision formula.

---

# Smart Heating / Away Integration

Away Mode is not part of the final EnergyHub 1.0 architecture.

The original implementation was deferred after design review showed that occupancy, comfort, solar surplus, cheap-tariff use, and battery reserve should be handled through a broader Smart Heating / flexible-load architecture.

This work is planned for EnergyHub 1.1.

---

# Floor 3 Heat Pump Auto-Off

The Floor 3 Auto-Off automation currently:

- starts the countdown timer;
- restarts the timer when duration changes;
- cancels the timer when the heat pump is switched off;
- switches the heat pump off when the timer finishes;
- resets the Auto-Off helper to 0.

This is a household automation and remains an appropriate Home Assistant responsibility.

---

# Grid Import Integration

The PowMr inverter does not expose a reliable accumulated Grid Import counter.

EnergyHub therefore estimates Grid Import while SUB-based strategies are active.

Current entities include:

```text
sensor.energyhub_grid_import_power_estimated
sensor.energyhub_daily_grid_import_estimated
sensor.energyhub_grid_import_yesterday_estimated
sensor.energyhub_daily_summary_grid_import
```

Daily Summary history uses the stable finalized entity shown above.

## Accounting Window

Accounting starts when EnergyHub enters a SUB-based strategy:

- Hybrid Charging;
- Hybrid Grid Hold;
- Panic.

Accounting stops after EnergyHub returns to Solar/SBU.

## Current Calculation

```text
Grid Import
=
House Energy Supplied During SUB
+
Positive Battery SOC Gain × Nominal Battery Capacity
```

Current nominal battery capacity:

```text
16 kWh
```

Battery contribution uses positive SOC gain relative to the start of the SUB interval.

Temporary SOC drops do not inflate the estimate.

EnergyHub persists current-day Grid Import state and publishes yesterday and Daily Summary values for Home Assistant history.

Current persistence schema:

```text
schema_version = 2
```

The schema migration discarded incompatible current-day values produced by the previous estimator.

Daily Grid Import Estimated remains:

- informational;
- useful for historical comparison;
- useful for dashboard analysis;
- not billing-grade.

---

# Notification Integration

EnergyHub owns significant automatic decision events.

Home Assistant owns notification delivery.

Current event topic:

```text
energyhub/event/notification
```

Architecture:

```text
EnergyHub Decision / Event
        ↓
MQTT Notification Event
        ↓
Home Assistant Automation
        ↓
Persistent Notification
        +
Mobile Notification
        +
Future Telegram Notification
```

This keeps decision context in EnergyHub while leaving delivery channels in Home Assistant.

Routine telemetry and expected no-action evaluations should normally remain in logs.

---

# Dashboard Architecture

Current EnergyHub dashboards separate operational state, decision intelligence, and historical energy results.

The current dashboard set is functional and forms the EnergyHub 1.0 reference UI. Further visual refinement may continue in later releases.

## EnergyHub Status

Purpose:

```text
What is happening now?
```

Current information includes:

- Autopilot;
- Operating Mode;
- Operating Mode reason;
- Output Source Priority;
- Charger Source Priority;
- Communication;
- Battery SOC;
- House Load;
- PV1 Power;
- Grid Voltage;
- Grid Import information;
- manual developer controls.

Operating Mode is displayed prominently with strategy-specific icons.

## EnergyHub Decision Logic

Purpose:

```text
Why did EnergyHub make this decision?
```

Current sections include:

### Grid Situation

- Grid Confidence;
- Grid Available — Last 24 Hours;
- Grid Available — Last 48 Hours.

### Night Tariff Decision

- final Hybrid decision;
- Battery SOC used;
- House Consumption used;
- Battery Energy to Full;
- Total Energy Required;
- Solar Forecast Tomorrow;
- Decision Reason.

### Panic Decision

- Solar Forecast Today;
- Previous Daily Consumption;
- Panic Decision;
- Panic Decision Reason.

The main decision lines are visually emphasized while detailed evaluation inputs remain available below them.

## Energy Balance Chart

The current 7-day chart displays:

- House Consumption;
- Solar Surplus Estimated;
- Grid Import;
- Grid Availability.

Live header values include:

- Consumption Today;
- Grid Import Today;
- Forecast Today;
- Forecast Tomorrow.

Daily Summary history uses `sensor.energyhub_daily_summary_grid_import`.

Further chart and dashboard refinement may continue during 1.1 without changing the 1.0 operating architecture.

---

# Dashboard Responsibilities

The main EnergyHub dashboard components have separate responsibilities.

## Energy Balance

```text
What happened over time?
```

Provides:

- historical House Consumption;
- historical Solar Surplus Estimated;
- historical Grid Import Estimated;
- historical Grid Availability;
- live Consumption Today;
- current solar forecasts.

## EnergyHub Status

```text
What is happening now?
```

Provides:

- current Operating Mode;
- current strategy reason;
- inverter settings;
- battery behavior;
- current power telemetry;
- Grid Import estimation;
- communication state;
- user controls.

## EnergyHub Intelligence

```text
What does EnergyHub know?
```

Provides:

- Grid Confidence;
- recent Grid Availability;
- previous-day energy facts;
- future solar forecasts.

---

# Home Assistant Repository Structure

Selected current Home Assistant configuration is versioned in Git.

```text
homeassistant/
└── live/
    ├── config/
    │   ├── automations.yaml
    │   ├── configuration.yaml
    │   ├── scenes.yaml
    │   └── scripts.yaml
    └── storage/
        ├── input_boolean
        ├── input_number
        ├── timer
        ├── lovelace.dashboard_powmr1
        ├── lovelace_dashboards
        └── lovelace_resources
```

`live/` contains selected configuration synchronized from the current Home Assistant installation.

The old manually maintained `homeassistant/legacy/` structure was removed from Git.

The complete Home Assistant `.storage` directory must never be committed.

---

# Synchronization from Home Assistant

Current tool:

```text
tools/dev/sync-from-ha.ps1
```

Workflow:

```text
Edit and Test in Home Assistant
        ↓
Run sync-from-ha.ps1
        ↓
Copy Selected Configuration
        ↓
homeassistant/live/
        ↓
Review Git Changes
        ↓
Commit
```

Only explicitly approved Home Assistant files should be synchronized.

The repository copy is a selected, reviewable representation of the real installation.

It is not a complete Home Assistant backup.


---

# Persistent USB Serial Access

EnergyHub must use the inverter FTDI adapter's persistent device identity:

```text
/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_<device-id>-if00-port0
```

Do not configure `/dev/ttyUSB0` or `/dev/ttyUSB1` because numerical assignment can change after a host restart or when another USB serial device is connected.

The EnergyHub app manifest enables:

```yaml
uart: true
udev: true
```

A Zigbee coordinator may remain connected through its own persistent `by-id` path. EnergyHub must always be configured with the FTDI path, not an Itead/Sonoff Zigbee path.

Installation and upgrade steps are documented in:

```text
docs/INSTALLATION.md
```

---

# EnergyHub Add-on Deployment

Current deployment tool:

```text
tools/dev/deploy-to-ha.ps1
```

Deployment uses:

```text
tools/dev/sync-to-ha.ps1
```

Workflow:

```text
Git Repository
        ↓
deploy-to-ha.ps1
        ↓
sync-to-ha.ps1
        ↓
Home Assistant Add-on Directory
        ↓
Manual Add-on Restart
        ↓
Inspect Logs
        ↓
Test
```

---

# Deployment and Synchronization Boundary

The two workflows have different purposes.

## EnergyHub Application Code

```text
Git
→ Home Assistant
```

## Selected Home Assistant Configuration

```text
Home Assistant
→ Git
```

Architecture:

```text
EnergyHub Code
        ↓
Deploy
        ↓
Home Assistant Add-on

Home Assistant Configuration
        ↓
Synchronize
        ↓
Git Repository
```

These workflows should remain separate and explicit.

---

# Configuration Authority

The authoritative current Home Assistant configuration is the real Home Assistant installation.

The Git repository stores selected synchronized configuration for:

- review;
- history;
- architectural understanding;
- recovery of important configuration.

Current synchronized files include:

```text
homeassistant/live/config/automations.yaml
homeassistant/live/config/configuration.yaml
homeassistant/live/config/scenes.yaml
homeassistant/live/config/scripts.yaml
homeassistant/live/storage/input_boolean
homeassistant/live/storage/input_number
homeassistant/live/storage/timer
homeassistant/live/storage/lovelace.dashboard_powmr1
homeassistant/live/storage/lovelace_dashboards
homeassistant/live/storage/lovelace_resources
```

---

# Configuration Rule

Home Assistant configuration stored in Git should remain:

- selected;
- understandable;
- reviewable;
- safe to commit;
- useful for EnergyHub development.

The goals are:

```text
Understand Changes
        ↓
Review Changes
        ↓
Preserve EnergyHub Integration
        ↓
Recover Important Configuration
        ↓
Maintain Architectural Documentation
```

The goal is not to turn the EnergyHub repository into a complete Home Assistant backup.