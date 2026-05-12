from market.products.base import Product


class RawMaterial(Product):

    LAYER_NUM = 1
    _existing = []

    def __init__(self, name : str = None, unit_cost : float = 0, units_avail : int = 0, infinite_supply : bool = True, **kwargs) -> None:
        super().__init__(name, unit_cost)
        self.units_avail = units_avail
        self.infinite_supply = infinite_supply
        if self.name is None:
            self.setName(self.generateName())
        RawMaterial._existing.append(self)
    
    @staticmethod
    def getLayerName() -> str:
        return "Raw"
    
    @staticmethod
    def getAll() -> list:
        return RawMaterial._existing