from datetime import datetime
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from app.services.grid_stability import GridStabilityEngine
from app.services.hybrid_decision import HybridDecisionEngine
from app.services.inverter_controller import InverterController
from app.services.panic_decision import PanicDecisionEngine
from app.services.telemetry_freshness import TelemetryFreshnessMonitor


class FixedAvailabilityHistory:
    def __init__(self, availability):
        self.availability = availability
        self.requested_hours = []

    def availability_percent(self, hours):
        self.requested_hours.append(hours)
        return self.availability


class FakeInverter:
    OUTPUT_PRIORITY_VALUES = {
        "POP01": "Solar Utility Battery",
        "POP02": "Solar Battery Utility",
    }

    def __init__(self, failed_charger_commands=None):
        self.failed_charger_commands = set(
            failed_charger_commands or []
        )
        self.output_priority_raw = "Solar Battery Utility"
        self.calls = []

    def set_output_source_priority(self, command):
        self.calls.append(("menu_01", command))

        raw_value = self.OUTPUT_PRIORITY_VALUES.get(command)
        if raw_value is None:
            return False

        self.output_priority_raw = raw_value
        return True

    def set_charger_source_priority(self, command):
        self.calls.append(("menu_16", command))
        return command not in self.failed_charger_commands

    def read_settings(self):
        self.calls.append(("read_settings", None))
        return {
            "output_source_priority": self.output_priority_raw,
        }


class HybridDecisionTests(unittest.TestCase):
    def setUp(self):
        self.engine = HybridDecisionEngine()

    def evaluate(self, **overrides):
        values = {
            "autopilot_enabled": True,
            "operating_mode": "solar",
            "battery_soc": 50,
            "forecast_tomorrow": 30,
            "consumption_today": 14,
        }
        values.update(overrides)
        return self.engine.evaluate(**values)

    def test_requests_hybrid_when_forecast_is_insufficient(self):
        result = self.evaluate(forecast_tomorrow=21.9)

        self.assertEqual(result["status"], "hybrid")
        self.assertEqual(result["request"], "hybrid")
        self.assertAlmostEqual(
            result["missing_battery_energy"],
            8.0,
        )
        self.assertAlmostEqual(
            result["required_energy"],
            22.0,
        )

    def test_keeps_solar_when_forecast_equals_requirement(self):
        result = self.evaluate(forecast_tomorrow=22.0)

        self.assertEqual(result["status"], "solar")
        self.assertIsNone(result["request"])
        self.assertAlmostEqual(
            result["required_energy"],
            22.0,
        )

    def test_skips_when_autopilot_is_disabled(self):
        result = self.evaluate(autopilot_enabled=False)

        self.assertEqual(result["status"], "skipped")
        self.assertIsNone(result["request"])

    def test_skips_when_another_strategy_is_active(self):
        result = self.evaluate(
            operating_mode="hybrid_grid_hold"
        )

        self.assertEqual(result["status"], "skipped")
        self.assertIsNone(result["request"])

    def test_skips_when_required_input_is_missing(self):
        result = self.evaluate(forecast_tomorrow=None)

        self.assertEqual(result["status"], "skipped")
        self.assertIsNone(result["request"])


class PanicDecisionTests(unittest.TestCase):
    def setUp(self):
        self.engine = PanicDecisionEngine()

    def evaluate(self, **overrides):
        values = {
            "autopilot_enabled": True,
            "operating_mode": "solar",
            "grid_confidence": "normal",
            "battery_soc": 60,
            "forecast_today": 20,
            "consumption_yesterday": 10,
            "now": datetime(2026, 8, 1, 13, 0),
        }
        values.update(overrides)
        return self.engine.evaluate(**values)

    def test_risk_grid_triggers_95_percent_target(self):
        result = self.evaluate(
            grid_confidence="risk",
            battery_soc=79,
            forecast_today=10,
            consumption_yesterday=10,
        )

        self.assertEqual(result["status"], "trigger_95")
        self.assertEqual(result["request"], "panic_95")
        self.assertEqual(result["target_soc"], 95)

    def test_panic_grid_uses_same_95_percent_policy(self):
        result = self.evaluate(
            grid_confidence="panic",
            battery_soc=40,
            forecast_today=5,
            consumption_yesterday=10,
        )

        self.assertEqual(result["status"], "trigger_95")
        self.assertEqual(result["target_soc"], 95)

    def test_unstable_grid_triggers_80_percent_target(self):
        result = self.evaluate(
            grid_confidence="unstable",
            battery_soc=49,
            forecast_today=10,
            consumption_yesterday=10,
        )

        self.assertEqual(result["status"], "trigger_80")
        self.assertEqual(result["request"], "panic_80")
        self.assertEqual(result["target_soc"], 80)

    def test_sufficient_soc_prevents_panic(self):
        result = self.evaluate(
            grid_confidence="risk",
            battery_soc=80,
            forecast_today=1,
            consumption_yesterday=10,
        )

        self.assertEqual(result["status"], "no_action")
        self.assertIsNone(result["request"])

    def test_sufficient_forecast_prevents_panic(self):
        result = self.evaluate(
            grid_confidence="unstable",
            battery_soc=30,
            forecast_today=12,
            consumption_yesterday=10,
        )

        self.assertEqual(result["status"], "no_action")
        self.assertIsNone(result["request"])

    def test_normal_grid_does_not_trigger_panic(self):
        result = self.evaluate(
            grid_confidence="normal",
            battery_soc=10,
            forecast_today=1,
        )

        self.assertEqual(result["status"], "no_action")
        self.assertIsNone(result["request"])

    def test_evaluation_window_boundaries(self):
        with self.subTest("12:00 is included"):
            result = self.evaluate(
                grid_confidence="risk",
                battery_soc=20,
                forecast_today=1,
                now=datetime(2026, 8, 1, 12, 0),
            )
            self.assertEqual(result["status"], "trigger_95")

        with self.subTest("23:50 is excluded"):
            result = self.evaluate(
                grid_confidence="risk",
                battery_soc=20,
                forecast_today=1,
                now=datetime(2026, 8, 1, 23, 50),
            )
            self.assertEqual(result["status"], "skipped")

    def test_active_hybrid_strategy_is_not_interrupted(self):
        result = self.evaluate(
            operating_mode="hybrid_charging",
            grid_confidence="panic",
            battery_soc=10,
            forecast_today=1,
        )

        self.assertEqual(result["status"], "skipped")
        self.assertIsNone(result["request"])


class GridStabilityTests(unittest.TestCase):
    def test_grid_confidence_thresholds(self):
        cases = (
            (100.0, "normal"),
            (90.0, "normal"),
            (89.9, "unstable"),
            (60.0, "unstable"),
            (59.9, "risk"),
            (30.0, "risk"),
            (29.9, "panic"),
            (0.0, "panic"),
        )

        for availability, expected in cases:
            with self.subTest(
                availability=availability,
                expected=expected,
            ):
                history = FixedAvailabilityHistory(
                    availability
                )
                engine = GridStabilityEngine(history)

                self.assertEqual(engine.level(), expected)
                self.assertEqual(
                    history.requested_hours,
                    [24, 48],
                )


class TelemetryFreshnessTests(unittest.TestCase):
    def test_no_valid_telemetry_is_stale(self):
        monitor = TelemetryFreshnessMonitor()
        state = SimpleNamespace(
            valid=False,
            load_power=None,
        )

        with patch(
            "app.services.telemetry_freshness.time.monotonic",
            return_value=100.0,
        ):
            monitor.update(state)

        self.assertEqual(monitor.status, "stale")
        self.assertEqual(
            monitor.reason,
            "no_valid_telemetry",
        )

    def test_valid_telemetry_becomes_stale_after_60_seconds(self):
        monitor = TelemetryFreshnessMonitor()
        state = SimpleNamespace(
            valid=True,
            load_power=500,
        )

        with patch(
            "app.services.telemetry_freshness.time.monotonic",
            return_value=100.0,
        ):
            monitor.update(state)

        self.assertEqual(monitor.status, "fresh")

        with patch(
            "app.services.telemetry_freshness.time.monotonic",
            return_value=159.9,
        ):
            monitor.update_status()

        self.assertEqual(monitor.status, "fresh")

        with patch(
            "app.services.telemetry_freshness.time.monotonic",
            return_value=160.0,
        ):
            monitor.update_status()

        self.assertEqual(monitor.status, "stale")
        self.assertEqual(
            monitor.reason,
            "no_recent_valid_telemetry",
        )

    def test_unchanged_load_is_diagnostic_not_stale(self):
        monitor = TelemetryFreshnessMonitor()
        state = SimpleNamespace(
            valid=True,
            load_power=500,
        )

        with patch(
            "app.services.telemetry_freshness.time.monotonic",
            return_value=100.0,
        ):
            monitor.update(state)

        with patch(
            "app.services.telemetry_freshness.time.monotonic",
            return_value=400.0,
        ):
            monitor.update(state)

        with patch(
            "app.services.telemetry_freshness.time.monotonic",
            return_value=400.0,
        ):
            values = monitor.mqtt_values()

        self.assertEqual(monitor.status, "fresh")
        self.assertEqual(
            values["house_load_unchanged_minutes"],
            5,
        )


class InverterControllerTests(unittest.TestCase):
    def make_controller(self, inverter=None):
        return InverterController(
            inverter or FakeInverter(),
            state_path=None,
        )

    def test_reconstructs_solar_without_writing(self):
        inverter = FakeInverter()
        controller = self.make_controller(inverter)
        controller.confirmed_mode = "solar"
        controller.known_charger_priority = "OSO"

        result = controller.reconstruct_mode("SBU")

        self.assertTrue(result)
        self.assertEqual(controller.mode, "solar")
        self.assertEqual(inverter.calls, [])

    def test_reconstructs_hybrid_grid_hold_from_context(self):
        controller = self.make_controller()
        controller.confirmed_mode = "hybrid_charging"
        controller.known_charger_priority = "OSO"

        result = controller.reconstruct_mode("SUB")

        self.assertTrue(result)
        self.assertEqual(
            controller.mode,
            "hybrid_grid_hold",
        )

    def test_reconstructs_panic_from_persisted_target(self):
        controller = self.make_controller()
        controller.confirmed_mode = "solar"
        controller.known_charger_priority = "SNU"
        controller.panic_target_soc = 95

        result = controller.reconstruct_mode("SUB")

        self.assertTrue(result)
        self.assertEqual(controller.mode, "panic")
        self.assertEqual(controller.panic_target_soc, 95)

    def test_rejects_ambiguous_startup_state(self):
        controller = self.make_controller()
        controller.confirmed_mode = "solar"
        controller.known_charger_priority = "SNU"
        controller.panic_target_soc = None

        result = controller.reconstruct_mode("SUB")

        self.assertFalse(result)
        self.assertEqual(controller.mode, "inconsistent")
        self.assertIn(
            "Startup reconstruction is incomplete",
            controller.last_error,
        )

    @patch(
        "app.services.inverter_controller.time.sleep",
        return_value=None,
    )
    def test_enter_hybrid_executes_verified_transition(
        self,
        _sleep,
    ):
        inverter = FakeInverter()
        controller = self.make_controller(inverter)

        result = controller.enter_hybrid()

        self.assertTrue(result)
        self.assertEqual(
            controller.mode,
            "hybrid_charging",
        )
        self.assertIn(("menu_01", "POP01"), inverter.calls)
        self.assertIn(
            ("read_settings", None),
            inverter.calls,
        )
        self.assertIn(("menu_16", "PCP01"), inverter.calls)

    @patch(
        "app.services.inverter_controller.time.sleep",
        return_value=None,
    )
    def test_partial_hybrid_failure_recovers_to_solar(
        self,
        _sleep,
    ):
        inverter = FakeInverter(
            failed_charger_commands={"PCP01"}
        )
        controller = self.make_controller(inverter)

        result = controller.enter_hybrid()

        self.assertFalse(result)
        self.assertEqual(controller.mode, "solar")
        self.assertIn(("menu_16", "PCP02"), inverter.calls)
        self.assertIn(("menu_01", "POP02"), inverter.calls)

    def test_rejects_invalid_panic_target(self):
        controller = self.make_controller()

        self.assertFalse(controller.set_panic_target_soc(0))
        self.assertFalse(controller.set_panic_target_soc(101))
        self.assertFalse(
            controller.set_panic_target_soc("invalid")
        )
        self.assertIsNone(controller.panic_target_soc)


if __name__ == "__main__":
    unittest.main()