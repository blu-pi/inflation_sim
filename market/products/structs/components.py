import warnings
from market.products.base import Product


class ComponentDict:
    """Structure representing 'ingredients' required for a Composite product."""

    def __init__(self, *products : Product) -> None:
        self._components = {}
        for prod in products:
            assert(isinstance(prod, Product))
            self._components.update({prod : 1})

    def changeWeight(self, product : Product, new_weight : float) -> None:
        assert(new_weight > 0)
        if product not in self._components.keys():
            warnings.warn("Attempted to change weight of a product not found in component dict! Likely unwanted behaviour")
        else:
            self._components[product] = new_weight

    def getAllComponents(self) -> list:
        return self._components.keys()
    
    def getWeight(self, component) -> float:
        return self._components[component]
    
    def getComponentLayers(self) -> list:
        return [prod.LAYER_NUM for prod in self.getComponents()]