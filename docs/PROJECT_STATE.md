# EnergyHub Project State

Last updated: 2026-07-19.

## Current milestone

**EnergyHub 1.0 — Autonomous Home, release candidate/test drive.**

Feature development is complete. Functional High-priority audit findings and selected Medium findings are implemented. Real 23:50 and midnight behavior has been validated. Charts, dashboards, and documentation have been redesigned. Release engineering remains open.

## Current architecture

```text
PowMr inverter
  ↕ PI30MAX / USB-RS232
EnergyHub add-on
  ↕ MQTT
Home Assistant
  ↕
Solcast, helpers, schedules, dashboards, notifications, smart plugs
```

Responsibilities:

- decisions decide;
- Inverter Controller executes and verifies;
- `main.py` orchestrates;
- Home Assistant owns UI and household integrations.

## Implemented operating strategies

| Strategy | State | Target/exit |
|---|---|---|
| Solar | SBU + OSO | default |
| Hybrid Charging | SUB + SNU | SOC 80% |
| Hybrid Grid Hold | SUB + OSO | 07:00 |
| Panic | SUB + SNU | SOC 80% or 95% |

## Confirmed inverter behavior

### Menu 01

- SUB → POP01;
- SBU → POP02;
- read back through QPIRI;
- verified before transition success.

### Menu 16

- SNU → PCP01;
- OSO → PCP02;
- ACK-confirmed;
- persisted because no read-back command is available.

## Current decision logic

### Hybrid

- HA publishes daily inputs at 23:49;
- HA requests evaluation at 23:50;
- EnergyHub uses live tomorrow forecast;
- compares forecast with current consumption plus battery refill to 100%;
- charges to 80% if Hybrid is selected;
- enters Grid Hold after target;
- HA requests Solar at 07:00.

The 2026-07-18 evaluation completed successfully and selected Solar because forecast was sufficient.

### Panic

- window 12:00–23:50;
- reevaluation every 15 minutes;
- normal grid → no action;
- unstable + SOC <50% + insufficient forecast → target 80%;
- risk/panic + SOC <80% + insufficient forecast → target 95%;
- forecast sufficiency uses previous daily consumption ×1.20;
- current code has no live-PV threshold.

## Health

Implemented:

- Communication Watchdog;
- Battery Health;
- Telemetry Freshness;
- Inverter Health;
- System Health.

Telemetry Freshness now remains fresh while valid telemetry arrives, even when house load is unchanged.

## Availability

- `energyhub/status`: process/intelligence;
- `powmr/status`: raw inverter telemetry.

Diagnostics remain visible during serial failure.

## Daily Summary

- retained individual inputs update stored values only;
- one atomic JSON snapshot at 23:51 creates the record;
- duplicate snapshots are idempotent;
- midnight Grid Import finalization updates or confirms the completed day.

Validated at 2026-07-19 00:00 with a completed value of 0.000 kWh.

## Grid Import

- active during confirmed SUB strategies;
- integrates house output power;
- adds positive SOC gain ×16 kWh;
- persists interval state;
- current-day value and finalized Daily Summary value are separate entities;
- entity naming cleanup complete;
- no unwanted `_2` EnergyHub entities remain.

Limit: daytime simultaneous PV may affect accuracy. Validation remains 1.1 work.

## Restart reconstruction

Implemented and validated:

- load controller state;
- read actual Menu 01;
- combine with remembered Menu 16 and mode context;
- accept consistent Solar without inverter writes;
- queue one safe Solar recovery only when needed and allowed.

## Persistence

All current service state uses atomic JSON replacement.

- raw telemetry snapshot throttled to ~60 seconds;
- Grid Import incremental save throttled to ~60 seconds;
- important transitions and day boundaries save immediately;
- no residual `.tmp` files observed in validation.

## Notifications

- automatic activation events are published only after transition success;
- transition failure events include error and current mode;
- manual Panic blocked by Autopilot off produces a clear notification.

## Home Assistant runtime

Current automations:

- beacon;
- daily surplus snapshot;
- third-floor heat-pump auto-off;
- scheduled Daily Summary inputs/snapshot;
- live Solcast publication;
- Autopilot publication;
- Hybrid schedule;
- mode notifications.

Current script:

- Start Panic.

Current helpers:

- Autopilot;
- Daily Solar Surplus Estimated;
- third-floor auto-off duration;
- third-floor timer.

Away Mode helpers and automation are removed.

## Dashboard state

Implemented:

- three consistent charts;
- Modes & Controls;
- EnergyHub Status;
- Decision Logic;
- 1st, 2nd, and 3rd floor cards;
- conditional green/red Grid tile;
- future Smart Thermal card.

Remaining visual cleanup:

- replace placeholder `New section` titles;
- final mobile and dark-theme review.

## Infographics

- `docs/Images/Infographic#1_logic.png` — family Autopilot logic;
- `docs/Images/Infographic#2_details.png` — technical architecture.

## Removed from 1.0

The experimental Away Mode runtime implementation was removed completely. The underlying energy-to-comfort idea is planned for 1.5 as Smart Thermal Energy.

## Known limitations

- no PV2 telemetry;
- no output 2 telemetry;
- no reliable direct import counter;
- Menu 16 cannot be read back;
- battery capacity and policy thresholds are hard-coded;
- 07:00 restoration depends on Home Assistant;
- no executable automated tests;
- dependencies unpinned;
- weak example/default MQTT credentials remain in add-on config;
- no general telemetry quarantine layer;
- no graceful shutdown handler.

## Immediate next work

1. Automated tests.
2. Release security and dependency pinning.
3. Installation/upgrade documentation.
4. Final UI/repository cleanup.
5. Release package/tag.

## Next product milestones

- 1.1 test-drive and telemetry robustness;
- 1.2 configurable strategies;
- 1.3 recovery and resilience;
- 1.4 remote access and Telegram;
- 1.5 Smart Thermal Energy.
