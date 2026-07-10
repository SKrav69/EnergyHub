from app.utils.logger import log


class AutopilotState:
    def __init__(self):
        self.enabled = False

    def update(self, value):
        normalized = str(value).strip().lower()

        enabled_values = {
            "on",
            "true",
            "1",
            "yes",
            "enabled",
        }

        disabled_values = {
            "off",
            "false",
            "0",
            "no",
            "disabled",
        }

        if normalized in enabled_values:
            new_state = True
        elif normalized in disabled_values:
            new_state = False
        else:
            log(f"Ignore invalid Autopilot value: {value}")
            return False

        if self.enabled != new_state:
            self.enabled = new_state
            log(f"Autopilot {'enabled' if self.enabled else 'disabled'}")

        return True

    def is_enabled(self):
        return self.enabled

    def mqtt_values(self):
        return {
            "autopilot_status": "on" if self.enabled else "off",
        }