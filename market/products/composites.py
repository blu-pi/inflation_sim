import warnings

from market.products.base import Product
from market.products.structs.components import ComponentDict


class Composite(Product):
    """Essentially abstract. Any Product made of other products (excluding globals)"""

    class_args = None #args that apply to all class members, can be overriden by individual args

    def __init__(self, name: str = None, unit_cost: float = 0, components : ComponentDict = None) -> None:
        super().__init__(name, unit_cost)
        self.components = components

    def hasComponents(self) -> bool:
        return self.components is not None
    
    def setComponents(self, components : ComponentDict) -> None:
        self.components = components

    def changeWeight(self, target : Product, new_weight : int) -> None:
        self.components.changeWeight(target, new_weight)

    def getAllArgs(self) -> dict:
        return super().getAllArgs() | self.class_args