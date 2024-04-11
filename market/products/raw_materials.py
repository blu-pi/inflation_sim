from market.products.base import Product


class RawMaterial(Product):

    LAYER_NUM = 1

    def __init__(self, name : str = None, unit_cost : float = 0, units_avail : int = 0) -> None:
        super().__init__(name, unit_cost)
        self.units_avail = units_avail