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


def publish_grid_history(client, history, stability):
    values = {
        "grid_available_hours_24h": history.available_hours(24),
        "grid_available_hours_48h": history.available_hours(48),
        "grid_outage_hours_24h": history.outage_hours(24),
        "grid_availability_percent_24h": history.availability_percent(24),
        "grid_confidence_level": stability.level(),
    }

    for key, value in values.items():
        client.publish(f"{BASE_TOPIC}/{key}/state", str(value), retain=True)


def publish_grid_discovery(client):
    device = {
        "identifiers": ["energyhub_core"],
        "name": "EnergyHub",
        "manufacturer": "EnergyHub",
        "model": "Core",
    }

    sensors = {
        "grid_available_hours_24h": ("Grid Available 24h", "h", None, "measurement"),
        "grid_available_hours_48h": ("Grid Available 48h", "h", None, "measurement"),
        "grid_outage_hours_24h": ("Grid Outage 24h", "h", None, "measurement"),
        "grid_availability_percent_24h": ("Grid Availability 24h", "%", None, "measurement"),
        "grid_confidence_level": ("Grid Confidence", None, None, None),
    }

    for key, (name, unit, device_class, state_class) in sensors.items():
        payload = {
            "name": name,
            "unique_id": f"energyhub_{key}",
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

        topic = f"homeassistant/sensor/energyhub_{key}/config"
        client.publish(topic, json.dumps(payload), retain=True)

    log("Grid MQTT discovery published")


def publish_health(client, health):
    for key, value in health.mqtt_values().items():
        client.publish(f"{BASE_TOPIC}/{key}/state", str(value), retain=True)


def publish_health_discovery(client):
    device = {
        "identifiers": ["energyhub_core"],
        "name": "EnergyHub",
        "manufacturer": "EnergyHub",
        "model": "Core",
    }

    sensors = {
        "communication_status": ("Communication Status", None, None, None),
    }

    for key, (name, unit, device_class, state_class) in sensors.items():
        payload = {
            "name": name,
            "unique_id": f"energyhub_{key}",
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

        topic = f"homeassistant/sensor/energyhub_{key}/config"
        client.publish(topic, json.dumps(payload), retain=True)

    log("Health MQTT discovery published")


def publish_daily_summary(client, daily_summary):
    for key, value in daily_summary.mqtt_values().items():
        client.publish(f"{BASE_TOPIC}/{key}/state", str(value), retain=True)


def publish_daily_summary_discovery(client):
    device = {
        "identifiers": ["energyhub_core"],
        "name": "EnergyHub",
        "manufacturer": "EnergyHub",
        "model": "Core",
    }

    sensors = {
        "daily_house_consumption": (
            "Daily House Consumption",
            "kWh",
            "energy",
            "measurement",
        ),
        "daily_solar_forecast": (
            "Daily Solar Forecast",
            "kWh",
            "energy",
            "measurement",
        ),
        "daily_solar_surplus_estimated": (
            "Daily Solar Surplus Estimated",
            "kWh",
            "energy",
            "measurement",
        ),
        "daily_grid_availability": (
            "Daily Grid Availability",
            "%",
            None,
            "measurement",
        ),
    }

    for key, (name, unit, device_class, state_class) in sensors.items():
        payload = {
            "name": name,
            "unique_id": f"energyhub_{key}",
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

        topic = f"homeassistant/sensor/energyhub_{key}/config"
        client.publish(topic, json.dumps(payload), retain=True)

    log("Daily Summary MQTT discovery published")