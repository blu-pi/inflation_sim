
import statistics
from typing import TYPE_CHECKING

from market.products.globals import GlobalMaterial

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

    @classmethod
    def createFromList(cls, records: list[ProductRecord]) -> 'LayerStats':
        prices = [r.sale_price for r in records]
        return cls(
            layer_name=records[0].layer_name,
            product_count=len(records),
            mean_price=statistics.mean(prices),
            std_dev_price=statistics.pstdev(prices),
            min_price=min(prices),
            max_price=max(prices),
            mean_unit_cost=statistics.mean(r.unit_cost for r in records),
        )


class EconomySnapshot:
    """
    Store observable analytics of an economy at the time it's snapshotted.
    """

    def __init__(self, economy: 'Economy', timestamp: int):
        self.timestamp = timestamp
        self.record_dict : dict[str,list[ProductRecord]]= {} #dict[layer_name,list[ProductRecord]]
        self.layer_insights : dict[str,LayerStats] = {}
        for layer in economy.layers.values():
            if layer.getMembers() and isinstance(layer.getMembers()[0], GlobalMaterial):
                continue  #globals don't publish sale_price; mirrors Economy.runNextTimeStep
            layer_records : list[ProductRecord] = []
            for product in layer.getMembers():
                record = ProductRecord(
                    name = product.name,
                    layer_name = product.getLayerName(),
                    id = product.getId(),
                    sale_price = product.sale_price,
                    unit_cost = product.unit_cost
                )
                layer_records.append(record)
            layer_name = layer_records[0].layer_name
            
            layer_stats = LayerStats.createFromList(layer_records)
            self.layer_insights.update({layer_name : layer_stats})
            self.record_dict.update({layer_name : layer_records})