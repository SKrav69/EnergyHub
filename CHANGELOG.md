# Changelog

All notable EnergyHub changes are recorded here.

## [Unreleased]

No unreleased changes yet.

## [1.0.2] - 2026-08-01

First release-ready EnergyHub 1.0 build.

### Added

- Solar, Hybrid Charging, Hybrid Grid Hold, and Panic operating strategies.
- Explainable Hybrid and Panic decision services.
- Verified PowMr Menu 01 control with QPIRI read-back.
- ACK-confirmed and persisted Menu 16 control.
- Startup strategy reconstruction without unnecessary inverter writes.
- Communication, Battery, Telemetry Freshness, Inverter, and System Health monitoring.
- QPIWS warning and fault polling.
- Rolling Grid History, Grid Availability, and weighted Grid Confidence.
- Persistent Daily Summary and mode-aware Grid Import estimation.
- MQTT Discovery for EnergyHub and PowMr entities.
- Home Assistant Autopilot, schedules, manual Panic control, notifications, dashboards, and selected configuration synchronization.
- Executable release tests for decision boundaries, telemetry freshness, restart reconstruction, transition sequencing, and recovery behavior.
- Docker build test gate using `python3 -m unittest discover -s tests -v`.
- Installation, upgrade, app-store, release, project-state, roadmap, and Home Assistant integration documentation.

### Changed

- Pinned tested Python dependencies:
  - `paho-mqtt==1.6.1`;
  - `mppsolar==0.16.56`.
- Replaced weak public MQTT credential defaults with blank values that must be configured by the installer.
- Changed serial access from unstable `/dev/ttyUSB*` numbering to a configurable persistent `/dev/serial/by-id/...` path.
- Enabled app access to UART and udev device information.
- Made the startup banner use the Home Assistant build version instead of a hard-coded string.
- Removed the experimental Away Mode runtime from EnergyHub 1.0 and deferred the broader concept to Smart Thermal Energy.
- Removed obsolete MQTT Discovery/state for the raw inverter warning sensor.
- Standardized Daily Summary Grid Import naming as `sensor.energyhub_daily_summary_grid_import`.
- Clarified that Menu 16 is ACK-confirmed but cannot be independently read back on the current inverter.
- Clarified that Grid Import is informational and not billing-grade.

### Fixed

- App startup after USB device numbering changes.
- Serial permission/access behavior after Home Assistant restarts.
- Packaging path mismatch between `/publisher.py` and `/app/publisher.py`.
- Hard-coded `1.0.0` startup banner in later 1.0.x builds.
- False Telemetry Freshness warnings caused by unchanged but valid house-load telemetry.
- Startup ambiguity and unnecessary inverter writes during consistent Solar reconstruction.
- Partial Hybrid transition recovery back to Solar.
- Stale Daily Summary snapshot handling across date boundaries.
- Invalid raw inverter warning MQTT entity publication.

### Validation

- Rebuilt successfully on Home Assistant OS for `linux/arm64`.
- All 24 release tests passed during the Docker image build.
- Live telemetry and MQTT Discovery validated after rebuild.
- Full Home Assistant host restart validated with both the inverter FTDI adapter and a SONOFF Zigbee coordinator connected.
- Solar mode reconstructed from actual Menu 01 plus persisted Menu 16 without inverter writes.

### Known limitations

- `aarch64` only in 1.0.2.
- Current hardware support is PowMr 10.2M / PI30MAX.
- No PV2 or output-2 telemetry.
- Menu 16 cannot be read back.
- Grid Import is estimated and may be affected by simultaneous daytime PV.
- Strategy parameters are still code/configuration constants.
- The 07:00 return to Solar depends on Home Assistant scheduling.
- General telemetry quarantine, direct BMS integration, and bounded recovery services are future work.

## [0.1] - 2026-06

### Added

- Project philosophy, manifesto, vision, design principles, initial architecture, roadmap, backlog, and repository structure.
