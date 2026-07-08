import time


class TelemetryFreshnessMonitor:
    def __init__(self):
        self.last_valid_telemetry_time = None

        self.previous_house_load = None
        self.house_load_unchanged_since = None

        self.status = "fresh"
        self.reason = "ok"

    def update(self, state):
        now = time.monotonic()

        if not state.valid:
            self._update_status(now)
            return

        self.last_valid_telemetry_time = now

        house_load = state.load_power

        if house_load is not None:
            if self.previous_house_load is None:
                self.previous_house_load = house_load
                self.house_load_unchanged_since = now

            elif house_load != self.previous_house_load:
                self.previous_house_load = house_load
                self.house_load_unchanged_since = now

        self._update_status(now)

    def _update_status(self, now):
        if self.last_valid_telemetry_time is None:
            self.status = "stale"
            self.reason = "no_valid_telemetry"
            return

        telemetry_age = now - self.last_valid_telemetry_time

        if telemetry_age >= 60:
            self.status = "stale"
            self.reason = "no_recent_valid_telemetry"
            return

        if self.house_load_unchanged_since is not None:
            unchanged_time = now - self.house_load_unchanged_since

            if unchanged_time >= 300:
                self.status = "warning"
                self.reason = "house_load_unchanged"
                return

        self.status = "fresh"
        self.reason = "ok"

    def update_status(self):
        self._update_status(time.monotonic())

    def mqtt_values(self):
        now = time.monotonic()

        if self.house_load_unchanged_since is None:
            unchanged_minutes = 0
        else:
            unchanged_minutes = int(
                (now - self.house_load_unchanged_since) / 60
            )

        return {
            "telemetry_freshness": self.status,
            "telemetry_freshness_reason": self.reason,
            "house_load_unchanged_minutes": unchanged_minutes,
        }