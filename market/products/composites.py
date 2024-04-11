from market.products.base import Product
from market.products.structs.components import ComponentDict


class Composite(Product):
    """Essentially abstract. Any Product made of other products (excluding globals)"""

    def __init__(self, name: str = None, unit_cost: float = 0, components : ComponentDict = None) -> None:
        super().__init__(name, unit_cost)
        self.components = components

    def hasComponents(self) -> bool:
        return self.components is not None