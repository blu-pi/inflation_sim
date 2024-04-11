from .base import *

class Layer:

    #TODO add arg for product type contained within layer
    def __init__(self, size : int, parent_layer : 'Layer' = None, **kwargs) -> None:
        self.size = size
        self.parent = parent_layer