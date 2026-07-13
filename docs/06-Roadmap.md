# EnergyHub Roadmap

> Build the foundation first. Add intelligence second. Scale third.

---

# EnergyHub 1.0 — Autonomous Home Foundation

Goal:

Create a reliable local-first energy system that can monitor the house, understand current conditions, make explainable decisions, and safely control the real inverter and selected loads.

## Foundation

Deliverables:

* GitHub repository
* Documentation architecture
* Project philosophy
* System architecture
* Home Assistant integration
* PowMr communication
* Repository structure
* Development and deployment workflow

Status:

✅ Completed

## Device Layer

Deliverables:

* PowMr PI30MAX integration
* MQTT communication
* MQTT Discovery
* Inverter telemetry
* Battery monitoring
* Setting 01 control
* Setting 16 control
* Verified inverter transitions
* Operating-mode telemetry

Status:

✅ Completed for the current PowMr installation

## Health & Reliability

Deliverables:

* Communication Watchdog
* Communication Health
* Battery Health Monitor
* Telemetry Freshness Monitor
* Inverter Health Monitor
* System Health aggregation
* Grid monitoring
* Grid history
* Grid Confidence
* QPIWS monitoring
* Bounded recovery architecture

Status:

🚧 Core monitoring completed; recovery implementation remains in progress

## Daily Intelligence

Deliverables:

* Daily Summary Engine
* Daily House Consumption
* Daily Solar Forecast
* Daily Solar Surplus Estimated
* Daily Grid Availability
* 7-day historical visualization
* Estimated Grid Import power
* Estimated Daily Grid Import
* Persistent Grid Import history

Status:

✅ v1 Completed

## Decision Engine

Deliverables:

* Solar strategy
* Hybrid Decision Engine
* Hybrid Charging
* Hybrid Grid Hold
* Panic Decision Engine
* Automatic Panic charging
* Manual Panic
* Away Mode v1
* Explainable decision reasons
* Automatic mode notifications

Status:

✅ Core v1 Completed and under real-world validation

## Home Assistant Experience

Deliverables:

* Family-oriented dashboards
* Engineering and testing views
* EnergyHub Controls
* EnergyHub Status
* EnergyHub Intelligence
* Energy Balance charts
* Grid Import visualization
* Away Mode control
* Panic control
* Home Assistant configuration synchronization to Git

Status:

🚧 Functional; visual and naming polish remains

## Remaining 1.0 Work

Priorities:

* Validate current decision behavior over real household operation
* Improve restart recovery by reconstructing strategy from inverter settings
* Add Hybrid Decision MQTT sensors
* Polish dashboards and charts
* Remove duplicate helpers and naming inconsistencies
* Continue bounded recovery implementation
* Investigate persistent inverter `eeprom_fault`
* Complete documentation alignment
* Create final operating-mode infographic

Success criterion:

> The house can operate safely and economically with minimal homeowner intervention, while every important automated decision remains understandable.

---

# EnergyHub 1.1 — Configurable Home Intelligence

Goal:

Make EnergyHub behavior adjustable without editing Python code or Home Assistant YAML.

Deliverables:

* Configurable Hybrid evaluation time
* Configurable Hybrid target SOC
* Configurable morning exit time
* Configurable Panic thresholds and targets
* Configurable Away Mode SOC thresholds
* Configurable Away Mode temperature thresholds
* Configurable Away Mode PV threshold
* Configurable technical health thresholds where appropriate
* Safe parameter bounds
* Parameter dashboard for trusted users
* Clear separation between technical hardware limits and household strategy settings

Examples:

```text
Hybrid target:
80% → configurable

Away Mode battery range:
95% / 81% → configurable

Away Mode temperature range:
18°C / 23°C → configurable
```

Status:

📋 Planned after EnergyHub 1.0 stabilization

---

# EnergyHub 1.x — Better Prediction and Autonomy

Goal:

Improve the quality of decisions while keeping the system local, explainable and reliable.

Deliverables:

* Remaining solar forecast integration
* House consumption prediction
* Battery reserve prediction
* SOC trend analysis
* Proactive reserve protection
* Improved Grid Confidence weighting
* Better outage preparation
* Advanced historical analysis
* 30-day energy visualization
* Notification policy engine
* Recovery service
* External heartbeat / watchdog
* Direct BMS integration where useful
* Additional flexible-load automation
* Future EV charging logic

Core question:

> Can the house safely survive until the next expected charging opportunity?

Status:

📋 Planned

---

# EnergyHub 2.x — Energy Optimization Platform

Goal:

Optimize the monetary and technical value of home energy across different hardware ecosystems.

## Multi-Vendor Platform

Deliverables:

* Multiple inverter support
* Deye support
* GoodWe support
* Victron support
* Additional inverter vendors
* Additional BMS vendors
* Device capability abstraction
* Multi-inverter architecture

## Economic Optimization

Deliverables:

* Dynamic electricity tariffs
* Energy price forecasting
* Import optimization
* Export optimization
* Net Billing optimization
* Smart export
* Smart charging
* Battery degradation model
* Cost-aware battery reserve management

Decision questions:

> Is it better to consume, store, import or export energy now?

> What action creates the best value without compromising household resilience?

Status:

📋 Future

---

# EnergyHub 3.x — Full Home Energy Management System

Goal:

Coordinate the complete household energy ecosystem.

Deliverables:

* Solar generation
* Weather forecasting
* Dynamic electricity markets
* Battery storage
* EV charging
* Vehicle-to-home / vehicle-to-grid integration where supported
* Heat pumps
* Water heating
* Flexible household loads
* Grid reliability
* Energy trading
* Advanced forecasting
* Whole-home optimization

Vision:

```text
Weather
+
Solar Forecast
+
House Consumption
+
Battery State
+
Grid Reliability
+
Electricity Prices
+
EV Requirements
+
Heating Requirements
        ↓
EnergyHub
        ↓
Explainable Whole-Home Energy Strategy
```

Status:

📋 Long-term vision

---

# Product Principles

EnergyHub should remain:

* Local-first
* Human-centric
* Calm
* Explainable
* Modular
* Hardware-aware
* Progressively automated
* Safe by design
* Resilient to communication failures

Automation progression:

```text
Monitoring
    ↓
Reliable Facts
    ↓
Health Awareness
    ↓
Recommendations
    ↓
Validated Automation
    ↓
Autonomous Home Operation
    ↓
Whole-Home Energy Optimization
```

---

# Success Metric

EnergyHub development is ultimately measured by one question:

> How often does the homeowner need to think about the energy system?

The ideal answer is:

**Almost never.**