from enum import Enum

class Product:
    """Essentially abstract."""

    LAYER_NUM = 0

    def __init__(self, name : str = None, unit_cost : float = 0) -> None:
        self.name = name
        self.unit_cost = unit_cost
    
    def setName(self, name : str) -> None:
        self.name = name
    
    def setUnitCost(self, cost : float) -> None:
        self.unit_cost = cost

    def hasComponents(self) -> bool:
        return False