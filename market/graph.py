import networkx

from market.products.product_layer import Layer

class Graph:

    def __init__(self, layers : list[Layer]):
        self.layers = layers
        self.nxg = self._genNxGraph()

    def _genNxGraph(self) -> networkx.DiGraph:
        G = networkx.DiGraph()

        #TODO stuff

        return G