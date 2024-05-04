from market.products.base import Product


class RawMaterial(Product):

    LAYER_NUM = 1
    _existing = []

    def __init__(self, name : str = None, unit_cost : float = 0, units_avail : int = 0) -> None:
        super().__init__(name, unit_cost)
        self.units_avail = units_avail
        if self.name is None:
            self.setName(self.generateName())
        RawMaterial._existing.append(self)
    
    def getLayerName(self) -> str:
        return "Raw"
    
    def getAll(self) -> list:
        return self._existing