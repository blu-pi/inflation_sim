
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
    """
    A connection between 2 layers where each Product has the same (+-1) amount of connections.
    preferred_connections is the target number of components for composite products that are in the parent_layer.
    preferred_connections arg should only be passed for testing purposes. User input is handled elsewhere.
    Passing an argument here will OVERRIDE user input and/or DEFAULT value.
    """

    def __init__(self, child_layer: 'Layer', parent_layer: 'Layer', preferred_connections : int = 0) -> None:
        super().__init__(child_layer, parent_layer)
        self.preferred_connections = preferred_connections

        parent_product = self.parent_layer.products[0]
        child_product = self.child_layer.products[0]

        if self.preferred_connections == 0:
            #check num components argument from pre-defined arg dict tied to the Composite class.
            #This is essentially the hard coded default value found in sim_args.py unless changed by user in input UI
            #(value of num_preferred_components gets overwritten)
            self.preferred_connections = child_product.getAllArgs()["num_preferred_components"] #I know it's ugly but it works
            #change to find connection from composite

        #find min_connections for legal SymmetricalConnection
        min_connections = 1
        if len(child_layer.products) < len(parent_layer.products):
            min_connections = len(child_layer.products) // len(parent_layer.products)
            min_connections += 1
        
        if self.preferred_connections < min_connections:
            self.preferred_connections = min_connections

        if self.preferred_connections > self.child_layer.getSize():
            #bad input from user - can't happen any other way
            #just try again with different settings
            exit(0)
        
        #creating connection itself
        target_products = {0 : self.parent_layer.products.copy()} #maybe 2D array? -potential optimisation?
        for child_product in self.child_layer.products:
            components = []
            for x in range(self.preferred_connections): #had a max clause why?
                min_key = min(target_products.keys())
                potential = target_products[min_key]
                random.shuffle(potential)
                chosen = potential.pop(0)
                components.append(chosen)
                if min_key + 1 not in target_products:
                    target_products.update({min_key + 1 : []})
                target_products[min_key + 1].append(chosen)
                if target_products[min_key] == []:
                    del target_products[min_key]
            comp_dict = ComponentDict(components)
            child_product.setComponents(comp_dict)
        
        self.child_layer.setParentLayer(self.parent_layer)