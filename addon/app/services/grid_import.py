import json
import time
from datetime import datetime
from pathlib import Path

from app.utils.logger import log


GRID_IMPORT_FILE = Path("/data/grid_import.json")
SOLAR_NOISE_FLOOR_W = 50.0


class GridImportService:
    def __init__(self):
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.daily_energy_kwh = 0.0
        self.current_power_w = 0.0
        self.last_update_monotonic = None
        self.last_saved_energy_kwh = 0.0

        self.load()

    def load(self):
        if not GRID_IMPORT_FILE.exists():
            log("Grid import history not found. Starting from 0 kWh.")
            return

        try:
            data = json.loads(
                GRID_IMPORT_FILE.read_text()
            )

            stored_date = data.get("date")
            today = datetime.now().strftime("%Y-%m-%d")

            if stored_date == today:
                self.date = stored_date
                self.daily_energy_kwh = float(
                    data.get("daily_energy_kwh", 0.0)
                )
                self.current_power_w = float(
                    data.get("current_power_w", 0.0)
                )
                self.last_saved_energy_kwh = (
                    self.daily_energy_kwh
                )

                log(
                    "Grid import loaded: "
                    f"{self.daily_energy_kwh:.3f} kWh "
                    f"for {self.date}"
                )

            else:
                self.date = today
                self.daily_energy_kwh = 0.0
                self.current_power_w = 0.0
                self.last_saved_energy_kwh = 0.0

                log(
                    "Grid import started for new day: "
                    f"{self.date}"
                )

                self.save()

        except Exception as e:
            log(
                "Failed to load grid import: "
                f"{e}"
            )

    def save(self):
        data = {
            "date": self.date,
            "daily_energy_kwh": round(
                self.daily_energy_kwh,
                6,
            ),
            "current_power_w": round(
                self.current_power_w,
                1,
            ),
            "timestamp": int(time.time()),
        }

        try:
            GRID_IMPORT_FILE.write_text(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2,
                )
            )

            self.last_saved_energy_kwh = (
                self.daily_energy_kwh
            )

        except Exception as e:
            log(
                "Failed to save grid import: "
                f"{e}"
            )

    def update(
        self,
        operating_mode,
        output_power_w,
        pv_power_w,
        battery_voltage_v,
        battery_charging_current_a,
        battery_discharge_current_a,
    ):
        self._check_new_day()

        values = (
            output_power_w,
            pv_power_w,
            battery_voltage_v,
            battery_charging_current_a,
            battery_discharge_current_a,
        )

        if any(value is None for value in values):
            self.last_update_monotonic = None
            return False

        try:
            output_power_w = float(output_power_w)
            pv_power_w = float(pv_power_w)
            battery_voltage_v = float(
                battery_voltage_v
            )
            battery_charging_current_a = float(
                battery_charging_current_a
            )
            battery_discharge_current_a = float(
                battery_discharge_current_a
            )

        except (TypeError, ValueError):
            self.last_update_monotonic = None
            return False

        battery_charging_power_w = (
            battery_voltage_v
            * battery_charging_current_a
        )

        battery_discharging_power_w = (
            battery_voltage_v
            * battery_discharge_current_a
        )

        if operating_mode in {
            "hybrid_charging",
            "panic",
        }:
            estimated_grid_power_w = (
                output_power_w
                + battery_charging_power_w
            )

        elif operating_mode == "hybrid_grid_hold":
            estimated_grid_power_w = output_power_w

        else:
            estimated_grid_power_w = (
                output_power_w
                + battery_charging_power_w
                - battery_discharging_power_w
                - pv_power_w
            )

            if estimated_grid_power_w < SOLAR_NOISE_FLOOR_W:
                estimated_grid_power_w = 0.0

        self.current_power_w = round(
            max(0.0, estimated_grid_power_w),
            1,
        )

        now_monotonic = time.monotonic()

        if self.last_update_monotonic is None:
            self.last_update_monotonic = now_monotonic
            return True

        elapsed_seconds = (
            now_monotonic
            - self.last_update_monotonic
        )

        self.last_update_monotonic = now_monotonic

        if elapsed_seconds <= 0 or elapsed_seconds > 60:
            return True

        energy_increment_kwh = (
            self.current_power_w
            * elapsed_seconds
            / 3_600_000
        )

        self.daily_energy_kwh += (
            energy_increment_kwh
        )

        if (
            self.daily_energy_kwh
            - self.last_saved_energy_kwh
            >= 0.001
        ):
            self.save()

        return True

    def _check_new_day(self):
        today = datetime.now().strftime("%Y-%m-%d")

        if today == self.date:
            return

        log(
            "Grid import day completed: "
            f"{self.date}="
            f"{self.daily_energy_kwh:.3f} kWh"
        )

        self.date = today
        self.daily_energy_kwh = 0.0
        self.current_power_w = 0.0
        self.last_update_monotonic = None
        self.last_saved_energy_kwh = 0.0

        self.save()

    def mqtt_values(self):
        return {
            "grid_import_power_estimated": round(
                self.current_power_w,
                0,
            ),
            "daily_grid_import_estimated": round(
                self.daily_energy_kwh,
                3,
            ),
        }