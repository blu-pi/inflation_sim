
import random
from typing import TYPE_CHECKING

from market.products.structs.components import ComponentDict
if TYPE_CHECKING:
    from market.products.product_layer import Layer


#RULES FOR ALL CONNECTIONS
#All 'parent_layer' products must connect to a product in the 'child_layer' at least once and vice versa

class Connection:

    def __init__(self, child_layer : 'Layer', parent_layer : 'Layer') -> None:
        self.parent_layer = parent_layer
        self.child_layer = child_layer


class SymmetricalConnection(Connection):
    """A connection between 2 layers where each Product has the same (+-1) amount of connections."""

    def __init__(self, child_layer: 'Layer', parent_layer: 'Layer', preferred_connections : int = 0) -> None:
        super().__init__(child_layer, parent_layer)
        self.preferred_connections = preferred_connections
        parent_product = self.parent_layer.products[0]
        child_product = self.child_layer.products[0]
        if self.preferred_connections == 0:
            #check num components argument from pre-defined arg dict tied to the Composite class.
            self.preferred_connections = parent_product.getAllArgs()["num_preferred_components"]

        min_connections = 1
        if len(child_layer.products) < len(parent_layer.products):
            min_connections = len(child_layer.products) // len(parent_layer.products)
            min_connections += 1
        
        if self.preferred_connections < min_connections:
            self.preferred_connections = min_connections
        
        #TODO faulty
        target_products = {0 : self.parent_layer.products.copy()}
        for child_product in self.child_layer.products:
            components = []
            for x in range(self.preferred_connections): #had a max clause why?
                min_key = min(target_products.keys())
                potential = target_products[min_key]
                print(len(potential))
                random.shuffle(potential)
                chosen = potential.pop(0)
                components.append(chosen)
                #dont overwrite here #TODO
                target_products.update({min_key + 1 : chosen})
                if target_products[min_key] == []:
                    print("happened")
                    del target_products[min_key]
            comp_dict = ComponentDict(components)
            child_product.setComponents(comp_dict)