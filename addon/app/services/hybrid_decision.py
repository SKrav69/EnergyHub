class HybridDecisionEngine:
    BATTERY_CAPACITY_KWH = 16.0

    def __init__(self):
        self.status = "not_evaluated"
        self.reason = "Hybrid decision has not been evaluated yet"

        self.evaluated_soc = None
        self.evaluated_consumption = None
        self.evaluated_forecast = None
        self.missing_battery_energy = None
        self.required_energy = None

    def evaluate(
        self,
        autopilot_enabled,
        operating_mode,
        battery_soc,
        forecast_tomorrow,
        consumption_today,
    ):
        if not autopilot_enabled:
            return self._result(
                status="skipped",
                reason="Autopilot is disabled",
            )

        if operating_mode not in {
            "solar",
            "unknown",
        }:
            return self._result(
                status="skipped",
                reason=(
                    f"Operating mode is {operating_mode}; "
                    "Hybrid decision was not evaluated"
                ),
            )

        if not self._valid_number(battery_soc):
            return self._result(
                status="skipped",
                reason="Battery SOC is unavailable",
            )

        if not self._valid_number(forecast_tomorrow):
            return self._result(
                status="skipped",
                reason="Tomorrow solar forecast is unavailable",
            )

        if not self._valid_number(consumption_today):
            return self._result(
                status="skipped",
                reason="Today house consumption is unavailable",
            )

        battery_soc = float(battery_soc)
        forecast_tomorrow = float(forecast_tomorrow)
        consumption_today = float(consumption_today)

        missing_battery_energy = (
            self.BATTERY_CAPACITY_KWH
            * (100.0 - battery_soc)
            / 100.0
        )

        required_energy = (
            consumption_today
            + missing_battery_energy
        )

        self.evaluated_soc = round(battery_soc, 2)
        self.evaluated_consumption = round(
            consumption_today,
            2,
        )
        self.evaluated_forecast = round(
            forecast_tomorrow,
            2,
        )
        self.missing_battery_energy = round(
            missing_battery_energy,
            2,
        )
        self.required_energy = round(
            required_energy,
            2,
        )

        if forecast_tomorrow < required_energy:
            return self._result(
                status="hybrid",
                reason=(
                    f"Forecast {forecast_tomorrow:.2f} kWh "
                    f"< required {required_energy:.2f} kWh "
                    f"(consumption {consumption_today:.2f} kWh "
                    f"+ battery refill "
                    f"{missing_battery_energy:.2f} kWh); "
                    "activate Hybrid"
                ),
                request="hybrid",
                missing_battery_energy=missing_battery_energy,
                required_energy=required_energy,
            )

        return self._result(
            status="solar",
            reason=(
                f"Forecast {forecast_tomorrow:.2f} kWh "
                f">= required {required_energy:.2f} kWh "
                f"(consumption {consumption_today:.2f} kWh "
                f"+ battery refill "
                f"{missing_battery_energy:.2f} kWh); "
                "remain in Solar"
            ),
            missing_battery_energy=missing_battery_energy,
            required_energy=required_energy,
        )

    def mqtt_values(self):
        values = {
            "hybrid_decision": self.status,
            "hybrid_decision_reason": self.reason,
        }

        optional_values = {
            "hybrid_evaluated_soc": self.evaluated_soc,
            "hybrid_evaluated_consumption": (
                self.evaluated_consumption
            ),
            "hybrid_evaluated_forecast": (
                self.evaluated_forecast
            ),
            "hybrid_battery_refill_required": (
                self.missing_battery_energy
            ),
            "hybrid_total_energy_required": (
                self.required_energy
            ),
        }

        for key, value in optional_values.items():
            if value is not None:
                values[key] = value

        return values

    def _result(
        self,
        status,
        reason,
        request=None,
        missing_battery_energy=None,
        required_energy=None,
    ):
        self.status = status
        self.reason = reason

        if missing_battery_energy is not None:
            self.missing_battery_energy = round(
                float(missing_battery_energy),
                2,
            )

        if required_energy is not None:
            self.required_energy = round(
                float(required_energy),
                2,
            )

        return {
            "status": status,
            "reason": reason,
            "request": request,
            "missing_battery_energy": (
                self.missing_battery_energy
            ),
            "required_energy": self.required_energy,
        }

    @staticmethod
    def _valid_number(value):
        if value is None:
            return False

        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False