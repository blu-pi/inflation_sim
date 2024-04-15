

class Layer:
    """Manages collections of Products."""

    #TODO add arg for product type contained within layer
    def __init__(self, layer_name : str, products : dict, parent_layer : 'Layer' = None) -> None:
        self.layer_name = layer_name
        self.products = products
        self.parent = parent_layer

    def setParentLayer(self, parent_layer : 'Layer') -> None:
        self.parent = parent_layer