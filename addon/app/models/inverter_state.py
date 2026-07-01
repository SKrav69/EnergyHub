from dataclasses import dataclass
from typing import Any


@dataclass
class InverterState:
    raw: dict[str, Any]

    @property
    def battery_soc(self):
        return self.raw.get("battery_capacity")

    @property
    def pv1_power(self):
        return self.raw.get("pv1_charging_power")

    @property
    def house_load(self):
        return self.raw.get("ac_output_active_power")

    @property
    def grid_voltage(self):
        return self.raw.get("ac_input_voltage")

    @property
    def battery_voltage(self):
        return self.raw.get("battery_voltage")

    @property
    def temperature(self):
        return self.raw.get("inverter_heat_sink_temperature")

    @property
    def is_grid_available(self):
        try:
            return float(self.grid_voltage) > 180
        except Exception:
            return False