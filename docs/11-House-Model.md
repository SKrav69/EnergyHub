# EnergyHub House Model

## Overview

The current EnergyHub installation manages a three-floor country house. The model separates physical assets and capabilities from decision policy.

```text
House Model = assets + sensors + controllable loads + capabilities
Decision Policy = rules for using those capabilities
```

## Energy assets

### Solar PV

- LONGi Hi-MO X10 LR7-54HVH-490M panels;
- Field 1: 7 × 490 W = 3.43 kWp, tilt 35°;
- Field 2: 8 × 490 W = 3.92 kWp, tilt 65°;
- approximate azimuth: 130°;
- modeled total of the two documented fields: 7.35 kWp;
- PI30MAX exposes reliable PV1 telemetry only;
- Solcast supplies whole-system Today and Tomorrow forecasts.

### Inverter

- PowMr 10.2M;
- PI30MAX;
- USB-RS232;
- Menu 01 and Menu 16 strategy control.

### Battery

- LiFePO4;
- 16 kWh nominal capacity;
- primary reserve and time-shifting buffer.

### Grid

- utility connection;
- cheap night tariff;
- voltage stabilizer before the inverter;
- inverter normally sees approximately 220 V when the grid exists and 0 V when absent;
- planned and unexpected outages are possible;
- historical availability contributes to Grid Confidence.

## Building and comfort

### Basement

- inverter and energy equipment;
- water system;
- 40 L electric boiler;
- boiler heating from approximately 10°C to 70°C requires roughly 3 kWh and is a future flexible-load candidate.

### 1st Floor

| Capability | Entity |
|---|---|
| Temperature | `sensor.miaomiaoce_t2_e515_temperature` |
| Humidity | `sensor.miaomiaoce_t2_e515_relative_humidity` |
| Heat-pump plug | `switch.lumi_v1_64d7_switch` |
| Heat-pump power | `sensor.lumi_v1_64d7_electric_power` |

### 2nd Floor · Kids Room

| Capability | Entity |
|---|---|
| Temperature | `sensor.miaomiaoce_t2_1bf2_temperature` |
| Humidity | `sensor.miaomiaoce_t2_1bf2_relative_humidity` |
| Heat-pump plug | planned hardware |

The dashboard will add manual control after a compatible smart plug is installed.

### 3rd Floor

| Capability | Entity |
|---|---|
| Temperature | `sensor.lumi_weather_v1_b318_temperature` |
| Humidity | `sensor.lumi_weather_v1_b318_relative_humidity` |
| Heat-pump plug | `switch.chuangmi_212a01_ea40_switch` |
| Heat-pump power | `sensor.chuangmi_212a01_ea40_electric_power` |
| Auto-off duration | `input_number.input_number_floor3_heat_pump_timer_hours` |
| Remaining time | `timer.floor_3_heat_pump_auto_off` |

Duration `0 h` means manual mode: cancel the countdown but leave the heat pump in its current state. When a non-zero duration expires, HA switches the plug off and resets the duration to zero.

## Current EnergyHub-controlled capability

In 1.0 EnergyHub directly controls only inverter strategy. Heat-pump controls shown on the dashboard are Home Assistant household controls, not EnergyHub automatic strategy outputs.

## Current strategies

### Solar

```text
Menu 01 = SBU
Menu 16 = OSO
```

### Hybrid Charging

```text
Menu 01 = SUB
Menu 16 = SNU
Target SOC = 80%
```

### Hybrid Grid Hold

```text
Menu 01 = SUB
Menu 16 = OSO
Exit = 07:00 Solar request
```

### Panic

```text
Menu 01 = SUB
Menu 16 = SNU
Target SOC = 80% or 95%
```

## Removed experimental capability

The old Away Mode first-floor heat-pump automation and helpers are not part of 1.0. They were removed because energy-to-comfort optimization should not depend on occupancy.

## Future Smart Thermal Energy

Smart Thermal will model thermal loads as capabilities:

- controllable plug;
- measured or expected power;
- room temperature/humidity;
- heating/cooling role;
- comfort band;
- minimum runtime and cooldown;
- ownership state;
- load priority.

It may use:

- surplus solar;
- cheap night electricity;
- battery reserve;
- forecast;
- Grid Confidence;
- seasonal comfort goals.

## Flexible-load candidates

- 1st-floor heat pump;
- future 2nd-floor heat pump plug;
- 3rd-floor heat pump;
- electric boiler;
- future EV charger.

## Measurements

### Measured

- grid voltage/frequency;
- output power/load;
- battery SOC/voltage/current;
- PV1 power/voltage/current;
- inverter temperature;
- floor temperatures/humidity;
- selected smart-plug power.

### Derived

- grid availability and history;
- Grid Confidence;
- Daily Summary;
- estimated solar surplus;
- estimated Grid Import;
- health states;
- operating strategy and decision reason.

## Model principle

Physical assets change slowly. Policies change more quickly. Device entities should be mapped into stable capabilities, while strategy rules remain replaceable and configurable.
