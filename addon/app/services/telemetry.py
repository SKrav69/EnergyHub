import json

from app.config import LAST_FILE
from app.models.inverter_state import InverterState
from app.mqtt.publisher import publish_values
from app.utils.logger import log


class TelemetryService:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.previous = {}

    def process(self, data):
        state = InverterState(data)

        published = publish_values(self.mqtt_client, data, self.previous)
        self.previous.update(data)

        LAST_FILE.write_text(json.dumps(data, ensure_ascii=False))

        log(
            "OK | "
            f"SOC={state.battery_soc}% | "
            f"PV1={state.pv1_power}W | "
            f"Load={state.house_load}W | "
            f"Grid={'online' if state.is_grid_available else 'offline'} | "
            f"Published={published}"
        )