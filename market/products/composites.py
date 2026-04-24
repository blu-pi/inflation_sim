import warnings

from market.products.base import Product
from market.products.structs.components import ComponentDict


class Composite(Product):
    """Essentially abstract. Any Product made of other products (excluding globals)"""

    class_args = None #args that apply to all class members, can be overriden by individual args

    def __init__(self, name: str = None, unit_cost: float = 0, num_preferred_components : int = 0, components : ComponentDict = None, **kwargs) -> None:
        super().__init__(name, unit_cost)
        self.components = components
        self.num_preferred_components = num_preferred_components

    def hasComponents(self) -> bool:
        return self.components is not None
    
    def setComponents(self, components : ComponentDict) -> None:
        self.components = components

    def changeWeight(self, target : Product, new_weight : int) -> None:
        self.components.changeWeight(target, new_weight)

    def getComponentCost(self) -> float:
        if self.components is None:
            warnings.warn("{} has no components. Returning 0.".format(self.getDisplayName()))
            return 0
        return self.components.getTotalCost()

    def getAllArgs(self) -> dict:
        return super().getAllArgs() | Composite.class_args 