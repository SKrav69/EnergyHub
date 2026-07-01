import json

from app.config import LAST_FILE
from app.mqtt.publisher import publish_values
from app.utils.logger import log


class TelemetryService:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.previous = {}

    def process(self, data):
        published = publish_values(self.mqtt_client, data, self.previous)
        self.previous.update(data)

        LAST_FILE.write_text(json.dumps(data, ensure_ascii=False))

        log(
            "OK | "
            f"SOC={data.get('battery_capacity')}% | "
            f"PV1={data.get('pv1_charging_power')}W | "
            f"Load={data.get('ac_output_active_power')}W | "
            f"Published={published}"
        )