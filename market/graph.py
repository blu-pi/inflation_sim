import networkx as nx
import matplotlib.pyplot as plt

from itertools import repeat
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from market.products.product_layer import Layer

class Graph:

    def __init__(self, consumer_layer : 'Layer'):
        self.consumer_layer = consumer_layer
        self.nxg = nx.DiGraph()
        self._populate()

    def _populate(self) -> None:
        y_offset = -1
        x_offset = 20

        current_products = self.consumer_layer.products
        parent_layer = self.consumer_layer.parent
        pos = {}
        while True:
            current_layer_num = current_products[0].LAYER_NUM
            self.nxg.add_nodes_from(current_products)
            x = 0
            for product in current_products:
                pos.update({product : (x * x_offset , current_layer_num * y_offset)})
                if product.hasComponents():
                    connected_products = product.components.getAll()
                    edges_list = zip(connected_products,repeat(product))
                    self.nxg.add_edges_from(edges_list)
                x += 1
            
            if current_layer_num == 1:
                break
            
            #now repeat for parent layer of original
            current_products = parent_layer.products
            parent_layer = parent_layer.parent

        nx.draw(self.nxg, with_labels=True, pos=pos)
        plt.show()