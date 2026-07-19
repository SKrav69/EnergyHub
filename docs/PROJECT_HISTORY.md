# EnergyHub Project History

## June 2026 — Foundation

EnergyHub began as a personal automation layer around a PowMr inverter and Home Assistant.

Initial work established:

- local PI30MAX telemetry;
- MQTT Discovery;
- normalized inverter state;
- communication watchdog;
- project documentation and Git workflow.

## Late June 2026 — Grid and health intelligence

Added:

- Grid History;
- rolling availability;
- Grid Confidence;
- Daily Summary;
- Battery Health;
- Telemetry Freshness;
- Inverter Health;
- System Health.

The project shifted from a telemetry bridge toward a stateful energy decision system.

## Early July 2026 — Architecture and real inverter control

Verified commands and mappings:

- QPIGS, QPIRI, QPIWS, QMOD;
- POP01/SUB and POP02/SBU;
- PCP01/SNU and PCP02/OSO.

Established the central boundary:

```text
Decision services decide
Inverter Controller executes and verifies
main.py orchestrates
Home Assistant owns UI and integration
```

## July 2026 — Autonomous strategies

Implemented:

- Solar;
- Hybrid Charging;
- Hybrid Grid Hold;
- Panic;
- Autopilot permission;
- manual Panic;
- explanations and notifications;
- target monitoring and exits.

## July 2026 — Energy accounting and HA project state

Added:

- estimated Grid Import;
- persistent daily state;
- Daily Summary chart entities;
- Home Assistant configuration synchronization;
- versioned dashboard and helper storage;
- beacon and floor controls.

## Away Mode experiment

An early automation used high SOC and solar conditions to run the first-floor heat pump while the house was unoccupied.

The implementation taught two useful lessons:

- surplus energy can be stored as comfort;
- automation must stop only loads it started.

The name and occupancy coupling were wrong for the general feature. The runtime automation, helpers, and dashboard control were removed from 1.0. The concept evolved into future Smart Thermal Energy.

## 2026-07-17 — Full project review

A repository-wide review identified functional, architecture, MQTT, entity, persistence, dashboard, recovery, and documentation findings.

High-priority functional findings included:

- stale decision forecasts;
- incorrect health aggregation;
- unsafe or incomplete transition recovery;
- restart reconstruction based on clock assumptions;
- queue race/priority;
- non-atomic Daily Summary;
- Away runtime still active;
- false freshness warnings;
- premature activation notifications;
- incomplete midnight Grid Import reconciliation.

## 2026-07-18 — High-priority corrections

Completed:

- separate availability topics;
- live Solcast synchronization;
- atomic Daily Summary;
- Grid Hold recovery;
- safe Solar queue priority;
- persisted restart reconstruction;
- midnight finalization hand-off;
- Away removal;
- stable entity naming and `_2` cleanup.

## 2026-07-18 to 2026-07-19 — Medium corrections

Completed:

- unchanged load no longer causes freshness warning;
- transition notifications wait for success;
- failed transitions create explicit failure events;
- blocked manual Panic is explained;
- persistence is atomic;
- routine disk writes are throttled;
- third-floor manual timer mode cancels countdown correctly.

## 2026-07-19 — Real validation

Validated:

- Autopilot retained state;
- fresh telemetry;
- clean persistence with no temporary files;
- one-minute telemetry snapshot cadence;
- Solar-mode Grid Import persistence stability;
- 23:50 Hybrid evaluation;
- midnight Grid Import and Daily Summary reconciliation.

## 2026-07-19 — Visual and documentation phase

Created:

- family Autopilot infographic;
- technical architecture infographic;
- consistent charts;
- Modes & Controls;
- redesigned Status and Decision Logic;
- floor comfort cards;
- full documentation audit.

## Current era

EnergyHub 1.0 is a release candidate for the personal installation. The next step is release engineering rather than new feature development.

## Future eras

- 1.1: test-drive and telemetry robustness;
- 1.2: configurable policy;
- 1.3: recovery and resilience;
- 1.4: remote access and Telegram;
- 1.5: Smart Thermal Energy;
- 2.x: broader optimization;
- 3.x: full HEMS.
