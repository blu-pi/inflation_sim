
from market.consumers.demand_map import DemandMap
from market.products.types import AnyProduct
from util.priority import Priority


class ConsumerSegment:
    """
    Mirror of basic Product class but for consumers. Individual consumers not used, treated as group with shared budget.
    """

    def __init__(self, name: str, budget: float, size: int, mapping: DemandMap):
        self.name = name
        self.budget = budget
        self.size = size

    