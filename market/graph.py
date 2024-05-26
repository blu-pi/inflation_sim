import networkx as nx
import matplotlib.pyplot as plt

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from market.products.product_layer import Layer

class Graph:

    def __init__(self, consumer_layer : 'Layer'):
        self.consumer_layer = consumer_layer
        self.nxg = nx.DiGraph()
        self._populate()

    def _populate(self) -> None:
        self.nxg.add_nodes_from(self.consumer_layer)
        nx.draw(self.nxg, with_labels=True)
        plt.show()