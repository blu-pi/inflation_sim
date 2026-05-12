
from typing import TYPE_CHECKING, Union

from market.products.behaviour.product_behaviour import DemandBehaviour, SupplyBehaviour, SimpleDemand, SimpleSupply

if TYPE_CHECKING:
    from market.products.base import Product

Strategy = Union['StaticStrategy', 'AdaptiveStrategy'] #type hint for strategy types. Add more strategy types as they are implemented.

class StaticStrategy():
    """
    Responsible for combining demand and supply behaviours of a product.
    """

    def __init__(self, product : 'Product', supply_behaviour : SupplyBehaviour, demand_behaviour : DemandBehaviour) -> None:
        self.product = product
        self.supply_behaviour = supply_behaviour
        self.demand_behaviour = demand_behaviour

    def apply(self) -> None:
        """
        Attempts to apply demand behaviour then supply behaviour if available. At least 1 must be available or an error is raised.
        """
        #TODO consider offloading more to either base Product class or behaviour classes.
        if self.demand_behaviour is not None:
            #Not implemted yet
            print("Demand behaviour not implemented yet. Demand behaviour will not be applied.")
            #self.demand_behaviour.makePurchaseDecision()
        if self.supply_behaviour is not None:
            sale_price : float = self.supply_behaviour.calcSupplyPrice()
            self.product.publishSalePrice(sale_price)

class SimpleSupplySideStrategy(StaticStrategy):
    """
    Simple strategy focused on supply-side behaviour. Demand fully dependent on decisions made by supply behaviour.
    """

    def __init__(self, product : 'Product') -> None:
        super().__init__(product, SimpleSupply(product), demand_behaviour=None)


class AdaptiveStrategy():
    """
    Responsible for applying varying strategies that aren't simple hard-coded behaviours. 
    Might eventually include goal-oriented decision making and learning from past behaviour to adapt strategy over time.
    NOT YET IMPLEMENTED.
    """

    def __init__(self, product : 'Product') -> None:
        self.product = product

    def apply(self) -> None:
        """
        Attempts to apply demand behaviour then supply behaviour if available. At least 1 must be available or an error is raised.
        """
        pass