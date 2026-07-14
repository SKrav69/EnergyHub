from datetime import datetime


PANIC_START_TIME = (12, 0)
PANIC_END_TIME = (23, 50)

FORECAST_SAFETY_FACTOR = 1.20

UNSTABLE_TRIGGER_SOC = 50
UNSTABLE_TARGET_SOC = 80

RISK_TRIGGER_SOC = 80
RISK_TARGET_SOC = 95


class PanicDecisionEngine:
    def __init__(self):
        self.status = "not_evaluated"
        self.reason = "Automatic Panic has not been evaluated yet"

    def evaluate(
        self,
        *,
        autopilot_enabled,
        operating_mode,
        grid_confidence,
        battery_soc,
        forecast_today,
        consumption_yesterday,
        now=None,
    ):
        current_time = now or datetime.now()

        if not autopilot_enabled:
            return self._result(
                status="skipped",
                reason="Autopilot is disabled",
            )

        if not self._inside_evaluation_window(current_time):
            return self._result(
                status="skipped",
                reason=(
                    "Outside Panic evaluation window "
                    f"{self._format_time(PANIC_START_TIME)}–"
                    f"{self._format_time(PANIC_END_TIME)}"
                ),
            )

        if operating_mode in {
            "hybrid_charging",
            "hybrid_grid_hold",
        }:
            return self._result(
                status="skipped",
                reason="Hybrid mode is active",
            )

        if operating_mode == "panic":
            return self._result(
                status="skipped",
                reason="Panic mode is already active",
            )

        if operating_mode == "transitioning":
            return self._result(
                status="skipped",
                reason="Inverter transition is in progress",
            )

        if operating_mode != "solar":
            return self._result(
                status="skipped",
                reason=(
                    f"Operating mode is {operating_mode}, "
                    "not Solar"
                ),
            )

        if not self._valid_number(battery_soc):
            return self._result(
                status="skipped",
                reason="Battery SOC is unavailable",
            )

        if not self._valid_number(forecast_today):
            return self._result(
                status="skipped",
                reason="Solar forecast today is unavailable",
            )

        if not self._valid_number(consumption_yesterday):
            return self._result(
                status="skipped",
                reason="Yesterday house consumption is unavailable",
            )

        battery_soc = float(battery_soc)
        forecast_today = float(forecast_today)
        consumption_yesterday = float(consumption_yesterday)

        conservative_consumption = (
            consumption_yesterday
            * FORECAST_SAFETY_FACTOR
        )

        # Decision order:
        # 1. Evaluation time and operating mode.
        # 2. Grid quality.
        # 3. Battery SOC threshold for that grid quality.
        # 4. Forecast shortage using yesterday's consumption +20%.
        if grid_confidence in {"risk", "panic"}:
            if battery_soc >= RISK_TRIGGER_SOC:
                return self._result(
                    status="no_action",
                    reason=(
                        f"Grid confidence={grid_confidence}, "
                        f"but SOC={battery_soc:.1f}% is sufficient "
                        f"(Panic 95% requires SOC < "
                        f"{RISK_TRIGGER_SOC}%)"
                    ),
                )

            if forecast_today >= conservative_consumption:
                return self._result(
                    status="no_action",
                    reason=(
                        f"Grid confidence={grid_confidence} and "
                        f"SOC={battery_soc:.1f}% < "
                        f"{RISK_TRIGGER_SOC}%, but forecast is "
                        f"sufficient: {forecast_today:.2f} kWh >= "
                        f"{conservative_consumption:.2f} kWh "
                        "(yesterday consumption +20%)"
                    ),
                )

            return self._result(
                status="trigger_95",
                reason=(
                    f"Grid confidence={grid_confidence}; "
                    f"SOC={battery_soc:.1f}% < "
                    f"{RISK_TRIGGER_SOC}%; "
                    f"forecast={forecast_today:.2f} kWh < "
                    f"required={conservative_consumption:.2f} kWh "
                    "(yesterday consumption +20%); "
                    f"activate Panic and charge to "
                    f"{RISK_TARGET_SOC}%"
                ),
                request="panic_95",
                target_soc=RISK_TARGET_SOC,
            )

        if grid_confidence == "unstable":
            if battery_soc >= UNSTABLE_TRIGGER_SOC:
                return self._result(
                    status="no_action",
                    reason=(
                        "Grid confidence=unstable, "
                        f"but SOC={battery_soc:.1f}% is sufficient "
                        f"(Panic 80% requires SOC < "
                        f"{UNSTABLE_TRIGGER_SOC}%)"
                    ),
                )

            if forecast_today >= conservative_consumption:
                return self._result(
                    status="no_action",
                    reason=(
                        "Grid confidence=unstable and "
                        f"SOC={battery_soc:.1f}% < "
                        f"{UNSTABLE_TRIGGER_SOC}%, but forecast is "
                        f"sufficient: {forecast_today:.2f} kWh >= "
                        f"{conservative_consumption:.2f} kWh "
                        "(yesterday consumption +20%)"
                    ),
                )

            return self._result(
                status="trigger_80",
                reason=(
                    "Grid confidence=unstable; "
                    f"SOC={battery_soc:.1f}% < "
                    f"{UNSTABLE_TRIGGER_SOC}%; "
                    f"forecast={forecast_today:.2f} kWh < "
                    f"required={conservative_consumption:.2f} kWh "
                    "(yesterday consumption +20%); "
                    f"activate Panic and charge to "
                    f"{UNSTABLE_TARGET_SOC}%"
                ),
                request="panic_80",
                target_soc=UNSTABLE_TARGET_SOC,
            )

        return self._result(
            status="no_action",
            reason=(
                f"Grid confidence={grid_confidence}; "
                "automatic Panic is not required"
            ),
        )

    def mqtt_values(self):
        return {
            "panic_decision": self.status,
            "panic_decision_reason": self.reason,
        }

    def _result(
        self,
        *,
        status,
        reason,
        request=None,
        target_soc=None,
    ):
        self.status = status
        self.reason = reason

        return {
            "status": status,
            "reason": reason,
            "request": request,
            "target_soc": target_soc,
        }

    def _inside_evaluation_window(self, current_time):
        minutes_now = (
            current_time.hour * 60
            + current_time.minute
        )

        start_minutes = (
            PANIC_START_TIME[0] * 60
            + PANIC_START_TIME[1]
        )

        end_minutes = (
            PANIC_END_TIME[0] * 60
            + PANIC_END_TIME[1]
        )

        return start_minutes <= minutes_now < end_minutes

    @staticmethod
    def _format_time(value):
        return f"{value[0]:02d}:{value[1]:02d}"

    @staticmethod
    def _valid_number(value):
        if value is None:
            return False

        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False