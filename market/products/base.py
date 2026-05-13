
from market.products.behaviour.strategy import Strategy, SimpleSupplySideStrategy

class Product:
    """Essentially abstract."""

    def __init__(self, name : str = None, unit_cost : float = 0, strategy : Strategy = None) -> None:
        """
        Should never be called explicitly. Only through constructor of child Classes.
        - name : str - display name of product. If None, will be generated based on layer and id.
        - unit_cost : float - arbitrary base cost of product independent of all other factors.
        - strategy : Strategy (StaticStrategy or AdaptiveStrategy) - strategy that this product will follow in terms of supply and demand behaviour.
        """
        self.name = name
        self.unit_cost = unit_cost
        self.global_members = []
        self.setStrategy(strategy)
        self._id = len(self._existing)
        self.sale_price = None
        Product.total_created += 1
    
    def setGlobalMaterials(self, global_materials : list) -> None:
        self.global_members = global_materials

    def setStrategy(self, strategy : Strategy) -> None:
        """Use default (SimpleSupplySideStrategy) if no strategy is provided."""
        self.strategy : Strategy = SimpleSupplySideStrategy(self) if strategy is None else strategy

    def applyStrategy(self) -> None:
        self.strategy.apply()
    
    def publishSalePrice(self, price : float) -> None:
        """
        Publishes per-unit sale price of product to market. Might in future contain a fixed supply limit that buyers must compete for.
        For now, infinite supply is assumed.
        """
        self.sale_price = price

    def setName(self, new_name : str) -> None:
        self.name = new_name
    
    def setUnitCost(self, cost : float) -> None:
        self.unit_cost = cost

    def findSupplyChainCost(self) -> float:
        """Only called by method with same name from child class. Acts as base case for recursion."""
        return self.findTotalCost()

    def findTotalCost(self) -> float:
        """Return total cost of production of this product."""
        total_cost : float = self.unit_cost
        if self not in self.global_members:
            total_cost += self.findGlobalCost()
        return total_cost
    
    def findGlobalCost(self, weightings : dict = None) -> float:
        """
        Calculates total cost of global products required for production of this product.
        For now, simply sums unit costs of all global products. 
        In future, may include weight that can be adjusted per product.
        """
        if self.global_members is None or len(self.global_members) == 0:
            return 0
        return sum([global_product.unit_cost for global_product in self.global_members]) #TODO -add weightings functionality one day mayhaps

    def hasComponents(self) -> bool:
        return False
    
    def getDisplayName(self) -> str:
        return self.name

    #experimental
    def __repr__(self) -> str:
        return self.getDisplayName()