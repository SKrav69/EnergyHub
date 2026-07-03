# EnergyHub Backlog

> Ideas are valuable. A backlog keeps them organized until the right time.

---

# High Priority

## Inverter Control

* Programmatically change inverter operating modes
* Summer Mode
* Winter Mode
* Panic Mode
* Away Mode
* Manual Override

---

## Battery Charging

* Control AC charging current
* Dynamic charging power
* Night tariff optimization
* Panic charging mode

---

## Home Assistant

* Family dashboard
* Engineering dashboard
* Dashboard redesign
* Better status indicators

---

## Notifications

* Power outage detection
* Battery reserve warnings
* High load alerts
* System health monitoring

---

# Medium Priority

## Forecasting

* Weather forecast
* Solar production forecast
* Battery prediction
* Consumption prediction

Dashboard: Grid Availability & Grid Charging

- Add grid availability sensor:
  grid_available = ac_input_voltage > 180

- Show grid availability on dashboard:
  100% = grid available
  0% = grid unavailable

- Add daily / weekly statistics:
  grid charging energy
  grid charging during Winter Mode
  grid charging during Panic Mode
  night tariff charging amount

- Show this on Engineering Dashboard first.
- Later simplify for Family Dashboard.

---

## Electric Vehicle

* Solar-first charging
* Smart charging schedules
* Battery reserve protection

---

## Energy Optimization

* Dynamic tariffs
* Net Billing optimization
* Smart export
* Smart import

---

# Low Priority

## BMS Integration

Status:

Postponed.

Reason:

Current inverter data is sufficient for the first development stages.

Future work:

* JK BMS
* Daly BMS
* Cell voltage monitoring
* Balancing information
* Temperature monitoring

---

## Additional Hardware

* Deye
* Victron
* Growatt
* LuxPower

---

## Infrastructure

* Remote Home Assistant access
* Secure VPN access
* Automatic backups
* OTA updates

---

# Research

Ideas that require investigation before implementation.

Examples:

* AI energy optimization
* Machine learning consumption prediction
* Dynamic electricity pricing
* Automatic anomaly detection

---

# Rule

Backlog items are not forgotten.

They are simply waiting for the right stage of development.

## Reliability

- Telemetry freshness detection
- Automatic add-on restart
- Communication Health MQTT sensor
- Health dashboard card
- Recovery notifications

---

## Dashboard

Developer Dashboard

- Health card
- Grid Confidence
- Grid Availability

Family Dashboard

- Current mode
- Battery SOC
- Sunrise / Sunset
- Heating controls
- Panic mode

---

## Daily Summary

Replace PV Generation with:

- House Consumption
- Energy Opportunity
- Grid Availability

Store:

- Last 7 days
- Last 30 days

Future:

- Grid charging energy
- Exported energy
- Imported energy

---

## Documentation

Update documentation at the end of every development session.

PROJECT_STATE.md becomes the primary entry point for future development.