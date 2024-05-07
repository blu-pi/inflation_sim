

class Product:
    """Essentially abstract."""

    LAYER_NUM = 0
    total_created = 0
    class_args = None #args that apply to all class members, can be overriden by individual args

    def __init__(self, name : str = None, unit_cost : float = 0) -> None:
        self.name = name
        self.unit_cost = unit_cost
        Product.total_created += 1

    def setName(self, new_name : str) -> None:
        self.name = new_name

    def generateName(self) -> str:
        return self.getLayerName() + str(self.total_created)
    
    def setUnitCost(self, cost : float) -> None:
        self.unit_cost = cost

    def hasComponents(self) -> bool:
        return False
    
    def getAllArgs(self) -> dict:
        return self.class_args