# EnergyHub Backlog

> The Backlog contains unfinished work. Completed implementation belongs in Project State and Project History.

---

# Immediate — EnergyHub 1.0 Test Drive & Cleanup

## Full Code Review

Status:

Planned for the next session.

Goals:

- review all EnergyHub 1.0 application code after the implementation sprint;
- identify duplicated, obsolete, or overly complex logic;
- verify service responsibilities and boundaries;
- review logging quality and consistency;
- verify startup and shutdown behavior;
- review MQTT topics and retained-state behavior;
- correct issues discovered during review without adding unnecessary new features.

---

## Entity Naming Cleanup

Status:

Known issue.

Goals:

- resolve entity IDs such as `sensor.energyhub_daily_grid_import_estimated_2`;
- identify the retained MQTT Discovery configuration that created duplicate entities;
- define the final Grid Import entity names;
- remove obsolete entities safely;
- update dashboards and documentation after cleanup.

---

## Obsolete MQTT Discovery Cleanup

Status:

Planned.

Goals:

- identify obsolete retained MQTT Discovery entities;
- remove stale discovery configuration topics;
- confirm that only current EnergyHub entities remain;
- avoid accidental loss of valid entity history where possible.

---

## Grid Import Real-System Validation

Status:

Implementation complete. Real-system validation and presentation cleanup required.

Goals:

- verify Grid Import accounting during Hybrid Charging;
- verify accounting during Hybrid Grid Hold;
- verify accounting during Panic;
- verify accounting stops after return to Solar;
- verify persistence across EnergyHub restart;
- verify midnight rollover;
- verify yesterday finalization;
- verify Daily Summary history;
- verify chart continuity;
- resolve the temporary `0 today / historical previous value` presentation;
- compare estimates with observed household behavior.

Current calculation:

```text
Grid Import
=
House Energy Supplied During SUB
+
Positive Battery SOC Gain × Battery Capacity
```

Grid Import remains informational and not billing-grade.

---

## Dashboard and Chart Redesign

Status:

Functional dashboards exist. Full visual review planned.

Goals:

- review every EnergyHub dashboard and chart;
- standardize visual style;
- improve naming;
- reduce duplicated information;
- make layouts more compact;
- make dashboards context-aware where useful;
- emphasize important current states and decisions;
- improve icons and visual hierarchy;
- improve chart labels and date presentation;
- clearly separate family-facing information from developer diagnostics.

The goal is not merely prettier dashboards.

The goal is dashboards that show the right information at the right time.

---

## Autopilot Test Drive

Status:

Active.

Goals:

- run EnergyHub under real household conditions for approximately 2–3 weeks;
- validate nightly Hybrid decisions;
- validate Hybrid Charging and Grid Hold;
- validate morning Solar restoration;
- validate automatic Panic decisions;
- validate notification behavior;
- inspect restart behavior;
- collect bugs and unexpected edge cases;
- avoid speculative changes unless real operation justifies them.

---

## Restart Strategy Reconstruction

Status:

High priority cleanup / resilience issue.

Goal:

Recover the real EnergyHub strategy after restart from verified inverter settings rather than time alone.

Initial mapping:

```text
SBU + OSO
→ Solar

SUB + OSO
→ Hybrid Grid Hold

SUB + SNU
→ active grid-charging strategy requiring context reconstruction
```

Future work:

- verify Setting 01 and Setting 16 after startup;
- reconstruct Operating Mode;
- avoid unnecessary inverter commands;
- handle inconsistent or unknown combinations safely;
- determine how to distinguish Hybrid Charging and Panic when settings are identical;
- integrate reconstruction with the future Recovery Strategy.

---

# EnergyHub 1.1 — Smart Loads & Test-Drive Improvements

## Test-Drive Corrections

Goals:

- fix bugs discovered during real Autopilot operation;
- improve logs and naming;
- make cosmetic improvements;
- improve usability;
- simplify confusing controls;
- improve family-facing presentation.

---

## Smart Heating / Away Rethink

Status:

Original Away Mode concept paused.

Problem:

The original Away Mode mixed occupancy, solar-surplus heating, battery reserve, and flexible-load control.

Heating strategy should not depend only on whether the family is home or away.

Goals:

- redesign Away as part of a broader Smart Heating strategy;
- prioritize comfort while the house is occupied;
- use otherwise unused solar energy for useful heating;
- consider cheap night electricity;
- preserve required battery reserve;
- maintain safe temperatures while away;
- decide which logic belongs in EnergyHub and which belongs in Home Assistant.

Possible behavior:

```text
At Home
→ comfort first
→ use surplus solar for additional heating
→ optionally use cheap night tariff

Away
→ maintain useful / safe temperature
→ consume otherwise unused solar
→ preserve battery reserve
```

---

## EV Charging Template

Status:

Planned.

Goal:

Create a reusable EnergyHub strategy template for future EV charging.

Possible inputs:

- solar surplus;
- battery SOC;
- house consumption;
- cheap tariff period;
- required EV energy;
- required departure time;
- household priorities.

Requirements:

- preserve household comfort;
- preserve required battery reserve;
- avoid unnecessary Grid Import;
- support both solar-surplus and cheap-tariff charging strategies.

---

## Flexible Load Architecture

Status:

Design required.

Future loads may include:

- heat pumps;
- water heating;
- EV charging;
- other controllable household loads.

Possible intentions:

```text
Heat Now
Heat Later
Heat Only from Surplus
Allow Water Heating
Prioritize EV Charging
Preserve Battery Reserve
```

Goals:

- define generic flexible-load concepts;
- preserve user ownership and manual control;
- avoid device-specific logic in the core Decision Engine;
- use surplus energy without compromising comfort or resilience.

---

# EnergyHub 1.2 — Configurable EnergyHub

## Configurable Strategy Parameters

Status:

Planned.

Goal:

Move safe household strategy parameters from hard-coded values into validated configuration.

Candidates:

- cheap electricity tariff start time;
- cheap electricity tariff end time;
- Panic evaluation start time;
- Panic evaluation end time;
- nominal battery capacity;
- grid charging current;
- Hybrid target SOC;
- Panic SOC thresholds;
- Panic target SOC values;
- Panic forecast margin;
- other safe Decision Engine parameters.

Requirements:

- safe bounds;
- validated values;
- clear defaults;
- clear descriptions;
- separation between hardware limits and household strategy preferences.

---

## Panic Profiles

Status:

Planned.

Possible profiles:

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

Goals:

- make the preferred resilience strategy selectable;
- keep profile behavior understandable;
- expose the active profile in Home Assistant;
- preserve explainable decisions.

---

## Configuration Dashboard

Status:

Planned.

Goals:

- create a trusted-user configuration dashboard;
- expose safe strategy variables;
- explain every configurable value;
- validate inputs;
- avoid source-code or YAML editing for normal configuration.

---

# EnergyHub 1.3 — Recovery & Resilience

## Recovery Strategy Implementation

Status:

Architecture documented. Implementation deferred to 1.3.

Goals:

- define recovery responsibilities for each EnergyHub service;
- investigate MQTT connection failures;
- investigate network failures;
- investigate serial communication failures;
- investigate `mpp-solar` timeouts and blocking;
- investigate Home Assistant connectivity failures;
- investigate inverter communication failures;
- implement limited automatic recovery where safe;
- keep recovery bounded and verifiable;
- stop automatic recovery after repeated failure;
- add recovery notifications.

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

## External Heartbeat / Watchdog

Status:

Research required.

Goal:

Detect failures where EnergyHub or Home Assistant cannot report their own failure.

Possible responsibilities:

- monitor EnergyHub heartbeat;
- monitor Home Assistant availability;
- notify externally after sustained failure;
- avoid unsafe automatic actions.

---

# Ongoing Improvements

## Proactive Battery Reserve Protection

Status:

Research and future Decision Engine development.

Core question:

```text
Can the house safely survive until the next expected charging opportunity?
```

Possible inputs:

- Battery SOC;
- SOC trend;
- remaining solar production;
- expected House Consumption;
- Grid Confidence;
- current Operating Mode;
- time until the next charging opportunity.

Goals:

- estimate whether current battery reserve is sufficient;
- improve outage preparation;
- avoid unnecessary daytime Grid Import;
- preserve explainability.

---

## Battery Health Improvements

Status:

v1 implemented.

Future work:

- preserve better diagnostic information for anomaly events;
- add useful Battery Health notifications;
- investigate additional generic anomaly rules if real-system behavior justifies them;
- evaluate direct JK BMS data when integration architecture is ready.

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

- validate unchanged-load detection against long-term behavior;
- investigate false warnings;
- consider additional telemetry verification methods.

---

## Inverter Health Improvements

Status:

v1 implemented.

Future work:

- investigate persistent `eeprom_fault`;
- determine whether it is active, historical/sticky, firmware-specific, or a protocol interpretation issue;
- classify warnings and faults by severity;
- add notifications for significant conditions;
- determine how known persistent warnings should affect System Health.

---

## System Health Improvements

Status:

v1 implemented.

Future work:

- improve severity classification;
- add notification policies;
- improve Developer Dashboard presentation;
- determine whether System Health should become a prerequisite for selected automatic decisions.

---

## Daily Summary Improvements

Status:

v1 implemented.

Future work:

- add 30-day visualization if useful;
- improve historical analysis;
- evaluate forecast accuracy;
- compare forecast, consumption, Grid Import, and battery behavior;
- add new daily facts only when useful for decisions or analysis.

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

# Future Platform Work

## Additional Hardware Support

Potential future platforms:

- Deye;
- Victron;
- GoodWe;
- Growatt;
- LuxPower.

Rule:

Do not build speculative abstractions before real hardware requirements exist.

---

## Infrastructure

Goals:

- secure remote Home Assistant access;
- VPN backup access;
- automatic backups;
- OTA update strategy;
- external EnergyHub/Home Assistant heartbeat monitoring;
- external failure notifications.

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
- keep `06-Roadmap.md` focused on project milestones and direction;
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

Ideas remain in the Backlog only while they are relevant to the current direction of EnergyHub.