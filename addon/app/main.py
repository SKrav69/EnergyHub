import subprocess
import time
import traceback

from app.adapters.powmr import PowMrLocalAdapter
from app.config import AVAILABILITY_TOPIC, load_options
from app.mqtt.publisher import make_client, publish_discovery
from app.services.grid_history import GridHistoryService
from app.services.grid_monitor import GridMonitor
from app.services.grid_stability import GridStabilityEngine
from app.services.telemetry import TelemetryService
from app.services.watchdog import CommunicationWatchdog
from app.utils.logger import log
from app.services.event_bus import EventBus


def main():
    options = load_options()

    if not options.get("powmr_enabled", True):
        log("PowMr module disabled. Sleeping forever.")
        while True:
            time.sleep(3600)

    log("Options loaded")
    log(f"MQTT: {options['mqtt_host']}:{options['mqtt_port']}")
    log(f"Serial: {options['serial_port']}")
    log(f"Protocol: {options['protocol']}")
    log(f"Poll interval: {options['poll_interval']} sec")

    inverter = PowMrLocalAdapter(options)
    client = make_client(options)
    telemetry = TelemetryService(client)
    watchdog = CommunicationWatchdog()
    grid = GridMonitor()
    history = GridHistoryService()
    stability = GridStabilityEngine(history)
    bus = EventBus()

    while True:
        try:
            log("Connecting to MQTT...")
            client.connect(options["mqtt_host"], int(options["mqtt_port"]), 60)
            break
        except Exception as e:
            log(f"MQTT connection failed: {e}")
            time.sleep(10)

    client.loop_start()

    publish_discovery(client, options["device_name"])
    client.publish(AVAILABILITY_TOPIC, "online", retain=True)

    while True:
        try:
            data = inverter.read_telemetry()

            watchdog.success()

            state = telemetry.process(data)
            grid.update(state)
            history.update(grid.is_available)

            log(f"Grid stability: {stability.level()}")

        except subprocess.TimeoutExpired:
            watchdog.failure()

            log("ERROR: mpp-solar timeout")
            log(
                f"Communication state: {watchdog.state()} "
                f"(errors={watchdog.consecutive_errors})"
            )

            client.publish(AVAILABILITY_TOPIC, "offline", retain=True)

        except Exception:
            watchdog.failure()

            log("ERROR:")
            log(traceback.format_exc())
            log(
                f"Communication state: {watchdog.state()} "
                f"(errors={watchdog.consecutive_errors})"
            )

            client.publish(AVAILABILITY_TOPIC, "offline", retain=True)

        time.sleep(int(options["poll_interval"]))


if __name__ == "__main__":
    main()