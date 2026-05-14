
from market.economy import Economy


class Simulation:
    """
    Responsible for running economies through time-steps.
    """

    def __init__(self, economies : list[Economy], config : dict):
        self.economies = economies
        self.config = config

    def runNextLayer(self) -> None:
        """Calls Economy and runs the next layer's decisions and transactions."""
        self.economy.runNextLayer()

    def runNextTimeStep(self) -> None:
        """
        Calls Economy and runs all Layer decisions sequentially until all Layers made their decisions.
        Each time step generates a new State of the economy.
        """
        self.economy.runNextTimeStep()