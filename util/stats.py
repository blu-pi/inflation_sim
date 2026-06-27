import statistics
from collections.abc import Iterable


class DescriptiveStats:
    """
    Descriptive statistics for a single numerical dataset, with a label.
    Low key just lightweight pandas but worse =)

    >>> ds = DescriptiveStats([2, 4, 4, 4, 5, 5, 7, 9], label="Sale Price")
    >>> ds.mean
    5.0
    >>> ds.population_stdev
    2.0
    """

    def __init__(self, data: Iterable[float], label: str = "") -> None:
        vals = list(data)
        n = len(vals)

        self.label: str = label
        self.count: int = n
        self.sum: float = sum(vals) if n else 0.0
        self.mean: float = statistics.mean(vals) if n else 0.0
        self.median: float = statistics.median(vals) if n else 0.0
        self.min: float = min(vals) if n else 0.0
        self.max: float = max(vals) if n else 0.0
        self.population_stdev: float = statistics.pstdev(vals) if n >= 2 else 0.0
        self.sample_stdev: float = statistics.stdev(vals) if n >= 2 else 0.0
        self.variance: float = statistics.pvariance(vals) if n >= 2 else 0.0

    @staticmethod
    def getChangeRate(data: list[float]) -> list[float | None]:
        """Returns None-padded slope measure at all time-steps"""
        # In this example delta = slope since it's only measured over time delta 1.
        # Slope = delta y / delta x and since delta x is always 1, slope = delta y
        out = []
        prev = None
        delta = None
        if len(data) < 2:
            return [None] * len(data)
        for value in data:
            if prev is not None:
                delta = value - prev
            prev = value
            out.append(delta)
        return out

    @staticmethod
    def getMovingAverage(data: list[float], window: int = 3) -> list[float | None]:
        """Returns None-padded simple moving average at all time-steps.

        The first ``window - 1`` entries are None because there aren't enough
        prior values to fill the window.  Subsequent entries are the unweighted
        mean of the *window* most recent values (inclusive of the current step).
        """
        out: list[float | None] = []
        if window < 1:
            raise ValueError("window must be >= 1")
        if len(data) < window:
            return [None] * len(data)
        for i in range(len(data)):
            if i < window - 1:
                out.append(None)
            else:
                window_slice = data[i - window + 1 : i + 1]
                out.append(sum(window_slice) / window)
        return out

    def __repr__(self) -> str:
        return (
            f'DescriptiveStats(label={self.label!r}, n={self.count}, '
            f'mean={self.mean:.3g}, min={self.min:.3g}, max={self.max:.3g})'
        )

    def to_dict(self) -> dict:
        """Serialize all fields to a plain dict (for JSON or display)."""
        return {
            'label': self.label,
            'count': self.count,
            'sum': self.sum,
            'mean': self.mean,
            'median': self.median,
            'min': self.min,
            'max': self.max,
            'population_stdev': self.population_stdev,
            'sample_stdev': self.sample_stdev,
            'variance': self.variance,
        }


class StatsCollection:
    """
    A labeled group of DescriptiveStats instances.

    >>> sc = StatsCollection()
    >>> sc.add([2, 4, 4, 4, 5, 5, 7, 9], label="Sale Price")
    >>> sc.add([1, 2, 3], label="Unit Cost")
    >>> sc.get("Sale Price").mean
    5.0
    >>> len(sc)
    2
    """

    def __init__(self, *stats: DescriptiveStats) -> None:
        self._stats: dict[str, DescriptiveStats] = {}
        for ds in stats:
            self._stats[ds.label] = ds

    def add(self, data: Iterable[float], label: str) -> DescriptiveStats:
        """Compute stats for *data* and store under *label*. Returns the new instance."""
        ds = DescriptiveStats(data, label=label)
        self._stats[label] = ds
        return ds

    def get(self, label: str) -> DescriptiveStats | None:
        """Return the DescriptiveStats for *label*, or None."""
        return self._stats.get(label)

    def __getitem__(self, label: str) -> DescriptiveStats:
        return self._stats[label]

    def __len__(self) -> int:
        return len(self._stats)

    def __iter__(self):
        return iter(self._stats.items())

    def __repr__(self) -> str:
        labels = ', '.join(repr(k) for k in self._stats)
        return f'StatsCollection({labels})'

    def as_list(self) -> list[dict]:
        """All stats as a list of dicts, suitable for JSON serialization."""
        return [ds.to_dict() for ds in self._stats.values()]
