# Changelog

This changelog records material product and architecture changes. Git history remains the detailed implementation record.

## 2026-07-19 — 1.0 hardening, validation and dashboard redesign

### Validated

- Hybrid was evaluated automatically at 23:50 and selected Solar when forecast conditions were sufficient.
- Midnight Grid Import rollover completed successfully:
  - completed-day value created;
  - Daily Summary finalization queued;
  - existing identical value recognized idempotently;
  - finalization hand-off acknowledged.
- Telemetry remained fresh after the unchanged-load warning correction.
- Atomic persistence produced no residual temporary files.
- Raw telemetry persistence updated approximately once per minute rather than every poll.
- Grid Import persistence remained unchanged while Solar was active.

### Changed

- Removed the experimental Away Mode automation, helpers, and dashboard control from 1.0.
- Reframed the future feature as **Smart Thermal Energy**, independent of occupancy.
- Stabilized MQTT entity IDs with explicit `default_entity_id` values.
- Renamed the finalized daily chart entity to `sensor.energyhub_daily_summary_grid_import`.
- Removed the only unwanted `_2` EnergyHub entity from the Home Assistant registry by preserving its unique ID and renaming the entity ID.
- Separated telemetry freshness from unchanged house-load diagnostics.
- Automatic Hybrid and Panic activation notifications are now published only after a successful transition.
- Failed automatic transitions publish explicit failure notifications.
- Manual Panic now explains when it is blocked because Autopilot is disabled.
- Added shared atomic JSON persistence with durable replacement.
- Throttled raw telemetry and incremental Grid Import writes to reduce SD-card wear.
- Corrected third-floor heat-pump manual mode: duration `0 h` cancels an active countdown without switching the heat pump off.

### Dashboard

- Redesigned the 24-hour Solar, Load & Battery chart.
- Redesigned the 7-day Energy Balance chart.
- Redesigned the 24-hour Inverter Load & Temperature chart.
- Added a clear Modes & Controls section.
- Added family-readable EnergyHub Status and Decision Logic sections.
- Added consistent 1st, 2nd, and 3rd floor comfort cards.
- Added one conditional Grid Online/Grid Offline tile with real voltage.
- Added two project infographics:
  - simple Autopilot logic;
  - detailed technical architecture.

## 2026-07-18 — High-priority audit closure

### Fixed

- System Health now aggregates the actual Communication Health state.
- Raw inverter availability and EnergyHub diagnostic availability use separate topics.
- Solcast Today and Tomorrow forecasts are synchronized live for decisions.
- Daily Summary is created from one atomic JSON snapshot instead of sequential retained values.
- Failed Hybrid Grid Hold transitions make one bounded Solar recovery attempt.
- Safe Solar requests have priority over ordinary queued mode requests.
- Add-on restart reconstructs strategy from actual Menu 01, remembered ACK-confirmed Menu 16, and persisted context.
- Grid Import final values are reconciled into the previous day's Daily Summary after midnight.
- Obsolete Away Mode runtime implementation was removed.
- Grid Import MQTT naming and Home Assistant entity IDs were clarified.

### Accepted or deferred

- Menu 16 cannot be independently read back on the current inverter.
- General SOC/telemetry anomaly handling remains a later 1.x task.
- The 07:00 Solar request still depends on Home Assistant and belongs to 1.3 resilience work.
- Broad `main.py` refactoring remains deferred until executable tests exist.

## 2026-07-17 — Full project review

- Completed a repository-wide architecture, code, MQTT, entity, dashboard, documentation, startup, rollover, and recovery audit.
- Classified findings by severity and implemented all functional High-priority corrections.
- Selected and completed the Medium corrections that materially improved 1.0 without risky restructuring.

See [Project Review Resolution](docs/ProjectReview-17-07.md).

## 2026-07-13 to 2026-07-14 — EnergyHub 1.0 feature completion

- Implemented real inverter strategy control for Solar, Hybrid Charging, Hybrid Grid Hold, and Panic.
- Added Autopilot, manual Panic, strategy explanations, and notifications.
- Added Grid Import estimation and daily energy records.
- Added Home Assistant dashboards, beacon logic, and versioned configuration workflow.
- Declared feature development complete and moved into test drive and hardening.

## June to early July 2026 — Foundation

- Created the Home Assistant add-on and local PI30MAX adapter.
- Added MQTT Discovery and stable telemetry entities.
- Added Communication Watchdog, Grid History, Grid Confidence, Daily Summary, Battery Health, Telemetry Freshness, Inverter Health, and System Health.
- Established the responsibility boundary between Home Assistant, decision services, `main.py`, and Inverter Controller.
