# Communication Reliability

EnergyHub continuously evaluates communication quality.

Current implementation:

## Telemetry Validation

Telemetry containing invalid values is rejected.

Examples:

SOC = None

PV = None

Load = None

These values are never published to MQTT.

---

## Communication Watchdog

Tracks:

- Last successful telemetry
- Consecutive communication failures

States:

- Starting
- Online
- Recovering
- Offline

---

## Health Monitor

Monitors overall EnergyHub communication health.

Current scope:

- Communication state

Future scope:

- MQTT connectivity
- Serial communication
- Forecast availability
- Self-tests
- Notification status

---

## Planned Recovery

1. Retry telemetry

2. Reconnect serial

3. Restart EnergyHub add-on

4. Notify homeowner

5. Manual intervention

Future:

Restart Home Assistant if necessary.