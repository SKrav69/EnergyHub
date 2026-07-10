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
        self.known_charger_priority = "unknown"
        self.last_error = None

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
                f"Output priority command {command} was not acknowledged"
            )
            log(self.last_error)
            return False

        try:
            settings = self.inverter.read_settings()
        except Exception as exc:
            self.last_error = (
                f"Could not verify output priority {priority}: {exc}"
            )
            log(self.last_error)
            return False

        expected = OUTPUT_QPIRI_VALUES[priority]
        actual = settings.get("output_source_priority")

        if actual != expected:
            self.last_error = (
                f"Output priority verification failed: "
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
                f"Charger priority command {command} was not acknowledged"
            )
            log(self.last_error)
            return False

        # QPIRI decodes Setting 16 incorrectly on this inverter.
        # ACK plus the verified PCP command mapping is therefore used.
        self.known_charger_priority = priority
        self.last_error = None

        log(f"Charger source priority accepted: {priority}")
        return True

    def enter_hybrid(self):
        log("Starting transition to Hybrid: SUB + SNU")

        # Move the house to grid first.
        if not self.set_output_priority("SUB"):
            return False

        # Then allow utility charging.
        if not self.set_charger_priority("SNU"):
            log(
                "Hybrid transition partially failed. "
                "Attempting Solar recovery."
            )
            self.restore_solar()
            return False

        log("Hybrid configuration active: SUB + SNU")
        return True

    def restore_solar(self):
        log("Starting transition to Solar: SBU + OSO")

        # Stop utility charging first.
        charger_ok = self.set_charger_priority("OSO")

        # Then return loads to Solar/Battery priority.
        output_ok = self.set_output_priority("SBU")

        if charger_ok and output_ok:
            log("Solar configuration active: SBU + OSO")
            return True

        log(
            "Solar recovery incomplete: "
            f"charger_ok={charger_ok}, output_ok={output_ok}"
        )
        return False