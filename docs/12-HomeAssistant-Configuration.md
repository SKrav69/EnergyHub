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
input_boolean.energyhub_away_mode
input_boolean.energyhub_away_heat_pump_active
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
- Away Mode;
- manual strategy requests.

Disabling Autopilot does not disable monitoring, telemetry, history, or health evaluation.

---

# Away Mode Helpers

User control:

```text
input_boolean.energyhub_away_mode
```

Ownership helper:

```text
input_boolean.energyhub_away_heat_pump_active
```

The ownership helper records whether EnergyHub started the first-floor heat pump.

Rule:

> EnergyHub may automatically stop the heat pump only when EnergyHub previously started it.

This prevents EnergyHub from stopping a heat pump that the user started manually.

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

Current EnergyHub-related Home Assistant automations include:

```text
EnergyHub - Daily Energy Balance Snapshot
EnergyHub - Floor 3 Heat Pump Auto-Off
EnergyHub - Hybrid Schedule
EnergyHub - Mode Notifications
EnergyHub - Publish Autopilot State
EnergyHub - Publish Daily Summary Inputs
EnergyHub - Restore Mode After Restart
EnergyHub - Away Mode Heat Pump
```

Some automation names may retain older wording while the architecture evolves.

The authoritative current automation configuration is stored in:

```text
homeassistant/live/config/automations.yaml
```

This document describes architecture and responsibilities.

It should not duplicate the complete automation YAML.

---

# Daily Solar Surplus Snapshot

The daily snapshot runs before midnight.

Current snapshot time:

```text
23:50
```

Purpose:

Store Daily Solar Surplus Estimated before daily source sensors reset.

Architecture:

```text
Solcast Forecast Today
        +
Daily House Consumption
        ↓
Daily Solar Surplus Estimated
        ↓
Home Assistant Helper
```

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
sensor.energyhub_daily_grid_import_estimated
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
away
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

# Away Mode Integration

Away Mode v1 controls the first-floor heat pump.

Start conditions:

```text
Away Mode ON
Temperature < 18°C
SOC > 95%
PV > 200 W
```

Stop conditions:

```text
Temperature >= 23°C
OR
SOC <= 81%
```

After EnergyHub starts the heat pump, temporary PV fluctuations do not stop it.

Current ownership helper:

```text
input_boolean.energyhub_away_heat_pump_active
```

Current Away Mode v1 logic remains implemented through Home Assistant automation.

Future flexible-load decision logic may move into dedicated EnergyHub services when justified.

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

EnergyHub publishes estimated values:

```text
sensor.energyhub_grid_import_power_estimated
sensor.energyhub_daily_grid_import_estimated
```

The estimation is mode-aware.

## Solar

```text
Grid Import
=
House Load
+
Battery Charging Power
-
Battery Discharging Power
-
PV Power
```

Small Solar-mode estimates below the configured noise threshold are treated as zero.

Current threshold:

```text
50 W
```

## Hybrid Charging

```text
Grid Import
=
House Load
+
Battery Charging Power
```

## Hybrid Grid Hold

```text
Grid Import
=
House Load
```

## Panic

```text
Grid Import
=
House Load
+
Battery Charging Power
```

EnergyHub integrates estimated Grid Import power over time and persists the daily result.

Daily Grid Import Estimated is:

- informational;
- useful for historical comparison;
- useful for dashboard testing;
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

# Developer Dashboard Architecture

The Developer Dashboard separates current operational state from analytical information.

Architecture:

```text
EnergyHub Status
→ What is happening now?

EnergyHub Intelligence
→ What does EnergyHub know?
```

The current dashboard is intentionally optimized for development and testing.

Visual polishing is deferred until behavior is stable.

---

# EnergyHub Status Dashboard

Purpose:

```text
What is happening now?
```

Current controls and information include:

- EnergyHub Autopilot;
- Start Panic button;
- Away Mode control;
- Operating Mode visualization;
- Operating Mode reason;
- Output Source Priority;
- Charger Source Priority;
- Communication;
- Battery SOC;
- Battery Charging Current;
- Battery Discharge Current;
- House Load;
- PV1 Power;
- Grid Voltage;
- Grid Import Power Estimated;
- Daily Grid Import Estimated.

Operating Mode is displayed prominently.

Current visualization includes:

```text
☀️ SOLAR
🌙 HYBRID CHARGING
🌙 HYBRID GRID HOLD
🔴 PANIC
🏠 AWAY
🔄 TRANSITIONING
❌ TRANSITION FAILED
⚪ UNKNOWN
```

---

# EnergyHub Intelligence Dashboard

Purpose:

```text
What does EnergyHub know?
```

Current information includes:

- Grid Confidence;
- Grid Available last 24h;
- Grid Available last 48h;
- Consumption Yesterday;
- Solar Surplus Yesterday;
- Forecast Today;
- Forecast Tomorrow.

Grid Confidence is displayed prominently:

```text
🟢 NORMAL
🟡 UNSTABLE
🟠 RISK
🔴 PANIC
⚪ UNKNOWN
```

Current Grid Confidence thresholds:

```text
90–100% → normal
60–90%  → unstable
30–60%  → risk
0–30%    → panic
```

Decision explanations may be added or reorganized during later dashboard polishing.

---

# Energy Balance Chart

The 7-day Energy Balance chart displays completed historical values.

Historical series:

```text
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_surplus_estimated
sensor.energyhub_daily_grid_import_estimated
sensor.energyhub_daily_grid_availability
```

Live header values:

```text
sensor.powmr_10_2m_daily_house_consumption
sensor.solcast_pv_forecast_forecast_today
sensor.solcast_pv_forecast_forecast_tomorrow
```

The distinction is intentional:

```text
Chart
→ completed historical values

Header
→ live current-day values
```

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
├── live/
│   ├── config/
│   │   ├── automations.yaml
│   │   ├── configuration.yaml
│   │   ├── scenes.yaml
│   │   └── scripts.yaml
│   └── storage/
│       ├── input_boolean
│       ├── input_number
│       ├── timer
│       ├── lovelace.dashboard_powmr1
│       ├── lovelace_dashboards
│       └── lovelace_resources
└── legacy/
```

`live/` contains selected configuration synchronized from the current Home Assistant installation.

`legacy/` contains older manually maintained files retained for reference.

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