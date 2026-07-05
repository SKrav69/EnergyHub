# Changelog

## 2026-07-05

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
```

- Updated the 23:50 Home Assistant snapshot automation for the new Solar Surplus terminology and calculation.
- Migrated the Energy Statistics dashboard from Home Assistant source/helper entities to EnergyHub-owned Daily Summary sensors.
- Changed Grid Confidence calculation to use rolling 48-hour grid availability percentages:
  - `90–100%` → `normal`
  - `60–90%` → `unstable`
  - `30–60%` → `risk`
  - `0–30%` → `panic`

### Improved

- Daily Summary snapshot processing is idempotent.
- Retained MQTT messages received after EnergyHub restart no longer cause unnecessary snapshot writes when values are unchanged.
- Separated operational Grid Confidence from historical Daily Grid Availability.
- Clarified ownership boundaries between Home Assistant, Daily Summary Engine and future Decision Engine.

### Architecture Decisions

- Home Assistant owns Daily Summary snapshot timing for now.
- EnergyHub owns the Daily Summary data model, persistence and published sensors.
- Daily Solar Surplus Estimated uses Solcast forecast rather than incomplete inverter PV telemetry.
- Daily Grid Import Estimated is deferred to a future controlled grid-charging model.
- Daily Grid Import Estimated will be informational only and must not be used as an authoritative Decision Engine input.
- Decision Engine will consume Daily Summary facts rather than create historical data.

### Validation

- Deployed and tested Daily Summary Engine on the real EnergyHub system.
- Verified retained MQTT input delivery.
- Verified Daily Summary persistence.
- Verified MQTT Discovery and all four new Home Assistant entities.
- Verified dashboard migration.
- Verified idempotent behavior after EnergyHub rebuild and restart.

---

## v0.1 Foundation

- Project philosophy
- Manifesto
- Vision
- Design philosophy
- Development principles
- System architecture
- Initial roadmap
- Initial backlog
- Repository structure