# EnergyHub Project State

Last Updated: 2026-07-09

---

# Project Vision

EnergyHub is an autonomous home energy management system built on top of Home Assistant.

Its goal is not only to monitor energy, but to make intelligent decisions about battery usage, heating, EV charging and household energy consumption.

EnergyHub should remain:

- local first;
- calm;
- explainable;
- modular;
- reliable;
- suitable for real daily family use.

---

# Current Architecture

```text
Homeowner
   ↓
Dashboards
   ↓
Home Assistant
   ↓
MQTT
   ↓
EnergyHub Core
   ↓
Services / Engines
   ↓
Devices
```

Current EnergyHub Core modules:

- Telemetry Service
- Event Bus
- Grid Monitor
- Grid History
- Grid Stability Engine
- Communication Watchdog
- Health Monitor
- Battery Health Monitor
- Telemetry Freshness Monitor
- Inverter Health Monitor
- System Health Monitor
- Daily Summary Engine

Future modules:

- Decision Engine
- Recovery Service
- Notification Engine
- Forecast Engine
- Device Manager
- BMS Adapter
- Telegram Bot

---

# Current Features Implemented

✅ PowMr telemetry  
✅ MQTT Discovery  
✅ Telemetry validation  
✅ Communication Watchdog  
✅ Communication Health Monitor  
✅ Grid History  
✅ Grid Availability  
✅ Grid Stability Engine  
✅ Grid Confidence  
✅ Battery Health Monitor v1  
✅ Telemetry Freshness Monitor v1  
✅ Inverter Health Monitor v1  
✅ System Health aggregation v1  
✅ QPIWS warning and fault monitoring  
✅ Family Dashboard v1  
✅ Developer Dashboard improvements  
✅ Daily Energy Statistics dashboard  
✅ EnergyHub Status dashboard card  
✅ EnergyHub Intelligence dashboard card  
✅ Floor 3 Heat Pump Auto-Off  
✅ House Model  
✅ Daily Solar Surplus Estimated  
✅ Daily Summary MQTT input path  
✅ Daily Summary Engine v1  

---

# Current Health Architecture

EnergyHub separates different classes of system problems into independent health services.

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

Different failures require different responses.

EnergyHub does not use one universal recovery action for every detected problem.

## Communication Health

Purpose:

Detect communication failures between EnergyHub and the inverter.

Current components:

- Communication Watchdog
- Health Monitor

Current states include:

```text
starting
online
recovering
unavailable
```

## Battery Health

Purpose:

Detect abnormal battery behavior.

Current Battery Health Monitor v1 rules:

```text
SOC < 15%
→ warning

SOC between 15% and 95%
AND absolute SOC change >= 2%
→ warning
```

Battery Health thresholds are technical configuration values and may differ between battery systems.

Current MQTT entities:

```text
sensor.energyhub_battery_health
sensor.energyhub_battery_health_reason
```

Battery Health anomalies are detection and warning events only.

## Telemetry Freshness

Purpose:

Detect missing or suspiciously frozen inverter telemetry.

Current rules:

```text
No valid telemetry for 60 seconds
→ stale

House Load unchanged for 5 minutes
→ warning
```

Current MQTT entities:

```text
sensor.energyhub_telemetry_freshness
sensor.energyhub_telemetry_freshness_reason
sensor.energyhub_house_load_unchanged
```

Battery parameters are intentionally excluded from frozen telemetry detection because they may legitimately remain unchanged for long periods.

Grid voltage is unsuitable as the primary telemetry movement indicator in the current installation because a voltage stabilizer keeps input voltage relatively stable.

House Load is currently used as the primary telemetry movement indicator because it normally changes during real household operation.

## Inverter Health

Purpose:

Read and interpret inverter-reported warnings and faults.

EnergyHub polls:

```text
QPIWS
```

every 60 seconds.

Current MQTT entities:

```text
sensor.energyhub_inverter_health
sensor.energyhub_inverter_health_reason
sensor.energyhub_inverter_warning_raw
```

Real-system testing discovered:

```text
eeprom_fault = 1
```

All other observed QPIWS warning and fault flags were zero.

The operational significance of the persistent `eeprom_fault` remains under investigation.

EnergyHub must never automatically restart the inverter.

## System Health

Purpose:

Provide one aggregated EnergyHub operational health state.

Current inputs:

```text
Communication Health
Battery Health
Telemetry Freshness
Inverter Health
```

Current MQTT entities:

```text
sensor.energyhub_system_health
sensor.energyhub_system_health_reason
```

Current basic rules:

```text
Communication unavailable
→ System Health unavailable

Any component warning
→ System Health warning

All components healthy
→ System Health normal
```

The persistent inverter `eeprom_fault` currently causes System Health to report a warning.

This behavior is intentionally preserved until the meaning of the fault is investigated.

---

# Current Dashboard Architecture

The EnergyHub Developer Dashboard separates current operational state from information used for analysis and future decisions.

## EnergyHub Status

Purpose:

```text
What is happening now?

Is the system healthy?
```

Current information:

- Communication Status
- Battery SOC
- Battery Charging Current
- Battery Discharge Current
- House Load
- PV1 Power
- Grid Voltage

New health information available for future dashboard integration:

- Battery Health
- Telemetry Freshness
- Inverter Health
- System Health

Future:

- Current Operating Mode
- prominent Operating Mode visualization
- consistent Operating Mode colors
- System Health visualization

## EnergyHub Intelligence

Purpose:

```text
What does EnergyHub know?

What information is available for decisions?
```

Current information:

- Grid Confidence
- Grid Available 24h
- Grid Available 48h
- Consumption Yesterday
- Solar Surplus Yesterday
- Solar Forecast Today
- Solar Forecast Tomorrow

Future:

- Recommended Mode
- Recommendation
- Reason
- Recommended Action
- Battery Reserve Forecast
- expected ability to operate until the next charging opportunity

---

# Known Hardware Limitations

PowMr PI30MAX currently exposes:

- Battery information
- Grid voltage
- Grid frequency
- Load
- PV1 telemetry only

Not available from the inverter:

- PV2 telemetry
- second output status
- reliable grid import/export counters
- reliable total PV generation when both PV inputs are involved

Because of this:

- inverter PV telemetry is treated primarily as operational and diagnostic information;
- daily solar surplus is based on Solcast forecast, not inverter PV production;
- total Grid Import must be calculated or estimated by EnergyHub;
- Grid Import statistics will initially be informational rather than meter-accurate.

---

# Current Inverter Control Knowledge

EnergyHub has successfully tested programmatic control of Setting 16.

Verified mapping:

```text
Setting 16 — Charger Source Priority

PCP02 → OSO
PCP03 → CSO
PCP01 → SNU
```

The inverter may expose command names and display names differently.

The real inverter display was used to verify actual Setting 16 behavior.

## Setting 01

Setting 01 controls output source priority.

The future EnergyHub operating strategy requires programmatic switching between:

```text
SBU
↕
SUB
```

This has not yet been tested programmatically.

Testing Setting 01 control is the next critical inverter-control milestone.

Automatic Operating Mode execution must not begin until EnergyHub can safely:

- switch SBU → SUB;
- verify the resulting inverter state;
- switch SUB → SBU;
- verify restoration of the expected inverter state.

---

# Current Inverter Charging-Source Modes

The current PowMr firmware exposes three usable Setting 16 charging-source modes:

```text
OSO
CSO
SNU
```

`CUB` is not available on the current inverter firmware.

## OSO

Only Solar.

Current intended use:

```text
Solar Mode
```

## CSO

Solar First.

Real-system testing showed that CSO is not suitable for planned continuous grid charging.

Observed behavior:

```text
Night
PV = 0
Utility charging active

↓

PV generation begins

↓

Utility charging current significantly decreases
```

## SNU

SNU is the selected candidate for controlled utility and solar charging.

Current intended use:

```text
Hybrid charging
Panic charging
```

Important real-system finding:

Changing Setting 16 from OSO to SNU alone does not necessarily force immediate grid charging.

Controlled EnergyHub charging requires coordinated Setting 01 and Setting 16 changes.

---

# Current Operating Mode Strategy

Current mode names:

```text
Solar
Hybrid
Panic
Away
```

The modes describe how the house obtains and manages energy rather than the current season.

## Solar Mode

Expected inverter configuration:

```text
Setting 01 → SBU
Setting 16 → OSO
```

Behavior:

- house prefers solar and battery operation;
- battery charging is solar-only;
- normal inverter low-battery fallback behavior remains available.

Current inverter thresholds:

```text
Battery SOC reaches 15%
→ inverter switches house load to grid

Battery charges from solar to 30%
→ inverter switches house back to SBU operation
```

This behavior may be acceptable when Grid Confidence is good.

During the fallback period, house consumption supplied by the grid must eventually be included in Daily Grid Import.

## Hybrid Mode

Expected charging configuration:

```text
Setting 01 → SUB
Setting 16 → SNU
```

Initial charging target:

```text
Battery SOC → 80%
```

After the target is reached:

```text
Restore SBU + OSO
```

Initial expected use:

```text
Controlled night-tariff battery charging
```

Hybrid Mode should eventually consider:

- Grid Confidence;
- Solar Forecast;
- expected House Consumption;
- current Battery SOC;
- expected battery reserve.

## Panic Mode

Expected charging configuration:

```text
Setting 01 → SUB
Setting 16 → SNU
```

Initial charging target:

```text
Battery SOC → 95%
```

After the target is reached:

```text
Restore SBU + OSO
```

Unlike Hybrid Mode, Panic charging may occur at any time of day.

Possible triggers include:

- poor Grid Confidence;
- falling Battery SOC;
- low remaining solar generation;
- high expected House Consumption;
- insufficient projected battery reserve.

EnergyHub should not always wait until the battery reaches the inverter's 15% low-battery fallback threshold.

## Away Mode

Status:

```text
Requires additional design
```

Current concept:

- prioritize safe autonomous house operation;
- protect battery reserve;
- use excess solar energy for flexible heating loads;
- reduce unnecessary grid import.

---

# Proactive Battery Reserve Protection

A key future Decision Engine responsibility is predicting whether the house can safely operate until the next expected charging opportunity.

Example scenario:

```text
Night
        ↓
Hybrid charging to 80%
        ↓
Day
        ↓
Low solar generation
+
High house consumption
        ↓
Battery SOC falls
        ↓
Grid Confidence is poor
        ↓
Risk of battery depletion
```

Future EnergyHub behavior may be:

```text
Grid Confidence poor
+
SOC falling
+
Remaining Solar Forecast low
+
Expected House Consumption high
+
Projected Battery Reserve insufficient
        ↓
Temporary daytime Panic charging while grid is available
```

The central future Decision Engine question is:

```text
Can the house safely survive until the next expected charging opportunity?
```

---

# Current Daily Summary Model

Daily Summary Engine v1 is implemented inside EnergyHub.

Home Assistant provides selected daily values through retained MQTT input topics.

EnergyHub consumes these inputs, stores a daily snapshot, and republishes EnergyHub-owned MQTT sensors for dashboards and future engines.

Current values:

- Daily House Consumption
- Daily Solar Forecast
- Daily Solar Surplus Estimated
- Daily Grid Availability

MQTT input topics:

```text
energyhub/input/ha/daily_house_consumption
energyhub/input/ha/solar_forecast_today
energyhub/input/ha/daily_solar_surplus_estimated
```

EnergyHub Daily Sensors:

```text
sensor.energyhub_daily_house_consumption
sensor.energyhub_daily_solar_forecast
sensor.energyhub_daily_solar_surplus_estimated
sensor.energyhub_daily_grid_availability
```

Persistence:

```text
/data/daily_summary.json
```

The Decision Engine must consume Daily Summary data rather than create historical facts itself.

---

# Daily Grid Import

Status:

```text
Planned
```

The PowMr inverter does not expose a reliable accumulated Grid Import counter.

EnergyHub must calculate or estimate Daily Grid Import.

Grid Import may occur during:

- Solar Mode low-battery fallback;
- Hybrid charging;
- Panic charging.

Planned entity:

```text
sensor.energyhub_daily_grid_import
```

Future Energy Statistics:

```text
House Consumption
Unused Solar
Grid Import
Grid Availability
```

---

# Grid Confidence

Grid Confidence is calculated from rolling 48-hour grid availability.

Current thresholds:

```text
90–100%  → normal
60–90%   → unstable
30–60%   → risk
0–30%    → panic
```

Grid Confidence is an operational metric.

Daily Grid Availability is a historical metric.

Future Decision Engine behavior should use Grid Confidence to determine how aggressively EnergyHub protects battery reserve.

---

# Recovery Strategy

Status:

```text
Initial design complete
Implementation intentionally deferred
```

Core principle:

```text
Detection
    ↓
Classification
    ↓
Safe bounded recovery where appropriate
```

## Inverter Recovery

Policy:

```text
EnergyHub must never automatically restart the inverter.
```

## Battery Recovery

Policy:

```text
Battery Health anomalies
→ detect
→ report
→ no automatic recovery action
```

## EnergyHub Recovery

Future EnergyHub self-recovery may be allowed where the failure type is understood and software recovery is considered safe.

Automatic recovery must be bounded.

Initial concept:

```text
Failure detected
        ↓
Retry and verify
        ↓
First automatic recovery attempt
        ↓
Verify result
        ↓
If still failed
        ↓
Cooldown approximately 30 minutes
        ↓
Second automatic recovery attempt
        ↓
Verify result
        ↓
If still failed
        ↓
Stop automatic recovery
        ↓
Require human attention
```

Infinite restart loops are prohibited.

## Home Assistant Failure Limitation

EnergyHub and Home Assistant cannot reliably report their own failure if the entire Home Assistant platform is frozen or unavailable.

Future infrastructure should include an external heartbeat or watchdog.

---

# Current Priorities

1. Complete documentation updates and commit the current Health Monitoring milestone.
2. Move development to a new clean chat.
3. Test programmatic Setting 01 control:
   - SBU → SUB
   - SUB → SBU
4. Verify Setting 01 state and real inverter behavior.
5. Add inverter operating mode telemetry where useful.
6. Begin Solar / Hybrid / Panic control implementation.
7. Begin Decision Engine v1 after inverter control is validated.
8. Implement Daily Grid Import estimation.
9. Revisit JK BMS integration.
10. Investigate persistent `eeprom_fault`.

---

# Current Milestone Status

## Foundation

Status:

```text
Complete
```

## Daily Summary Engine

Status:

```text
v1 Complete
```

## Health Monitoring

Status:

```text
v1 Complete
```

Implemented:

- Communication Health
- Battery Health Monitor
- Telemetry Freshness Monitor
- Inverter Health Monitor
- QPIWS polling
- System Health aggregation
- MQTT Discovery for all current health services

## Recovery Strategy

Status:

```text
Initial design complete
```

Implementation is intentionally deferred until specific recovery mechanisms are justified by real-system failure behavior.

## Inverter Control

Status:

```text
Next
```

Completed:

- Setting 16 control tested successfully.
- OSO, CSO and SNU mappings confirmed.

Critical next step:

```text
Test Setting 01 control

SBU ↔ SUB
```

## Operating Modes

Status:

```text
Strategy defined
Automatic execution not implemented
```

## Decision Engine

Status:

```text
Planned after Inverter Control validation
```

## JK BMS Integration

Status:

```text
Paused / Revisit
```

Goal:

Provide direct cell-level battery information to Battery Health Monitor.

JK BMS protocol handling and Battery Health analysis must remain separate architectural responsibilities.

---

# Development Workflow

EnergyHub development follows this cycle:

```text
Architecture
    ↓
Implement
    ↓
Deploy
    ↓
Test on Real System
    ↓
Document
    ↓
Commit
```

Every runtime change must be deployed and tested on the real EnergyHub system before commit.

Documentation must be updated whenever architecture or confirmed system behavior changes.

Git and project documentation remain the source of truth.

---

# Next Session

Start with the critical inverter-control experiment:

```text
Setting 01

SBU ↔ SUB
```

The goal is to determine:

1. Which PI30MAX command changes Setting 01.
2. Whether the inverter accepts the command.
3. Whether the real inverter display confirms the expected state.
4. Whether EnergyHub can read the current Setting 01 state.
5. Whether EnergyHub can safely restore SBU after switching to SUB.

After successful validation:

```text
Setting 01 control
        ↓
Operating Mode control
        ↓
Solar / Hybrid / Panic implementation
        ↓
Decision Engine v1
```

Daily Grid Import estimation should also be implemented during the upcoming energy-management phase.

---

# Immediate Next Actions

```text
1. Commit current code and documentation
2. Move to a new clean development chat
3. Test Setting 01 SBU ↔ SUB control
4. Add inverter mode telemetry where useful
5. Implement controlled Solar / Hybrid / Panic transitions
6. Begin Decision Engine v1
7. Implement Daily Grid Import estimation
8. Investigate persistent eeprom_fault
9. Revisit JK BMS integration
```

---

# Project Principle

EnergyHub should evolve from:

```text
Monitoring
    ↓
Reliable Facts
    ↓
Health Awareness
    ↓
Recommendations
    ↓
Explainable Decisions
    ↓
Carefully Validated Automation
```

The system should not automate behavior simply because automation is technically possible.

Every automated decision should be based on reliable facts, observable system behavior and validated real-world experience.