from market.products.behaviour.strategy import Strategy, SimpleStrategy, AdaptiveStrategy

class Product:
    """Essentially abstract."""

    LAYER_NUM = 0
    total_created = 0
    class_args = None #args that apply to all class members, can be overriden by individual args

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
        Product.total_created += 1
    
    def setStrategy(self, strategy : Strategy) -> None:
        """Use default (SimpleStrategy) if no strategy provided."""
        self.strategy = SimpleStrategy(self) if strategy is None else strategy

    def setName(self, new_name : str) -> None:
        self.name = new_name

    def generateName(self) -> str:
        return self.getLayerName() + str(self._id)
    
    def setUnitCost(self, cost : float) -> None:
        self.unit_cost = cost

    def findTotalCost(self) -> float:
        """Calculates actual total cost of production includeing all potential factors.
        total_cost = unit_cost + component_cost + cost of global products (Not yet implemented).
        """
        total_cost : float = self.unit_cost
        if self.hasComponents():
            total_cost += self.getComponentCost()
        #global product costs not implemented yet, but would be added here.
        return total_cost

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