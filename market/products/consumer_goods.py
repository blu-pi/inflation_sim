from collections import Counter

from market.products.composites import Composite
from market.products.structs.components import ComponentDict


class ConsumerProduct(Composite):

    LAYER_NUM = 3
    _existing = []

    def __init__(self, name : str = None, unit_cost : float = 0, components : ComponentDict = None, **kwargs) -> None:
        super().__init__(name, unit_cost, kwargs["num_preferred_components"], components)
        ConsumerProduct._existing.append(self)

    def deriveRawMaterialComposition(self) -> dict:
        """
        Derives which Raw Materials are used to create this Consumer Product.
        Also calculates the proportional weighting of each taking into account both:
        -The amount of times raw materials are used in parent products
        -The weighting of these components in their respective parent product
        Weighting will be normalised and rounded. Output purely for data analysis
        """

        raw_components = {}
        norm_components = self.components.getNormalisedWeights()
        for product, norm_weight in norm_components.items():
            product : Composite
            norm_weight : list[float] 
            norm_parent_products = product.components.getNormalisedWeights()
            norm_parent_products = {k: v * norm_weight for k, v in norm_parent_products.items()} #adjust for weight
            #Append new raw weights with existing using union. Overlapped keys have values added together. 
            raw_components = dict(Counter(norm_parent_products) + Counter(raw_components)) 
        return raw_components

    @staticmethod
    def getLayerName() -> str:
        return "Consumer"
    
    @staticmethod
    def getAll() -> list:
        return ConsumerProduct._existing