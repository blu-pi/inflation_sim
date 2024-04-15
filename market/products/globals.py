from market.products.base import Product


class GlobalMaterial(Product):
    """Products that are components in every other type of product"""

    LAYER_NUM = 0
    NAMES = ["Energy", "Labour"]

    def __init__(self, name : str = None, unit_cost : float = 0) -> None:
        super().__init__(name, unit_cost)

    def getLayerName(self) -> str:
        return "Global"
        