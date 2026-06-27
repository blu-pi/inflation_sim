
from typing import TYPE_CHECKING

from market.products.globals import GlobalMaterial
from util.stats import DescriptiveStats, StatsCollection

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
        production_cost: float = None,
        component_weights: dict[str, float] | None = None,
    ) -> None:
        self.name = name
        self.layer_name = layer_name
        self.id = id
        self.sale_price = sale_price
        self.unit_cost = unit_cost
        self.component_weights = component_weights  # product_name -> normalised weight; None for non-composites


class LayerStats:
    """
    Per-layer aggregate statistics, backed by a StatsCollection.

    The frontend consumes ``stats.as_list()`` (a list of labelled stat dicts)
    rather than flat named properties, so adding a new metric only requires
    adding a DescriptiveStats to the collection in createFromList().
    """

    def __init__(self, layer_name: str, stats_collection: StatsCollection) -> None:
        self.layer_name = layer_name
        self.stats = stats_collection  # StatsCollection with labels "Sale Price" & "Unit Cost"

    @classmethod
    def createFromList(cls, records: list[ProductRecord]) -> 'LayerStats':
        prices = [r.sale_price for r in records]
        costs = [r.unit_cost for r in records]
        sc = StatsCollection(
            DescriptiveStats(prices, label="Sale Price"),
            DescriptiveStats(costs, label="Unit Cost"),
        )
        return cls(layer_name=records[0].layer_name, stats_collection=sc)


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
                    unit_cost = product.unit_cost,
                    production_cost = product.total_cost_history[-1] if product.total_cost_history else None
                )
                layer_records.append(record)
            layer_name = layer_records[0].layer_name
            
            layer_stats = LayerStats.createFromList(layer_records)
            self.layer_insights.update({layer_name : layer_stats})
            self.record_dict.update({layer_name : layer_records})