# Changelog

## 2026-07-06

### Changed

- Updated Energy Statistics dashboard card.
- Separated historical Daily Summary values from live current-day values.
- Added live `Consumption Today` to the Energy Statistics header.
- Historical Daily House Consumption remains displayed in the 7-day chart as completed-day data.
- Redesigned EnergyHub dashboard monitoring into two separate responsibilities:
  - `EnergyHub Status` — current operational state and system health.
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

### Improved

- Clarified dashboard responsibilities between current operational monitoring and information used for future decision-making.
- Improved visibility of battery charging and discharging behavior.
- Improved Grid Confidence visibility and interpretation.
- Reduced duplicated information between EnergyHub dashboard cards.

### Findings

- Real-system testing showed that `CSO` is not suitable for planned continuous grid charging.
- During CSO testing, utility charging operated at night while PV generation was zero.
- When PV generation started, even at very low power, utility charging current dropped significantly.
- `SNU` was identified as the candidate charging-source mode for future Winter scheduled charging and Panic charging.
- SNU behavior with simultaneous PV and utility charging requires additional real-system validation.
- The PowMr firmware exposes three usable charging-source modes:
  - `OSO`
  - `CSO`
  - `SNU`
- `CUB` is not available on the current inverter firmware.
- An unexpected inverter restart identified the need to investigate available inverter warning and fault information.

### Architecture Decisions

- EnergyHub dashboards now follow two distinct concepts:

```text
EnergyHub Status
→ What is happening now?
→ Is the system healthy?

EnergyHub Intelligence
→ What does EnergyHub know?
→ What information is available for decisions?

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