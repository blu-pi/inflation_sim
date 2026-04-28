
from market.products.structs.layer_connection import SymmetricalConnection


class Layer:
    """Manages collections of Products."""

    def __init__(self, layer_name : str, products : list, parent_layer : 'Layer' = None) -> None:
        self.layer_name = layer_name
        self.products = products
        self.parent = parent_layer
        self.connection = None

    def setParentLayer(self, parent_layer : 'Layer') -> None:
        self.parent = parent_layer

    def connect(self, parent : 'Layer') -> None:
        self.connection = SymmetricalConnection(self, parent)
        self.setParentLayer(parent)

    def makeDecisions(self) -> None:
        """Each product in the layer makes decisions and transactions based on its behaviour."""
        for product in self.products:
            #product.makeDecisions()
            #TODO implement products accessing their strategy and implementing it's decisions.
            pass

    def getSize(self) -> int:
        return len(self.products)
    