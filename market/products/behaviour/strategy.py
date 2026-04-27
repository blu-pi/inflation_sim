
from typing import TYPE_CHECKING, Union

from market.products.behaviour.product_behaviour import DemandBehaviour, SupplyBehaviour, SimpleDemand, SimpleSupply

if TYPE_CHECKING:
    from market.products.base import Product

Strategy = Union['SimpleStrategy', 'AdaptiveStrategy'] #type hint for strategy types. Add more strategy types as they are implemented.

class StaticStrategy():
    """
    Responsible for combining demand and supply behaviours of a product.
    """

    def __init__(self, product : 'Product', supply_behaviour : SupplyBehaviour, demand_behaviour : DemandBehaviour) -> None:
        self.product = product
        self.supply_behaviour = supply_behaviour
        self.demand_behaviour = demand_behaviour

class SimpleStrategy(StaticStrategy):
    """
    Simple strategy where producers produce as much as they can of a product regardless of demand, and consumers will buy at any price.
    """

    def __init__(self, product : 'Product') -> None:
        super().__init__(product, SimpleSupply(product), SimpleDemand(product))


class AdaptiveStrategy():
    """
    Responsible for applying varying strategies that aren't simple hard-coded behaviours. 
    Might eventually include goal-oriented decision making and learning from past behaviour to adapt strategy over time.
    NOT YET IMPLEMENTED.
    """

    def __init__(self, product : 'Product') -> None:
        self.product = product