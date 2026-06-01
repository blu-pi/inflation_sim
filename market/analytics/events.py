
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from market.products.types import AnyProduct, AnyComposite


class ChangeEventType(Enum):
    UNIT_COST_CHANGED = "unit_cost_changed"
    WEIGHT_CHANGED = "weight_changed"
    VERTEX_ADDED = "vertex_added" #not used right now
    VERTEX_REMOVED = "vertex_removed" #not used right now


class ChangeEvent:

    def __init__(self, timestamp: int, event_type: ChangeEventType, product_name: str, layer_name: str) -> None:
        self.timestamp = timestamp
        self.event_type = event_type
        self.product_name = product_name
        self.layer_name = layer_name


class AttributeChange(ChangeEvent):

    def __init__(self, timestamp: int, event_type: ChangeEventType, product_name: str, layer_name: str,
                 old_value: float, new_value: float, component_name: str = None) -> None:
        super().__init__(timestamp, event_type, product_name, layer_name)
        self.old_value = old_value
        self.new_value = new_value
        self.component_name = component_name


class GraphStructureChange(ChangeEvent):

    def __init__(self, timestamp: int, event_type: ChangeEventType, product_name: str, layer_name: str,
                 other_product: str = None, other_layer: str = None) -> None:
        super().__init__(timestamp, event_type, product_name, layer_name)
        self.other_product = other_product
        self.other_layer = other_layer
