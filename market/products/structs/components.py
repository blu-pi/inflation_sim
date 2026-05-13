import warnings
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from market.products.types import AnyComposite, AnyProduct


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

    def __init__(self, products : list['AnyProduct']) -> None:
        self._components : dict[AnyProduct, float] = {}
        for prod in products:
            self._components.update({prod : 1})

    def changeWeight(self, target : 'AnyProduct', new_weight : float) -> None:
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
        Essentially a product's assigned Component list should always returns absolute weights - not relative/normalised ones.
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
    
    def getTotalCost(self) -> float:
        """
        Expensive recursive call. Returns total cost of components based on ALL products in the supply chain of components.
        Information might not be very relevant for the simulation runtime.
        Could be used for data analysis and visualisation of supply chains after the fact, but not sure if it's worth it.
        """
        total = 0
        for product, weight in self._components.items():
            total += product.findSupplyChainCost() * weight
        return total
    
    def getTotalPrice(self) -> float:
        """
        Lighter and more useful version of getTotalCost. Returns price instead of cost which is more relevant.
        Additionally, the call is not recursive and prices are 'cached' by each product that publishes it's price to the market.
        This turns a recursive cost calculation into a simple linear-complexity lookup for prices.
        The downside - can't find prices that aren't published to the market. 
            This method can only be successfully called if all layers that come ahead in the supply chain have published prices already. 
        """
        total = 0
        for product, weight in self._components.items():
            total += product.sale_price * weight #TODO handle case where price is not published yet. For now, just assume all prices are always published before getTotalPrice is called.
        return total

    #potential rename to for clarity?
    def getDict(self) -> dict['AnyProduct' : float]:
        return self._components

    def getAll(self) -> list['AnyProduct']:
        return list(self._components.keys())
    
    def getWeight(self, component : 'AnyProduct') -> float:
        return self._components[component]
    
    def getComponentLayerNums(self) -> list:
        return [prod.LAYER_NUM for prod in self.getAll()]
    
    def contains(self, component : 'AnyProduct') -> bool:
        return component in self._components.keys()