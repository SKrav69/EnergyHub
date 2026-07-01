class GridStabilityEngine:
    def __init__(self, history):
        self.history = history

    def level(self):
        # Basic first version.
        # Later this will analyze outage hours over 24h/48h.
        if self.history.outage_count == 0:
            return "normal"

        if self.history.outage_count <= 2:
            return "unstable"

        if self.history.outage_count <= 5:
            return "risk"

        return "blackout"