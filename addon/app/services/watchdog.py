import time


class CommunicationWatchdog:
    def __init__(self):
        self.last_success = None
        self.consecutive_errors = 0

    def success(self):
        self.last_success = time.time()
        self.consecutive_errors = 0

    def failure(self):
        self.consecutive_errors += 1

    def seconds_since_success(self):
        if self.last_success is None:
            return None

        return int(time.time() - self.last_success)

    def is_online(self):
        return self.consecutive_errors == 0

    def state(self):
        if self.last_success is None:
            return "starting"

        age = self.seconds_since_success()

        if age < 30:
            return "online"

        if age < 120:
            return "recovering"

        return "offline"