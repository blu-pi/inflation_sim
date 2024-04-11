
from market.products.composites import Composite
from market.products.structs.components import ComponentList


class ConsumerProduct(Composite):

    LAYER_NUM = 3

    def __init__(self, name : str = None, unit_cost : float = 0, components : ComponentList = None) -> None:
        super().__init__(name, unit_cost)
        self.components = components