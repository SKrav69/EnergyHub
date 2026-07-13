class HybridDecisionEngine:
    BATTERY_CAPACITY_KWH = 16.0

    def __init__(self):
        self.status = "unknown"
        self.reason = "Hybrid decision has not been evaluated yet"

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
                    f"Operating mode is {operating_mode}, "
                    "Hybrid decision not evaluated"
                ),
            )

        if battery_soc is None:
            return self._result(
                status="skipped",
                reason="Battery SOC is unavailable",
            )

        if forecast_tomorrow is None:
            return self._result(
                status="skipped",
                reason="Tomorrow solar forecast is unavailable",
            )

        if consumption_today is None:
            return self._result(
                status="skipped",
                reason="Today house consumption is unavailable",
            )

        missing_battery_energy = (
            self.BATTERY_CAPACITY_KWH
            * (100.0 - battery_soc)
            / 100.0
        )

        required_energy = (
            consumption_today
            + missing_battery_energy
        )

        if forecast_tomorrow < required_energy:
            return self._result(
                status="hybrid",
                reason=(
                    f"Forecast {forecast_tomorrow:.2f} kWh "
                    f"< required {required_energy:.2f} kWh "
                    f"(consumption {consumption_today:.2f} kWh "
                    f"+ battery refill "
                    f"{missing_battery_energy:.2f} kWh)"
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
                f"{missing_battery_energy:.2f} kWh)"
            ),
            missing_battery_energy=missing_battery_energy,
            required_energy=required_energy,
        )

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

        return {
            "status": status,
            "reason": reason,
            "request": request,
            "missing_battery_energy": missing_battery_energy,
            "required_energy": required_energy,
        }