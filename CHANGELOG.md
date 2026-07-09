# Changelog

## 2026-07-09

### Added

- Battery Health Monitor v1.
- New `BatteryHealthMonitor`.
- Battery Health MQTT sensors:
  - `sensor.energyhub_battery_health`
  - `sensor.energyhub_battery_health_reason`
- Low battery detection:
  - SOC below 15% → `warning`
- SOC jump detection:
  - active between 15% and 95% SOC;
  - SOC change of 2% or more between telemetry readings → `warning`;
  - SOC above 95% is excluded from SOC jump detection because BMS behavior near full charge may be non-linear.

- Telemetry Freshness Monitor v1.
- New `TelemetryFreshnessMonitor`.
- Telemetry Freshness MQTT sensors:
  - `sensor.energyhub_telemetry_freshness`
  - `sensor.energyhub_telemetry_freshness_reason`
  - `sensor.energyhub_house_load_unchanged`
- Detection of missing valid telemetry.
- Detection of unchanged House Load telemetry for 5 minutes.
- Battery parameters are intentionally excluded from frozen telemetry detection because battery SOC, voltage and current may legitimately remain unchanged for long periods.

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
- System Health combines:
  - Communication Health;
  - Battery Health;
  - Telemetry Freshness;
  - Inverter Health.

### Changed

- Removed legacy SOC jump filtering from the MQTT publisher.
- Suspicious SOC values are no longer silently hidden from Home Assistant.
- SOC anomalies are now explicitly detected and reported by `BatteryHealthMonitor`.
- Refactored `PowMrLocalAdapter` to support reusable inverter commands.
- Added separate `read_warnings()` path for `QPIWS`.
- Health monitoring architecture now separates:
  - communication failures;
  - battery anomalies;
  - stale or suspicious telemetry;
  - inverter-reported warnings and faults;
  - aggregated system health.

### Findings

- `QPIWS` is supported by the PowMr 10.2M inverter and returns structured warning and fault information.
- Real-system testing detected a persistent:

```text
eeprom_fault = 1

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
- Daily Solar Surplus Estimated is now calculated as:

```text
max(0, Solcast Forecast Today - Daily House Consumption)