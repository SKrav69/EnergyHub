# EnergyHub Project State

Last Updated: 2026-07-14

---

# Current Milestone

EnergyHub 1.0 feature development is complete.

The project has reached the point where the house can make and execute its own energy decisions using:

- current battery SOC;
- house consumption;
- solar forecast;
- grid reliability;
- operating time windows;
- verified inverter control.

EnergyHub 1.0 now enters a test-drive and cleanup phase.

The immediate goal is no longer to add major features. The goal is to:

- run EnergyHub in Autopilot;
- catch bugs;
- verify real overnight and daytime decisions;
- review code quality;
- clean entity naming;
- improve charts and dashboards;
- confirm daily Grid Import rollover;
- polish documentation and infographics.

---

# Project Vision

EnergyHub is a local-first home energy management system built on top of Home Assistant.

Its purpose is not only to monitor energy, but to make explainable decisions about:

- solar use;
- battery reserve;
- grid reliability;
- cheap-tariff charging;
- emergency charging;
- flexible loads;
- future heating control;
- future EV charging;
- future import and export optimization.

EnergyHub should remain:

- local first;
- explainable;
- calm;
- modular;
- resilient;
- suitable for daily family use;
- progressively automated.

---

# Current Architecture

```text
Homeowner
   ↓
Home Assistant Dashboards
   ↓
Home Assistant Automations / Helpers
   ↓
MQTT
   ↓
EnergyHub Core
   ↓
Decision and Control Services
   ↓
PowMr Inverter / Battery / Future Smart Loads
```

Current EnergyHub Core services:

- Telemetry Service
- Event Bus
- Grid Monitor
- Grid History Service
- Grid Stability Engine
- Communication Watchdog
- Health Monitor
- Battery Health Monitor
- Telemetry Freshness Monitor
- Inverter Health Monitor
- System Health Monitor
- Daily Summary Service
- Hybrid Decision Engine
- Panic Decision Engine
- Inverter Controller
- Grid Import Service
- Autopilot State

Future services:

- Configurable Parameter Service
- Recovery Service
- Smart Load Engine
- EV Charging Engine
- Notification Policy Engine
- Multi-Inverter Device Manager
- Direct BMS Adapter
- Tariff and Export Optimization Services

---

# EnergyHub 1.0 — Implemented Features

## Inverter Integration

- PowMr 10.2M communication through PI30MAX
- MQTT communication
- MQTT Discovery
- real-time inverter telemetry
- QPIGS support
- QPIRI support
- QPIWS support
- QMOD support
- programmatic Setting 01 control
- programmatic Setting 16 control
- ACK handling
- bounded verification retries
- real-inverter validation

## Operating Strategies

- Solar
- Hybrid Charging
- Hybrid Grid Hold
- Panic
- Manual Panic
- automatic return to Solar
- safe Solar recovery when Autopilot is disabled

## Decision Engines

- Hybrid Decision Engine
- Panic Decision Engine
- Hybrid evaluation at 23:50
- Panic evaluation every 15 minutes in the configured window
- explainable decision reasons
- retained Hybrid evaluation data
- automatic notification events

## Grid Intelligence

- Grid event history
- Grid Availability 24h
- Grid Availability 48h
- Grid Confidence
- Grid Confidence states:
  - Normal
  - Unstable
  - Risk
  - Panic

## Health Monitoring

- Communication Watchdog
- Communication Health
- Battery Health Monitor
- Telemetry Freshness Monitor
- Inverter Health Monitor
- System Health aggregation
- QPIWS warning and fault polling
- SOC jump detection
- low SOC warning
- stale telemetry detection

## Home Assistant Integration

- Autopilot helper
- manual mode scripts
- Hybrid schedule automation
- restore-after-restart automation
- notification automation
- Decision Logic dashboard
- EnergyHub Status dashboard
- Energy Balance chart
- human-readable inverter priority display
- Home Assistant → Git synchronization workflow
- Git → Home Assistant deployment workflow

---

# Inverter Control Knowledge

## Setting 01 — Output Source Priority

Verified commands:

```text
POP01 → SUB
POP02 → SBU
```

## Setting 16 — Charger Source Priority

Verified commands:

```text
PCP01 → SNU
PCP02 → OSO
PCP03 → CSO
```

## Current Strategy Mapping

```text
Solar
Setting 01 → SBU
Setting 16 → OSO

Hybrid Charging
Setting 01 → SUB
Setting 16 → SNU

Hybrid Grid Hold
Setting 01 → SUB
Setting 16 → OSO

Panic
Setting 01 → SUB
Setting 16 → SNU
```

QPIRI verification may occasionally return no result on the first attempt.

EnergyHub handles this with bounded retries.

---

# Operating Logic

## Solar

Solar is the default strategy.

```text
Setting 01 → SBU
Setting 16 → OSO
```

Behavior:

- solar powers the house first;
- battery supports the house when needed;
- grid remains the final fallback;
- battery charging is solar-only.

At 07:00, EnergyHub restores Solar after the night strategy.

---

## Hybrid Decision

Hybrid is evaluated at 23:50.

Inputs:

- current Battery SOC;
- current-day house consumption;
- next-day solar forecast;
- nominal battery capacity of 16 kWh.

Battery refill energy:

```text
Battery Refill Required
=
16 kWh × Missing SOC Percentage
```

Required energy:

```text
Required Energy
=
Current-Day House Consumption
+
Battery Refill Required
```

Decision:

```text
Forecast Tomorrow >= Required Energy
→ remain in Solar

Forecast Tomorrow < Required Energy
→ activate Hybrid
```

No additional loss factor is used.

The battery itself provides the practical buffer against imperfect forecasts and changing consumption.

Hybrid evaluation data is retained in MQTT and shown in the Decision Logic dashboard:

- final decision;
- decision reason;
- SOC used;
- house consumption used;
- battery energy to full;
- total energy required;
- forecast tomorrow.

---

## Hybrid Charging

```text
Setting 01 → SUB
Setting 16 → SNU
Target SOC → 80%
```

When the battery reaches the target:

```text
Hybrid Charging
→ Hybrid Grid Hold
```

---

## Hybrid Grid Hold

```text
Setting 01 → SUB
Setting 16 → OSO
```

Behavior:

- house remains on the cheap night grid;
- battery is preserved;
- no correction is required if SOC stabilizes around 79–80%;
- at 07:00 EnergyHub restores Solar.

---

## Panic Decision

Automatic Panic is evaluated every 15 minutes between 12:00 and 23:50.

Decision order:

```text
1. Autopilot enabled
2. Inside Panic evaluation window
3. EnergyHub operating in Solar
4. Grid Confidence
5. Battery SOC threshold
6. Solar forecast versus previous daily consumption × 1.20
```

Current logic no longer uses current PV power.

### Normal Grid

```text
Grid Confidence = normal
→ no automatic Panic
```

### Unstable Grid

```text
Grid Confidence = unstable
AND
SOC < 50%
AND
Forecast Today < Previous Daily Consumption × 1.20
→ Panic target 80%
```

### Risk or Panic Grid State

```text
Grid Confidence = risk or panic
AND
SOC < 80%
AND
Forecast Today < Previous Daily Consumption × 1.20
→ Panic target 95%
```

Panic configuration:

```text
Setting 01 → SUB
Setting 16 → SNU
```

When target SOC is reached:

```text
Panic
→ restore Solar
→ reevaluate Panic after Solar confirmation
```

Manual Panic uses a 95% target.

---

# Autopilot

Autopilot controls whether EnergyHub may execute automatic operating strategies.

When enabled, EnergyHub may:

- evaluate Hybrid;
- activate Hybrid;
- enter Hybrid Grid Hold;
- restore Solar at 07:00;
- evaluate Panic;
- activate Panic;
- return to Solar.

When disabled during an active or unknown strategy, EnergyHub performs a final safe Solar recovery.

Current helper:

```text
input_boolean.energyhub_autopilot
```

The duplicate Autopilot helper was removed.

---

# Notifications

EnergyHub publishes non-retained notification events to:

```text
energyhub/event/notification
```

Current automatic notifications:

- Hybrid activated
- Panic activated

Notifications are published only after the relevant automatic decision is made.

The event payload can be reused by:

- Home Assistant persistent notifications;
- mobile notifications;
- future Telegram integration.

---

# Grid Import Accounting

The PowMr inverter does not provide a reliable accumulated Grid Import counter.

EnergyHub therefore calculates Grid Import while SUB-based strategies are active.

## Accounting Start

Accounting starts when EnergyHub enters:

- Hybrid Charging;
- Hybrid Grid Hold;
- Panic.

These strategies use:

```text
Setting 01 = SUB
```

## Accounting Stop

Accounting stops when EnergyHub returns to:

```text
Setting 01 = SBU
```

## Calculation Model

```text
Grid Import
=
House Energy Supplied During SUB
+
Positive Battery SOC Gain × 16 kWh
```

Battery contribution uses the highest SOC reached relative to the SOC at the start of the SUB interval.

Temporary SOC drops do not inflate the estimate.

Example:

```text
SUB starts at 66%
SUB ends at 80%

Battery gain:
14% × 16 kWh = 2.24 kWh

House energy during SUB:
0.85 kWh

Grid Import:
2.24 + 0.85 = 3.09 kWh
```

Current MQTT entities:

```text
sensor.energyhub_grid_import_power_estimated
sensor.energyhub_daily_grid_import_estimated
sensor.energyhub_grid_import_yesterday_estimated
sensor.energyhub_daily_grid_import_estimated_2
```

Current naming conflict:

```text
sensor.energyhub_daily_grid_import_estimated_2
```

This is a known cleanup item for the next session.

Persistence:

```text
/data/grid_import.json
```

Current schema:

```text
schema_version = 2
```

The schema v2 migration discarded incompatible current-day totals from the previous estimator.

Grid Import values are informational and not billing-grade.

---

# Daily Summary

Current Home Assistant inputs:

```text
energyhub/input/ha/daily_house_consumption
energyhub/input/ha/solar_forecast_today
energyhub/input/ha/solar_forecast_tomorrow
energyhub/input/ha/daily_solar_surplus_estimated
```

Current EnergyHub daily values:

```text
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_forecast
sensor.energyhub_daily_solar_surplus_estimated
sensor.energyhub_daily_grid_availability
sensor.energyhub_daily_grid_import_estimated_2
```

Schedule:

```text
23:49
→ publish decision inputs

23:50
→ evaluate Hybrid

23:51
→ refresh final daily snapshot
```

Persistence:

```text
/data/daily_summary.json
```

---

# Decision Logic Dashboard

The Decision Logic dashboard now shows:

## Grid Situation

- Grid Confidence
- Grid Available — Last 24 Hours
- Grid Available — Last 48 Hours

## Night Tariff Decision

- Final Decision
- Battery SOC used
- House Consumption Today
- Battery Energy to Full
- Total Energy Required
- Solar Forecast Tomorrow
- Decision Reason

## Panic Decision

- Solar Forecast Today
- Previous Daily Consumption
- Panic Decision
- Panic Decision Reason

The dashboard now explains why EnergyHub remains in Solar or activates Hybrid/Panic.

Further visual optimization is deferred to the next session.

---

# Energy Balance Chart

Current chart content:

- House Consumption
- Unused Solar Estimated
- Grid Import
- Grid Availability

Header values:

- Consumption Today
- Grid Import Today
- Forecast Today
- Forecast Tomorrow

Known presentation issue:

- current-day Grid Import may show `0`;
- old Daily Summary history may still show a previous incompatible value;
- historical entity naming includes `_2`.

This is a temporary cleanup issue, not a logic failure.

---

# Away Mode Status

Away Mode is not part of the final EnergyHub 1.0 logic.

The original Away concept mixed:

- occupancy state;
- solar-surplus heating;
- cheap-tariff heating;
- flexible-load control.

This requires a cleaner Smart Load architecture.

Away / Smart Heating development is deferred to EnergyHub 1.1.

---

# Home Assistant Configuration in Git

Current structure:

```text
homeassistant/
└── live/
    ├── config/
    └── storage/
```

The old manually maintained `homeassistant/legacy/` files were removed from Git.

Current synchronized files include:

```text
config/
  automations.yaml
  configuration.yaml
  scenes.yaml
  scripts.yaml

storage/
  input_boolean
  input_number
  timer
  lovelace.dashboard_powmr1
  lovelace_dashboards
  lovelace_resources
```

Workflow:

```text
Edit in Home Assistant
→ run tools/dev/sync-from-ha.ps1
→ review in GitHub Desktop
→ commit
→ push
```

Add-on workflow:

```text
Edit in VS Code
→ deploy with tools/dev/deploy-to-ha.ps1
→ rebuild / restart
→ test
→ review in GitHub Desktop
→ commit
→ push
```

---

# Current Health Architecture

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

## Battery Health

```text
SOC < 15%
→ warning

SOC between 15% and 95%
AND absolute SOC change >= 2%
→ warning
```

## Telemetry Freshness

```text
No valid telemetry for 60 seconds
→ stale

House Load unchanged for 5 minutes
→ warning
```

## Inverter Health

EnergyHub polls QPIWS every 60 seconds.

Persistent real-system finding:

```text
eeprom_fault = 1
```

Its operational meaning remains under investigation.

EnergyHub must never automatically restart the inverter.

---

# Known Hardware Limitations

PowMr PI30MAX does not expose:

- PV2 telemetry;
- second output telemetry;
- reliable accumulated Grid Import;
- reliable lifetime energy counters;
- complete export data.

Therefore:

- PV telemetry is operational rather than complete;
- Solcast is used for forecast-based decisions;
- Grid Import is calculated;
- totals are informational rather than billing-grade.

---

# Known Issues and Deferred Cleanup

## Entity Naming

Resolve naming conflicts such as:

```text
sensor.energyhub_daily_grid_import_estimated_2
```

## Obsolete MQTT Discovery

Review and remove obsolete retained MQTT Discovery entities.

## Grid Import Rollover

Verify:

- midnight reset;
- yesterday finalization;
- Daily Summary history;
- chart continuity.

## Dashboard and Chart Review

Review all dashboards and charts for:

- consistent style;
- compact layout;
- better naming;
- smart summaries;
- less duplicate information;
- clearer icons;
- better date labels;
- dynamic visual states.

## Code Review

Perform a complete post-1.0 code review after the implementation sprint.

## Restart Recovery

Improve reconstruction of operating strategy from verified inverter settings:

```text
SUB + SNU → Hybrid Charging or Panic
SUB + OSO → Hybrid Grid Hold
SBU + OSO → Solar
```

## Persistent Inverter Fault

Investigate:

```text
eeprom_fault = 1
```

---

# Next Session

The next session is a quality and cleanup session.

Planned order:

```text
1. Full code review
2. Fix entity names such as *_2
3. Remove obsolete MQTT Discovery entities
4. Verify Grid Import rollover and history
5. Review every chart and dashboard
6. Make dashboards more compact, consistent, visual, and smart
7. Fix test-drive bugs
8. Update documentation if implementation changes
```

No large feature development is planned for this session.

---

# Product Roadmap

## EnergyHub 1.0 — Autonomous Home

Status:

```text
Feature development complete
Test-drive and cleanup phase started
```

Focus:

- autonomous Solar / Hybrid / Panic operation;
- battery management;
- grid reliability;
- solar forecast;
- explainable decisions;
- health monitoring;
- Grid Import accounting;
- Home Assistant integration.

## EnergyHub 1.1 — Smart Loads & Test-Drive Improvements

Planned after 2–3 weeks of real Autopilot operation.

Focus:

- bug fixes;
- dashboard improvements;
- chart cleanup;
- Smart Heating architecture;
- rethink Away;
- solar-surplus heating;
- cheap-tariff heating;
- EV charging template;
- cosmetic and usability improvements.

## EnergyHub 1.2 — Configurable EnergyHub

Focus:

- configurable cheap-tariff window;
- configurable Panic evaluation window;
- battery capacity;
- grid charging current;
- Hybrid target SOC;
- Panic profiles;
- safe user-adjustable thresholds;
- family settings dashboard.

Possible Panic profiles:

```text
Conservative
SOC 80% → charge to 95%

Relaxed
SOC 50% → charge to 80%
```

## EnergyHub 1.3 — Recovery & Resilience

Focus:

- MQTT recovery;
- network recovery;
- serial communication recovery;
- inverter communication recovery;
- mpp-solar timeout handling;
- Home Assistant connectivity recovery;
- bounded retries;
- safe-state reconstruction;
- external watchdog strategy.

## EnergyHub 2.x — Energy Economics

Focus:

- multiple inverter support;
- Deye / GoodWe / Victron / other platforms;
- dynamic tariffs;
- energy price forecasting;
- import optimization;
- export optimization;
- net billing;
- battery degradation model.

## EnergyHub 3.x — Full Home Energy Management System

Focus:

- solar forecast;
- weather;
- dynamic electricity market;
- EV charging;
- heat pumps;
- battery storage;
- grid reliability;
- energy trading.

---

# Project Principle

EnergyHub evolves through:

```text
Monitoring
    ↓
Reliable Facts
    ↓
Health Awareness
    ↓
Explainable Decisions
    ↓
Validated Automation
    ↓
Autonomous Home Operation
```

Automation should only be trusted after validation against real household operation.