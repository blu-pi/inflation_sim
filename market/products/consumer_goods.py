
from market.products.composites import Composite
from market.products.structs.components import ComponentDict


class ConsumerProduct(Composite):

    LAYER_NUM = 3
    _existing = {}

    def __init__(self, name : str = None, unit_cost : float = 0, components : ComponentDict = None) -> None:
        super().__init__(name, unit_cost, components)
        ConsumerProduct._existing.update({name : self})

    def getLayerName(self) -> str:
        return "Consumer"
    
    def getAll(self) -> dict:
        return self._existing