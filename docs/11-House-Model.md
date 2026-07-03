# House Model

## Overview

EnergyHub manages the energy consumption of a three-floor country house.

The objective is to maximize the use of solar energy while maintaining comfort and minimizing electricity costs.

---

# Energy Sources

## Solar PV

- PowMr 10.2M inverter
- 9.9 kWp PV array
- Two roof orientations
- Battery charging priority

## Battery

- LiFePO4
- 16 kWh
- Primary energy buffer

## Grid

- Utility power
- May become unavailable
- Night tariff available

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

# Future

## Electric Vehicle

Status:
Planned

Charging priority:
Solar surplus

---

# Operating Modes

Summer

Winter

Away

Panic

Manual

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