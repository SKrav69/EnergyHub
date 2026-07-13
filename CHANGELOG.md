# Changelog

## 2026-07-13

### Added

- Hybrid Decision Engine.
- New `HybridDecisionEngine`.
- Hybrid evaluation request path:
  - `energyhub/input/ha/inverter_mode`
  - payload `evaluate_hybrid`
- Hybrid decision inputs:
  - current Battery SOC;
  - current-day House Consumption;
  - next-day Solar Forecast;
  - nominal 16 kWh battery capacity.
- Hybrid required-energy calculation:

```text
Required Energy
=
Today's House Consumption
+
Energy required to refill the battery to 100%
```

- Automatic Hybrid decision at 23:50:
  - remain in Solar when tomorrow's forecast is sufficient;
  - enter Hybrid when tomorrow's forecast is insufficient.
- Hybrid Charging target of 80% SOC.
- Hybrid Grid Hold:
  - Setting 01 → SUB;
  - Setting 16 → OSO;
  - preserve battery until 07:00.
- Automatic Solar restoration at 07:00.
- Automatic Hybrid and Panic notification events over MQTT:
  - `energyhub/event/notification`
- Home Assistant automation for Hybrid and Panic notifications.
- Away Mode v1.
- Manual Away Mode helper:
  - `input_boolean.energyhub_away_mode`
- Away Mode smart-load ownership helper:
  - `input_boolean.energyhub_away_heat_pump_active`
- Away Mode first-floor heat-pump control.
- Grid Import Estimator.
- New `GridImportService`.
- Estimated Grid Import MQTT sensors:
  - `sensor.energyhub_grid_import_power_estimated`
  - `sensor.energyhub_daily_grid_import_estimated`
- Persistent Grid Import state in:
  - `/data/grid_import.json`
- Mode-aware Grid Import estimation.
- 50 W Solar-mode noise floor.
- Daily Grid Import accumulation and midnight reset.
- Grid Import integration into the 7-day Energy Balance chart.
- Grid Import values in the EnergyHub Status dashboard.
- EnergyHub Controls dashboard card.
- Human-readable inverter source-priority presentation.
- Expanded EnergyHub Intelligence decision-input card.
- Home Assistant reverse synchronization script:
  - `tools/dev/sync-from-ha.ps1`
- Home Assistant repository structure:
  - `homeassistant/live`
  - `homeassistant/legacy`
- Reviewed synchronization of:
  - `automations.yaml`
  - `scripts.yaml`
  - `scenes.yaml`
  - `configuration.yaml`
  - selected helper storage files;
  - selected Lovelace storage files.

### Changed

- Hybrid Schedule no longer forces Hybrid at 23:50.
- Hybrid Schedule now requests evaluation through EnergyHub.
- Daily Summary inputs are published before the 23:50 Hybrid decision.
- Added retained input:
  - `energyhub/input/ha/solar_forecast_tomorrow`
- Daily Summary input schedule now supports:
  - 23:49 decision inputs;
  - 23:50 Hybrid evaluation;
  - 23:51 final daily snapshot refresh.
- Hybrid no longer uses only the comparison:

```text
Forecast Tomorrow > Consumption Today
```

- Hybrid now also accounts for remaining battery energy.
- Panic notifications are generated only when an automatic Panic decision triggers.
- Hybrid notifications are generated only when an automatic Hybrid decision triggers.
- Away Mode OFF no longer blindly switches off the first-floor heat pump.
- EnergyHub now switches off that plug only when Away Mode previously started it.
- Away Mode start PV threshold was adjusted to 200 W for the current installation.
- Grid Import estimation changed from a universal power-balance formula to mode-aware logic.
- Solar-mode measurement noise below 50 W is treated as zero.
- Dashboard controls and status information were split for clarity.
- Legacy manually exported Home Assistant files were moved under:
  - `homeassistant/legacy`
- Current Home Assistant configuration is now stored under:
  - `homeassistant/live`
- Home Assistant configuration changes can now be copied back to Git without manual card-by-card export.

### Confirmed Operating Logic

#### Solar

```text
Setting 01 → SBU
Setting 16 → OSO
```

#### Hybrid Charging

```text
Setting 01 → SUB
Setting 16 → SNU
Target SOC → 80%
```

#### Hybrid Grid Hold

```text
Setting 01 → SUB
Setting 16 → OSO
Hold until 07:00
```

#### Panic

Automatic evaluation window:

```text
12:00–23:50
```

Common prerequisites:

```text
PV < 200 W
AND
Forecast Today < Previous Daily Consumption × 1.20
```

Unstable grid:

```text
SOC < 50%
→ charge to 80%
```

Risk / very poor grid:

```text
SOC < 80%
→ charge to 95%
```

#### Away Mode

Start heat pump:

```text
Away Mode ON
Temperature < 18°C
SOC > 95%
PV > 200 W
```

Stop heat pump:

```text
Temperature >= 23°C
OR
SOC <= 81%
```

Temporary PV fluctuations are ignored after the heat pump starts.

### Grid Import Estimation

Solar / SBU:

```text
Grid Import
=
House Load
+ Battery Charging Power
- Battery Discharging Power
- PV Power
```

Hybrid Charging / Panic:

```text
Grid Import
=
House Load
+
Battery Charging Power
```

Hybrid Grid Hold:

```text
Grid Import
=
House Load
```

### Tested

- Hybrid decision Solar branch.
- Hybrid decision Hybrid branch.
- Automatic transition:
  - Hybrid Charging → Hybrid Grid Hold.
- Automatic return:
  - Hybrid / Grid Hold → Solar.
- Notification event publishing.
- Home Assistant persistent notification handling.
- Away Mode start and stop behavior.
- Away Mode ownership behavior.
- Grid Import estimation in Solar.
- Grid Import estimation in Hybrid Grid Hold.
- Daily Grid Import accumulation.
- Home Assistant reverse synchronization.

### Known Issues / Deferred Polishing

- Startup Panic evaluation may log that operating mode is unknown before Solar restoration.
- Night restart recovery still needs strategy reconstruction from verified inverter settings.
- Duplicate Autopilot helpers remain:
  - `input_boolean.energyhub_autopilot`
  - `input_boolean.name_energyhub_autopilot`
- Hybrid Decision MQTT sensors are not yet published.
- Dashboard naming and visual style still require cleanup.
- Persistent inverter `eeprom_fault` remains under investigation.

### Future Direction

EnergyHub 1.x:

- autonomous and cost-effective home operation;
- battery management;
- grid reliability;
- solar forecast;
- smart loads;
- configurable operating parameters in v1.1.

EnergyHub 2.x:

- multiple inverter support;
- dynamic tariffs;
- import and export optimization;
- net billing;
- battery degradation model.

EnergyHub 3.x:

- full Home Energy Management System;
- EV charging;
- heat pumps;
- weather;
- dynamic markets;
- energy trading.

---

## 2026-07-09

### Added

- Battery Health Monitor v1.
- New `BatteryHealthMonitor`.
- Battery Health MQTT sensors:
  - `sensor.energyhub_battery_health`
  - `sensor.energyhub_battery_health_reason`
- Low battery detection.
- SOC jump detection.
- Telemetry Freshness Monitor v1.
- New `TelemetryFreshnessMonitor`.
- Telemetry Freshness MQTT sensors:
  - `sensor.energyhub_telemetry_freshness`
  - `sensor.energyhub_telemetry_freshness_reason`
  - `sensor.energyhub_house_load_unchanged`
- Detection of missing valid telemetry.
- Detection of unchanged House Load telemetry for 5 minutes.
- Inverter Health Monitor v1.
- New `InverterHealthMonitor`.
- Added `QPIWS` warning and fault polling every 60 seconds.
- Added PowMr adapter support for separate inverter warning reads.
- Inverter Health MQTT sensors:
  - `sensor.energyhub_inverter_health`
  - `sensor.energyhub_inverter_health_reason`
  - `sensor.energyhub_inverter_warning_raw`
- Automatic parsing of active `QPIWS` warning and fault flags.
- System Health aggregation v1.
- New `SystemHealthMonitor`.
- System Health MQTT sensors:
  - `sensor.energyhub_system_health`
  - `sensor.energyhub_system_health_reason`

### Changed

- Removed legacy SOC jump filtering from the MQTT publisher.
- Suspicious SOC values are no longer silently hidden from Home Assistant.
- SOC anomalies are now explicitly detected and reported by `BatteryHealthMonitor`.
- Battery Health Monitor v1 now uses simple generic rules:
  - SOC below 15% → warning;
  - SOC change of 2% or more between telemetry readings → warning;
  - SOC jump detection is active between 15% and 95%.
- Battery Health thresholds are treated as technical configuration values that may differ between battery systems.
- Battery parameters are intentionally excluded from frozen telemetry detection because battery SOC, voltage and current may legitimately remain unchanged for long periods.
- House Load is used as the initial telemetry movement indicator.
- Refactored `PowMrLocalAdapter` to support reusable inverter commands.
- Added separate `read_warnings()` path for `QPIWS`.
- Health monitoring architecture now separates:
  - communication failures;
  - battery anomalies;
  - stale or suspicious telemetry;
  - inverter-reported warnings and faults;
  - aggregated System Health.

### Findings

- `QPIWS` is supported by the PowMr 10.2M inverter and returns structured warning and fault information.
- Real-system testing detected a persistent:

```text
eeprom_fault = 1
```

- All other currently observed `QPIWS` warning and fault flags were zero.
- The meaning and operational significance of the persistent `eeprom_fault` requires additional investigation.
- Battery parameters are not reliable indicators of frozen telemetry because they may legitimately remain unchanged for hours.
- Grid voltage is not suitable as the primary telemetry movement indicator in the current installation because a voltage stabilizer keeps input voltage relatively stable.
- House Load was selected as the initial telemetry movement indicator because it normally changes during real house operation.
- Changing Setting 16 from OSO to SNU alone does not force immediate controlled grid charging.
- Controlled Hybrid and Panic charging requires investigation of Setting 01 control.
- Programmatic `SBU ↔ SUB` switching is the next critical inverter-control experiment.

### Recovery Strategy Decisions

- EnergyHub must never automatically restart the inverter.
- The inverter owns its internal protection and restart behavior.
- Battery Health anomalies are detection and warning events only.
- Inverter warnings and faults are detection and warning events only in Recovery v1.
- Detection and recovery remain separate responsibilities.
- Automatic EnergyHub recovery must be bounded.
- Infinite automatic restart loops are prohibited.
- Future EnergyHub recovery may:
  - attempt one automatic recovery;
  - verify the result;
  - wait approximately 30 minutes before a possible second recovery attempt;
  - stop automatic recovery after repeated failure.
- Home Assistant and EnergyHub cannot reliably report their own failure if the entire platform is frozen.
- External heartbeat/watchdog monitoring is required as a future reliability feature.

### Operating Strategy Decisions

- Operating modes are defined as:
  - Solar;
  - Hybrid;
  - Panic;
  - Away.
- Solar Mode expected configuration:

```text
Setting 01 → SBU
Setting 16 → OSO
```

- Hybrid charging expected configuration:

```text
Setting 01 → SUB
Setting 16 → SNU
Target SOC → 80%
Then restore SBU + OSO
```

- Panic charging expected configuration:

```text
Setting 01 → SUB
Setting 16 → SNU
Target SOC → 95%
Then restore SBU + OSO
```

- Panic charging may be activated during the day when Grid Confidence is poor and projected battery reserve is insufficient.
- Future Decision Engine logic should consider whether the house can safely operate until the next expected charging opportunity.
- Daily Grid Import must eventually include:
  - normal Solar Mode fallback import;
  - Hybrid charging import;
  - Panic charging import.

### Architecture Decisions

Health monitoring now follows:

```text
Communication Health
        +
Battery Health
        +
Telemetry Freshness
        +
Inverter Health
        ↓
System Health
```

- System Health provides one aggregated operational health state.
- Recovery actions must depend on the detected failure type.
- No universal automatic restart action is allowed.

---

## 2026-07-06

### Added

- Daily Summary Engine v1.
- New `DailySummaryService`.
- Persistent daily summary history in `/data/daily_summary.json`.
- Home Assistant → MQTT → EnergyHub Daily Summary input path.
- Retained MQTT inputs:
  - `energyhub/input/ha/daily_house_consumption`
  - `energyhub/input/ha/solar_forecast_today`
  - `energyhub/input/ha/daily_solar_surplus_estimated`
- MQTT Discovery for EnergyHub Daily Summary sensors:
  - `sensor.energyhub_daily_house_consumption`
  - `sensor.energyhub_daily_solar_forecast`
  - `sensor.energyhub_daily_solar_surplus_estimated`
  - `sensor.energyhub_daily_grid_availability`
- Home Assistant automation for publishing Daily Summary inputs at 23:51.

### Changed

- Renamed `Daily Energy Balance` to `Daily Solar Surplus Estimated`.
- Daily Solar Surplus Estimated is calculated as:

```text
max(0, Solcast Forecast Today - Daily House Consumption)
```

- Updated Energy Statistics dashboard card.
- Separated historical Daily Summary values from live current-day values.
- Added live `Consumption Today` to the Energy Statistics header.
- Historical Daily House Consumption remains displayed in the 7-day chart as completed-day data.
- Redesigned EnergyHub dashboard monitoring into two separate responsibilities:
  - `EnergyHub Status` — current operational state and system health;
  - `EnergyHub Intelligence` — information available for monitoring and future Decision Engine decisions.
- Updated EnergyHub Status card with:
  - Communication Status
  - Battery SOC
  - Battery Charging Current
  - Battery Discharge Current
  - House Load
  - PV1 Power
  - Grid Voltage
- Updated EnergyHub Intelligence card.
- Removed historical Solar Forecast Yesterday from EnergyHub Intelligence.
- Added rolling 24-hour and 48-hour Grid Availability information.
- Added prominent dynamic Grid Confidence visualization:
  - `normal` → 🟢 NORMAL
  - `unstable` → 🟡 UNSTABLE
  - `risk` → 🟠 RISK
  - `panic` → 🔴 PANIC

### Findings

- Real-system testing showed that `CSO` is not suitable for planned continuous grid charging.
- During CSO testing, utility charging operated at night while PV generation was zero.
- When PV generation started, even at very low power, utility charging current dropped significantly.
- `SNU` was identified as the candidate charging-source mode for future controlled charging.
- The PowMr firmware exposes three usable charging-source modes:
  - `OSO`
  - `CSO`
  - `SNU`
- `CUB` is not available on the current inverter firmware.
- An unexpected inverter restart identified the need to investigate available inverter warning and fault information.

### Architecture Decisions

EnergyHub dashboards follow two distinct concepts:

```text
EnergyHub Status
→ What is happening now?
→ Is the system healthy?

EnergyHub Intelligence
→ What does EnergyHub know?
→ What information is available for decisions?
```

- Home Assistant provides selected daily energy values that are not reliably available from the PowMr inverter.
- EnergyHub owns:
  - persistent Daily Summary history;
  - Daily Summary MQTT sensors;
  - historical data used by dashboards;
  - the future data interface for the Decision Engine.