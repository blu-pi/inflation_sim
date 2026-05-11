import warnings

from market.products.behaviour.strategy import Strategy, SimpleSupplySideStrategy

class Product:
    """Essentially abstract."""

    LAYER_NUM = 0
    total_created = 0
    class_args = None #args that apply to all class members, can be overriden by individual args
    global_members = []

    def __init__(self, name : str = None, unit_cost : float = 0, strategy : Strategy = None) -> None:
        """
        Should never be called explicitly. Only through constructor of child Classes.
        - name : str - display name of product. If None, will be generated based on layer and id.
        - unit_cost : float - arbitrary base cost of product independent of all other factors.
        - strategy : Strategy (StaticStrategy or AdaptiveStrategy) - strategy that this product will follow in terms of supply and demand behaviour.
        """
        self.name = name
        self.unit_cost = unit_cost
        self.setStrategy(strategy)
        self._id = len(self._existing)
        self.sale_price = None
        Product.total_created += 1
    
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

    def generateName(self) -> str:
        return self.getLayerName() + str(self._id)
    
    def setUnitCost(self, cost : float) -> None:
        self.unit_cost = cost

    def findSupplyChainCost(self) -> float:
        """
        THIS IS A TOOL FOR DATA ANALYSIS ONLY!
        Calculates total cost of production for this products entire supply chain.
        total_cost = unit_cost + component_cost + cost of global products (Not yet implemented).
        """
        #I should totally just get rid of this
        total_cost : float = self.unit_cost
        if self.hasComponents():
            warnings.warn("Expensive and unnessacary call to find total costs for components of a composite product. This better not be call during simulation runtime >=/.")
            total_cost += self.getComponentCost()
        #global product costs not implemented yet, but would be added here.
        return total_cost
    
    def findTotalCost(self) -> float:
        total_cost : float = self.unit_cost
        if self.hasComponents():
            total_cost += self.getComponentPrice()
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
    
    def getAllArgs(self) -> dict:
        return Product.class_args

    def getId(self) -> int:
        """ID of object within its Layer. Ids are shared across layers"""
        return self._id
    
    def getDisplayName(self) -> str:
        return "{}: {}".format(self.getLayerName(), self.getId())

    #experimental
    def __repr__(self) -> str:
        return self.getDisplayName()