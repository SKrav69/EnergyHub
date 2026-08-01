class InverterHealthMonitor:
    IGNORED_KEYS = {
        "_command",
        "_command_description",
        "reserved",
    }

    def __init__(self):
        self.status = "unknown"
        self.reason = "not_checked"

    def update(self, data):
        if not data:
            self.status = "warning"
            self.reason = "warning_read_failed"
            return

        active = []

        for key, value in data.items():
            if key in self.IGNORED_KEYS:
                continue

            if str(value) == "1":
                active.append(key)

        if active:
            self.status = "warning"
            self.reason = ",".join(active)
        else:
            self.status = "normal"
            self.reason = "ok"

    def failure(self):
        self.status = "warning"
        self.reason = "warning_read_failed"

    def mqtt_values(self):
        return {
            "inverter_health": self.status,
            "inverter_health_reason": self.reason,
        }