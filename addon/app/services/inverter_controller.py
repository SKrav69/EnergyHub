from app.utils.logger import log


MENU_01_COMMANDS = {
    "SUB": "POP01",
    "SBU": "POP02",
}

MENU_01_QPIRI_VALUES = {
    "SUB": "Solar Utility Battery",
    "SBU": "Solar Battery Utility",
}

MENU_16_COMMANDS = {
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
            "solar": "Solar strategy: Menu 01=SBU, Menu 16=OSO",
            "hybrid_charging": (
                "Night grid charging: Menu 01=SUB, Menu 16=SNU"
            ),
            "hybrid_grid_hold": (
                "Battery charged; house remains on night grid: "
                "Menu 01=SUB, Menu 16=OSO"
            ),
            "transition_failed": (
                self.last_error or "Inverter transition failed"
            ),
        }

        return reasons.get(
            self.mode,
            "Unknown operating mode",
        )

    def set_output_priority(self, priority):
        command = MENU_01_COMMANDS.get(priority)

        if command is None:
            self.last_error = (
                f"Unsupported Menu 01 value: {priority}"
            )
            log(self.last_error)
            return False

        log(
            f"Setting Menu 01: {priority} using {command}"
        )

        if not self.inverter.set_output_source_priority(command):
            self.last_error = (
                f"Menu 01 command {command} was not acknowledged"
            )
            log(self.last_error)
            return False

        try:
            settings = self.inverter.read_settings()
        except Exception as exc:
            self.last_error = (
                f"Could not verify Menu 01={priority}: {exc}"
            )
            log(self.last_error)
            return False

        expected = MENU_01_QPIRI_VALUES[priority]
        actual = settings.get("output_source_priority")

        if actual != expected:
            self.last_error = (
                "Menu 01 verification failed: "
                f"expected={priority}, raw={actual}"
            )
            log(self.last_error)
            return False

        self.last_error = None
        log(f"Menu 01 verified: {priority}")
        return True

    def set_charger_priority(self, priority):
        command = MENU_16_COMMANDS.get(priority)

        if command is None:
            self.last_error = (
                f"Unsupported Menu 16 value: {priority}"
            )
            log(self.last_error)
            return False

        log(
            f"Setting Menu 16: {priority} using {command}"
        )

        if not self.inverter.set_charger_source_priority(command):
            self.last_error = (
                f"Menu 16 command {command} was not acknowledged"
            )
            log(self.last_error)
            return False

        # QPIRI decodes Menu 16 incorrectly on this PowMr model.
        # The verified PCP command mapping plus ACK is authoritative.
        self.known_charger_priority = priority
        self.last_error = None

        log(f"Menu 16 command accepted: {priority}")
        return True

    def enter_hybrid(self):
        self.mode = "transitioning"
        log(
            "Starting transition to Hybrid: "
            "Menu 01=SUB, Menu 16=SNU"
        )

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

        log(
            "Hybrid Charging active: "
            "Menu 01=SUB, Menu 16=SNU"
        )
        return True

    def enter_hybrid_grid_hold(self):
        self.mode = "transitioning"
        log(
            "Starting Hybrid Grid Hold: "
            "Menu 01=SUB, Menu 16=OSO"
        )

        if not self.set_output_priority("SUB"):
            self.mode = "transition_failed"
            return False

        if not self.set_charger_priority("OSO"):
            self.mode = "transition_failed"
            return False

        self.mode = "hybrid_grid_hold"
        self.last_error = None

        log(
            "Hybrid Grid Hold active: "
            "Menu 01=SUB, Menu 16=OSO"
        )
        return True

    def restore_solar(self):
        self.mode = "transitioning"
        log(
            "Starting transition to Solar: "
            "Menu 01=SBU, Menu 16=OSO"
        )

        menu_16_ok = self.set_charger_priority("OSO")
        menu_01_ok = self.set_output_priority("SBU")

        if menu_16_ok and menu_01_ok:
            self.mode = "solar"
            self.last_error = None

            log(
                "Solar active: "
                "Menu 01=SBU, Menu 16=OSO"
            )
            return True

        self.mode = "transition_failed"

        log(
            "Solar recovery incomplete: "
            f"menu_01_ok={menu_01_ok}, "
            f"menu_16_ok={menu_16_ok}"
        )

        return False