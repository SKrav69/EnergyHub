# EnergyHub 1.0 — Autonomous Home

EnergyHub is a local-first Home Assistant add-on that turns a PowMr 10.2M inverter, a 16 kWh battery, solar forecasts, grid history, and Home Assistant inputs into an explainable household energy strategy.

The current codebase is a **1.0 release candidate in real-system test drive**. Feature development is complete. The functional High-priority audit and the selected Medium-priority corrections were completed and validated on the live installation in July 2026. Release closure still includes automated tests, dependency pinning, credential hardening, installation documentation, and final repository cleanup.

![How EnergyHub Autopilot works](docs/Images/Infographic%231_logic.png)

The detailed architecture is available in [System Architecture](docs/05-System-Architecture.md) and [Developer Architecture](docs/10-Developer-Architecture.md).

![EnergyHub technical architecture](docs/Images/Infographic%232_details.jpg)

## What EnergyHub does

EnergyHub:

- polls PowMr PI30MAX telemetry over local USB-RS232;
- publishes stable Home Assistant entities through MQTT Discovery;
- tracks grid availability over rolling 24-hour and 48-hour windows;
- derives a Grid Confidence state;
- evaluates a nightly Hybrid strategy from battery SOC, current consumption, and tomorrow's solar forecast;
- evaluates daytime Panic reserve protection from Grid Confidence, battery SOC, and the live solar forecast;
- executes verified inverter setting changes through one Inverter Controller;
- explains decisions and transition failures in Home Assistant;
- estimates Grid Import when the inverter is intentionally operating in SUB;
- stores restart-critical state atomically on local disk;
- reconstructs the operating strategy after an add-on restart;
- returns to Solar safely when Autopilot is disabled during an active automatic strategy.

## Operating strategies

| Strategy | Menu 01 | Menu 16 | Purpose |
|---|---:|---:|---|
| **Solar** | SBU | OSO | Default. Use solar and battery first. |
| **Hybrid Charging** | SUB | SNU | Charge from the cheap night tariff to 80% SOC. |
| **Hybrid Grid Hold** | SUB | OSO | After 80%, preserve the battery and keep the house on grid until 07:00. |
| **Panic** | SUB | SNU | Build daytime emergency reserve to 80% or 95%, depending on Grid Confidence. |

Menu 01 is written and independently read back through QPIRI. Menu 16 has no supported read-back command on this inverter; EnergyHub therefore stores the last **ACK-confirmed** value and never describes it as independently verified.

## Autopilot logic

### Solar

Solar is the default and recovery strategy:

```text
Menu 01 = SBU
Menu 16 = OSO
```

### Hybrid

At 23:50 Home Assistant requests a Hybrid evaluation. EnergyHub compares tomorrow's live Solcast forecast with:

```text
required energy
= today's house consumption
+ energy required to fill the 16 kWh battery from current SOC to 100%
```

If the forecast is insufficient, EnergyHub enters Hybrid Charging. At 80% SOC it enters Hybrid Grid Hold. Home Assistant requests Solar again at 07:00 when Autopilot is enabled.

### Panic

Between 12:00 and 23:50, EnergyHub reevaluates automatic Panic every 15 minutes while Solar is active.

- **Unstable grid:** if SOC is below 50% and today's forecast is below yesterday's consumption plus 20%, charge to 80%.
- **Risk or panic grid:** if SOC is below 80% and today's forecast is below yesterday's consumption plus 20%, charge to 95%.
- **Normal grid:** no automatic Panic.

The current implementation uses Grid Confidence, SOC, and forecast sufficiency. A separate live-PV threshold is not part of the current code and remains a policy-review item for a later test-drive release.

Manual Panic uses a 95% target and requires Autopilot to be enabled. When Autopilot is off, Home Assistant shows a clear notification instead of silently ignoring the request.

## Decision and execution boundary

```text
Home Assistant schedules and supplies inputs
                ↓ MQTT
Decision services select a requested strategy
                ↓
main.py queues and orchestrates the request
                ↓
InverterController writes and confirms settings
                ↓
MQTT state + notification event
                ↓
Home Assistant dashboards and notifications
```

Decision services do not write hardware. The Inverter Controller is the only owner of strategy transitions.

## Grid intelligence

EnergyHub stores grid up/down transitions for 48 hours and calculates:

- available hours in the last 24 and 48 hours;
- outage hours in the last 24 hours;
- availability percentage in the last 24 hours;
- weighted Grid Confidence from 24-hour and 48-hour availability.

| Weighted availability | Grid Confidence |
|---:|---|
| 90% or more | normal |
| 60–89.9% | unstable |
| 30–59.9% | risk |
| below 30% | panic |

## Grid Import accounting

The inverter does not expose a reliable billing-grade import counter. EnergyHub therefore estimates import during intentionally grid-prioritized SUB strategies:

```text
estimated import
= integrated house output power during SUB
+ positive battery SOC gain × 16 kWh
```

The live entities are:

- `sensor.energyhub_grid_import_power_estimated` — current grid-supplied house power estimate;
- `sensor.energyhub_daily_grid_import_estimated` — current-day accumulated estimate;
- `sensor.energyhub_grid_import_yesterday_estimated` — completed previous day;
- `sensor.energyhub_daily_summary_grid_import` — finalized Daily Summary value for charts.

The midnight hand-off is persistent and idempotent. A completed day is queued by Grid Import, reconciled into Daily Summary, and acknowledged only after reconciliation.

## Health and availability

EnergyHub separates two kinds of availability:

- `energyhub/status` — the EnergyHub process and diagnostic intelligence;
- `powmr/status` — valid raw inverter telemetry.

This allows communication, health, and decision entities to remain visible when the serial cable or inverter telemetry fails.

Current health services include:

- Communication Watchdog;
- Battery Health;
- Telemetry Freshness;
- Inverter Health from QPIWS;
- System Health aggregation.

Telemetry Freshness depends on the age of valid telemetry. An unchanged house load is retained as diagnostic information but no longer creates a false warning.

## Persistence and restart reconstruction

The following files are stored under the add-on `/data` directory:

| File | Purpose |
|---|---|
| `grid_history.json` | rolling grid transition history |
| `grid_import.json` | current-day import, previous day, SUB interval, pending finalizations |
| `daily_summary.json` | daily snapshots and finalized values |
| `inverter_controller_state.json` | last confirmed strategy, ACK-confirmed Menu 16, Panic target |
| `energy_hub_powmr_last.json` | latest valid raw telemetry snapshot |

Writes use temporary files, `fsync`, and atomic replacement. Incremental telemetry and Grid Import persistence are throttled to reduce SD-card writes; important transitions are persisted immediately.

At startup, EnergyHub combines:

- actual Menu 01 read from QPIRI;
- persisted ACK-confirmed Menu 16;
- persisted strategy context and Panic target.

If reconstruction is consistent, no inverter write occurs. If it is incomplete and Autopilot is enabled, EnergyHub queues one prioritized safe Solar recovery.

## Home Assistant integration

Home Assistant owns:

- the Autopilot helper;
- the 23:50 Hybrid and 07:00 Solar schedule;
- Solcast input publication;
- the atomic 23:51 Daily Summary snapshot;
- the manual Panic script;
- persistent notifications;
- the EnergyHub beacon;
- floor comfort controls and the third-floor auto-off timer;
- dashboards and charts.

EnergyHub owns:

- telemetry processing;
- grid history and Grid Confidence;
- health aggregation;
- Hybrid and Panic decisions;
- operating-strategy execution and verification;
- persistence and restart reconstruction;
- EnergyHub MQTT state.

See [Home Assistant Configuration](docs/12-HomeAssistant-Configuration.md).

## Dashboard

The current dashboard contains:

1. **Solar, Load & Battery — 24h**
2. **Energy Balance — 7 days**
3. **Inverter Load & Temperature — 24h**
4. **Modes & Controls**
5. **EnergyHub Status**
6. **EnergyHub Decision Logic**
7. **1st Floor**
8. **2nd Floor · Kids Room**
9. **3rd Floor**, including manual auto-off duration and remaining time

The planned Smart Thermal control is shown as a future 1.5 capability, not as a fake active switch.

## Development workflow

```text
Edit in Git
→ deploy/rebuild add-on
→ test on the real inverter
→ edit HA through the UI where appropriate
→ sync HA configuration back to Git
→ review in GitHub Desktop
→ commit one coherent change
```

Useful scripts:

```powershell
.\tools\dev\sync-to-ha.ps1
.\tools\dev\sync-from-ha.ps1
.\tools\dev\deploy-to-ha.ps1
```

The repository is the project source of truth. Home Assistant remains the runtime source of truth for the live installation.

## Project structure

```text
addon/
  app/
    adapters/      PowMr/mpp-solar boundary
    models/        normalized state objects
    mqtt/          Discovery, state and event publishing
    services/      decisions, health, history, control and persistence
    utils/         atomic JSON storage and logging
  config.yaml
  Dockerfile
  requirements.txt
  run.sh

homeassistant/
  live/config/     YAML automations, scripts and configuration
  live/storage/    selected versioned HA storage objects
  README.md

docs/
  product, architecture, decision, recovery and hardware documentation

tools/dev/
  deployment and synchronization scripts
```

## Current release blockers

Before presenting 1.0 as an external release rather than a personal release candidate:

- add executable automated tests for pure services and transition behavior;
- pin the tested Python dependency versions;
- remove weak default MQTT credentials from published defaults;
- finish installation and upgrade instructions;
- remove placeholder dashboard section titles;
- validate daytime SUB Grid Import behavior during real Panic operation;
- complete final repository and packaging checks.

## Roadmap

- **1.0 — Autonomous Home:** current release-candidate milestone.
- **1.1 — Test-drive and telemetry robustness:** real-world corrections, Grid Import refinement, general anomaly handling, flexible-load groundwork.
- **1.2 — Configurable EnergyHub:** strategy parameters and profiles.
- **1.3 — Recovery & Resilience:** bounded recovery for MQTT, network, serial, `mpp-solar`, and Home Assistant outages.
- **1.4 — Remote Access & Telegram:** secure remote Home Assistant access, status, alerts, and commands.
- **1.5 — Smart Thermal Energy:** use surplus solar or cheap-tariff electricity for heating and cooling, independent of occupancy.
- **2.x — Energy Optimization:** broader economic and multi-vendor optimization.
- **3.x — Full HEMS:** whole-home energy management.

See [Roadmap](docs/06-Roadmap.md) and [Backlog](docs/07-Backlog.md).

## Safety principles

- Manual control remains available.
- Autopilot is the master permission for automatic inverter strategy changes.
- EnergyHub does not automatically restart the inverter.
- Automatic recovery is bounded and observable.
- Menu 16 is described as ACK-confirmed, not read-back verified.
- Grid Import is informational and not billing-grade.
- Future flexible-load logic must stop only loads that EnergyHub started.

## Documentation index

- [Project](docs/01-Project.md)
- [System Architecture](docs/05-System-Architecture.md)
- [Roadmap](docs/06-Roadmap.md)
- [Backlog](docs/07-Backlog.md)
- [Decision Log](docs/09-Decision-Log.md)
- [Developer Architecture](docs/10-Developer-Architecture.md)
- [House Model](docs/11-House-Model.md)
- [Home Assistant Configuration](docs/12-HomeAssistant-Configuration.md)
- [Recovery Strategy](docs/13-Recovery-Strategy.md)
- [Decision Engine](docs/DECISION_ENGINE.md)
- [Current Project State](docs/PROJECT_STATE.md)
- [Project History](docs/PROJECT_HISTORY.md)
- [PowMr Verified Commands](docs/hardware/powmr-10-2m-verified-commands.md)
