from dataclasses import dataclass
from typing import Optional


@dataclass
class InverterState:
    # Communication quality
    valid: bool = True

    # Grid
    grid_available: bool = False

    # Battery
    battery_soc: Optional[float] = None
    battery_voltage: Optional[float] = None
    battery_current: Optional[float] = None

    # PV
    pv_power: Optional[float] = None

    # Load
    load_power: Optional[float] = None

    # Raw telemetry
    raw: dict | None = None