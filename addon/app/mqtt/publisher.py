import json

import paho.mqtt.client as mqtt

from app.config import AVAILABILITY_TOPIC, BASE_TOPIC, SENSORS
from app.utils.logger import log


def make_client(options):
    client = mqtt.Client(client_id="energy_hub_powmr")
    client.username_pw_set(options["mqtt_user"], options["mqtt_password"])
    client.will_set(AVAILABILITY_TOPIC, "offline", retain=True)
    return client


def publish_discovery(client, device_name):
    device = {
        "identifiers": ["powmr_10_2m"],
        "name": device_name,
        "manufacturer": "PowMr",
        "model": "10.2M",
    }

    for key, (name, unit, device_class, state_class) in SENSORS.items():
        unique_id = f"powmr_10_2m_{key}"

        payload = {
            "name": name,
            "unique_id": unique_id,
            "state_topic": f"{BASE_TOPIC}/{key}/state",
            "availability_topic": AVAILABILITY_TOPIC,
            "device": device,
        }

        if unit:
            payload["unit_of_measurement"] = unit
        if device_class:
            payload["device_class"] = device_class
        if state_class:
            payload["state_class"] = state_class

        topic = f"homeassistant/sensor/{unique_id}/config"
        client.publish(topic, json.dumps(payload), retain=True)

    log("MQTT discovery published")


def publish_values(client, data, previous):
    published = 0

    for key in SENSORS:
        if key not in data:
            continue

        value = data.get(key)

        if not is_valid_value(key, value, previous):
            continue

        client.publish(f"{BASE_TOPIC}/{key}/state", str(value), retain=True)
        published += 1

    client.publish(AVAILABILITY_TOPIC, "online", retain=True)
    return published


def is_valid_value(key, value, previous):
    if value is None:
        return False

    if key == "battery_capacity":
        try:
            soc = float(value)
        except Exception:
            return False

        if soc <= 0 or soc > 100:
            log(f"Skip invalid SOC: {soc}")
            return False

        prev_soc = previous.get("battery_capacity")
        if prev_soc is not None:
            try:
                prev_soc = float(prev_soc)

                if prev_soc > 50 and soc < 30:
                    log(f"Skip suspicious SOC jump: {prev_soc} -> {soc}")
                    return False

                if prev_soc - soc > 25:
                    log(f"Skip suspicious SOC drop: {prev_soc} -> {soc}")
                    return False

            except Exception:
                pass

    return True