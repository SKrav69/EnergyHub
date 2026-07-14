# EnergyHub Roadmap

> Build the foundation first. Add intelligence second. Scale third.

---

# EnergyHub 1.0 — Autonomous Home

Goal:

Create a reliable local-first energy system that monitors the house, understands current conditions, makes explainable decisions, and safely controls the real inverter.

Status:

✅ Feature development complete  
🧪 Test-drive and cleanup phase

## Delivered

* PowMr PI30MAX integration
* MQTT communication and MQTT Discovery
* Real-time inverter telemetry
* Setting 01 and Setting 16 control
* Verified Solar, Hybrid Charging, Hybrid Grid Hold and Panic transitions
* Autopilot
* Hybrid Decision Engine
* Panic Decision Engine
* Explainable decision reasons
* Grid monitoring and Grid History
* 24-hour and 48-hour Grid Availability
* Grid Confidence
* Communication, Battery, Telemetry, Inverter and System Health monitoring
* Daily Summary Engine
* Estimated Grid Import accounting
* Automatic Hybrid and Panic notifications
* Home Assistant dashboards and controls
* Home Assistant configuration synchronization to Git
* Deployment workflow from Git to Home Assistant

## Final 1.0 Cleanup

* Full post-implementation code review
* Clean entity IDs such as `*_2`
* Remove obsolete retained MQTT Discovery entities
* Verify Grid Import midnight rollover with real data
* Resolve temporary Grid Import history presentation issues
* Review and standardize charts and dashboards
* Make dashboards more compact and context-aware
* Fix bugs discovered during Autopilot test driving
* Keep documentation aligned with implementation

Success criterion:

> The house operates safely and economically with minimal homeowner intervention, while every important automated decision remains understandable.

---

# EnergyHub 1.1 — Smart Loads & Test-Drive Improvements

Goal:

Use the first weeks of real autonomous operation to improve EnergyHub and begin intelligent control of flexible household loads.

Planned after approximately 2–3 weeks of Autopilot operation.

## Test-Drive Improvements

* Fix bugs discovered during real operation
* Improve logs and naming
* Cosmetic improvements
* Dashboard and chart improvements
* Reduce unnecessary information and duplication
* Improve family-oriented presentation

## Smart Heating

Reconsider the original Away Mode concept.

Heating should not depend only on whether the house is occupied.

Future logic should consider:

* occupancy and comfort;
* available solar surplus;
* battery reserve;
* cheap night tariff;
* expected future energy availability.

Possible behavior:

```text
At Home
→ comfort has priority
→ use surplus solar for additional heating
→ optionally use cheap night tariff

Away
→ maintain safe / useful house temperature
→ consume otherwise unused solar generation
→ preserve required battery reserve
```

The goal is a general Smart Heating strategy rather than a simple Away Mode.

## EV Charging Template

Create a reusable EV charging strategy template.

Future decisions may consider:

* available solar surplus;
* battery SOC;
* house priorities;
* cheap tariff periods;
* required vehicle energy;
* required departure time.

Status:

📋 Planned

---

# EnergyHub 1.2 — Configurable EnergyHub

Goal:

Make household strategy variables adjustable without editing Python code or Home Assistant YAML.

## Configurable Strategy Parameters

Examples:

* cheap electricity tariff start time;
* cheap electricity tariff end time;
* Panic evaluation window;
* nominal battery capacity;
* grid charging current;
* Hybrid target SOC;
* Panic SOC thresholds;
* Panic charging targets;
* other safe Decision Engine variables.

Example:

```text
Cheap tariff:
23:00–07:00
→ configurable
```

```text
Battery capacity:
16 kWh
→ configurable
```

```text
Grid charging current:
30 A
→ configurable within safe limits
```

## Panic Profiles

Possible selectable strategies:

```text
Conservative
SOC below 80%
→ charge to 95%
```

```text
Relaxed
SOC below 50%
→ charge to 80%
```

## Configuration Dashboard

Provide a trusted-user dashboard for strategy configuration.

Requirements:

* safe parameter bounds;
* clear descriptions;
* separation between hardware limits and household strategy;
* no need to edit source code;
* no need to edit YAML.

Status:

📋 Planned after 1.1

---

# EnergyHub 1.3 — Recovery & Resilience

Goal:

Make EnergyHub recover safely and predictably from real system failures.

## Recovery Strategy

Investigate and define recovery for:

* MQTT connection failures;
* network failures;
* serial communication failures;
* `mpp-solar` timeouts and blocking;
* Home Assistant connectivity failures;
* inverter communication failures;
* EnergyHub service failures.

For each subsystem define:

* what failure means;
* how failure is detected;
* which service owns recovery;
* when automatic retry is safe;
* retry limits and backoff;
* when EnergyHub should only report the problem;
* when a safe operating state should be restored.

## State Reconstruction

Improve restart recovery by reconstructing strategy from verified inverter settings.

Examples:

```text
SBU + OSO
→ Solar

SUB + OSO
→ Hybrid Grid Hold

SUB + SNU
→ active grid-charging strategy requiring context reconstruction
```

## External Watchdog

Investigate an external heartbeat / watchdog capable of detecting when EnergyHub itself is no longer functioning.

EnergyHub must never automatically restart the inverter.

Status:

📋 Planned after configurable strategy work

---

# EnergyHub 2.x — Energy Optimization Platform

Goal:

Optimize the monetary and technical value of home energy across different hardware ecosystems.

## Multi-Vendor Platform

* Multiple inverter support
* Deye
* GoodWe
* Victron
* Additional inverter and BMS vendors
* Device capability abstraction
* Multi-inverter architecture

## Economic Optimization

* Dynamic electricity tariffs
* Energy price forecasting
* Import optimization
* Export optimization
* Net Billing optimization
* Smart export
* Smart charging
* Battery degradation models
* Cost-aware battery reserve management

Core question:

> Is it better to consume, store, import or export energy now?

Status:

📋 Future

---

# EnergyHub 3.x — Full Home Energy Management System

Goal:

Coordinate the complete household energy ecosystem.

Future scope:

* solar generation;
* weather forecasting;
* dynamic electricity markets;
* battery storage;
* EV charging;
* vehicle-to-home / vehicle-to-grid where supported;
* heat pumps;
* water heating;
* flexible household loads;
* grid reliability;
* energy trading;
* advanced forecasting;
* whole-home optimization.

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
Explainable Decisions
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