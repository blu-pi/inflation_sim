

from market.products.types import AnyProduct
from util.priority import Priority


class DemandMap:
    """
    Data structure representing priority-ordered 'shopping list' of Products for consumer use.
    Somewhat mirrors componentDict
    """

    def __init__(self, target_products: list[AnyProduct], make_nulls: bool = False):
        self.target_products = set(target_products)
        self.priority_mapping: dict[Priority,set[AnyProduct]] = {}
        self.percieved_utilities: dict[AnyProduct, list[float,Priority]] = {}
        #list[float,Priority] could be a namedtuple but it does not support type hinting

        if make_nulls:
            self._initNullMap()
        
    def _initNullMap(self) -> None:
        """No bias demand mapping"""
        self.priority_mapping[Priority.NONE] = self.target_products
        self.percieved_utilities = dict(zip(self.target_products,[0, Priority.NONE]))

    def updatePriority(self, target: AnyProduct, new_prio: Priority) -> None:
        old_prio: Priority = self.percieved_utilities.get(target)[1]
        self.percieved_utilities.get(target)[1] = new_prio
        self.priority_mapping[old_prio].discard(target)
        self.priority_mapping[new_prio].add(target)