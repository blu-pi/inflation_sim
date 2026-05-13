
from market.products.base import Product
from market.products.types import AnyComposite, AnyProduct
from market.products.structs.layer_connection import SymmetricalConnection


class Layer:
    """Manages collections of Products."""

    def __init__(self, layer_name : str, products : list[AnyProduct], parent_layer : 'Layer' = None) -> None:
        self.layer_name = layer_name
        self.products = products
        self.parent = parent_layer
        self.connection = None

    def setParentLayer(self, parent_layer : 'Layer') -> None:
        self.parent = parent_layer

    def connect(self, parent : 'Layer') -> None:
        self.connection = SymmetricalConnection(self, parent)
        self.setParentLayer(parent)

    def wireGlobals(self, global_materials : list) -> None:
        for product in self.products:
            product.setGlobalMaterials(global_materials)

    def wireMembers(self) -> None:
        """Pass relevant info to all members post-creation"""
        i = 0
        for product in self.products:
            product._id = i
            product.layer = self
            i += 1

    def makeDecisions(self) -> None:
        """Each product in the layer makes decisions and transactions based on its behaviour."""
        for product in self.products:
            product.applyStrategy()

    def getSize(self) -> int:
        return len(self.products)
    
    def getMembers(self) -> list[AnyProduct]:
        return self.products