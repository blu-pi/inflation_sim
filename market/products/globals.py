from market.products.base import Product


class GlobalMaterial(Product):
    """Products that are components in every other type of product"""

    LAYER_NUM = 0
    NAMES = ["Energy", "Labour"]
    _existing = []
    class_args = None #args that apply to all class members, can be overriden by individual args

    def __init__(self, name : str = None, unit_cost : float = 0) -> None:
        super().__init__(name, unit_cost)
        if name is None:
            self.setName(self.generateName())
        GlobalMaterial._existing.append(self)

    @staticmethod
    def getLayerName() -> str:
        return "Global"
    
    @staticmethod
    def getAll() -> list:
        return GlobalMaterial._existing

    def getAllArgs(self) -> dict:
        return super().getAllArgs() | self.class_args
        