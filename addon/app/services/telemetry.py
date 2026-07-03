import json

from app.config import LAST_FILE
from app.models.inverter_state import InverterState
from app.mqtt.publisher import publish_values
from app.utils.logger import log


REQUIRED_FIELDS = [
    "battery_capacity",
    "ac_output_active_power",
    "pv1_charging_power",
]


def _to_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


class TelemetryService:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.previous = {}

    def create_state(self, data):
        missing = [key for key in REQUIRED_FIELDS if data.get(key) is None]

        valid = len(missing) == 0

        grid_voltage = _to_float(data.get("ac_input_voltage"))

        return InverterState(
            valid=valid,
            grid_available=grid_voltage is not None and grid_voltage > 180,
            battery_soc=_to_float(data.get("battery_capacity")),
            battery_voltage=_to_float(data.get("battery_voltage")),
            battery_current=_to_float(data.get("battery_discharge_current")),
            pv_power=_to_float(data.get("pv1_charging_power")),
            load_power=_to_float(data.get("ac_output_active_power")),
            raw=data,
        )

    def process(self, data):
        state = self.create_state(data)

        if not state.valid:
            log("Telemetry invalid")
            log(
                "Invalid values | "
                f"SOC={state.battery_soc} | "
                f"PV={state.pv_power} | "
                f"Load={state.load_power}"
            )
            return state

        published = publish_values(self.mqtt_client, data, self.previous)
        self.previous.update(data)

        LAST_FILE.write_text(json.dumps(data, ensure_ascii=False))

        log(
            "OK | "
            f"SOC={state.battery_soc}% | "
            f"PV1={state.pv_power}W | "
            f"Load={state.load_power}W | "
            f"Grid={'online' if state.grid_available else 'offline'} | "
            f"Published={published}"
        )

        return state