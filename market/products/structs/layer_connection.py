
from typing import TYPE_CHECKING

from market.products.product_layer import Layer
if TYPE_CHECKING:
    from market.products.product_layer import Layer


#RULES FOR ALL CONNECTIONS
#All 'parent_layer' products must connect to a product in the 'child_layer' at least once and vice versa

class Connection:

    def __init__(self, child_layer : Layer, parent_layer : Layer) -> None:
        self.parent_layer = parent_layer
        self.child_layer = child_layer


class SymmetricalConnection(Connection):

    def __init__(self, child_layer: Layer, parent_layer: Layer, preferred_connections : int, strict_symmetry : bool = False) -> None:
        super().__init__(child_layer, parent_layer)
        if strict_symmetry:
            assert(len(child_layer.products) % len(parent_layer.products) == 0)
            preferred_connections = len(child_layer.products) / len(parent_layer.products)
        
        target_products = {0 : self.parent_layer.products}
        for child_product in self.child_layer.products:
            pass
        #TODO carry on

