from app.utils.logger import log


OUTPUT_COMMANDS = {
    "SUB": "POP01",
    "SBU": "POP02",
}

OUTPUT_QPIRI_VALUES = {
    "SUB": "Solar Utility Battery",
    "SBU": "Solar Battery Utility",
}

CHARGER_COMMANDS = {
    "SNU": "PCP01",
    "OSO": "PCP02",
    "CSO": "PCP03",
}


class InverterController:
    def __init__(self, inverter):
        self.inverter = inverter

        self.mode = "unknown"
        self.known_charger_priority = "unknown"
        self.last_error = None

    def mqtt_values(self):
        return {
            "operating_mode": self.mode,
            "operating_mode_reason": self._mode_reason(),
        }

    def _mode_reason(self):
        reasons = {
            "unknown": "Current inverter strategy is not confirmed",
            "transitioning": "Inverter settings are being changed",
            "solar": "Normal Solar strategy: SBU + OSO",
            "hybrid_charging": "Night grid charging: SUB + SNU",
            "hybrid_grid_hold": "Battery charged; house remains on night grid",
            "transition_failed": self.last_error or "Inverter transition failed",
        }

        return reasons.get(
            self.mode,
            "Unknown operating mode",
        )

    def set_output_priority(self, priority):
        command = OUTPUT_COMMANDS.get(priority)

        if command is None:
            self.last_error = (
                f"Unsupported output source priority: {priority}"
            )
            log(self.last_error)
            return False

        log(
            f"Setting output source priority: "
            f"{priority} using {command}"
        )

        if not self.inverter.set_output_source_priority(command):
            self.last_error = (
                f"Output priority command {command} "
                "was not acknowledged"
            )
            log(self.last_error)
            return False

        try:
            settings = self.inverter.read_settings()
        except Exception as exc:
            self.last_error = (
                f"Could not verify output priority "
                f"{priority}: {exc}"
            )
            log(self.last_error)
            return False

        expected = OUTPUT_QPIRI_VALUES[priority]
        actual = settings.get("output_source_priority")

        if actual != expected:
            self.last_error = (
                "Output priority verification failed: "
                f"expected={expected}, actual={actual}"
            )
            log(self.last_error)
            return False

        self.last_error = None
        log(f"Output source priority verified: {priority}")
        return True

    def set_charger_priority(self, priority):
        command = CHARGER_COMMANDS.get(priority)

        if command is None:
            self.last_error = (
                f"Unsupported charger source priority: {priority}"
            )
            log(self.last_error)
            return False

        log(
            f"Setting charger source priority: "
            f"{priority} using {command}"
        )

        if not self.inverter.set_charger_source_priority(command):
            self.last_error = (
                f"Charger priority command {command} "
                "was not acknowledged"
            )
            log(self.last_error)
            return False

        # QPIRI decodes Setting 16 incorrectly on this inverter.
        # The verified PCP command mapping plus ACK is used instead.
        self.known_charger_priority = priority
        self.last_error = None

        log(f"Charger source priority accepted: {priority}")
        return True

    def enter_hybrid(self):
        self.mode = "transitioning"
        log("Starting transition to Hybrid: SUB + SNU")

        if not self.set_output_priority("SUB"):
            self.mode = "transition_failed"
            return False

        if not self.set_charger_priority("SNU"):
            log(
                "Hybrid transition partially failed. "
                "Attempting Solar recovery."
            )

            recovered = self.restore_solar()

            if not recovered:
                self.mode = "transition_failed"

            return False

        self.mode = "hybrid_charging"
        self.last_error = None

        log("Hybrid configuration active: SUB + SNU")
        return True

    def enter_hybrid_grid_hold(self):
        self.mode = "transitioning"
        log("Starting Hybrid Grid Hold: SUB + OSO")

        if not self.set_output_priority("SUB"):
            self.mode = "transition_failed"
            return False

        if not self.set_charger_priority("OSO"):
            self.mode = "transition_failed"
            return False

        self.mode = "hybrid_grid_hold"
        self.last_error = None

        log("Hybrid Grid Hold active: SUB + OSO")
        return True

    def restore_solar(self):
        self.mode = "transitioning"
        log("Starting transition to Solar: SBU + OSO")

        charger_ok = self.set_charger_priority("OSO")
        output_ok = self.set_output_priority("SBU")

        if charger_ok and output_ok:
            self.mode = "solar"
            self.last_error = None

            log("Solar configuration active: SBU + OSO")
            return True

        self.mode = "transition_failed"

        log(
            "Solar recovery incomplete: "
            f"charger_ok={charger_ok}, "
            f"output_ok={output_ok}"
        )

        return False