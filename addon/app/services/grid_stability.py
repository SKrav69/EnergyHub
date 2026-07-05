class GridStabilityEngine:
    def __init__(self, history):
        self.history = history

    def level(self):
        availability = self.history.availability_percent(48)

        if availability >= 90:
            return "normal"

        if availability >= 60:
            return "unstable"

        if availability >= 30:
            return "risk"

        return "panic"