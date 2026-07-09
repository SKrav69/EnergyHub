# EnergyHub Backlog

> Ideas are valuable. A backlog keeps them organized until the right time.

---

# High Priority

## Inverter Control

Status:

Critical next development phase.

Confirmed Setting 16 control:

```text
PCP02 → OSO
PCP03 → CSO
PCP01 → SNU
```

Current operating strategy:

```text
SOLAR
Setting 01 → SBU
Setting 16 → OSO

HYBRID charging session
Setting 01 → SUB
Setting 16 → SNU
Target SOC → 80%
Then restore → SBU + OSO

PANIC charging session
Setting 01 → SUB
Setting 16 → SNU
Target SOC → 95%
Then restore → SBU + OSO
```

Critical next research:

- Identify the command used to change Setting 01.
- Test programmatic switching:

```text
SBU ↔ SUB
```

- Verify the real inverter display after each command.
- Verify inverter behavior after each command.
- Verify safe restoration to SBU + OSO.
- Add inverter operating mode telemetry where useful.
- Add current Setting 01 state.
- Add current Setting 16 state.

Automatic Solar / Hybrid / Panic mode execution must not begin until Setting 01 switching is confirmed on the real inverter.

---

## Recovery Strategy

Status:

Initial design complete.

Completed:

- Communication Watchdog.
- Communication Health monitoring.
- Battery Health Monitor v1.
- Telemetry Freshness Monitor v1.
- Inverter Health Monitor v1.
- System Health aggregation v1.
- `QPIWS` warning and fault reading.
- Initial Recovery Strategy principles defined.

Confirmed principles:

- EnergyHub must never automatically restart the inverter.
- The inverter owns its internal protection and restart behavior.
- Detection and recovery are separate responsibilities.
- Battery anomalies are warning events only.
- Inverter warnings and faults are warning events only in Recovery v1.
- Automatic recovery must be bounded.
- Infinite restart loops are prohibited.

Future work:

- Investigate MQTT connection failures.
- Investigate network failures.
- Investigate serial communication failures.
- Investigate `mpp-solar` timeouts and blocking.
- Investigate Home Assistant connectivity failures.
- Define recovery responsibilities for each EnergyHub service.
- Implement limited EnergyHub self-recovery where appropriate.
- Allow no more than one initial automatic recovery attempt.
- Allow a possible second recovery attempt after approximately 30 minutes.
- Stop automatic recovery after repeated failure.
- Add recovery notifications.
- Investigate external heartbeat/watchdog monitoring for cases where Home Assistant or EnergyHub is completely unavailable.

---

## Battery Health Monitoring

Status:

v1 Complete.

Implemented:

- Low SOC detection.
- SOC jump detection.
- Battery Health MQTT sensors.
- Battery Health reason reporting.

Current rules:

```text
SOC < 15%
→ warning

SOC between 15% and 95%
AND absolute SOC change >= 2%
→ warning
```

Battery Health thresholds are technical configuration values and may differ between battery systems.

Future work:

- Preserve diagnostic information for battery anomaly events.
- Add Battery Health alerts.
- Investigate additional generic battery anomaly detection rules if required.
- Add configuration options for Battery Health thresholds if required.

---

## Telemetry Freshness Monitoring

Status:

v1 Complete.

Implemented:

- Detection of missing valid telemetry.
- Detection of House Load remaining exactly unchanged for 5 minutes.
- Telemetry Freshness MQTT sensors.
- Telemetry Freshness reason reporting.

Current rules:

```text
No valid telemetry for 60 seconds
→ stale

House Load unchanged for 5 minutes
→ warning
```

Architecture decision:

Battery SOC, voltage and current are intentionally excluded from frozen telemetry detection because battery values may legitimately remain unchanged for long periods.

Future work:

- Validate House Load unchanged detection against long-term real-system behavior.
- Investigate additional telemetry verification methods if false warnings occur.
- Consider additional command verification using `QMOD` or other supported inverter commands.

---

## Inverter Health Monitoring

Status:

v1 Complete.

Implemented:

- `QPIWS` polling every 60 seconds.
- Automatic parsing of inverter warning and fault flags.
- Inverter Health MQTT sensors.
- Inverter Health reason reporting.

Current finding:

```text
eeprom_fault = 1
```

The inverter currently reports a persistent EEPROM fault while all other observed `QPIWS` flags remain zero.

Future work:

- Investigate the meaning and operational significance of persistent `eeprom_fault`.
- Determine whether the flag represents:
  - a real active fault;
  - a historical/sticky fault;
  - firmware behavior;
  - a protocol interpretation issue.
- Classify inverter warnings and faults by severity.
- Add notifications for significant inverter warnings and faults.

---

## System Health

Status:

v1 Complete.

Implemented:

- System Health aggregation.
- System Health MQTT sensor.
- System Health Reason MQTT sensor.

Current inputs:

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

Future work:

- Improve health severity classification.
- Add notification policies.
- Integrate System Health into Developer Dashboard.
- Determine how persistent known inverter warnings should affect long-term System Health status.

---

## Daily Grid Import

Status:

Planned.

Goal:

Estimate and store daily electricity imported from the grid.

### Solar Mode Fallback Import

Normal configuration:

```text
Setting 01 → SBU
Setting 16 → OSO
```

Possible behavior:

```text
Battery SOC reaches 15%
        ↓
Inverter switches house load to grid
        ↓
Solar charges battery
        ↓
Battery SOC reaches 30%
        ↓
Inverter switches house back to SBU operation
```

During the period between switching to grid and returning to SBU operation, house consumption is Grid Import.

Future work:

- Detect when house load is powered from the grid.
- Accumulate imported energy during the fallback period.
- Store Daily Grid Import.
- Publish:

```text
sensor.energyhub_daily_grid_import
```

- Add Grid Import to the Energy Statistics dashboard.

### Hybrid and Panic Grid Import

Grid Import must also include electricity imported during controlled charging sessions.

Future estimation model:

```text
Daily Grid Import
=
House Load supplied by grid
+
Estimated Battery Charging Energy supplied by grid
```

The PowMr inverter does not expose a reliable accumulated Grid Import counter.

EnergyHub must therefore calculate or estimate Grid Import from available telemetry and controlled operating state.

Daily Grid Import is initially intended for historical and informational purposes.

---

## Proactive Battery Reserve Protection

Status:

Research and Decision Engine design required.

Problem:

A battery charged to the Hybrid target during the night may still be depleted during the following day.

Example:

```text
Night
        ↓
Hybrid Mode charges battery to 80%
        ↓
Day
        ↓
Low solar generation
+
High house consumption
        ↓
SOC falls
        ↓
Grid Confidence is poor
        ↓
Risk of battery depletion
        ↓
Grid may be unavailable when battery reaches critical SOC
```

Waiting until the inverter reaches the normal 15% fallback threshold may be unsafe when Grid Confidence is poor.

Possible strategy:

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
Temporary Panic charging while grid is available
```

Future work:

- Estimate whether current battery reserve is sufficient until the next safe charging opportunity.
- Estimate remaining solar production for the current day.
- Estimate expected house consumption.
- Consider current SOC trend.
- Consider Grid Confidence.
- Define safe battery reserve thresholds.
- Define daytime Panic charging triggers.
- Define when Panic charging should stop.
- Avoid unnecessary daytime grid charging when Grid Confidence is good.

Core future Decision Engine question:

```text
Can the house safely survive until the next expected charging opportunity?
```

---

## Operating Modes

Status:

Strategy defined. Automatic execution not implemented.

Current mode names:

- Solar
- Hybrid
- Panic
- Away

### Solar Mode

Expected inverter configuration:

```text
Setting 01 → SBU
Setting 16 → OSO
```

### Hybrid Mode

Expected charging configuration:

```text
Setting 01 → SUB
Setting 16 → SNU
```

Initial target:

```text
Battery SOC → 80%
```

After target is reached:

```text
Restore SBU + OSO
```

### Panic Mode

Expected charging configuration:

```text
Setting 01 → SUB
Setting 16 → SNU
```

Initial target:

```text
Battery SOC → 95%
```

After target is reached:

```text
Restore SBU + OSO
```

Panic charging may occur during the night or day whenever Grid Confidence is poor and EnergyHub predicts insufficient battery reserve.

### Away Mode

Status:

Requires additional design.

Current concept:

- prioritize safe autonomous house operation;
- use excess solar energy for flexible heating loads;
- protect battery reserve;
- reduce unnecessary grid import.

---

## Decision Engine

Status:

Planned after Inverter Control validation.

Goals:

- Produce Operating Mode recommendations.
- Produce Battery Strategy recommendations.
- Produce Heating Strategy recommendations.
- Produce Flexible Load recommendations.
- Protect battery reserve proactively.
- Determine whether the house can safely operate until the next expected charging opportunity.
- Explain every significant recommendation.
- Publish Recommended Mode.
- Publish Reason.
- Publish Recommended Action.

Decision inputs may include:

- Grid Confidence.
- Grid Availability history.
- Current Battery SOC.
- Battery SOC trend.
- Daily House Consumption.
- Expected House Consumption.
- Solar Forecast Today.
- Solar Forecast Tomorrow.
- Remaining Solar Forecast.
- Current Operating Mode.
- Time of day.
- Night tariff period.
- System Health.

Initial implementation should remain recommendation-only where practical.

Automatic execution should be introduced progressively after inverter control and Decision Engine behavior have been validated against real household behavior.

---

## Home Assistant

Goals:

- Family Dashboard.
- Engineering Dashboard.
- Better status indicators.
- Continue dashboard improvements as new EnergyHub services and entities are added.

Future work:

- Add System Health.
- Add Battery Health.
- Add Telemetry Freshness.
- Add Inverter Health.
- Add current Operating Mode.
- Add current Setting 01 state.
- Add current Setting 16 state.
- Add Grid Import statistics.
- Add future Decision Engine recommendations and explanations.

---

## Daily Summary

Status:

v1 Complete.

Currently stores:

- Daily House Consumption.
- Daily Solar Forecast.
- Daily Solar Surplus Estimated.
- Daily Grid Availability.

Current history:

- Persistent daily history in EnergyHub.
- 7-day dashboard visualization.

Future:

- Last 30 days visualization.
- Daily Grid Import.
- Advanced historical analysis.

Future Energy Statistics chart:

```text
House Consumption
Unused Solar
Grid Import
Grid Availability
```

---

# Low Priority

## Additional Hardware

Goals:

- Deye.
- Victron.
- Growatt.
- LuxPower.

---

## Infrastructure

Goals:

- Remote Home Assistant access.
- Secure VPN access.
- Automatic backups.
- OTA updates.
- External EnergyHub / Home Assistant heartbeat monitoring.
- External failure notifications when Home Assistant cannot report its own failure.

---

# Research

Ideas and technical questions that require investigation before implementation:

- Persistent PowMr `eeprom_fault`.
- Programmatic Setting 01 control.
- `SBU ↔ SUB` command validation.
- Reliable detection of current load power source.
- Daily Grid Import estimation.
- Daytime Panic charging triggers.
- Battery reserve prediction.
- Remaining daily solar production estimation.
- House consumption prediction.
- External Home Assistant watchdog.
- AI energy optimization.
- Machine learning consumption prediction.
- Dynamic electricity pricing.
- Automatic anomaly detection.

---

## Documentation

Goals:

- Update documentation at the end of every development session.
- Keep `PROJECT_STATE.md` as the primary entry point for future development.
- Record significant real-system findings.
- Clearly distinguish confirmed behavior from hypotheses requiring additional testing.

---

# Rule

Backlog items are not forgotten.

They are simply waiting for the right stage of development.