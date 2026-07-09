# PowMr 10.2M Verified Commands

Protocol:

PI30MAX

---

## Read Commands

### QPIGS

Realtime inverter telemetry.

Verified working.

---

### QMOD

Current inverter operating mode.

Verified working.

Observed values:

- `Battery`
- `Line`

---

### QPIRI

Current inverter configuration and rated information.

Verified working.

Used to verify inverter settings after write commands.

Important fields:

- `output_source_priority`
- `charger_source_priority`
- `max_ac_charging_current`
- `max_charging_current`

---

### QPIWS

Inverter warning and fault status.

Verified working.

Used by Inverter Health Monitor.

---

## Write Commands

### Setting 01 — Output Source Priority

Programmatic control verified.

| Command | Inverter Setting | QPIRI Value |
|---|---|---|
| `POP01` | SUB | Solar Utility Battery |
| `POP02` | SBU | Solar Battery Utility |

Verification method:

1. Send command.
2. Verify `ACK`.
3. Read `QPIRI`.
4. Read `QMOD`.
5. Verify setting on physical inverter display.
6. Restore original setting.

Observed behavior:

#### POP01 → SUB

Command:

`POP01`

Result:

- command response: `ACK`
- QPIRI `output_source_priority`: `Solar Utility Battery`
- QMOD: `Line`
- physical inverter display: `SUB`

#### POP02 → SBU

Command:

`POP02`

Result:

- command response: `ACK`
- QPIRI `output_source_priority`: `Solar Battery Utility`
- physical inverter display: `SBU`

This mapping was experimentally verified on the PowMr 10.2M inverter.

---

### Setting 16 — Charger Source Priority

Programmatic control verified.

| Command | Inverter Setting |
|---|---|
| `PCP01` | SNU |
| `PCP02` | OSO |
| `PCP03` | CSO |

Verified mapping:

- `PCP01` → SNU
- `PCP02` → OSO
- `PCP03` → CSO

These commands control inverter Setting 16.

---

### Maximum Utility Charging Current

Programmatic control verified.

Command format:

`MUCHGCxxx`

Example:

`MUCHGC030`

sets the maximum utility charging current to:

30 A

Current EnergyHub target:

30 A

---

## EnergyHub Operating Strategy Mapping

The verified inverter commands allow EnergyHub to implement controlled operating strategies.

### Solar

Configuration:

- Setting 01: SBU
- Setting 16: OSO

Commands:

- `POP02`
- `PCP02`

---

### Hybrid Charging

Configuration:

- Setting 01: SUB
- Setting 16: SNU

Commands:

- `POP01`
- `PCP01`

Target:

Charge battery to 80% SOC.

After reaching target SOC, restore Solar configuration:

- `POP02`
- `PCP02`

---

### Panic Charging

Configuration:

- Setting 01: SUB
- Setting 16: SNU

Commands:

- `POP01`
- `PCP01`

Target:

Charge battery to 95% SOC.

After reaching target SOC, restore Solar configuration:

- `POP02`
- `PCP02`

---

## Command Verification Policy

EnergyHub must not assume that a successful write request changed the inverter configuration.

Write operations should be verified.

Expected sequence:

1. Send write command.
2. Check for `ACK`.
3. Read inverter configuration using `QPIRI`.
4. Verify that the requested setting is active.
5. Report or recover from failure when the requested state is not confirmed.

This policy should be used by the Inverter Strategy Controller.

---

## Tested but Unsupported

The following commands were tested and are not supported by this inverter:

- `QPIGS2`
- `QOPPT`
- `QET`
- `QEM`
- `QEY`
- `QED`
- `QLD`
- `QLM`
- `QLT`
- `QLY`

---

## Current Limitations

Unavailable from inverter:

- PV2 telemetry
- Second output telemetry
- Grid import/export energy counters
- Daily energy statistics

These limitations are hardware/protocol limitations rather than EnergyHub limitations.