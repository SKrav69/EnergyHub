#!/usr/bin/env python3

import json
import subprocess
import time
import traceback
from pathlib import Path

import paho.mqtt.client as mqtt


OPTIONS_FILE = Path("/data/options.json")
LAST_FILE = Path("/data/energy_hub_powmr_last.json")

BASE_TOPIC = "powmr"
AVAILABILITY_TOPIC = f"{BASE_TOPIC}/status"


SENSORS = {
    "ac_input_voltage": ("Grid Voltage", "V", "voltage", "measurement"),
    "ac_input_frequency": ("Grid Frequency", "Hz", "frequency", "measurement"),
    "ac_output_voltage": ("Output Voltage", "V", "voltage", "measurement"),
    "ac_output_frequency": ("Output Frequency", "Hz", "frequency", "measurement"),
    "ac_output_active_power": ("Output Power", "W", "power", "measurement"),
    "ac_output_apparent_power": ("Apparent Power", "VA", "apparent_power", "measurement"),
    "ac_output_load": ("Load", "%", None, "measurement"),
    "bus_voltage": ("Bus Voltage", "V", "voltage", "measurement"),
    "battery_voltage": ("Battery Voltage", "V", "voltage", "measurement"),
    "battery_voltage_from_scc": ("Battery Voltage From SCC", "V", "voltage", "measurement"),
    "battery_capacity": ("Battery SOC", "%", "battery", "measurement"),
    "battery_charging_current": ("Battery Charging Current", "A", "current", "measurement"),
    "battery_discharge_current": ("Battery Discharge Current", "A", "current", "measurement"),
    "pv1_input_voltage": ("PV1 Voltage", "V", "voltage", "measurement"),
    "pv1_input_current": ("PV1 Current", "A", "current", "measurement"),
    "pv1_charging_power": ("PV1 Power", "W", "power", "measurement"),
    "inverter_heat_sink_temperature": ("Temperature", "°C", "temperature", "measurement"),
}


def log(message):
    print(f"[Energy Hub] {message}", flush=True)


def load_options():
    with OPTIONS_FILE.open("r") as f:
        return json.load(f)


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


def read_inverter(options):
    cmd = [
        "mpp-solar",
        "-p",
        options["serial_port"],
        "-P",
        options["protocol"],
        "-c",
        options["command"],
        "-o",
        "json",
    ]

    output = subprocess.check_output(cmd, text=True, timeout=25)
    return json.loads(output)


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

    client = make_client(options)

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

    previous = {}

    while True:
        try:
            data = read_inverter(options)

            published = publish_values(client, data, previous)
            previous.update(data)

            LAST_FILE.write_text(json.dumps(data, ensure_ascii=False))

            log(
                "OK | "
                f"SOC={data.get('battery_capacity')}% | "
                f"PV1={data.get('pv1_charging_power')}W | "
                f"Load={data.get('ac_output_active_power')}W | "
                f"Published={published}"
            )

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
