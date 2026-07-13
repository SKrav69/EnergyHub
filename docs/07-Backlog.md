# EnergyHub Backlog

> The Backlog contains future work. Completed implementation belongs in Project State and Project History.

---

# High Priority

## Recovery Strategy Implementation

Status:

Design complete. Implementation is the next major development milestone.

Goals:

- define recovery responsibilities for each EnergyHub service;
- investigate MQTT connection failures;
- investigate network failures;
- investigate serial communication failures;
- investigate `mpp-solar` timeouts and blocking;
- investigate Home Assistant connectivity failures;
- implement limited automatic recovery where safe;
- keep automatic recovery bounded and verifiable;
- stop automatic recovery after repeated failure;
- add recovery notifications;
- investigate external heartbeat/watchdog monitoring for cases where Home Assistant or EnergyHub is completely unavailable.

Confirmed constraints:

```text
EnergyHub must never automatically restart the inverter.

Detection and recovery are separate responsibilities.

Automatic recovery must be bounded.

Infinite retry loops are prohibited.
```

Detailed architecture:

```text
13-Recovery-Strategy.md
```

---

## Grid Import Real-System Validation

Status:

Implementation complete. Real-system validation required.

Goals:

- test Grid Import Power Estimated in Solar;
- verify Solar-mode noise suppression;
- test Grid Import Power Estimated during Hybrid Charging;
- test Grid Import Power Estimated during Hybrid Grid Hold;
- test Grid Import Power Estimated during Panic;
- verify daily energy integration;
- verify persistence across EnergyHub restart;
- verify daily reset behavior;
- compare estimates with observed inverter and household behavior;
- correct formulas only when real-system observations justify changes.

Current entities:

```text
sensor.energyhub_grid_import_power_estimated
sensor.energyhub_daily_grid_import_estimated
```

Daily Grid Import remains informational and not billing-grade.

---

## Hybrid Strategy Validation

Status:

Hybrid Decision and execution v1 implemented. Real-world validation required.

Goals:

- test daily Hybrid evaluation;
- verify Solar decision when forecast is sufficient;
- verify Hybrid decision when forecast is insufficient;
- verify Hybrid Charging entry;
- verify target SOC behavior;
- verify transition from Hybrid Charging to Hybrid Grid Hold;
- verify morning return to Solar;
- verify behavior when the add-on restarts during Hybrid;
- verify notification behavior;
- inspect edge cases around missing or stale decision inputs.

---

## Restart Strategy Reconstruction

Status:

High priority.

Goal:

Recover the real EnergyHub strategy after restart from verified inverter settings rather than time alone.

Initial mapping:

```text
SBU + OSO
→ Solar

SUB + SNU
→ Hybrid Charging

SUB + OSO
→ Hybrid Grid Hold
```

Future work:

- verify Setting 01 and Setting 16 after startup;
- reconstruct Operating Mode;
- avoid unnecessary inverter commands;
- handle inconsistent or unknown combinations safely;
- determine how to distinguish strategies that may use identical inverter settings;
- integrate reconstruction with Recovery Strategy responsibilities.

---

## Proactive Battery Reserve Protection

Status:

Research and Decision Engine development required.

Problem:

A battery charged during the night may still be depleted before the next safe charging opportunity.

Core question:

```text
Can the house safely survive until the next expected charging opportunity?
```

Possible inputs:

- current Battery SOC;
- SOC trend;
- remaining solar production;
- expected House Consumption;
- Grid Confidence;
- current Operating Mode;
- time until the next charging opportunity.

Goals:

- estimate whether current battery reserve is sufficient;
- estimate remaining solar production for the current day;
- estimate expected House Consumption;
- consider current SOC trend;
- consider Grid Confidence;
- define safe reserve thresholds;
- improve daytime Panic triggers;
- avoid unnecessary daytime Grid Import when energy risk is low.

---

## EnergyHub 1.1 Configurable Strategy Parameters

Status:

Planned.

Goal:

Move trusted strategy parameters from hard-coded values into safely validated configuration.

Candidates:

- Hybrid evaluation time;
- Hybrid target SOC;
- Hybrid morning exit time;
- Panic PV threshold;
- Panic forecast margin;
- Panic SOC thresholds;
- Panic target SOC values;
- Away Mode SOC thresholds;
- Away Mode temperature thresholds;
- Away Mode PV threshold;
- Battery Health technical thresholds.

Requirements:

- safe bounds;
- validated values;
- clear defaults;
- separation between hardware limits and household strategy preferences.

---

# Medium Priority

## Away Mode Development

Status:

Away Mode v1 implemented.

Current behavior:

- controls the first-floor heat pump;
- uses SOC, PV, and temperature conditions;
- preserves automation ownership through a helper.

Future work:

- validate behavior over longer real-world use;
- improve notification and explanation quality;
- consider additional flexible loads;
- consider occupancy and expected arrival information;
- decide which future Away logic belongs in Home Assistant and which belongs in EnergyHub services.

---

## Battery Health Improvements

Status:

v1 implemented.

Future work:

- preserve better diagnostic information for anomaly events;
- add useful Battery Health notifications;
- investigate additional generic anomaly detection rules if real-system behavior justifies them;
- add safely configurable technical thresholds if required;
- evaluate additional JK BMS data when integration architecture is ready.

Possible future inputs:

- individual cell voltages;
- minimum and maximum cell voltage;
- cell delta;
- battery temperatures;
- BMS alarms;
- protection states;
- balancing status.

---

## Telemetry Freshness Improvements

Status:

v1 implemented.

Future work:

- validate House Load unchanged detection against long-term behavior;
- investigate false warnings if they occur;
- consider additional telemetry verification methods;
- consider command verification using supported inverter commands where useful.

---

## Inverter Health Improvements

Status:

v1 implemented.

Future work:

- investigate persistent `eeprom_fault`;
- determine whether it represents an active fault, historical/sticky state, firmware behavior, or protocol interpretation issue;
- classify inverter warnings and faults by severity;
- add notifications for significant warnings and faults;
- determine how known persistent warnings should affect System Health.

---

## System Health Improvements

Status:

v1 implemented.

Future work:

- improve severity classification;
- add notification policies;
- improve Developer Dashboard presentation;
- determine how persistent known warnings should affect long-term System Health;
- consider using System Health as a safety prerequisite for selected automatic decisions.

---

## Flexible Load Strategy

Status:

Early development.

Current implementation:

```text
Away Mode
→ First-Floor Heat Pump
```

Future goals:

- define generic flexible-load intentions;
- add boiler strategy;
- add additional heat-pump strategy;
- prepare for EV charging;
- preserve user ownership and manual control;
- use surplus energy without compromising battery reserve or comfort.

Possible future intentions:

```text
Heat Now
Heat Later
Heat Only from Surplus
Allow Water Heating
Prioritize EV Charging
Preserve Battery Reserve
```

---

## Daily Summary Improvements

Status:

v1 implemented.

Future work:

- add 30-day visualization if useful;
- improve historical analysis;
- evaluate forecast accuracy;
- compare forecast, consumption, Grid Import, and battery behavior;
- add new daily facts only when they are useful for decisions or analysis.

---

## Dashboard and Naming Polish

Status:

Deferred until behavior is stable.

Goals:

- expose useful Hybrid decision information and reasons;
- expose required energy and battery refill requirement if useful;
- remove duplicate Autopilot helper;
- align dashboard titles and entity names;
- reduce duplicate information;
- improve family-friendly labels;
- improve health presentation;
- polish charts after functional testing;
- separate developer diagnostics from family-facing information.

---

## Notification Improvements

Status:

Initial event flow implemented.

Goals:

- improve message consistency;
- define which events require notifications;
- avoid notifications for routine telemetry and expected no-action decisions;
- include decision reason, target, and next action where useful;
- add Telegram delivery if useful;
- consider escalation for repeated recovery failure or critical health conditions.

---

# Low Priority

## Additional Hardware Support

Potential future platforms:

- Deye;
- Victron;
- Growatt;
- LuxPower.

Rule:

Do not build speculative abstractions before real hardware requirements exist.

---

## Infrastructure

Goals:

- remote Home Assistant access;
- secure VPN access;
- automatic backups;
- OTA update strategy;
- external EnergyHub/Home Assistant heartbeat monitoring;
- external failure notifications when Home Assistant cannot report its own failure.

---

# Research

Technical questions and ideas requiring investigation:

- persistent PowMr `eeprom_fault`;
- reliable identification of current physical load source where required;
- improved battery reserve prediction;
- remaining daily solar production estimation;
- House Consumption prediction;
- forecast uncertainty;
- multi-day forecast use;
- external Home Assistant watchdog;
- dynamic electricity pricing;
- automatic anomaly detection;
- AI-assisted energy optimization;
- machine-learning consumption prediction.

Research items should move into implementation sections only when they solve a real EnergyHub problem.

---

# Documentation Maintenance

Goals:

- keep `PROJECT_STATE.md` as the primary current-state entry point;
- keep `PROJECT_HISTORY.md` focused on completed development history;
- keep this Backlog focused on unfinished work;
- record significant architectural decisions in `09-Decision-Log.md`;
- record real-system findings;
- distinguish confirmed behavior from hypotheses;
- remove completed items from the Backlog.

---

# Backlog Rule

The Backlog answers:

```text
What should we still do?
```

It should not answer:

```text
What have we already built?
```

Completed work belongs in Project State and Project History.

Ideas remain in the Backlog only while they are still relevant to the current direction of EnergyHub.