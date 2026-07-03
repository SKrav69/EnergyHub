import time


class CommunicationWatchdog:
    def __init__(self, stale_after_seconds=60):
        self.stale_after_seconds = stale_after_seconds
        self.last_success = None
        self.consecutive_errors = 0
        self.last_state = "starting"

    def success(self):
        self.last_success = time.time()
        self.consecutive_errors = 0

    def failure(self):
        self.consecutive_errors += 1

    def seconds_since_success(self):
        if self.last_success is None:
            return None

        return int(time.time() - self.last_success)

    def state(self):
        if self.last_success is None:
            return "starting"

        if self.consecutive_errors > 0:
            age = self.seconds_since_success()

            if age is not None and age >= self.stale_after_seconds:
                return "offline"

            return "recovering"

        age = self.seconds_since_success()

        if age is not None and age >= self.stale_after_seconds:
            return "stale"

        return "online"

    def state_changed(self):
        current_state = self.state()

        if current_state != self.last_state:
            previous_state = self.last_state
            self.last_state = current_state
            return previous_state, current_state

        return None