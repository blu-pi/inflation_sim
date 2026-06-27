
import statistics
from typing import TYPE_CHECKING

from market.products.product_layer import Layer
from market.products.types import AnyProduct, ConnectedProduct

if TYPE_CHECKING:
    from market.economy import Economy


class ProductTimeSeries:
    """General product analytics over time"""

    def __init__(self, product: AnyProduct):
        self.product_name: str = product.name
        self.layer_name = product.layer.layer_name
        self.layer_based_id: int = product._id
        self.price_history: list[float] = list(product.price_history)
        self.total_cost_history: list[float] = list(product.total_cost_history)
        self.margin_history = [p - c for p, c in zip(self.price_history, self.total_cost_history)]
        self.flex_data: dict[str, list] = {k: list(v) for k, v in product.flex_data_history.items()}
        self.unit_cost: float = product.unit_cost  # history not recorded per-step; changes in economy's event log
        self.steps: int = len(product.price_history)


class LayerTimeSeries:
    """Aggregated Layer analytics over time. Based on ProductTimeSeries data (not economy snapshot).

    Built-in field aggregates (price, total_cost, margin) are precomputed at init
    and accessible via ``self.precomputed[field][agg]`` — each a ``list[float]``
    of per-step values.

    Flex-data aggregates are computed on demand via ``aggregate()``.
    """

    _BUILTIN_FIELDS = {
        'price':      'price_history',
        'total_cost': 'total_cost_history',
        'margin':     'margin_history',
    }

    _AGGS = ('mean', 'median', 'min', 'max', 'std')

    def __init__(self, layer: Layer):
        self.layer_name = layer.layer_name
        self.product_series = [ProductTimeSeries(p) for p in layer.getMembers()]
        self.steps = max((ps.steps for ps in self.product_series), default=0)
        self.precomputed: dict[str, dict[str, list[float]]] = {}
        self._precompute()

    # ---------- precomputation ----------

    def _precompute(self) -> None:
        histories = {attr: [getattr(ps, attr) for ps in self.product_series]
                     for attr in self._BUILTIN_FIELDS.values()}
        for field, attr in self._BUILTIN_FIELDS.items():
            self.precomputed[field] = {agg: [] for agg in self._AGGS}
            for step in range(self.steps):
                step_values = self._collect_step(histories[attr], step)
                if step_values:
                    self.precomputed[field]['mean'].append(statistics.mean(step_values))
                    self.precomputed[field]['median'].append(statistics.median(step_values))
                    self.precomputed[field]['min'].append(min(step_values))
                    self.precomputed[field]['max'].append(max(step_values))
                    self.precomputed[field]['std'].append(
                        statistics.pstdev(step_values) if len(step_values) >= 2 else 0.0
                    )
                else:
                    for agg in self._AGGS:
                        self.precomputed[field][agg].append(0.0)

    # ---------- flex-data on-demand ----------

    def aggregate(self, field: str, agg: str) -> list[float]:
        """Per-step aggregate for a **flex-data** field only.

        ``agg``: ``'mean'`` | ``'median'`` | ``'min'`` | ``'max'`` | ``'std'``.
        For built-in fields use ``self.precomputed[field][agg]`` directly.
        """
        agg_fn = {
            'mean':   statistics.mean,
            'median': statistics.median,
            'min':    min,
            'max':    max,
            'std':    lambda vals: statistics.pstdev(vals) if len(vals) >= 2 else 0.0,
        }[agg]

        result: list[float] = []
        flex_series = [ps.flex_data[field] for ps in self.product_series if field in ps.flex_data]
        for step in range(self.steps):
            step_values = self._collect_step(flex_series, step)
            result.append(agg_fn(step_values) if step_values else 0.0)
        return result

    # ---------- helpers ----------

    @staticmethod
    def _collect_step(series_iter, step: int) -> list[float]:
        """Collect the *step*-th value from every series that is long enough."""
        values: list[float] = []
        for series in series_iter:
            if step < len(series):
                values.append(series[step])
        return values


class EconomyTimeSeries:
    """Time-series analytics for a single economy.

    Wraps each non-global layer in a ``LayerTimeSeries``.  Built via
    ``EconomyTimeSeries(economy)`` — the economy's layers are read at
    construction time and never updated.
    """

    def __init__(self, economy: 'Economy'):
        self.economy_id = economy.id
        self.economy_name = economy.name
        self.steps = economy.current_time_step

        self.layer_series: dict[str, LayerTimeSeries] = {}
        for layer in economy.layers.values():
            members = layer.getMembers()
            if members and isinstance(members[0], ConnectedProduct):
                lts = LayerTimeSeries(layer)
                self.layer_series[lts.layer_name] = lts

    def get_product(self, layer_name: str, product_name: str) -> ProductTimeSeries | None:
        """Return the ``ProductTimeSeries`` for a specific product, or ``None``."""
        lts = self.layer_series.get(layer_name)
        if lts is None:
            return None
        for ps in lts.product_series:
            if ps.product_name == product_name:
                return ps
        return None

    def get_layer(self, layer_name: str) -> LayerTimeSeries | None:
        """Return the ``LayerTimeSeries`` for a named layer, or ``None``."""
        return self.layer_series.get(layer_name)

