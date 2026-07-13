# House Model

## Overview

EnergyHub manages the energy consumption of a three-floor country house.

The objective is to maximize the use of solar energy while maintaining comfort and minimizing electricity costs.

---

# Energy Sources

## Solar PV

- PowMr 10.2M inverter
- LONGi Hi-MO X10 LR7-54HVH-490M panels
- Two PV fields with different tilt angles
- Field 1: 7 × 490 W = 3.43 kWp, tilt 35°
- Field 2: 8 × 490 W = 3.92 kWp, tilt 65°
- Approximate azimuth: 130°
- PI30MAX currently exposes reliable PV1 telemetry only
- Solcast provides forecast data for both PV fields

## Battery

- LiFePO4
- 16 kWh
- Primary energy buffer

## Grid

- Utility power
- May become unavailable
- Night tariff available
- Grid Availability is monitored historically
- Grid Confidence is derived from recent availability
- Grid Import is estimated by EnergyHub because the inverter does not expose a reliable import counter

---

# Building

## Basement

### Equipment

- Water system
- Boiler

---

## Floor 1

### Climate

- Heat pump
- Temperature sensor

### Occupancy

- Motion sensor

---

## Floor 2

### Climate

- Heat pump
- Temperature sensors

### Rooms

- Kids room
- Toilet

---

## Floor 3

### Climate

- Heat pump
- Temperature sensor

---

# Outside

## Weather

- Outdoor temperature
- Solar forecast
- Sunrise
- Sunset

---

# Flexible Loads

## Heat Pumps

Each floor has an independently controlled air-to-air heat pump.

Current EnergyHub automation uses the first-floor heat pump during Away Mode to convert available solar energy into useful thermal energy.

EnergyHub tracks automation ownership so that it stops a load only when EnergyHub previously started it.

## Boiler

- 40 L electric water heater
- Approximate energy requirement from 10°C to 70°C: 3 kWh
- Future candidate for flexible-load optimization

---

# Future

## Electric Vehicle

Status:
Planned

Charging priority:
Solar surplus

---

# Operating Strategies

Solar

Hybrid Charging

Hybrid Grid Hold

Panic

Away

---

# Decision Inputs

Battery SOC

PV production

Grid availability

Grid confidence

Weather forecast

Outdoor temperature

Indoor temperatures

Occupancy

Time

Electricity tariff

Manual override

1st floor
Temperature: sensor.miaomiaoce_t2_e515_temperature
Humidity: sensor.miaomiaoce_t2_e515_relative_humidity
Heat pump plug: switch.lumi_v1_64d7_switch

2nd floor
Temperature: sensor.miaomiaoce_t2_1bf2_temperature
Humidity: sensor.miaomiaoce_t2_1bf2_relative_humidity
Heat pump plug: pending Tuya

3rd floor
Temperature: sensor.lumi_weather_v1_b318_temperature
Humidity: sensor.lumi_weather_v1_b318_relative_humidity
Heat pump plug: switch.chuangmi_212a01_ea40_switch
Power: sensor.chuangmi_212a01_ea40_electric_power

---

# EnergyHub View of the House

EnergyHub should reason about the house as an energy system rather than as a collection of individual devices.

```text
Solar Generation
        ↓
     Inverter
        ↕
Battery Storage
        ↕
   House Loads
        ↕
       Grid
```

Flexible household loads include:

```text
Floor 1 Heat Pump
Floor 2 Heat Pump
Floor 3 Heat Pump
Water Heating
Future EV Charging
```

---

# Current Strategy Model

## Solar

Default strategy.

```text
Setting 01 → SBU
Setting 16 → OSO
```

The house prioritizes solar and battery energy according to inverter behavior.

## Hybrid Charging

Planned night-grid charging.

```text
Setting 01 → SUB
Setting 16 → SNU
Target SOC → 80%
```

## Hybrid Grid Hold

After the Hybrid charging target is reached:

```text
Setting 01 → SUB
Setting 16 → OSO
```

The house remains on cheap night grid power while preserving battery reserve until 07:00.

## Panic

Protective daytime charging when EnergyHub detects increased energy risk.

Current targets depend on Grid Confidence and Battery SOC.

## Away

Allows autonomous control of flexible household loads while the house is unoccupied.

Current v1 implementation controls the first-floor heat pump.

---

# Current Away Mode Model

Start first-floor heating when:

```text
Away Mode ON
Temperature < 18°C
SOC > 95%
PV > 200 W
```

Stop when:

```text
Temperature >= 23°C
OR
SOC <= 81%
```

After EnergyHub starts the heat pump, temporary PV fluctuations are ignored.

Ownership helper:

```text
input_boolean.energyhub_away_heat_pump_active
```

EnergyHub may automatically stop the heat pump only when EnergyHub previously started it.

---

# Energy Measurements

Current measured or derived values include:

- Battery SOC;
- Battery Voltage;
- Battery Charging Current;
- Battery Discharging Current;
- House Load;
- PV1 Power;
- Grid Voltage;
- Grid Availability;
- Grid Confidence;
- Solar Forecast;
- Daily House Consumption;
- Daily Solar Surplus Estimated;
- Grid Import Power Estimated;
- Daily Grid Import Estimated.

Grid Import is estimated and is not billing-grade.

---

# Physical and Strategy Parameters

The house model distinguishes between technical limits and strategy settings.

## Technical Limits

Examples:

- battery manufacturer current limits;
- inverter-supported current;
- battery capacity;
- inverter protocol capabilities.

## Strategy Parameters

Examples:

- Hybrid target SOC;
- Panic target SOC;
- Away Mode SOC thresholds;
- Away Mode temperature thresholds;
- Away Mode PV threshold.

Future EnergyHub versions should allow trusted strategy parameters to be configured without confusing them with hardware safety limits.

---

# Model Principle

The physical house changes slowly.

Energy strategies evolve more quickly.

Therefore:

```text
House Model
=
Physical Assets
+
Sensors
+
Controllable Loads
+
Energy Sources
+
Capabilities
```

while:

```text
Decision Policy
=
Rules for using those capabilities
```

The House Model should describe what exists.

Decision services should decide what EnergyHub does with it.