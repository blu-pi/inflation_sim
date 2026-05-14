
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from market.economy import Economy


class ProductRecord:
    def __init__(
        self,
        name: str,
        layer_name: str,
        id: int,
        sale_price: float,
        unit_cost: float,
        component_weights: dict[str, float] | None = None,
    ) -> None:
        self.name = name
        self.layer_name = layer_name
        self.id = id
        self.sale_price = sale_price
        self.unit_cost = unit_cost
        self.component_weights = component_weights  # product_name -> normalised weight; None for non-composites


class LayerStats:
    def __init__(
        self,
        layer_name: str,
        product_count: int,
        mean_price: float,
        std_dev_price: float,
        min_price: float,
        max_price: float,
        mean_unit_cost: float,
    ) -> None:
        self.layer_name = layer_name
        self.product_count = product_count
        self.mean_price = mean_price
        self.std_dev_price = std_dev_price
        self.min_price = min_price
        self.max_price = max_price
        self.mean_unit_cost = mean_unit_cost


class EconomySnapshot:
    """
    Store observable analytics of an economy at the point in time it was created.
    """

    def __init__(self, economy: Economy, timestamp: int):
        self.timestamp = timestamp
        for layer in economy.layers.values():
            for product in layer.getMembers():
                component_weights = None
                if product.hasComponents():
                    component_weights = {p.name: w for p, w in product.components.getNormalisedWeights().items()}

                record = ProductRecord(
                    name = product.name,
                    layer_name = product.getLayerName(),
                    id = product.getId(),
                    sale_price = product.sale_price,
                    unit_cost = product.unit_cost,
                    component_weights = component_weights
                )
                