# EnergyHub Backlog

This backlog contains open work. Completed High and selected Medium audit items are recorded in the changelog and project history rather than left as active tasks.

## EnergyHub 1.0 — Release closure

### Automated tests

Priority: High before external release.

Add tests for:

- Hybrid decision formula and skipped states;
- Panic thresholds and time window;
- queue priority for `safe_solar`;
- transition success/failure events;
- Menu 01 verification behavior;
- restart reconstruction combinations;
- Grid Import rollover and finalization;
- atomic Daily Summary idempotence;
- JSON persistence failure handling.

### Release security

- remove weak default MQTT username/password from published defaults;
- document secret configuration;
- verify no runtime exports or credentials are tracked;
- review add-on permissions and device mapping.

### Dependency pinning

- capture tested `paho-mqtt` and `mpp-solar` versions from the working add-on;
- pin exact compatible versions;
- rebuild from a clean environment;
- record upgrade policy.

### Installation and operations guide

- fresh add-on installation;
- Mosquitto user setup;
- serial device selection;
- HA configuration synchronization;
- Solcast prerequisites;
- dashboard resource prerequisites;
- backup and rollback;
- troubleshooting startup and MQTT.

### Final UI cleanup

- replace remaining `New section` headings with meaningful section names;
- verify mobile layout;
- confirm all icons and colours in light and dark themes;
- ensure the technical chart does not dominate the family view;
- verify Smart Thermal is visibly planned, not active.

### Real transition validation

- observe a real automatic Hybrid Charging entry;
- observe Hybrid target → Grid Hold;
- observe 07:00 Solar restoration;
- observe automatic Panic 80% and 95% paths when conditions permit;
- verify success and failure notification ordering.

## EnergyHub 1.1 — Test-drive corrections

### Telemetry anomaly framework

Current Battery Health detects low SOC and ≥2% jumps below 95%, but calculations still need a general plausibility policy.

Design:

- quality flags per telemetry sample;
- plausible rate-of-change checks;
- quarantine of suspicious values from accounting;
- separate warning from control inhibition;
- configurable hardware-specific limits.

### Grid Import validation

- compare estimated import against external meter or smart plug data;
- test daytime Panic with simultaneous PV;
- determine whether full house load during SUB overestimates grid contribution;
- avoid replacing one known approximation with an unvalidated subtraction formula;
- preserve explicit non-billing-grade labelling.

### Panic policy review

The current code uses Grid Confidence, SOC, and forecast sufficiency. Review whether a live PV power gate should be restored and, if so, whether it should use a fixed threshold, forecast trend, or net energy state.

### Second-floor smart plug

- purchase and pair compatible plug;
- add manual dashboard control;
- measure power where available;
- include later in Smart Thermal capabilities.

### Notification improvements

- optional transition completion message for manual requests;
- configurable notification channels;
- concise family message plus technical detail link;
- deduplication and severity policy.

## EnergyHub 1.2 — Configuration

- configuration schema and validation;
- migration from hard-coded defaults;
- Home Assistant configuration dashboard;
- safe reset to known defaults;
- policy profile export/import;
- separation of hardware limits and strategy preferences.

## EnergyHub 1.3 — Recovery & Resilience

- classify MQTT connection failures;
- classify network and DNS failures;
- classify serial lock, timeout, and malformed response failures;
- bounded adapter retries;
- process-level heartbeat;
- missed schedule recovery;
- HA-unavailable behavior;
- delayed retained-input behavior;
- external watchdog;
- recovery test matrix.

## EnergyHub 1.4 — Remote Access & Telegram

- Cloudflare Tunnel deployment and security review;
- WireGuard backup;
- Telegram bot authentication;
- `/status`, `/health`, `/mode`, `/forecast` commands;
- alerts for offline, transition failure, low reserve, and Panic;
- optional approved mode commands with Autopilot checks;
- audit trail.

## EnergyHub 1.5 — Smart Thermal Energy

### Requirements

- capability registry for heat pumps and smart plugs;
- room temperature and humidity inputs;
- comfort bands;
- SOC start/stop bands;
- surplus/cheap-tariff eligibility;
- minimum runtime;
- cooldown;
- ownership marker;
- manual override;
- multiple-load priority;
- restart reconstruction;
- notification policy.

### Research

- real heat-pump power curves;
- effect of inverter modes on available surplus;
- best thermal storage periods by season;
- preheating/precooling value;
- room-specific comfort priorities.

## Technical debt

### `main.py` lifecycle size

Do not perform a broad refactor before tests. Later candidates:

- request processor;
- strategy target monitor;
- startup reconstruction coordinator;
- notification coordinator;
- periodic task scheduler.

### Duplicated constants

Centralize battery capacity, targets, time windows, safety factors, and mappings as part of 1.2 configuration rather than creating a second temporary constants layer.

### Graceful shutdown

Add explicit process shutdown handling and final persistence where useful. Home Assistant add-on termination currently relies on normal process/container behavior.

## Documentation maintenance

After each release milestone:

- compare documentation with code and live HA configuration;
- update project state and changelog;
- preserve historical decisions;
- remove current-state contradictions;
- regenerate architecture visuals only when the architecture changes materially.

## Backlog rule

A backlog item should state:

- user outcome;
- current limitation;
- owner/service boundary;
- safe behavior;
- validation method;
- target milestone.
