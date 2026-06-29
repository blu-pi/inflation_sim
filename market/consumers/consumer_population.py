
from market.consumers.consumer_segment import ConsumerSegment
from market.products.product_layer import Layer


class ConsumerPopulation:
    """
    Mirrors Layer but for consumers. 
    Usually there is only 1 population per economy but even if not they don't connect to each other.
    """

    def __init__(self, name: str, segments: list[ConsumerSegment], target_layer: Layer):
        self.name = name
        self.segments = segments
        self.target_layer = target_layer