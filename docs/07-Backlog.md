# EnergyHub Backlog

> Ideas are valuable. A backlog keeps them organized until the right time.

---

# High Priority

## Recovery Strategy

Status:

Design started.

Completed:

* Communication Watchdog.
* Communication Health monitoring.
* Battery Health Monitor v1.
* Telemetry Freshness Monitor v1.
* Inverter Health Monitor v1.
* System Health aggregation v1.
* `QPIWS` warning and fault reading.
* Initial Recovery Strategy principles defined.

Confirmed principles:

* EnergyHub must never automatically restart the inverter.
* The inverter owns its internal protection and restart behavior.
* Detection and recovery are separate responsibilities.
* Battery anomalies are warning events only.
* Inverter warnings and faults are warning events only in Recovery v1.
* Automatic recovery must be bounded.
* Infinite restart loops are prohibited.

Future work:

* Investigate MQTT connection failures.
* Investigate network failures.
* Investigate serial communication failures.
* Investigate `mpp-solar` timeouts and blocking.
* Investigate Home Assistant connectivity failures.
* Define recovery responsibilities for each EnergyHub service.
* Implement limited EnergyHub self-recovery where appropriate.
* Allow no more than one initial automatic recovery attempt.
* Allow a possible second recovery attempt after approximately 30 minutes.
* Stop automatic recovery after repeated failure.
* Add recovery notifications.
* Investigate external heartbeat/watchdog monitoring for cases where Home Assistant or EnergyHub is completely unavailable.

---

## Battery Health Monitoring

Status:

v1 Complete.

Implemented:

* Low SOC detection.
* SOC jump detection.
* Battery Health MQTT sensors.
* Battery Health reason reporting.

Current rules:

```text
SOC < 15%
→ warning

SOC between 15% and 95%
AND absolute SOC change >= 2%
→ warning

SOC > 95%
→ SOC jump detection disabled

---

## Daily Grid Import

Status:

Planned.

Goal:

Estimate and store daily electricity imported from the grid.

Grid Import may occur in several different operating scenarios.

### Solar Mode Fallback Import

Normal configuration:

```text
Setting 01 → SBU
Setting 16 → OSO