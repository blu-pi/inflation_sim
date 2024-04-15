from market.products.base import Product


class RawMaterial(Product):

    LAYER_NUM = 1
    _existing = {}

    def __init__(self, name : str = None, unit_cost : float = 0, units_avail : int = 0) -> None:
        super().__init__(name, unit_cost)
        self.units_avail = units_avail
        RawMaterial._existing.update({name : self})
    
    def getLayerName(self) -> str:
        return "Raw"
    
    def getAll(self) -> dict:
        return self._existing