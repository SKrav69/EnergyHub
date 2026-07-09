# Communication Reliability

EnergyHub continuously evaluates communication quality and prevents invalid or stale inverter data from being treated as valid system state.

---

## Telemetry Validation

Telemetry containing invalid values is rejected.

Examples:

- SOC = None
- PV = None
- Load = None

Invalid telemetry values are never published to MQTT as valid inverter state.

---

## Communication Watchdog

Tracks inverter communication reliability.

Current scope:

- Last successful telemetry
- Consecutive communication failures

States:

- Starting
- Online
- Recovering
- Offline

The Communication Watchdog provides the primary communication health state used by EnergyHub.

---

## Telemetry Freshness Monitor

Monitors whether valid inverter telemetry continues to update.

Current implementation:

- No valid telemetry for 60 seconds → stale
- House Load unchanged for 5 minutes → warning

This monitor detects situations where communication may appear operational but telemetry is no longer updating correctly.

---

## Inverter Health Monitor

Monitors inverter warnings and faults independently from telemetry communication.

Current implementation:

- QPIWS queried every 60 seconds
- Active inverter warning and fault flags are parsed
- Inverter health state is published to MQTT

Current observed inverter warning:

- `eeprom_fault = 1`

---

## System Health Aggregation

EnergyHub combines individual health components into an overall System Health state.

Current components:

- Communication Health
- Battery Health
- Telemetry Health
- Inverter Health

System Health provides a single high-level view of EnergyHub operational health.

---

## Write Command Reliability

EnergyHub must not assume that an inverter write command succeeded only because the command returned `ACK`.

Write operations should use explicit verification.

Expected sequence:

1. Send write command.
2. Verify `ACK`.
3. Read inverter configuration using `QPIRI`.
4. Confirm that the requested setting is active.
5. Report failure if the requested state is not confirmed.
6. Apply recovery behavior when appropriate.

This policy is especially important for future automatic inverter strategy transitions.

---

## Recovery Strategy

Recovery behavior is the next development milestone.

The recovery design must investigate:

- MQTT connection failures
- Network failures
- Serial communication failures
- `mpp-solar` timeouts and blocking
- Partial inverter strategy transitions
- Write command failures
- Write verification failures

Recovery responsibilities must be defined for each EnergyHub service.

EnergyHub must distinguish between situations where:

- automatic recovery should occur
- retry should occur
- the failure should only be reported
- homeowner notification is required
- manual intervention is required

---

## Planned Recovery Layers

Possible recovery sequence:

1. Retry operation.
2. Retry telemetry or configuration read.
3. Reconnect serial communication.
4. Restore a known safe inverter configuration when appropriate.
5. Restart the affected EnergyHub service.
6. Restart the EnergyHub add-on.
7. Notify homeowner.
8. Require manual intervention.

Restarting Home Assistant should only be considered as a last-resort recovery action.

---

## Future Work

Planned reliability improvements:

- MQTT connectivity monitoring
- Serial connection recovery
- `mpp-solar` timeout protection
- Inverter command transaction handling
- Partial transition recovery
- External EnergyHub watchdog
- Notification integration
- Additional self-tests