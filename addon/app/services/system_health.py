class SystemHealthMonitor:
    def __init__(self):
        self.status = "unknown"
        self.reason = "not_checked"

    def update(
        self,
        health,
        battery_health,
        telemetry_freshness,
        inverter_health,
    ):
        communication = health.state
        battery = getattr(
            battery_health,
            "status",
            "unknown",
        )
        telemetry = getattr(
            telemetry_freshness,
            "status",
            "unknown",
        )
        inverter = getattr(
            inverter_health,
            "status",
            "unknown",
        )

        if communication in ["offline", "unavailable"]:
            self.status = "unavailable"
            self.reason = "communication_unavailable"
            return

        warnings = []

        if communication in [
            "starting",
            "recovering",
            "stale",
            "unknown",
        ]:
            warnings.append(
                f"communication_{communication}"
            )

        if battery == "warning":
            warnings.append(
                "battery_health_warning"
            )

        if telemetry in ["warning", "stale"]:
            warnings.append(
                "telemetry_freshness_warning"
            )

        if inverter == "warning":
            warnings.append(
                "inverter_health_warning"
            )

        if warnings:
            self.status = "warning"
            self.reason = ",".join(warnings)
            return

        self.status = "normal"
        self.reason = "ok"

    def mqtt_values(self):
        return {
            "system_health": self.status,
            "system_health_reason": self.reason,
        }