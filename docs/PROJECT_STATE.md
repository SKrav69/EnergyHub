# EnergyHub Project State

Last Updated: 2026-07-13

---

# Project Vision

EnergyHub is a local-first home energy management system built on top of Home Assistant.

Its purpose is not only to monitor energy, but to make explainable decisions about:

- solar use;
- battery reserve;
- grid reliability;
- night charging;
- emergency charging;
- flexible loads;
- heating;
- future EV charging and export optimization.

EnergyHub should remain:

- local first;
- calm;
- explainable;
- modular;
- reliable;
- suitable for daily family use;
- progressively automated rather than fully autonomous from day one.

---

# Current Milestone

EnergyHub has reached the point where it can make and execute its own operating decisions.

Current completed operating strategies:

- Solar
- Hybrid Charging
- Hybrid Grid Hold
- Panic
- Away Mode v1

The current chapter is focused on finishing EnergyHub 1.0:

- validate decision behavior;
- improve dashboards;
- synchronize Home Assistant configuration into Git;
- update documentation;
- polish naming, logs and user experience.

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
PowMr Inverter / Battery / Smart Loads
```

Current EnergyHub Core modules:

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
- Grid Import Estimator
- Autopilot State

Future modules:

- configurable parameter service;
- recovery service;
- notification policy engine;
- forecast engine;
- multi-inverter device manager;
- direct BMS adapter;
- tariff and export optimization services.

---

# Current Features Implemented

## Telemetry and Device Integration

- PowMr 10.2M communication through PI30MAX.
- MQTT communication.
- MQTT Discovery.
- Real-time inverter telemetry.
- QPIGS, QPIRI, QPIWS and QMOD support.
- Programmatic Setting 01 and Setting 16 control.
- Verified inverter transitions with ACK, QPIRI and physical inverter display.

## Health and Reliability

- Communication Watchdog.
- Communication Health.
- Battery Health Monitor v1.
- Telemetry Freshness Monitor v1.
- Inverter Health Monitor v1.
- System Health aggregation.
- QPIWS warning and fault polling.
- Safe transition verification with retries.
- Safe Solar recovery when Autopilot is disabled.

## Grid Intelligence

- Grid availability tracking.
- 24-hour and 48-hour availability.
- Grid Confidence.
- Grid event history.
- Daily Grid Availability.
- Estimated Grid Import power.
- Estimated Daily Grid Import energy.

## Decision and Operating Modes

- Solar strategy.
- Hybrid Decision Engine.
- Hybrid Charging.
- Hybrid Grid Hold.
- Panic Decision Engine.
- Automatic Panic targets of 80% or 95%.
- Manual Panic.
- Away Mode v1.
- Automatic notifications for Hybrid and Panic decisions.

## Home Assistant

- Family and engineering dashboard cards.
- EnergyHub control card.
- Human-readable source-priority display.
- EnergyHub Intelligence card.
- Energy Balance chart.
- Grid Import display and chart integration.
- Floor 3 heat-pump auto-off.
- Away Mode heat-pump control.
- Home Assistant configuration synchronization to Git.

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

Current mode mapping:

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

Transition verification may occasionally return no QPIRI result on the first attempt.

This is currently handled by bounded retries and has been validated successfully on the real inverter.

---

# Operating Mode Logic

## Solar

Solar is the default operating strategy.

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
- today's house consumption;
- tomorrow's solar forecast;
- nominal battery capacity of 16 kWh.

Battery refill energy:

```text
Battery refill required
=
16 kWh × missing SOC percentage
```

Required tomorrow energy:

```text
Required energy
=
Today's house consumption
+
Energy required to refill the battery to 100%
```

Decision:

```text
Tomorrow forecast >= required energy
→ remain in Solar

Tomorrow forecast < required energy
→ enter Hybrid
```

No additional loss factor is used for Hybrid.

The 16 kWh battery itself provides a practical buffer if the forecast or consumption is imperfect.

---

## Hybrid Charging

```text
Setting 01 → SUB
Setting 16 → SNU
Target SOC → 80%
```

When the battery reaches 80%:

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

- house remains on the night grid;
- battery is no longer intentionally charged from the grid;
- battery is preserved until morning;
- SOC may remain around 79–80% without correction;
- at 07:00 EnergyHub restores Solar.

---

## Panic Decision

Automatic Panic is evaluated every 15 minutes between 12:00 and 23:50.

Evaluation is skipped unless EnergyHub is in Solar mode.

Common prerequisites:

```text
PV power < 200 W
AND
Solar forecast today < previous daily consumption × 1.20
```

The 20% margin is intentionally used for Panic because Panic is a live protective decision.

### Unstable Grid

```text
Grid Confidence = unstable
AND
SOC < 50%
→ Panic target 80%
```

### Risk / Very Poor Grid

```text
Grid Confidence = risk
AND
SOC < 80%
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

Manual Panic currently uses a 95% target.

---

## Away Mode v1

Away Mode itself is enabled and disabled manually only.

Entity:

```text
input_boolean.energyhub_away_mode
```

Away Mode controls the first-floor heat-pump smart plug:

```text
switch.lumi_v1_64d7_switch
```

Temperature input:

```text
sensor.miaomiaoce_t2_e515_temperature
```

Start conditions:

```text
Away Mode = ON
Heat pump = OFF
Temperature < 18°C
SOC > 95%
PV > 200 W
```

Once the heat pump starts, temporary PV fluctuations are ignored.

Stop conditions:

```text
Temperature >= 23°C
OR
SOC <= 81%
```

Away Mode remains enabled after the plug stops.

If the start conditions become true again later, including on a later day, the heat pump may start again.

Ownership helper:

```text
input_boolean.energyhub_away_heat_pump_active
```

EnergyHub switches off the plug only when Away Mode started it.

If the plug was turned on manually while Away Mode was off, EnergyHub leaves it alone.

---

# Notifications

EnergyHub publishes non-retained notification events to:

```text
energyhub/event/notification
```

Current automatic notification types:

- Hybrid activated;
- Panic activated.

Home Assistant receives the MQTT event and creates the user-facing notification.

Architecture:

```text
EnergyHub decides
        ↓
MQTT notification event
        ↓
Home Assistant
        ↓
Persistent notification / mobile / future Telegram
```

Manual mode requests do not currently generate the same automatic-decision notification.

---

# Grid Import Estimation

The PowMr inverter does not provide a reliable accumulated Grid Import counter.

EnergyHub therefore estimates import from telemetry and known operating mode.

MQTT entities:

```text
sensor.energyhub_grid_import_power_estimated
sensor.energyhub_daily_grid_import_estimated
```

Persistence:

```text
/data/grid_import.json
```

## Solar / SBU

```text
Estimated Grid Import
=
House Load
+ Battery Charging Power
- Battery Discharging Power
- PV Power
```

Values below 50 W are treated as zero to suppress telemetry noise.

## Hybrid Charging / Panic

```text
Estimated Grid Import
=
House Load
+
Battery Charging Power
```

## Hybrid Grid Hold

```text
Estimated Grid Import
=
House Load
```

The estimator:

- integrates power into kWh;
- resets at midnight;
- survives EnergyHub restarts;
- avoids integrating gaps longer than 60 seconds;
- stores values only when the accumulated energy changes enough to justify a disk write.

The result is informational and not a certified utility-meter value.

---

# Daily Summary

Current Home Assistant inputs:

```text
energyhub/input/ha/daily_house_consumption
energyhub/input/ha/solar_forecast_today
energyhub/input/ha/solar_forecast_tomorrow
energyhub/input/ha/daily_solar_surplus_estimated
```

Current EnergyHub daily sensors:

```text
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_forecast
sensor.energyhub_daily_solar_surplus_estimated
sensor.energyhub_daily_grid_availability
sensor.energyhub_daily_grid_import_estimated
```

Schedule:

```text
23:49
→ publish decision inputs

23:50
→ evaluate Hybrid

23:51
→ publish final daily values / snapshot
```

Persistence:

```text
/data/daily_summary.json
```

---

# Current Dashboard Architecture

## EnergyHub Controls

Contains:

- Autopilot;
- Away Mode;
- Panic button;
- current operating mode.

## EnergyHub Status

Contains:

- human-readable house power priority;
- human-readable battery charging source;
- Communication;
- Battery SOC;
- battery currents;
- House Load;
- Solar Power;
- Grid Voltage;
- Estimated Grid Import Power;
- Estimated Grid Import Today.

## EnergyHub Intelligence

Contains current decision inputs:

- Grid Confidence;
- Grid Availability 24h;
- Grid Availability 48h;
- current SOC;
- consumption today;
- forecast tomorrow;
- PV power;
- forecast today;
- previous daily consumption;
- Panic Decision and reason;
- Grid Import results.

Future additions:

- Hybrid Decision;
- Hybrid Decision Reason;
- Hybrid Required Energy;
- Battery Refill Required.

## Energy Balance Chart

Current 7-day chart:

- House Consumption;
- Solar Surplus Estimated;
- Grid Import Estimated;
- Grid Availability.

Header values:

- Consumption Today;
- Grid Import Today;
- Forecast Today;
- Forecast Tomorrow.

Dashboard layout and naming will be polished later.

---

# Home Assistant Configuration in Git

Home Assistant configuration is now synchronized into the repository.

Structure:

```text
homeassistant/
├── live/
│   ├── config/
│   └── storage/
└── legacy/
```

## `live/`

Exact reviewed files copied from Home Assistant.

Current synchronized files:

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

## `legacy/`

Older manually exported YAML files retained for reference.

## Sync Workflow

```text
Edit dashboards / automations / helpers in HA
        ↓
Run tools/dev/sync-from-ha.ps1
        ↓
Review Git changes
        ↓
Commit
```

Only explicitly approved `.storage` files are synchronized.

The full `.storage` directory must never be committed.

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

## Battery Health v1

```text
SOC < 15%
→ warning

SOC between 15% and 95%
AND absolute SOC change >= 2%
→ warning
```

## Telemetry Freshness v1

```text
No valid telemetry for 60 seconds
→ stale

House Load unchanged for 5 minutes
→ warning
```

## Inverter Health v1

EnergyHub polls QPIWS every 60 seconds.

Persistent real-system finding:

```text
eeprom_fault = 1
```

The operational meaning remains under investigation.

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

- PV telemetry is operational rather than a complete generation meter;
- Solcast is used for forecast-based decisions;
- Grid Import is estimated;
- energy totals are informational rather than billing-grade.

---

# Known Issues and Deferred Polishing

## Startup Panic Log

During startup, Panic may initially log:

```text
Operating mode is unknown, not solar
```

This is expected before Solar is restored and confirmed.

Later polishing may rename this state to a deferred evaluation.

## Night Restart Recovery

The current Home Assistant restart automation still restores Hybrid based mainly on time.

Future recovery should reconstruct the strategy from verified inverter settings:

```text
SUB + SNU → Hybrid Charging
SUB + OSO → Hybrid Grid Hold
SBU + OSO → Solar
```

## Duplicate Autopilot Helpers

Both currently exist:

```text
input_boolean.energyhub_autopilot
input_boolean.name_energyhub_autopilot
```

The active configuration currently uses:

```text
input_boolean.name_energyhub_autopilot
```

The duplicate should be removed during cleanup.

## Dashboard and Naming Cleanup

Future polishing should:

- align entity names;
- align card titles;
- improve chart styling;
- reduce duplicate information;
- replace remaining abbreviations with family-friendly labels;
- expose Hybrid Decision sensors.

---

# Current Priorities

1. Complete documentation updates.
2. Commit the current EnergyHub decision and Home Assistant sync milestone.
3. Review and polish dashboards and charts.
4. Add Hybrid Decision MQTT sensors.
5. Improve restart recovery by reconstructing the current inverter strategy.
6. Add a configurable parameter dashboard.
7. Continue bounded recovery design.
8. Investigate persistent `eeprom_fault`.
9. Revisit direct JK BMS integration when useful.

---

# Future Parameter Dashboard — EnergyHub 1.1

A future dashboard should allow trusted family members to adjust operating parameters without editing code.

Examples:

- Hybrid evaluation time;
- Hybrid target SOC;
- Hybrid morning exit time;
- Panic SOC thresholds;
- Panic target SOC;
- Away Mode start SOC;
- Away Mode stop SOC;
- Away Mode start temperature;
- Away Mode stop temperature;
- Away Mode PV threshold;
- other technical thresholds.

Examples:

```text
Hybrid target:
80% → 70% or 90%

Away Mode SOC range:
95% / 81% → configurable values such as 95% / 60%
```

These values should become controlled helpers or EnergyHub configuration parameters with safe bounds.

---

# Product Evolution

## EnergyHub 1.x

Goal:

Build a house that operates by itself as much as possible while remaining cost-effective and resilient.

Focus:

- PowMr;
- autonomy;
- battery management;
- grid reliability;
- solar forecast;
- smart loads;
- explainable operating modes;
- parameter configuration in 1.1.

## EnergyHub 2.x

Goal:

Optimize import, export and monetary value.

Focus:

- multiple inverter support;
- Deye, GoodWe, Victron and other vendors;
- dynamic tariffs;
- energy price forecasting;
- import optimization;
- export optimization;
- net billing;
- battery degradation model.

## EnergyHub 3.x

Goal:

Become a full Home Energy Management System.

Focus:

- solar forecast;
- weather;
- dynamic electricity markets;
- EV charging;
- heat pumps;
- battery storage;
- grid reliability;
- energy trading.

---

# Development Workflow

## EnergyHub Python Code

```text
Edit in VS Code
→ deploy with tools/dev/deploy-to-ha.ps1
→ rebuild / restart add-on
→ test on real hardware
→ commit
```

## Home Assistant Configuration

```text
Edit in Home Assistant
→ run tools/dev/sync-from-ha.ps1
→ review synchronized files
→ commit
```

Every runtime change should be tested on the real EnergyHub system before commit.

Documentation remains part of the implementation.

---

# Next Session

Recommended next work:

```text
1. Finish and commit documentation
2. Review current charts and dashboard naming
3. Add Hybrid Decision MQTT sensors
4. Improve restart recovery
5. Review backlog and close completed items
6. Create final operating-mode infographic from confirmed logic
```

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

The system should automate only behavior that has been validated against real household operation.