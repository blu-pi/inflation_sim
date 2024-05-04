

class Layer:
    """Manages collections of Products."""

    def __init__(self, layer_name : str, products : list, parent_layer : 'Layer' = None) -> None:
        self.layer_name = layer_name
        self.products = products
        self.parent = parent_layer

    def setParentLayer(self, parent_layer : 'Layer') -> None:
        self.parent = parent_layer

    def connect(self, parent : 'Layer') -> None:
        pass
        #TODO connection methodology