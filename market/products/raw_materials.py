from market.products.base import Product


class RawMaterial(Product):

    LAYER_NUM = 1
    _existing = []
    class_args = None #args that apply to all class members, can be overriden by individual args

    def __init__(self, name : str = None, unit_cost : float = 0, units_avail : int = 0) -> None:
        super().__init__(name, unit_cost)
        self.units_avail = units_avail
        if self.name is None:
            self.setName(self.generateName())
        RawMaterial._existing.append(self)
    
    @staticmethod
    def getLayerName() -> str:
        return "Raw"
    
    @staticmethod
    def getAll() -> list:
        return RawMaterial._existing
    
    def getAllArgs(self) -> dict:
        return super().getAllArgs() | self.class_args