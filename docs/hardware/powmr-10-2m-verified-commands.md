# PowMr 10.2M Verified Commands

## Hardware

- Inverter: PowMr 10.2M
- Protocol: PI30MAX
- Transport: USB-RS232
- Tool: `mpp-solar`

This file records commands verified on the installed inverter. It is not a universal PI30MAX specification.

## Read commands

### QPIGS

Used for normal telemetry, including available values for:

- AC input voltage/frequency;
- AC output voltage/frequency/power/load;
- battery voltage/SOC/current;
- PV1 voltage/current/power;
- inverter temperature.

Poll interval: default 10 seconds.

### QPIRI

Used for rated/settings data and Menu 01 read-back.

Relevant raw values:

- `Solar Battery Utility` → SBU;
- `Solar Utility Battery` → SUB.

Read interval: 60 seconds.

### QPIWS

Used for inverter warning/fault bits.

Read interval: 60 seconds.

### QMOD

Verified for operating-source observation during manual tests. Current strategy truth is represented by EnergyHub controller state plus settings reconstruction rather than QMOD alone.

### QMUCHGCR / QMCHGCR

Verified for utility charging-current related values during investigation. They are not part of the current autonomous strategy transition path.

## Write commands

### Menu 01 — Output Source Priority

| Desired value | Command | Result |
|---|---|---|
| SUB | `POP01` | ACK, then QPIRI read-back |
| SBU | `POP02` | ACK, then QPIRI read-back |

EnergyHub treats Menu 01 as verified only after QPIRI matches the expected raw value.

### Menu 16 — Charger Source Priority

| Desired value | Command | Result |
|---|---|---|
| SNU | `PCP01` | ACK-confirmed |
| OSO | `PCP02` | ACK-confirmed |
| CSO | `PCP03` | mapping identified, not used by current strategies |

No verified query returns Menu 16. EnergyHub persists the last ACK-confirmed value.

### Maximum utility charging current

`MUCHGCxxx` commands were investigated and may be used in future configurable strategy work. Current 1.0 strategy transitions do not modify charging current dynamically.

## Strategy mapping

### Solar

```text
POP02 → SBU
PCP02 → OSO
```

### Hybrid Charging

```text
POP01 → SUB
PCP01 → SNU
```

### Hybrid Grid Hold

```text
POP01 → SUB
PCP02 → OSO
```

### Panic

```text
POP01 → SUB
PCP01 → SNU
```

Hybrid Charging and Panic share the same physical menu combination. Persisted strategy context and Panic target distinguish them.

## Write policy

- maximum three write attempts;
- one-second delay between attempts;
- Menu 01 requires QPIRI verification;
- Menu 16 requires ACK and immediate persistence;
- partial failure attempts bounded Solar recovery;
- no automatic inverter restart.

## Unsupported or unavailable features

Tests found no usable support for:

- QPIGS2;
- QOPPT;
- QET;
- QLT;
- QED;
- reliable PV2/output2/lifetime counters through the current path.

## Terminology

Use:

- **verified** for Menu 01 after read-back;
- **ACK-confirmed** for Menu 16;
- **remembered** for persisted context;
- **estimated** for Grid Import.

Do not describe Menu 16 as read-back verified.
