from app.utils.logger import log


class HealthMonitor:
    def __init__(self):
        self.communication_state = "starting"

    def update(self, watchdog):
        state = watchdog.state()

        if state != self.communication_state:
            log(
                f"EnergyHub health: Communication "
                f"{self.communication_state} -> {state}"
            )
            self.communication_state = state

    @property
    def state(self):
        return self.communication_state