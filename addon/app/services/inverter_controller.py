import time

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

WRITE_ATTEMPTS = 3
WRITE_RETRY_DELAY_SECONDS = 1

MENU_01_VERIFY_ATTEMPTS = 3
MENU_01_VERIFY_DELAY_SECONDS = 1

MODE_SETTLE_DELAY_SECONDS = 2


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
            "unknown": (
                "Current inverter strategy is not confirmed"
            ),
            "transitioning": (
                "Inverter settings are being changed"
            ),
            "solar": (
                "Solar strategy: Menu 01=SBU, Menu 16=OSO"
            ),
            "hybrid_charging": (
                "Night grid charging: "
                "Menu 01=SUB, Menu 16=SNU"
            ),
            "hybrid_grid_hold": (
                "Battery charged; house remains on night grid: "
                "Menu 01=SUB, Menu 16=OSO"
            ),
            "panic": (
                "Emergency grid charging: "
                "Menu 01=SUB, Menu 16=SNU"
            ),
            "transition_failed": (
                self.last_error
                or "Inverter transition failed"
            ),
        }

        return reasons.get(
            self.mode,
            "Unknown operating mode",
        )

    def _settle(self):
        log(
            "Waiting for inverter to settle: "
            f"{MODE_SETTLE_DELAY_SECONDS} sec"
        )

        time.sleep(MODE_SETTLE_DELAY_SECONDS)

    def _write_menu_01(self, command, priority):
        for attempt in range(1, WRITE_ATTEMPTS + 1):
            if attempt > 1:
                time.sleep(WRITE_RETRY_DELAY_SECONDS)

            try:
                acknowledged = (
                    self.inverter
                    .set_output_source_priority(command)
                )
            except Exception as exc:
                log(
                    "Menu 01 write failed: "
                    f"attempt={attempt}/{WRITE_ATTEMPTS}, "
                    f"value={priority}, "
                    f"command={command}, "
                    f"error={exc}"
                )
                continue

            if acknowledged:
                log(
                    "Menu 01 command accepted: "
                    f"{priority} on attempt {attempt}"
                )
                return True

            log(
                "Menu 01 command not acknowledged: "
                f"attempt={attempt}/{WRITE_ATTEMPTS}, "
                f"value={priority}, "
                f"command={command}"
            )

        self.last_error = (
            f"Menu 01 command {command} was not acknowledged "
            f"after {WRITE_ATTEMPTS} attempts"
        )
        log(self.last_error)
        return False

    def _write_menu_16(self, command, priority):
        for attempt in range(1, WRITE_ATTEMPTS + 1):
            if attempt > 1:
                time.sleep(WRITE_RETRY_DELAY_SECONDS)

            try:
                acknowledged = (
                    self.inverter
                    .set_charger_source_priority(command)
                )
            except Exception as exc:
                log(
                    "Menu 16 write failed: "
                    f"attempt={attempt}/{WRITE_ATTEMPTS}, "
                    f"value={priority}, "
                    f"command={command}, "
                    f"error={exc}"
                )
                continue

            if acknowledged:
                self.known_charger_priority = priority
                self.last_error = None

                log(
                    "Menu 16 command accepted: "
                    f"{priority} on attempt {attempt}"
                )
                return True

            log(
                "Menu 16 command not acknowledged: "
                f"attempt={attempt}/{WRITE_ATTEMPTS}, "
                f"value={priority}, "
                f"command={command}"
            )

        self.last_error = (
            f"Menu 16 command {command} was not acknowledged "
            f"after {WRITE_ATTEMPTS} attempts"
        )
        log(self.last_error)
        return False

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

        if not self._write_menu_01(command, priority):
            return False

        expected_raw = MENU_01_QPIRI_VALUES[priority]
        last_actual = None
        last_exception = None

        for attempt in range(
            1,
            MENU_01_VERIFY_ATTEMPTS + 1,
        ):
            if attempt > 1:
                time.sleep(
                    MENU_01_VERIFY_DELAY_SECONDS
                )

            try:
                settings = self.inverter.read_settings()

                last_actual = settings.get(
                    "output_source_priority"
                )

                last_exception = None

            except Exception as exc:
                last_exception = exc

                log(
                    "Menu 01 verification read failed: "
                    f"attempt={attempt}/"
                    f"{MENU_01_VERIFY_ATTEMPTS}, "
                    f"error={exc}"
                )

                continue

            if last_actual == expected_raw:
                self.last_error = None

                log(
                    f"Menu 01 verified: {priority} "
                    f"on attempt {attempt}"
                )

                return True

            log(
                "Menu 01 verification mismatch: "
                f"attempt={attempt}/"
                f"{MENU_01_VERIFY_ATTEMPTS}, "
                f"expected={priority}, "
                f"raw={last_actual}"
            )

        if last_exception is not None:
            self.last_error = (
                "Menu 01 verification failed for "
                f"{priority}: {last_exception}"
            )
        else:
            self.last_error = (
                "Menu 01 verification failed: "
                f"expected={priority}, "
                f"raw={last_actual}"
            )

        log(self.last_error)
        return False

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

        return self._write_menu_16(
            command,
            priority,
        )

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

        self._settle()
        return True

    def enter_hybrid_grid_hold(self):
        self.mode = "transitioning"

        log(
            "Starting Hybrid Grid Hold: "
            "Menu 01=SUB, Menu 16=OSO"
        )

        if not self.set_output_priority("SUB"):
            hold_error = (
                self.last_error
                or "Menu 01 could not be confirmed as SUB"
            )

            log(
                "Hybrid Grid Hold transition failed: "
                f"{hold_error}. Attempting Solar recovery."
            )

            recovered = self.restore_solar()

            if recovered:
                log(
                    "Hybrid Grid Hold was not activated. "
                    "Solar recovery succeeded."
                )
            else:
                recovery_error = (
                    self.last_error
                    or "Solar recovery did not complete"
                )

                self.mode = "transition_failed"
                self.last_error = (
                    "Hybrid Grid Hold failed: "
                    f"{hold_error}; Solar recovery failed: "
                    f"{recovery_error}"
                )
                log(self.last_error)

            return False

        if not self.set_charger_priority("OSO"):
            hold_error = (
                self.last_error
                or "Menu 16 OSO command was not acknowledged"
            )

            log(
                "Hybrid Grid Hold transition partially failed: "
                f"{hold_error}. Attempting Solar recovery."
            )

            recovered = self.restore_solar()

            if recovered:
                log(
                    "Hybrid Grid Hold was not activated. "
                    "Solar recovery succeeded."
                )
            else:
                recovery_error = (
                    self.last_error
                    or "Solar recovery did not complete"
                )

                self.mode = "transition_failed"
                self.last_error = (
                    "Hybrid Grid Hold failed: "
                    f"{hold_error}; Solar recovery failed: "
                    f"{recovery_error}"
                )
                log(self.last_error)

            return False

        self.mode = "hybrid_grid_hold"
        self.last_error = None

        log(
            "Hybrid Grid Hold active: "
            "Menu 01=SUB, Menu 16=OSO"
        )

        self._settle()
        return True

    def enter_panic(self):
        self.mode = "transitioning"

        log(
            "Starting transition to Panic: "
            "Menu 01=SUB, Menu 16=SNU"
        )

        if not self.set_output_priority("SUB"):
            self.mode = "transition_failed"
            return False

        if not self.set_charger_priority("SNU"):
            log(
                "Panic transition partially failed. "
                "Attempting Solar recovery."
            )

            recovered = self.restore_solar()

            if not recovered:
                self.mode = "transition_failed"

            return False

        self.mode = "panic"
        self.last_error = None

        log(
            "Panic active: "
            "Menu 01=SUB, Menu 16=SNU"
        )

        self._settle()
        return True

    def restore_solar(self):
        self.mode = "transitioning"

        log(
            "Starting transition to Solar: "
            "Menu 01=SBU, Menu 16=OSO"
        )

        menu_16_ok = self.set_charger_priority("OSO")
        menu_16_error = None if menu_16_ok else self.last_error

        menu_01_ok = self.set_output_priority("SBU")
        menu_01_error = None if menu_01_ok else self.last_error

        if menu_16_ok and menu_01_ok:
            self.mode = "solar"
            self.last_error = None

            log(
                "Solar active: "
                "Menu 01=SBU, Menu 16=OSO"
            )

            self._settle()
            return True

        errors = []

        if menu_16_error:
            errors.append(f"Menu 16: {menu_16_error}")

        if menu_01_error:
            errors.append(f"Menu 01: {menu_01_error}")

        self.mode = "transition_failed"
        self.last_error = (
            "Solar recovery incomplete: "
            + (
                "; ".join(errors)
                if errors
                else (
                    f"menu_01_ok={menu_01_ok}, "
                    f"menu_16_ok={menu_16_ok}"
                )
            )
        )

        log(self.last_error)
        return False
