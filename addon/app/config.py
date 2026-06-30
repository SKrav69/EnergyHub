import json
from pathlib import Path


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


def load_options():
    with OPTIONS_FILE.open("r") as f:
        return json.load(f)