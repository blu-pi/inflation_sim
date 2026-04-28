
from market.economy import Economy


class Simulation:
    """
    Responsible for running the economy through time-steps.
    """

    def __init__(self, economy : Economy, config : dict):
        self.economy = economy
        self.config = config
        self.current_time_step = 0

    def runNextLayer(self) -> None:
        """Calls Economy and runs the next layer's decisions and transactions."""
        self.economy.runNextLayer()

    def runNextTimeStep(self) -> None:
        """
        Calls Economy and runs all Layer decisions sequentially until all Layers made their decisions.
        Each time step generates a new State of the economy.
        """
        self.economy.runNextTimeStep()
        self.current_time_step += 1