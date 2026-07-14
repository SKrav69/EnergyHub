# EnergyHub

> **The Operating System for Autonomous Homes**

EnergyHub is an open-source home energy management project designed to
make a solar-powered home operate autonomously, efficiently, and
predictably.

The homeowner defines the strategy.

EnergyHub monitors the house, battery, solar forecast, and grid
reliability, explains its decisions, and automatically selects the
appropriate operating mode.

> **We optimize for people, not for kilowatt-hours.**

------------------------------------------------------------------------

# EnergyHub 1.0 --- Autonomous Home

EnergyHub 1.0 is the first functional project milestone.

The goal is simple:

> Build a house that can manage its energy automatically, minimize
> unnecessary grid dependence, use cheap electricity when useful, and
> remain understandable to the homeowner.

EnergyHub 1.0 currently runs with:

-   PowMr 10.2M inverter
-   16 kWh LiFePO₄ battery
-   solar generation
-   Home Assistant
-   MQTT
-   Solcast solar forecasting
-   Raspberry Pi 4

The current implementation is hardware-specific, but the architecture is
designed to evolve toward a vendor-independent Home Energy Management
System.

------------------------------------------------------------------------

# Core Operating Strategies

## Solar

The default operating strategy.

``` text
Menu 01 = SBU
Menu 16 = OSO
```

The house prioritizes solar and battery energy while using the grid as
backup.

## Hybrid

Evaluated every night before the cheap electricity tariff period.

EnergyHub compares:

``` text
Solar Forecast Tomorrow

against

Expected House Consumption
+
Energy Required to Refill the Battery
```

If tomorrow's solar forecast is insufficient, EnergyHub activates Hybrid
charging.

``` text
Menu 01 = SUB
Menu 16 = SNU
```

The battery charges from the grid to the Hybrid target.

After reaching the target, EnergyHub enters Grid Hold:

``` text
Menu 01 = SUB
Menu 16 = OSO
```

The battery is preserved while the house continues using the cheap night
tariff.

At the end of the tariff period, EnergyHub returns to Solar.

## Panic

Panic is the daytime emergency charging strategy.

EnergyHub evaluates current conditions and may activate Panic when grid
reliability is degraded and battery SOC becomes unsafe.

The decision process is intentionally explainable:

``` text
Evaluation Window
→ Grid Confidence
→ Battery SOC
→ Solar Forecast vs Expected Consumption
→ Panic Decision
```

Panic charges the battery from the grid to a target selected according
to the severity of the grid situation.

After reaching the target, EnergyHub automatically returns to Solar.

------------------------------------------------------------------------

# Decision Engine

EnergyHub does not simply execute fixed schedules.

It evaluates the state of the house and makes decisions using:

-   battery SOC
-   solar forecast
-   previous house consumption
-   grid availability history
-   grid confidence
-   current operating strategy
-   time windows

Every important automatic decision publishes both:

``` text
Decision
+
Decision Reason
```

The Home Assistant Decision Logic dashboard shows the inputs and
reasoning behind Hybrid and Panic decisions.

------------------------------------------------------------------------

# Grid Reliability

EnergyHub records grid availability and calculates Grid Confidence from
recent outage history.

The system currently classifies grid conditions as:

-   Normal
-   Unstable
-   Risk
-   Panic

Recent grid behavior has greater operational importance than older
history.

Grid Confidence is used by the Panic Decision Engine.

------------------------------------------------------------------------

# Grid Import Accounting

The inverter does not provide reliable grid import energy counters.

EnergyHub therefore calculates estimated grid import while operating in
SUB-based strategies.

The model accounts for:

``` text
House Energy Supplied During SUB
+
Positive Battery SOC Change × Battery Capacity
```

Accounting starts when Hybrid or Panic begins using SUB and stops after
EnergyHub returns to Solar/SBU.

The result is published to Home Assistant for live monitoring and daily
history.

------------------------------------------------------------------------

# Health Monitoring

EnergyHub includes multiple health-monitoring layers.

## Communication Health

Monitors successful communication with the inverter.

## Battery Health

Detects:

-   critically low SOC
-   suspicious SOC jumps

## Telemetry Freshness

Detects missing or stale inverter telemetry.

## Inverter Health

Reads inverter warning and fault information.

## System Health

Aggregates subsystem health into a high-level EnergyHub status.

------------------------------------------------------------------------

# Home Assistant Integration

EnergyHub integrates with Home Assistant through MQTT.

The integration provides:

-   MQTT Discovery
-   live inverter telemetry
-   operating strategy
-   inverter settings
-   Grid Confidence
-   Grid Availability
-   Hybrid Decision
-   Panic Decision
-   Decision Reasons
-   health sensors
-   Grid Import accounting
-   Daily Summary data
-   Autopilot control
-   notifications
-   dashboards and charts

Home Assistant configuration used by EnergyHub is synchronized into the
repository for version control.

------------------------------------------------------------------------

# Autopilot

Autopilot enables automatic EnergyHub strategy management.

When enabled, EnergyHub can automatically:

-   evaluate Hybrid
-   activate Hybrid charging
-   enter Grid Hold
-   restore Solar
-   evaluate Panic
-   activate Panic charging
-   return safely to Solar

When Autopilot is disabled during an active or unknown strategy,
EnergyHub performs a final safe Solar recovery.

------------------------------------------------------------------------

# Explainable Automation

EnergyHub follows a core design principle:

> The system should always explain why it made a decision.

Examples:

``` text
Forecast 39.21 kWh >= required 11.13 kWh
(consumption 10.65 kWh + battery refill 0.48 kWh);
remain in Solar
```

``` text
Grid confidence=normal;
automatic Panic is not required
```

The goal is not only automation.

The goal is automation that the homeowner can understand and trust.

------------------------------------------------------------------------

# Development Workflow

EnergyHub uses two synchronized development workflows.

## Add-on Code

``` text
Edit in VS Code
→ Deploy to Home Assistant
→ Rebuild and Restart
→ Test
→ Review in GitHub Desktop
→ Commit
→ Push
```

## Home Assistant Configuration

``` text
Edit in Home Assistant
→ Run sync-from-ha.ps1
→ Review in GitHub Desktop
→ Commit
→ Push
```

This keeps application code, automations, scripts, dashboards, and
selected Home Assistant configuration under version control.

------------------------------------------------------------------------

# Project Structure

``` text
EnergyHub/
├── addon/
│   └── app/
│       ├── inverter/
│       ├── models/
│       ├── mqtt/
│       ├── services/
│       └── main.py
│
├── docs/
│
├── homeassistant/
│   └── live/
│
├── tools/
│   └── dev/
│
├── CHANGELOG.md
└── README.md
```

------------------------------------------------------------------------

# Roadmap

## EnergyHub 1.0 --- Autonomous Home

Current milestone.

Focus:

-   autonomous energy management
-   Solar / Hybrid / Panic strategies
-   battery management
-   grid reliability
-   solar forecasting
-   explainable decisions
-   health monitoring
-   Home Assistant integration
-   Grid Import accounting

## EnergyHub 1.1 --- Smart Loads & Test-Drive Improvements

Planned after the initial EnergyHub 1.0 test-drive period.

Focus:

-   bug fixes
-   dashboard improvements
-   chart cleanup
-   smart-load development
-   rethink Away strategy
-   intelligent heat-pump use
-   EV charging template
-   cosmetic and usability improvements

## EnergyHub 1.2 --- Configurable EnergyHub

Focus:

-   configurable cheap-tariff window
-   configurable Panic evaluation window
-   battery capacity
-   grid charging current
-   Hybrid SOC target
-   configurable Panic profiles
-   safe user-adjustable Decision Engine parameters

## EnergyHub 1.3 --- Recovery & Resilience

Focus:

-   MQTT recovery
-   network recovery
-   serial communication recovery
-   inverter communication recovery
-   `mpp-solar` timeout handling
-   Home Assistant connectivity recovery
-   bounded retries
-   safe-state reconstruction
-   external watchdog strategy

## EnergyHub 2.x --- Energy Optimization

Focus:

-   multiple inverter support
-   Deye / GoodWe / Victron / other platforms
-   dynamic tariffs
-   energy price forecasting
-   import optimization
-   export optimization
-   net billing
-   battery degradation models

## EnergyHub 3.x --- Full Home Energy Management System

Long-term direction:

-   solar forecasting
-   weather intelligence
-   dynamic electricity markets
-   EV charging
-   heat pumps
-   battery storage
-   grid reliability
-   energy trading

------------------------------------------------------------------------

# Key Principles

-   Human-Centric Design
-   Comfort Before Savings
-   Progressive Automation
-   Explainable Decisions
-   Local First
-   Vendor Independence
-   Calm Technology

------------------------------------------------------------------------

# Vision

People should not manage their home.

Their home should manage itself.