class GridStabilityEngine:
    def __init__(self, history):
        self.history = history

    def level(self):
        availability_24h = self.history.availability_percent(24)
        availability_48h = self.history.availability_percent(48)

        weighted_availability = (
            availability_24h + availability_48h
        ) / 2

        if weighted_availability >= 90:
            return "normal"

        if weighted_availability >= 60:
            return "unstable"

        if weighted_availability >= 30:
            return "risk"

        return "panic"