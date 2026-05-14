from market.products.base import Product


class RawMaterial(Product):

    LAYER_NUM = 1

    def __init__(self, name : str = None, unit_cost : float = 0, units_avail : int = 0, infinite_supply : bool = True, **kwargs) -> None:
        super().__init__(name, unit_cost)
        self.units_avail = units_avail
        self.infinite_supply = infinite_supply

    def getLayerMembers(self) -> list['RawMaterial']:
        return self.layer.getMembers()

    @staticmethod
    def getLayerName() -> str:
        return "Raw"