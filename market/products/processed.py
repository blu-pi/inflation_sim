
from market.products.composites import Composite
from market.products.structs.components import ComponentDict


class ProcessedMaterial(Composite):

    LAYER_NUM = 2

    def __init__(self, name : str = None, unit_cost : float = 0, components : ComponentDict = None, **kwargs) -> None:
        super().__init__(name, unit_cost, kwargs["num_preferred_components"], components)

    def getLayerMembers(self) -> list['ProcessedMaterial']:
        return self.layer.getMembers()

    @staticmethod
    def getLayerName() -> str:
        return "Processed"