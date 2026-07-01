import subprocess
import time
import traceback

from app.adapters.powmr import PowMrLocalAdapter
from app.config import AVAILABILITY_TOPIC, load_options
from app.mqtt.publisher import make_client, publish_discovery
from app.services.telemetry import TelemetryService
from app.utils.logger import log


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
            telemetry.process(data)

        except subprocess.TimeoutExpired:
            log("ERROR: mpp-solar timeout")
            client.publish(AVAILABILITY_TOPIC, "offline", retain=True)

        except Exception:
            log("ERROR:")
            log(traceback.format_exc())
            client.publish(AVAILABILITY_TOPIC, "offline", retain=True)

        time.sleep(int(options["poll_interval"]))


if __name__ == "__main__":
    main()