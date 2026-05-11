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
    NAMES = ["Energy", "Labour"]
    _existing = []
    class_args = None #args that apply to all class members, can be overriden by individual args

    def __init__(self, name : str = None, unit_cost : float = 0, **kwargs) -> None:
        super().__init__(name, unit_cost)
        if name is None:
            self.setName(self.generateName())
        GlobalMaterial._existing.append(self)

    @staticmethod
    def publishGlobalProducts() -> None:
        """
        Publishes existance of crteated global products to market. 
        This is necessary because they are components of all other products and thus must be 'known' to them.
        """
        Product.global_members = GlobalMaterial.getAll()

    @staticmethod
    def getLayerName() -> str:
        return "Global"
    
    @staticmethod
    def getAll() -> list:
        return GlobalMaterial._existing

    def getAllArgs(self) -> dict:
        return super().getAllArgs() | self.class_args
        