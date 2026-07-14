# EnergyHub Recovery Strategy

> Recovery must be safe, bounded, explainable, and owned by the correct subsystem.

---

# Milestone

```text
EnergyHub 1.3 — Recovery & Resilience
```

Status:

```text
Architecture defined; implementation deferred to EnergyHub 1.3
```

---

# Purpose

This document defines how EnergyHub should react when communication, software, Home Assistant, inverter telemetry, or operating-state problems occur.

Recovery is not one universal action.

Different failures require different owners, different allowed actions, and different escalation rules.

---

# Core Principles

## Detection and Recovery Are Separate

A monitor may detect a problem without being responsible for fixing it.

```text
Detection
    ↓
Classification
    ↓
Recovery Decision
    ↓
Bounded Action
    ↓
Verification
    ↓
Escalation if required
```

## The Inverter Owns Its Internal Protection

EnergyHub must never automatically restart the inverter.

The inverter owns:

- over-current protection;
- over-temperature protection;
- low-voltage protection;
- internal fault handling;
- internal restart behavior.

EnergyHub may:

- detect;
- report;
- retry communication;
- restore a known safe configuration when appropriate.

## Recovery Must Be Bounded

Infinite restart or retry loops are prohibited.

A recovery action must have:

- a defined trigger;
- a defined owner;
- a maximum number of attempts;
- a cooldown;
- a verification step;
- an escalation path.

## Safe State Is More Important Than Perfect State

When EnergyHub cannot determine the current strategy reliably, it should prefer a known safe operating state.

Current safe fallback:

```text
Solar
Setting 01 → SBU
Setting 16 → OSO
```

This fallback should be used only when it is safe and justified by the failure type.

---

# Failure Classes

EnergyHub currently distinguishes these main failure classes:

- MQTT failure;
- network failure;
- serial communication failure;
- `mpp-solar` timeout or blocking;
- Home Assistant connectivity failure;
- invalid or stale telemetry;
- inverter warning or fault;
- battery anomaly;
- operating-mode transition failure;
- EnergyHub process failure;
- full Home Assistant platform failure.

Each class requires a different recovery policy.

---

# Recovery Ownership

## MQTT Client

Owns:

- reconnecting to the MQTT broker;
- resubscribing to input topics;
- republishing availability;
- republishing discovery and retained state when required.

Allowed automatic actions:

- immediate reconnect attempts;
- bounded retry delays;
- restoring subscriptions after reconnect.

Not allowed:

- restarting the inverter;
- changing operating strategy merely because MQTT was unavailable.

---

## PowMr Adapter / Serial Layer

Owns:

- command execution;
- command timeout handling;
- serial retry behavior;
- parsing validation.

Allowed automatic actions:

- retrying a failed command a limited number of times;
- reopening communication where safe;
- rejecting invalid responses;
- reporting timeout or protocol errors.

Not allowed:

- infinite retries;
- unverified mode changes;
- automatic inverter restart.

---

## Inverter Controller

Owns:

- operating-mode transitions;
- command order;
- ACK handling;
- QPIRI verification;
- transition retries;
- transition state;
- transition failure state;
- safe Solar restoration when justified.

Allowed automatic actions:

- bounded retries;
- waiting for inverter settling;
- verifying Setting 01 and Setting 16;
- marking transition failure;
- requesting safe Solar recovery when Autopilot is disabled during an active or unknown strategy.

Not allowed:

- claiming success without verification;
- repeatedly forcing commands forever;
- hiding transition failure.

---

## Health Services

Own:

- detection;
- classification;
- health state;
- health reason;
- event reporting.

Health services include:

- Communication Health;
- Battery Health;
- Telemetry Freshness;
- Inverter Health;
- System Health.

Health services do not automatically own recovery actions unless explicitly assigned.

---

## Home Assistant

Owns:

- dashboards;
- user controls;
- helper state;
- selected household automations;
- notification delivery;
- restart-time automation triggers.

Home Assistant should not attempt to reconstruct inverter state by assumption alone.

Future restart recovery should use verified inverter settings.

---

# Current Recovery Behavior

## MQTT Connection Failure

Current behavior:

```text
Connect
    ↓
Failure
    ↓
Log error
    ↓
Wait
    ↓
Retry
```

Future improvements:

- exponential or bounded backoff;
- connection-attempt counters;
- clear recovery state;
- notification after prolonged failure;
- republish critical retained state after reconnect.

---

## Serial / `mpp-solar` Timeout

Current behavior:

- timeout is caught;
- telemetry freshness is updated;
- Communication Health is degraded;
- availability is published offline;
- EnergyHub continues running;
- the next loop attempts communication again.

Future improvements:

- distinguish transient timeout from persistent serial failure;
- bounded adapter reinitialization;
- one automatic recovery attempt;
- second attempt after a cooldown if still failed;
- notification after repeated failure.

---

## Invalid Telemetry

Current behavior:

- telemetry is marked invalid;
- Communication Watchdog records failure;
- health state is updated;
- availability is published offline.

EnergyHub must not:

- integrate invalid Grid Import data;
- execute decisions requiring missing telemetry;
- use stale values as if they were current.

Future improvements:

- preserve the last valid telemetry timestamp;
- include missing fields in diagnostics;
- classify partial telemetry separately from complete failure.

---

## Stale or Frozen Telemetry

Current rules:

```text
No valid telemetry for 60 seconds
→ stale

House Load unchanged for 5 minutes
→ warning
```

Current action:

- report warning;
- do not restart the inverter;
- do not automatically change operating mode.

Future work:

- validate false-positive behavior;
- add optional additional telemetry checks;
- define whether adapter restart is safe after persistent stale data.

---

## Battery Health Anomaly

Current rules:

```text
SOC < 15%
→ warning

SOC between 15% and 95%
AND absolute SOC change >= 2%
→ warning
```

Current action:

- detect;
- report;
- preserve diagnostic context;
- no automatic battery recovery action.

Reason:

Battery anomalies may be caused by:

- BMS calibration;
- telemetry error;
- battery protection;
- real battery behavior.

EnergyHub should not guess the correct recovery action.

---

## Inverter Warning or Fault

Current behavior:

- poll `QPIWS` every 60 seconds;
- parse active warning and fault flags;
- publish Inverter Health and reason;
- aggregate into System Health.

Current policy:

- warning and fault detection only;
- no automatic inverter restart;
- no automatic fault clearing.

Persistent current finding:

```text
eeprom_fault = 1
```

Future work:

- classify severity;
- distinguish sticky historical faults from active faults;
- notify only on significant or changed conditions;
- document safe user response.

---

# Operating-Mode Transition Recovery

A transition may fail because:

- command was rejected;
- command timed out;
- QPIRI returned no result;
- verification did not match;
- serial communication was interrupted;
- inverter state changed unexpectedly.

Current transition design:

```text
Request Mode
    ↓
Set First Parameter
    ↓
Verify
    ↓
Set Second Parameter
    ↓
Verify
    ↓
Wait for Settling
    ↓
Publish Confirmed Mode
```

If verification fails:

```text
Retry within bounded attempt count
```

If all attempts fail:

```text
transition_failed
```

The failure must be visible in:

- logs;
- Operating Mode;
- reason;
- future notification policy.

---

# Restart Strategy Reconstruction

Current limitation:

Home Assistant may request Hybrid after a night restart based mainly on time.

This can be wrong because the inverter may already be in:

- Hybrid Charging;
- Hybrid Grid Hold;
- Solar;
- an inconsistent state.

Future strategy:

```text
Read verified Setting 01
+
Read verified Setting 16
        ↓
Reconstruct Operating Mode
```

Intended mapping:

```text
SUB + SNU → Hybrid Charging or Panic; additional context is required
SUB + OSO → Hybrid Grid Hold
SBU + OSO → Solar
```

Unknown combinations:

```text
Unknown / inconsistent
        ↓
Do not guess
        ↓
Report state
        ↓
Apply safe recovery only if policy allows
```

This is an important restart-recovery item and part of the EnergyHub 1.3 Recovery & Resilience milestone.

---

# Safe Solar Recovery

Safe Solar recovery may be appropriate when:

- Autopilot is disabled during an active EnergyHub-controlled strategy;
- EnergyHub is in an unknown controlled state;
- a user explicitly requests Solar;
- a completed Panic session exits successfully;
- the morning Hybrid schedule ends.

Safe Solar recovery means:

```text
Setting 16 → OSO
Setting 01 → SBU
```

The exact command order should remain controlled by the Inverter Controller.

Safe Solar recovery must still be:

- bounded;
- verified;
- logged;
- visible if it fails.

---

# Recovery Attempt Policy

Initial recommended policy:

```text
Failure detected
        ↓
Immediate bounded retry
        ↓
Verify result
        ↓
If still failed
        ↓
One automatic recovery attempt
        ↓
Verify result
        ↓
If still failed
        ↓
Cooldown approximately 30 minutes
        ↓
Possible second recovery attempt
        ↓
Verify result
        ↓
If still failed
        ↓
Stop automatic recovery
        ↓
Require human attention
```

This policy is a framework.

Each subsystem must define whether both attempts are appropriate.

---

# Notification Policy

Recovery notifications should be meaningful and not noisy.

Recommended notification events:

- automatic recovery started;
- automatic recovery succeeded;
- automatic recovery failed;
- repeated communication failure;
- transition failure;
- persistent inverter warning;
- Home Assistant connectivity failure;
- external watchdog detected EnergyHub unavailable.

Notifications should include:

```text
What failed
What EnergyHub tried
Whether recovery succeeded
What the homeowner should do
```

---

# Home Assistant Failure Limitation

EnergyHub and Home Assistant cannot reliably report their own failure when the entire Home Assistant platform is frozen, powered off, or disconnected.

Therefore, a complete reliability architecture requires an external observer.

Future options:

- external heartbeat service;
- router-based monitoring;
- second Raspberry Pi;
- cloud uptime monitor;
- Telegram bot hosted outside Home Assistant;
- external MQTT heartbeat consumer.

The external observer should notify only when:

- Home Assistant heartbeat stops;
- EnergyHub heartbeat stops;
- the outage lasts longer than a defined threshold.

---

# Persistence Requirements

Recovery-related state that may need persistence:

- last successful telemetry timestamp;
- last recovery attempt;
- recovery attempt count;
- cooldown expiry;
- last confirmed operating mode;
- last verified Setting 01;
- last verified Setting 16;
- last transition failure reason.

Persistence should prevent restart loops and repeated recovery attempts after process restart.

---

# Recovery State Model

Future generic recovery states:

```text
idle
detecting
retrying
recovering
verifying
recovered
cooldown
failed
manual_attention_required
```

Not every subsystem needs every state.

The model should remain simple enough to understand from logs and dashboards.

---

# Dashboard Requirements

Developer dashboard should eventually show:

- current recovery state;
- affected subsystem;
- last recovery action;
- last recovery result;
- recovery attempt count;
- next allowed retry time;
- manual attention required indicator.

Family dashboard should show only:

- normal;
- recovering;
- action required.

---

# Testing Strategy

Recovery behavior must be tested deliberately.

Recommended test scenarios:

- stop MQTT broker;
- disconnect network;
- disconnect serial adapter;
- force `mpp-solar` timeout;
- return invalid telemetry;
- restart EnergyHub during Solar;
- restart EnergyHub during Hybrid Charging;
- restart EnergyHub during Hybrid Grid Hold;
- restart EnergyHub during Panic;
- disable Autopilot during active Hybrid;
- simulate failed Setting 01 verification;
- simulate failed Setting 16 verification.

Every test should record:

- initial state;
- failure introduced;
- detected state;
- recovery action;
- verification result;
- final state.

---

# Current Status

Implemented:

- communication failure detection;
- timeout handling;
- invalid telemetry handling;
- Battery Health warnings;
- Telemetry Freshness warnings;
- Inverter Health warnings;
- System Health aggregation;
- bounded inverter-setting verification retries;
- safe Solar recovery path;
- transition failure state.

Planned:

- subsystem-specific recovery services;
- persisted recovery attempt state;
- restart strategy reconstruction;
- recovery notifications;
- external heartbeat monitoring;
- dashboard recovery visibility.

---

# Rule

EnergyHub should recover automatically only when the recovery action is:

- understood;
- safe;
- bounded;
- verifiable;
- appropriate for the detected failure.

When those conditions are not met:

```text
Detect
    ↓
Report
    ↓
Require human attention
```