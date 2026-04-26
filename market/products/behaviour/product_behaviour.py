from market.products.base import Product

#WIP - not fully implemented yet, but will eventually contain all behaviour related to production and supply of products, as well as demand and consumption of products.

class SupplyBehaviour():
    """
    Responsible for all behaviour related to production and supply of products.
    All supply behaviours should implement their own calcSalePrice method which determines the price at which producers will sell their product based on various factors.
    """

    def __init__(self, product : Product) -> None:
        self.product = product

class SimpleSupply(SupplyBehaviour):
    """
    Simple supply behaviour where producers produce as much as they can of a product regardless of demand.
    """

    def __init__(self, product : Product) -> None:
        super().__init__(product)

    def calcSalePrice(self) -> float:
        """For simple supply, sale price is just total cost of production."""
        return self.product.findTotalCost()

class DemandBehaviour():
    """
    Responsible for all behaviour related to consumption and demand of products.
    """

    def __init__(self, product : Product) -> None:
        self.product = product

class SimpleDemand(DemandBehaviour):
    """
    Simple demand behaviour where consumers will buy at any price.
    """

    def __init__(self, product : Product) -> None:
        super().__init__(product)