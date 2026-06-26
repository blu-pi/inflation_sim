import statistics
from collections.abc import Iterable


class DescriptiveStats:
    """
    Descriptive statistics for a single numerical dataset, with a label.
    Low key just pandas but worse =)

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
