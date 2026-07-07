# EnergyHub Backlog

> Ideas are valuable. A backlog keeps them organized until the right time.

---

# High Priority

## Recovery Strategy

Status:

Next development milestone.

Goals:

* Investigate MQTT connection failures.
* Investigate network failures.
* Investigate serial communication failures.
* Investigate `mpp-solar` timeouts and blocking.
* Investigate Home Assistant connectivity failures.
* Define recovery responsibilities for each EnergyHub service.
* Define when automatic recovery should occur.
* Define when EnergyHub should only report a failure.
* Add recovery notifications where appropriate.

---

## Battery Health Monitoring

Status:

Planned.

Goals:

* Detect abnormal Battery SOC changes.
* Detect sudden SOC jumps between telemetry updates.
* Define warning and critical SOC jump thresholds.
* Publish Battery Health information through MQTT.
* Generate alerts for suspicious battery behavior.
* Preserve enough diagnostic information to investigate battery events.

Initial detection concept:

```text
SOC change >= 3% between telemetry updates
→ warning

SOC change >= 10% between telemetry updates
→ critical

## Home Assistant

Goals:

* Family Dashboard.
* Engineering Dashboard.
* Better status indicators.
* Continue dashboard improvements as new EnergyHub services and entities are added.

Current dashboard architecture:

```text
EnergyHub Status
→ What is happening now?
→ Is the system healthy?

EnergyHub Intelligence
→ What does EnergyHub know?
→ What information is available for decisions?

# Low Priority

## Additional Hardware

Goals:

* Deye.
* Victron.
* Growatt.
* LuxPower.

---

## Infrastructure

Goals:

* Remote Home Assistant access.
* Secure VPN access.
* Automatic backups.
* OTA updates.

---

# Research

Ideas that require investigation before implementation:

* AI energy optimization.
* Machine learning consumption prediction.
* Dynamic electricity pricing.
* Automatic anomaly detection.

---

## Reliability

Goals:

* Telemetry freshness detection.
* Automatic add-on restart where appropriate.
* Communication Health MQTT sensor.
* Health dashboard card.
* Recovery notifications.

---

## Dashboard

### Developer Dashboard

Goals:

* EnergyHub Status card.
* EnergyHub Intelligence card.
* Grid Confidence.
* Grid Availability.
* Battery Health information.
* Inverter Health information.
* Decision Engine recommendations and explanations.

### Family Dashboard

Goals:

* Current Operating Mode.
* Battery SOC.
* Grid status.
* Sunrise / Sunset.
* Heating controls.
* Panic Mode.

The Family Dashboard should provide simple and understandable information without exposing unnecessary engineering details.

---

## Daily Summary

Status:

v1 Complete.

Currently stores:

* Daily House Consumption.
* Daily Solar Forecast.
* Daily Solar Surplus Estimated.
* Daily Grid Availability.

Current history:

* Persistent daily history in EnergyHub.
* 7-day dashboard visualization.

Future:

* Last 30 days visualization.
* Grid charging energy.
* Exported energy.
* Imported energy.
* Daily Grid Import Estimated.

---

## Decision Engine

Status:

Planned after Recovery Strategy investigation.

Goals:

* Produce Operating Mode recommendations.
* Produce Battery Strategy recommendations.
* Produce Heating Strategy recommendations.
* Produce Flexible Load recommendations.
* Explain every significant recommendation.
* Publish Recommended Mode.
* Publish Reason.
* Publish Recommended Action.

Initial implementation should remain recommendation-only.

Automatic execution should be introduced only after recommendations have been observed and validated against real household behavior.

---

## Documentation

Goals:

* Update documentation at the end of every development session.
* Keep `PROJECT_STATE.md` as the primary entry point for future development.
* Record significant real-system findings.
* Clearly distinguish confirmed behavior from hypotheses requiring additional testing.

---

# Rule

Backlog items are not forgotten.

They are simply waiting for the right stage of development.