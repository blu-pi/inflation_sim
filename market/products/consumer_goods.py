
from market.products.composites import Composite
from market.products.structs.components import ComponentDict


class ConsumerProduct(Composite):

    LAYER_NUM = 3
    _existing = []

    def __init__(self, name : str = None, unit_cost : float = 0, components : ComponentDict = None) -> None:
        super().__init__(name, unit_cost, components)
        if name is None:
            self.setName(self.generateName())
        ConsumerProduct._existing.append(self)

    def getLayerName(self) -> str:
        return "Consumer"
    
    def getAll(self) -> list:
        return self._existing