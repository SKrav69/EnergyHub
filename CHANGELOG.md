# Changelog

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