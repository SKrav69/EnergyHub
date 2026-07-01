import time


class GridHistoryService:
    def __init__(self):
        self.last_state = None
        self.last_change = None
        self.events = []

    def update(self, grid_available: bool):
        now = time.time()

        if self.last_state is None:
            self.last_state = grid_available
            self.last_change = now
            return

        if grid_available == self.last_state:
            return

        duration = now - self.last_change

        self.events.append(
            {
                "from": self.last_state,
                "to": grid_available,
                "duration": duration,
                "timestamp": now,
            }
        )

        self.last_state = grid_available
        self.last_change = now

    @property
    def outage_count(self):
        return len(
            [
                e
                for e in self.events
                if e["from"] is False and e["to"] is True
            ]
        )