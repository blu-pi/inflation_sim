import warnings

from market.products.base import Product
from market.products.structs.components import ComponentDict


class Composite(Product):
    """Essentially abstract. Any Product made of other products (excluding globals)"""

    def __init__(self, name: str = None, unit_cost: float = 0, num_preferred_components : int = 0, components : ComponentDict = None, **kwargs) -> None:
        super().__init__(name, unit_cost)
        self.components = components
        self.num_preferred_components = num_preferred_components

    def hasComponents(self) -> bool:
        return self.components is not None
    
    def setComponents(self, components : ComponentDict) -> None:
        self.components = components

    def changeWeight(self, target : Product, new_weight : int) -> None:
        self.components.changeWeight(target, new_weight)

    def getComponentCost(self) -> float:
        """Return total production cost of components"""
        if self.components is None:
            warnings.warn("{} has no components. Returning 0.".format(self.getDisplayName()))
            return 0
        return self.components.getTotalCost()
    
    def getComponentPrice(self) -> float:
        if self.components is None:
            warnings.warn("{} has no components. Returning 0.".format(self.getDisplayName()))
            return 0
        return self.components.getTotalPrice()

    def findSupplyChainCost(self) -> float:
        """
        THIS IS A TOOL FOR DATA ANALYSIS ONLY!
        Calculates total cost of production for this product's entire supply chain.
        total_cost = unit_cost + component_cost + cost of global products.
        Doesn't require published prices (so no time-steps needed) but expensive recursive call.
        """
        total_cost = super().findTotalCost()
        warnings.warn("Expensive and unnessacary call to find total costs for components of a composite product. This better not be called during simulation runtime >=/.")
        total_cost += self.getComponentCost()
        return total_cost

    def findTotalCost(self, report : bool = True) -> float:
        """
        Find total cost of production incurred by this Composite product based on published prices of it's components.
        Used to make accurate simulation-runtime decisions.
        """
        total_cost = super().findTotalCost(report=False)
        total_cost += self.getComponentPrice()
        if report:
            self.total_cost_history.append(total_cost)
        return total_cost