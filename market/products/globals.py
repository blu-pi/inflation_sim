from market.products.base import Product


class GlobalMaterial(Product):
    """
    Products that are components in every other type of product. As such they represent the 'processing cost' of production.
    Automatically assigned strategies as per defaults but NEVER use them.
    Purposely excluded from component dicts of other products
    as non-composite products still use them as 'components' required for production. 
    Simply treated as an implicit cost of production that all products must pay.
    """

    LAYER_NUM = 0
    NAMES = ["Energy", "Labour"] #TODO move to txt file and actually use it.

    def __init__(self, name : str = None, unit_cost : float = 0, **kwargs) -> None:
        super().__init__(name, unit_cost)

    def getLayerMembers(self) -> list['GlobalMaterial']:
        return self.layer.getMembers()

    @staticmethod
    def getLayerName() -> str:
        return "Global"
        