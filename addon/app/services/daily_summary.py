import json
import time
from datetime import datetime
from pathlib import Path

from app.utils.logger import log

DAILY_SUMMARY_FILE = Path("/data/daily_summary.json")


class DailySummaryService:
    def __init__(self, grid_history):
        self.grid_history = grid_history
        self.inputs = {}
        self.last_snapshot = None
        self.history = {}
        self.load()

    def load(self):
        if not DAILY_SUMMARY_FILE.exists():
            return

        try:
            data = json.loads(DAILY_SUMMARY_FILE.read_text())
            self.history = data.get("history", {})
            self.last_snapshot = data.get("last_snapshot")
            log(f"Daily summary loaded: {len(self.history)} days")
        except Exception as e:
            log(f"Failed to load daily summary: {e}")

    def save(self):
        data = {
            "last_snapshot": self.last_snapshot,
            "history": self.history,
        }

        try:
            DAILY_SUMMARY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception as e:
            log(f"Failed to save daily summary: {e}")

    def update_input(self, key, value):
        try:
            numeric_value = round(float(value), 2)
        except Exception:
            log(f"Daily summary ignored invalid input {key}: {value}")
            return False

        self.inputs[key] = numeric_value
        log(f"Daily summary input updated: {key}={numeric_value}")

        if self.ready():
            self.snapshot()

        return True

    def ready(self):
        required = [
            "daily_house_consumption",
            "solar_forecast_today",
            "daily_solar_surplus_estimated",
        ]

        return all(key in self.inputs for key in required)

    def snapshot(self):
        today = datetime.now().strftime("%Y-%m-%d")

        snapshot = {
            "date": today,
            "timestamp": int(time.time()),
            "house_consumption_kwh": self.inputs["daily_house_consumption"],
            "solar_forecast_kwh": self.inputs["solar_forecast_today"],
            "solar_surplus_estimated_kwh": self.inputs["daily_solar_surplus_estimated"],
            "grid_availability_24h_percent": self.grid_history.availability_percent(24),
        }

        existing = self.history.get(today)

        if existing:
            same_values = (
                existing.get("house_consumption_kwh") == snapshot["house_consumption_kwh"]
                and existing.get("solar_forecast_kwh") == snapshot["solar_forecast_kwh"]
                and existing.get("solar_surplus_estimated_kwh") == snapshot["solar_surplus_estimated_kwh"]
            )

            if same_values:
                self.last_snapshot = existing
                log(f"Daily summary snapshot unchanged for {today}")
                return

        self.history[today] = snapshot
        self.last_snapshot = snapshot
        self.save()

        log(f"Daily summary snapshot stored for {today}")

    def mqtt_values(self):
        if not self.last_snapshot:
            return {}

        return {
            "daily_house_consumption": self.last_snapshot["house_consumption_kwh"],
            "daily_solar_forecast": self.last_snapshot["solar_forecast_kwh"],
            "daily_solar_surplus_estimated": self.last_snapshot["solar_surplus_estimated_kwh"],
            "daily_grid_availability": self.last_snapshot["grid_availability_24h_percent"],
        }