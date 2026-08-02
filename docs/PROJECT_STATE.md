# EnergyHub Project State

Last updated: 2026-08-01.

## Current milestone

**EnergyHub 1.0 — Autonomous Home, release-ready as version 1.0.2.**

Feature development and the functional release audit are complete. Selected Medium-priority corrections, dependency pinning, credential hardening, packaging fixes, persistent serial access, executable build tests, Home Assistant rebuild validation, and full host-restart validation are complete.

The codebase is ready for the `v1.0.2` release tag.

## Current architecture

```text
PowMr inverter
  ↕ PI30MAX / persistent FTDI USB-RS232 path
EnergyHub app
  ↕ MQTT
Home Assistant
  ↕
Solar forecast, helpers, schedules, dashboards, notifications, smart plugs
```

Responsibilities:

- decision services decide;
- `InverterController` executes and verifies;
- `main.py` orchestrates;
- Home Assistant owns UI, schedules, integrations, and notification delivery.

## Release platform

- Home Assistant OS with Supervisor/Apps;
- `aarch64`, validated on Raspberry Pi 4;
- PowMr 10.2M / PI30MAX;
- FTDI USB-RS232 through `/dev/serial/by-id/...`;
- Mosquitto MQTT broker;
- Python 3.11 Alpine image;
- pinned `paho-mqtt==1.6.1` and `mppsolar==0.16.56`.

## Implemented operating strategies

| Strategy | State | Target/exit |
|---|---|---|
| Solar | SBU + OSO | default |
| Hybrid Charging | SUB + SNU | SOC 80% |
| Hybrid Grid Hold | SUB + OSO | 07:00 |
| Panic | SUB + SNU | SOC 80% or 95% |

Away Mode is not part of EnergyHub 1.0. Its energy-to-comfort concept is deferred to 1.5 Smart Thermal Energy.

## Confirmed inverter behavior

### Menu 01

- SUB → `POP01`;
- SBU → `POP02`;
- read back through QPIRI;
- independently verified before transition success.

### Menu 16

- SNU → `PCP01`;
- OSO → `PCP02`;
- ACK-confirmed and persisted;
- no supported read-back command exists on the current inverter.

## Current decision logic

### Hybrid

- Home Assistant publishes fresh decision inputs at 23:49;
- Home Assistant requests evaluation at 23:50;
- EnergyHub compares tomorrow's forecast with today's consumption plus battery refill to 100%;
- insufficient forecast selects Hybrid Charging;
- battery reaching 80% selects Hybrid Grid Hold;
- Home Assistant requests Solar at 07:00 when Autopilot is enabled.

### Panic

- evaluation window: 12:00–23:50;
- reevaluation every 15 minutes while Solar is active;
- normal grid → no action;
- unstable + SOC below 50% + insufficient forecast → target 80%;
- risk/panic + SOC below 80% + insufficient forecast → target 95%;
- forecast sufficiency uses previous completed daily consumption ×1.20;
- no live-PV threshold is used by the current implementation.

## Health and availability

Implemented:

- Communication Watchdog;
- Battery Health;
- Telemetry Freshness;
- Inverter Health;
- System Health aggregation;
- QPIWS polling every 60 seconds.

Availability topics remain separated:

- `energyhub/status` — EnergyHub process and diagnostic intelligence;
- `powmr/status` — valid inverter telemetry.

Diagnostics remain visible during serial or telemetry failure.

## Daily Summary

- retained inputs update current stored values;
- one atomic JSON snapshot at 23:51 creates or refreshes the completed record;
- duplicate snapshots are idempotent;
- midnight Grid Import finalization updates or confirms the completed day;
- stale retained snapshots from a previous date are ignored.

## Grid Import

- accounting is tied to confirmed SUB strategies;
- house output energy is integrated during the SUB interval;
- positive battery SOC gain is converted using nominal 16 kWh capacity;
- interval and daily state survive restarts;
- current-day, previous-day, and finalized Daily Summary values are separate;
- naming cleanup is complete;
- the result is informational and not billing-grade.

Known limitation: simultaneous daytime PV may affect estimated Grid Import accuracy.

## Restart reconstruction

Implemented and validated:

- load persisted controller state;
- read actual Menu 01;
- combine it with remembered Menu 16, confirmed-mode context, and Panic target;
- accept consistent Solar, Hybrid Grid Hold, Hybrid Charging, or Panic states without inverter writes;
- report an inconsistent state rather than guessing;
- queue one prioritized safe Solar recovery only when required and allowed.

## Persistent USB access

EnergyHub now uses a configurable FTDI `/dev/serial/by-id/...` path.

The app manifest enables:

```yaml
uart: true
udev: true
```

This avoids dependence on changing `/dev/ttyUSB0` and `/dev/ttyUSB1` assignments. Live validation passed with the inverter adapter and a SONOFF Zigbee coordinator connected through separate persistent device identities.

## Persistence

Current service state uses atomic JSON replacement.

- raw telemetry snapshots are throttled;
- Grid Import incremental saves are throttled;
- important transitions and day boundaries save immediately;
- controller state persists the confirmed mode, Menu 16 context, and Panic target.

## Home Assistant runtime

Current EnergyHub-specific integration includes:

- Autopilot helper publication;
- fresh solar forecast and daily input publication;
- 23:50 Hybrid schedule;
- 07:00 Solar restoration schedule;
- atomic Daily Summary snapshot;
- manual Panic script;
- EnergyHub notification delivery;
- EnergyHub beacon;
- selected household automation and dashboards.

Current helpers:

- `input_boolean.energyhub_autopilot`;
- `input_number.energyhub_daily_solar_surplus_estimated`;
- third-floor auto-off duration;
- third-floor timer.

Away Mode helpers and automation are removed.

## Release tests

The Docker build runs:

```text
python3 -m unittest discover -s tests -v
```

Current suite: 24 tests.

Covered areas:

- Hybrid branches and required-energy calculation;
- Panic thresholds, target selection, active-strategy guards, and window boundaries;
- Grid Confidence boundaries and 24/48-hour inputs;
- no-valid-telemetry and 60-second freshness behavior;
- unchanged-load diagnostic behavior;
- Solar, Grid Hold, and Panic restart reconstruction;
- ambiguous-state rejection;
- verified Hybrid transition;
- partial Hybrid failure recovery to Solar;
- invalid Panic target rejection.

## Release validation completed on 2026-08-01

- Home Assistant app image rebuilt successfully for `linux/arm64`;
- all 24 tests passed during the Docker build;
- version banner displayed `1.0.2` from `BUILD_VERSION`;
- persistent FTDI `by-id` path opened successfully;
- MQTT Discovery and retained inputs loaded successfully;
- valid inverter telemetry resumed;
- Solar was reconstructed without inverter writes;
- Communication health moved from starting to online;
- automatic Panic evaluation returned normal no-action;
- full Home Assistant host restart passed with the Zigbee coordinator connected.

## Known limitations and deferred work

- `aarch64` only;
- PowMr 10.2M / PI30MAX only;
- no PV2 telemetry;
- no output-2 telemetry;
- no direct reliable Grid Import counter;
- Menu 16 cannot be read back;
- strategy parameters remain hard-coded or Home Assistant-configured;
- the 07:00 Solar transition depends on Home Assistant;
- no general trusted/raw telemetry quarantine layer;
- no direct JK BMS integration;
- no general bounded recovery service yet;
- no external heartbeat capable of detecting a fully frozen platform.

## Next product milestones

- 1.1 — Test-drive and Telemetry Robustness;
- 1.2 — Configurable EnergyHub;
- 1.3 — Recovery & Resilience;
- 1.4 — Remote Access & Telegram;
- 1.5 — Smart Thermal Energy.
