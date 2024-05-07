
from market.products.composites import Composite
from market.products.structs.components import ComponentDict


class ProcessedMaterial(Composite):

    LAYER_NUM = 2
    _existing = []
    class_args = None #args that apply to all class members, can be overriden by individual args

    def __init__(self, name : str = None, unit_cost : float = 0, components : ComponentDict = None) -> None:
        super().__init__(name, unit_cost, components)
        if name is None:
            self.setName(self.generateName())
        ProcessedMaterial._existing.append(self)

    def getLayerName(self) -> str:
        return "Processed"
    
    def getAll(self) -> list:
        return self._existing
    
    def getAllArgs(self) -> dict:
        return super().getAllArgs() | self.class_args