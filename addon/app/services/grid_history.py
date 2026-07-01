import json
import time
from pathlib import Path

from app.utils.logger import log


GRID_HISTORY_FILE = Path("/data/grid_history.json")


class GridHistoryService:
    def __init__(self):
        self.last_state = None
        self.last_change = None
        self.events = []
        self.load()

    def load(self):
        if not GRID_HISTORY_FILE.exists():
            return

        try:
            data = json.loads(GRID_HISTORY_FILE.read_text())
            self.last_state = data.get("last_state")
            self.last_change = data.get("last_change")
            self.events = data.get("events", [])
            log(f"Grid history loaded: {len(self.events)} events")
        except Exception as e:
            log(f"Failed to load grid history: {e}")

    def save(self):
        data = {
            "last_state": self.last_state,
            "last_change": self.last_change,
            "events": self.events,
        }

        try:
            GRID_HISTORY_FILE.write_text(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            log(f"Failed to save grid history: {e}")

    def update(self, grid_available: bool):
        now = time.time()

        if self.last_state is None:
            self.last_state = grid_available
            self.last_change = now
            self.save()
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
        self.save()

        log(
            "Grid state changed: "
            f"{'online' if grid_available else 'offline'}"
        )

    @property
    def outage_count(self):
        return len(
            [
                event
                for event in self.events
                if event["from"] is False and event["to"] is True
            ]
        )