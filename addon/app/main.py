import queue
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
    publish_grid_import,
    publish_grid_import_discovery,
    publish_health,
    publish_health_discovery,
    publish_inverter_health,
    publish_inverter_health_discovery,
    publish_inverter_settings,
    publish_inverter_settings_discovery,
    publish_notification_event,
    publish_operating_mode,
    publish_operating_mode_discovery,
    publish_panic_decision,
    publish_panic_decision_discovery,
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
from app.services.grid_import import GridImportService
from app.services.grid_monitor import GridMonitor
from app.services.grid_stability import GridStabilityEngine
from app.services.health_monitor import HealthMonitor
from app.services.hybrid_decision import HybridDecisionEngine
from app.services.inverter_controller import InverterController
from app.services.inverter_health import InverterHealthMonitor
from app.services.panic_decision import PanicDecisionEngine
from app.services.system_health import SystemHealthMonitor
from app.services.telemetry import TelemetryService
from app.services.telemetry_freshness import (
    TelemetryFreshnessMonitor,
)
from app.services.watchdog import CommunicationWatchdog
from app.utils.logger import log


INVERTER_WARNING_INTERVAL_SECONDS = 60
INVERTER_SETTINGS_INTERVAL_SECONDS = 60
PANIC_EVALUATION_INTERVAL_SECONDS = 15 * 60

HYBRID_TARGET_SOC = 80
PANIC_DEFAULT_TARGET_SOC = 95

MENU_01_QPIRI_MAP = {
    "Solar Battery Utility": "SBU",
    "Solar Utility Battery": "SUB",
}

AUTOPILOT_SAFE_RECOVERY_MODES = {
    "unknown",
    "hybrid_charging",
    "hybrid_grid_hold",
    "panic",
    "transitioning",
    "transition_failed",
}


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
    grid_import = GridImportService()
    stability = GridStabilityEngine(history)
    daily_summary = DailySummaryService(history)
    hybrid_decision = HybridDecisionEngine()
    panic_decision = PanicDecisionEngine()

    mode_requests = queue.Queue(maxsize=1)

    panic_target_soc = PANIC_DEFAULT_TARGET_SOC

    last_warning_read = 0
    last_settings_read = 0
    last_panic_evaluation = 0

    hybrid_evaluation_requested = False
    panic_evaluation_requested = False

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

    def publish_controller_state():
        publish_charger_source_priority(
            client,
            inverter_controller.known_charger_priority,
        )

        publish_operating_mode(
            client,
            inverter_controller,
        )

    def queue_mode_request(requested_mode):
        try:
            mode_requests.get_nowait()
        except queue.Empty:
            pass

        try:
            mode_requests.put_nowait(requested_mode)

            log(
                "Inverter mode request queued: "
                f"{requested_mode}"
            )

        except queue.Full:
            log(
                "Could not queue inverter mode request: "
                f"{requested_mode}"
            )

    def process_mode_request():
        nonlocal hybrid_evaluation_requested
        nonlocal panic_target_soc
        nonlocal panic_evaluation_requested

        try:
            requested_mode = mode_requests.get_nowait()
        except queue.Empty:
            return

        if requested_mode == "safe_solar":
            if (
                inverter_controller.mode
                not in AUTOPILOT_SAFE_RECOVERY_MODES
            ):
                log(
                    "Autopilot safe Solar recovery not required: "
                    f"current mode={inverter_controller.mode}"
                )
                return

            log(
                "Autopilot disabled during active or unknown "
                "strategy. Performing final safe Solar recovery."
            )

            inverter_controller.restore_solar()
            publish_controller_state()
            return

        if requested_mode == "evaluate_hybrid":
            hybrid_evaluation_requested = True

            log("Hybrid evaluation requested")
            return

        if not autopilot.is_enabled():
            log(
                "Ignore inverter mode request "
                f"{requested_mode}: "
                "Autopilot disabled"
            )
            return

        log(
            "Processing inverter mode request: "
            f"{requested_mode}"
        )

        if requested_mode == "hybrid":
            inverter_controller.enter_hybrid()

        elif requested_mode == "hybrid_grid_hold":
            inverter_controller.enter_hybrid_grid_hold()

        elif requested_mode == "solar":
            inverter_controller.restore_solar()

        elif requested_mode == "panic":
            panic_target_soc = PANIC_DEFAULT_TARGET_SOC

            log(
                "Manual Panic requested: "
                f"target SOC={panic_target_soc}%"
            )

            inverter_controller.enter_panic()

        elif requested_mode == "panic_80":
            panic_target_soc = 80

            log(
                "Automatic Panic requested: "
                f"target SOC={panic_target_soc}%"
            )

            inverter_controller.enter_panic()

        elif requested_mode == "panic_95":
            panic_target_soc = 95

            log(
                "Automatic Panic requested: "
                f"target SOC={panic_target_soc}%"
            )

            inverter_controller.enter_panic()

        else:
            log(
                "Ignore unsupported inverter mode request: "
                f"{requested_mode}"
            )
            return

        publish_controller_state()

        if inverter_controller.mode == "solar":
            panic_evaluation_requested = True

            log(
                "Automatic Panic reevaluation requested "
                "after Solar confirmation"
            )

    def evaluate_hybrid(state):
        forecast_tomorrow = daily_summary.inputs.get(
            "solar_forecast_tomorrow"
        )

        consumption_today = daily_summary.inputs.get(
            "daily_house_consumption"
        )

        decision = hybrid_decision.evaluate(
            autopilot_enabled=autopilot.is_enabled(),
            operating_mode=inverter_controller.mode,
            battery_soc=state.battery_soc,
            forecast_tomorrow=forecast_tomorrow,
            consumption_today=consumption_today,
        )

        log(
            "Hybrid evaluation: "
            f"status={decision['status']}, "
            f"reason={decision['reason']}"
        )

        requested_mode = decision.get("request")

        if requested_mode is None:
            return

        log(
            "Hybrid decision triggered: "
            f"request={requested_mode}, "
            f"required_energy="
            f"{decision['required_energy']:.2f} kWh"
        )

        publish_notification_event(
            client,
            {
                "type": "automatic_mode_activation",
                "mode": "hybrid",
                "soc": state.battery_soc,
                "forecast": forecast_tomorrow,
                "required_energy": decision["required_energy"],
                "target_soc": HYBRID_TARGET_SOC,
                "reason": decision["reason"],
            },
        )

        queue_mode_request(requested_mode)

    def evaluate_panic(state):
        grid_confidence = stability.level()

        forecast_today = daily_summary.inputs.get(
            "solar_forecast_today"
        )

        consumption_yesterday = daily_summary.inputs.get(
            "daily_house_consumption"
        )

        decision = panic_decision.evaluate(
            autopilot_enabled=autopilot.is_enabled(),
            operating_mode=inverter_controller.mode,
            grid_confidence=grid_confidence,
            pv_power=state.pv_power,
            battery_soc=state.battery_soc,
            forecast_today=forecast_today,
            consumption_yesterday=consumption_yesterday,
        )

        publish_panic_decision(
            client,
            panic_decision,
        )

        log(
            "Automatic Panic evaluation: "
            f"status={decision['status']}, "
            f"reason={decision['reason']}"
        )

        requested_mode = decision.get("request")

        if requested_mode is None:
            return

        log(
            "Automatic Panic triggered: "
            f"request={requested_mode}, "
            f"target={decision['target_soc']}%"
        )

        publish_notification_event(
            client,
            {
                "type": "automatic_mode_activation",
                "mode": "panic",
                "soc": state.battery_soc,
                "forecast": forecast_today,
                "grid_confidence": grid_confidence,
                "target_soc": decision["target_soc"],
                "reason": decision["reason"],
            },
        )

        queue_mode_request(requested_mode)

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
            was_enabled = autopilot.is_enabled()

            if autopilot.update(payload):
                publish_autopilot(
                    client,
                    autopilot,
                )

                if (
                    was_enabled
                    and not autopilot.is_enabled()
                ):
                    queue_mode_request("safe_solar")

            return

        if key == "inverter_mode":
            requested_mode = payload.strip().lower()
            queue_mode_request(requested_mode)
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
    publish_grid_import_discovery(client)
    publish_health_discovery(client)
    publish_battery_health_discovery(client)
    publish_telemetry_freshness_discovery(client)
    publish_inverter_health_discovery(client)
    publish_inverter_settings_discovery(client)
    publish_operating_mode_discovery(client)
    publish_panic_decision_discovery(client)
    publish_autopilot_discovery(client)
    publish_system_health_discovery(client)
    publish_daily_summary_discovery(client)

    publish_daily_summary(
        client,
        daily_summary,
    )

    publish_grid_import(
        client,
        grid_import,
    )

    publish_autopilot(
        client,
        autopilot,
    )

    publish_panic_decision(
        client,
        panic_decision,
    )

    publish_charger_source_priority(
        client,
        "unknown",
    )

    publish_operating_mode(
        client,
        inverter_controller,
    )

    client.publish(
        AVAILABILITY_TOPIC,
        "online",
        retain=True,
    )

    while True:
        try:
            process_mode_request()

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
                    warning_data = inverter.read_warnings()

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
                    settings_data = inverter.read_settings()

                    publish_inverter_settings(
                        client,
                        settings_data,
                    )

                    raw_menu_01 = settings_data.get(
                        "output_source_priority"
                    )

                    menu_01 = MENU_01_QPIRI_MAP.get(
                        raw_menu_01,
                        "unknown",
                    )

                    menu_16 = (
                        inverter_controller
                        .known_charger_priority
                    )

                    log(
                        "Inverter settings updated: "
                        f"Menu 01={menu_01}, "
                        f"Menu 16={menu_16}"
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

                soc = state.battery_soc

                grid_import.update(
                    operating_mode=inverter_controller.mode,
                    output_power_w=state.load_power,
                    pv_power_w=state.pv_power,
                    battery_voltage_v=state.battery_voltage,
                    battery_charging_current_a=state.raw.get(
                        "battery_charging_current"
                    ),
                    battery_discharge_current_a=state.raw.get(
                        "battery_discharge_current"
                    ),
                )

                publish_grid_import(
                    client,
                    grid_import,
                )

                if hybrid_evaluation_requested:
                    evaluate_hybrid(state)
                    hybrid_evaluation_requested = False

                if (
                    autopilot.is_enabled()
                    and inverter_controller.mode
                    == "hybrid_charging"
                    and soc is not None
                    and soc >= HYBRID_TARGET_SOC
                ):
                    log(
                        "Hybrid target reached: "
                        f"SOC={soc}%. "
                        "Switching to Grid Hold."
                    )

                    inverter_controller.enter_hybrid_grid_hold()
                    publish_controller_state()

                if (
                    autopilot.is_enabled()
                    and inverter_controller.mode == "panic"
                    and soc is not None
                    and soc >= panic_target_soc
                ):
                    log(
                        "Panic target reached: "
                        f"SOC={soc}%, "
                        f"target={panic_target_soc}%. "
                        "Returning to Solar."
                    )

                    solar_restored = (
                        inverter_controller.restore_solar()
                    )

                    publish_controller_state()

                    if solar_restored:
                        panic_evaluation_requested = True

                        log(
                            "Automatic Panic reevaluation requested "
                            "after Panic returned to Solar"
                        )

                    else:
                        log(
                            "Panic exit failed: "
                            "Solar was not restored"
                        )

                if (
                    panic_evaluation_requested
                    or (
                        now - last_panic_evaluation
                        >= PANIC_EVALUATION_INTERVAL_SECONDS
                    )
                ):
                    evaluate_panic(state)

                    last_panic_evaluation = now
                    panic_evaluation_requested = False

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