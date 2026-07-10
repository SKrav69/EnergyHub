import subprocess
import time
import traceback

from app.adapters.powmr import PowMrLocalAdapter
from app.config import AVAILABILITY_TOPIC, load_options
from app.mqtt.publisher import (
    make_client,
    publish_autopilot,
    publish_autopilot_discovery,
    publish_battery_health,
    publish_battery_health_discovery,
    publish_charger_source_priority,
    publish_daily_summary,
    publish_daily_summary_discovery,
    publish_discovery,
    publish_grid_discovery,
    publish_grid_history,
    publish_health,
    publish_health_discovery,
    publish_inverter_health,
    publish_inverter_health_discovery,
    publish_inverter_settings,
    publish_inverter_settings_discovery,
    publish_system_health,
    publish_system_health_discovery,
    publish_telemetry_freshness,
    publish_telemetry_freshness_discovery,
)
from app.services.autopilot import AutopilotState
from app.services.battery_health import BatteryHealthMonitor
from app.services.daily_summary import DailySummaryService
from app.services.event_bus import EventBus
from app.services.grid_history import GridHistoryService
from app.services.grid_monitor import GridMonitor
from app.services.grid_stability import GridStabilityEngine
from app.services.health_monitor import HealthMonitor
from app.services.inverter_controller import InverterController
from app.services.inverter_health import InverterHealthMonitor
from app.services.system_health import SystemHealthMonitor
from app.services.telemetry import TelemetryService
from app.services.telemetry_freshness import (
    TelemetryFreshnessMonitor,
)
from app.services.watchdog import CommunicationWatchdog
from app.utils.logger import log


INVERTER_WARNING_INTERVAL_SECONDS = 60
INVERTER_SETTINGS_INTERVAL_SECONDS = 60


def main():
    options = load_options()

    if not options.get("powmr_enabled", True):
        log("PowMr module disabled. Sleeping forever.")

        while True:
            time.sleep(3600)

    log("Options loaded")
    log(
        f"MQTT: "
        f"{options['mqtt_host']}:"
        f"{options['mqtt_port']}"
    )
    log(f"Serial: {options['serial_port']}")
    log(f"Protocol: {options['protocol']}")
    log(
        f"Poll interval: "
        f"{options['poll_interval']} sec"
    )

    inverter = PowMrLocalAdapter(options)
    inverter_controller = InverterController(inverter)

    client = make_client(options)

    telemetry = TelemetryService(client)
    watchdog = CommunicationWatchdog()
    health = HealthMonitor()
    battery_health = BatteryHealthMonitor()
    telemetry_freshness = TelemetryFreshnessMonitor()
    inverter_health = InverterHealthMonitor()
    system_health = SystemHealthMonitor()
    autopilot = AutopilotState()

    grid = GridMonitor()
    history = GridHistoryService()
    stability = GridStabilityEngine(history)
    daily_summary = DailySummaryService(history)

    last_warning_read = 0
    last_settings_read = 0

    bus = EventBus()
    bus.subscribe(grid.handle_inverter_state)

    def publish_all_health():
        system_health.update(
            health,
            battery_health,
            telemetry_freshness,
            inverter_health,
        )

        publish_system_health(
            client,
            system_health,
        )

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            log("MQTT connected")

            client.subscribe(
                "energyhub/input/ha/#"
            )

            log(
                "Subscribed to "
                "energyhub/input/ha/#"
            )

        else:
            log(
                "MQTT connection failed "
                f"with code {rc}"
            )

    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")

        prefix = "energyhub/input/ha/"

        if not topic.startswith(prefix):
            return

        key = topic.replace(prefix, "")

        if key == "autopilot":
            if autopilot.update(payload):
                publish_autopilot(
                    client,
                    autopilot,
                )

            return

        if key == "inverter_mode":
            requested_mode = payload.strip().lower()

            if not autopilot.is_enabled():
                log(
                    "Ignore inverter mode request "
                    f"{requested_mode}: "
                    "Autopilot disabled"
                )

                return

            if requested_mode == "hybrid":
                if inverter_controller.enter_hybrid():
                    publish_charger_source_priority(
                        client,
                        inverter_controller.known_charger_priority,
                    )

                return

            if requested_mode == "solar":
                if inverter_controller.restore_solar():
                    publish_charger_source_priority(
                        client,
                        inverter_controller.known_charger_priority,
                    )

                return

            log(
                "Ignore unsupported inverter mode "
                f"request: {requested_mode}"
            )

            return

        daily_summary.update_input(
            key,
            payload,
        )

        publish_daily_summary(
            client,
            daily_summary,
        )

    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            log("Connecting to MQTT...")

            client.connect(
                options["mqtt_host"],
                int(options["mqtt_port"]),
                60,
            )

            break

        except Exception as e:
            log(
                "MQTT connection failed: "
                f"{e}"
            )

            time.sleep(10)

    client.loop_start()

    publish_discovery(
        client,
        options["device_name"],
    )

    publish_grid_discovery(client)
    publish_health_discovery(client)
    publish_battery_health_discovery(client)
    publish_telemetry_freshness_discovery(client)
    publish_inverter_health_discovery(client)
    publish_inverter_settings_discovery(client)
    publish_autopilot_discovery(client)
    publish_system_health_discovery(client)
    publish_daily_summary_discovery(client)

    publish_daily_summary(
        client,
        daily_summary,
    )

    publish_autopilot(
        client,
        autopilot,
    )

    publish_charger_source_priority(
        client,
        "unknown",
    )

    client.publish(
        AVAILABILITY_TOPIC,
        "online",
        retain=True,
    )

    while True:
        try:
            data = inverter.read_telemetry()
            state = telemetry.process(data)

            telemetry_freshness.update(state)

            publish_telemetry_freshness(
                client,
                telemetry_freshness,
            )

            now = time.monotonic()

            if (
                now - last_warning_read
                >= INVERTER_WARNING_INTERVAL_SECONDS
            ):
                try:
                    warning_data = (
                        inverter.read_warnings()
                    )

                    inverter_health.update(
                        warning_data
                    )

                except Exception as e:
                    inverter_health.failure()

                    log(
                        "ERROR: QPIWS warning "
                        f"read failed: {e}"
                    )

                publish_inverter_health(
                    client,
                    inverter_health,
                )

                last_warning_read = now

            if (
                now - last_settings_read
                >= INVERTER_SETTINGS_INTERVAL_SECONDS
            ):
                try:
                    settings_data = (
                        inverter.read_settings()
                    )

                    publish_inverter_settings(
                        client,
                        settings_data,
                    )

                    output_priority = (
                        settings_data.get(
                            "output_source_priority"
                        )
                    )

                    raw_charger_priority = (
                        settings_data.get(
                            "charger_source_priority"
                        )
                    )

                    log(
                        "Inverter settings updated: "
                        f"output={output_priority}, "
                        "charger_raw="
                        f"{raw_charger_priority}"
                    )

                except Exception as e:
                    log(
                        "ERROR: QPIRI settings "
                        f"read failed: {e}"
                    )

                last_settings_read = now

            if not state.valid:
                watchdog.failure()
                health.update(watchdog)

                publish_health(
                    client,
                    health,
                )

                publish_all_health()

                client.publish(
                    AVAILABILITY_TOPIC,
                    "offline",
                    retain=True,
                )

            else:
                watchdog.success()
                health.update(watchdog)

                publish_health(
                    client,
                    health,
                )

                battery_health.update(state)

                publish_battery_health(
                    client,
                    battery_health,
                )

                publish_all_health()

                client.publish(
                    AVAILABILITY_TOPIC,
                    "online",
                    retain=True,
                )

                bus.publish(state)

                history.update(
                    grid.is_available
                )

                publish_grid_history(
                    client,
                    history,
                    stability,
                )

        except subprocess.TimeoutExpired:
            telemetry_freshness.update_status()

            publish_telemetry_freshness(
                client,
                telemetry_freshness,
            )

            watchdog.failure()
            health.update(watchdog)

            publish_health(
                client,
                health,
            )

            publish_all_health()

            log("ERROR: mpp-solar timeout")

            client.publish(
                AVAILABILITY_TOPIC,
                "offline",
                retain=True,
            )

        except Exception:
            telemetry_freshness.update_status()

            publish_telemetry_freshness(
                client,
                telemetry_freshness,
            )

            watchdog.failure()
            health.update(watchdog)

            publish_health(
                client,
                health,
            )

            publish_all_health()

            log("ERROR:")
            log(traceback.format_exc())

            client.publish(
                AVAILABILITY_TOPIC,
                "offline",
                retain=True,
            )

        time.sleep(
            int(options["poll_interval"])
        )


if __name__ == "__main__":
    main()