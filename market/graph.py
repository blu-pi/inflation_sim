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
        self.pos = {}
        while True:
            current_layer_num = current_products[0].LAYER_NUM
            self.nxg.add_nodes_from(current_products)
            x = 0
            for product in current_products:
                self.pos.update({product : (x * x_offset , current_layer_num * y_offset)})
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

        # Store node attributes for display
        self.node_info = self._extract_node_info()

    def _extract_node_info(self) -> dict:
        """Extract useful information about each node for display"""
        info = {}
        for node in self.nxg.nodes:
            node_info = {}
            
            # Add any relevant product attributes
            if hasattr(node, 'name'):
                node_info['name'] = node.name
            if hasattr(node, 'price'):
                node_info['price'] = node.price
            if hasattr(node, 'quantity'):
                node_info['quantity'] = node.quantity
            if hasattr(node, 'LAYER_NUM'):
                node_info['layer'] = node.LAYER_NUM
            
            info[node] = node_info
        return info