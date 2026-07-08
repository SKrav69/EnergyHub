import subprocess
import time
import traceback

from app.adapters.powmr import PowMrLocalAdapter
from app.config import AVAILABILITY_TOPIC, load_options
from app.mqtt.publisher import (
    make_client,
    publish_battery_health,
    publish_battery_health_discovery,
    publish_daily_summary,
    publish_daily_summary_discovery,
    publish_discovery,
    publish_grid_discovery,
    publish_grid_history,
    publish_health,
    publish_health_discovery,
)
from app.services.battery_health import BatteryHealthMonitor
from app.services.daily_summary import DailySummaryService
from app.services.event_bus import EventBus
from app.services.grid_history import GridHistoryService
from app.services.grid_monitor import GridMonitor
from app.services.grid_stability import GridStabilityEngine
from app.services.health_monitor import HealthMonitor
from app.services.telemetry import TelemetryService
from app.services.watchdog import CommunicationWatchdog
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
    watchdog = CommunicationWatchdog()
    health = HealthMonitor()
    battery_health = BatteryHealthMonitor()

    grid = GridMonitor()
    history = GridHistoryService()
    stability = GridStabilityEngine(history)
    daily_summary = DailySummaryService(history)

    bus = EventBus()
    bus.subscribe(grid.handle_inverter_state)

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            log("MQTT connected")
            client.subscribe("energyhub/input/ha/#")
            log("Subscribed to energyhub/input/ha/#")
        else:
            log(f"MQTT connection failed with code {rc}")

    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")

        prefix = "energyhub/input/ha/"
        if not topic.startswith(prefix):
            return

        key = topic.replace(prefix, "")
        daily_summary.update_input(key, payload)
        publish_daily_summary(client, daily_summary)

    client.on_connect = on_connect
    client.on_message = on_message

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
    publish_grid_discovery(client)
    publish_health_discovery(client)
    publish_battery_health_discovery(client)
    publish_daily_summary_discovery(client)
    publish_daily_summary(client, daily_summary)

    client.publish(AVAILABILITY_TOPIC, "online", retain=True)

    while True:
        try:
            data = inverter.read_telemetry()
            state = telemetry.process(data)

            if not state.valid:
                watchdog.failure()
                health.update(watchdog)
                publish_health(client, health)
                client.publish(AVAILABILITY_TOPIC, "offline", retain=True)
            else:
                watchdog.success()
                health.update(watchdog)
                publish_health(client, health)

                battery_health.update(state)
                publish_battery_health(client, battery_health)

                client.publish(AVAILABILITY_TOPIC, "online", retain=True)

                bus.publish(state)
                history.update(grid.is_available)
                publish_grid_history(client, history, stability)

        except subprocess.TimeoutExpired:
            watchdog.failure()
            health.update(watchdog)
            publish_health(client, health)
            log("ERROR: mpp-solar timeout")
            client.publish(AVAILABILITY_TOPIC, "offline", retain=True)

        except Exception:
            watchdog.failure()
            health.update(watchdog)
            publish_health(client, health)
            log("ERROR:")
            log(traceback.format_exc())
            client.publish(AVAILABILITY_TOPIC, "offline", retain=True)

        time.sleep(int(options["poll_interval"]))


if __name__ == "__main__":
    main()