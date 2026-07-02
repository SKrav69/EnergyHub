class GridStabilityEngine:
    def __init__(self, history):
        self.history = history

    def level(self):
        outage_hours_48h = self.history.outage_hours(48)

        if outage_hours_48h < 2:
            return "normal"

        if outage_hours_48h < 6:
            return "unstable"

        if outage_hours_48h < 12:
            return "risk"

        if outage_hours_48h < 24:
            return "blackout"

        return "panic"