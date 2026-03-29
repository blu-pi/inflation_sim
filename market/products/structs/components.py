import warnings
from market.products.base import Product


class ComponentDict:
    """
    Structure representing 'ingredients' required for a Composite product.

    Weights are only normalised for data analysis!
    Simulation is run on NON-NORMALISED absolute values.
    This is simply because:
    1 - Not bothering with rounding errors and float errors, Do not want to use long float type when there is no real need.
    2 - Weights may be edited by the user during the simulation and it's more intuative to set absolute values.
        Users may also add new components mid sim, if weights are normalised it's hard for users to input new weight values
        proportionally to existing ones. It's very easy using absolute values.
    """

    def __init__(self, products : list[Product], debugMode : bool = False) -> None:
        self._components = {}
        self.debugMode = debugMode
        for prod in products:
            if not debugMode:
                assert(isinstance(prod, Product))
            self._components.update({prod : 1})

    def changeWeight(self, target : Product, new_weight : float) -> None:
        assert(new_weight > 0)
        if target not in self._components.keys():
            warnings.warn("Attempted to change weight of a product not found in component dict! Likely unwanted behaviour")
        else:
            self._components[target] = new_weight
    
    def updateWeights(self, new : dict) -> None:
        """Update multiple weights using dict"""
        for product, weight in new.items():
            self.changeWeight(product, weight)

    def getNormalisedWeights(self, use_fractions : bool = False) -> dict:
        """
        Return value is a dict and NOT a ComponentDict
        This is to ensure normalised values are never used outside of data analysis
        Essentially a product's assigned Component list should never return normalised weights
        """
        weight_total = sum(self._components.values())
        if weight_total != 1:
            out = {}
            for product, weight in self._components.items():
                out.update({product : weight / weight_total})
            return out
        else:
            return self._components
    
    def hasUniformWeights(self) -> bool:
        #small optimisation possible for potentially large ._contents dicts. Not significant for values <100 for sure.
        weights = {self._components.values()}
        return len(weights) == 1

    def getDict(self) -> dict[Product : float]:
        return self._components

    def getAll(self) -> list:
        return list(self._components.keys())
    
    def getWeight(self, component : Product) -> float:
        return self._components[component]
    
    def getComponentLayers(self) -> list:
        return [prod.LAYER_NUM for prod in self.getComponents()]
    
    def contains(self, component : Product) -> bool:
        return component in self._components.keys()