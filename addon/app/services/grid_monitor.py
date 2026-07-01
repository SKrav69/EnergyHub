from app.models.inverter_state import InverterState


class GridMonitor:
    def __init__(self):
        self.grid_available = False

    def update(self, state: InverterState):
        self.grid_available = state.is_grid_available

    @property
    def is_available(self):
        return self.grid_available