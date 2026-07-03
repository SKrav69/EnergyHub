# Home Assistant Configuration

This document describes Home Assistant objects created specifically for EnergyHub.

---

# Helpers

## Daily Energy Balance

Entity:

input_number.energyhub_daily_energy_balance

Purpose:

Stores the daily solar energy balance.

Updated:

23:50 every day by automation:

EnergyHub - Daily Energy Balance Snapshot

Formula:

Energy Balance = Forecast Today - House Consumption Today

---

## Floor 3 Heat Pump Auto-Off

Entity:

input_number.input_number_floor3_heat_pump_timer_hours

Purpose:

Number of hours before automatic switch-off.

Values:

0 = Manual

1..9 = Auto-Off after N hours

---

## Floor 3 Countdown Timer

Entity:

timer.floor_3_heat_pump_auto_off

Purpose:

Displays remaining time until automatic switch-off.

---

# Automations

## Daily Energy Balance Snapshot

Runs every day at 23:50.

Stores Daily Energy Balance.

---

## Floor 3 Heat Pump Auto-Off

Responsibilities:

- Starts countdown timer.
- Restarts timer when duration changes.
- Cancels timer when heat pump is switched off.
- Switches heat pump off when timer finishes.
- Resets Auto-Off helper to 0.