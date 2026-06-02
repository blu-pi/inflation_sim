
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from market.economy import Economy
    from market.analytics.events import ChangeEvent
    from market.simulation import Simulation

class RelationType:
    IDENTICAL = "a and b are the same economy"
    ANCESTOR = "a is ancestor of b"
    DESCENDANT = "a is descendant of b"
    COMMON_ANCESTOR = "a and b share at least one ancestor x" #but only used when no other enum is accurate
    NULL_RELATION = "a and b are not related"

class EconomyComparison:
    """Set up comparison for multiple economies. Will quietly use PairComparison when possible."""

    def __init__(self, sim: 'Simulation', target_economies: list['Economy']):
        self.sim = sim
        self.target_economies = target_economies


class EconomyPairComparison:
    """Compare aspects of 2 given economies."""

    def __init__(self,sim: 'Simulation', economy_pair: tuple['Economy']):
        self.sim = sim
        self.economies = economy_pair
        self.relation: RelationType = self._validate_relationship()
        self.shared_events: list['ChangeEvent'] = None
        self.unique_events: dict[int,list[ChangeEvent]] = None

    def _validate_relationship(self) -> RelationType:
        """Check for relationship between two economies."""
        econ_a: 'Economy' = self.economies[0]
        econ_b: 'Economy' = self.economies[1]
        a_ancestors = self.sim.getAncestorIds(econ_a.id)
        b_ancestors = self.sim.getAncestorIds(econ_b.id)
        #I know the following can be written in a much more compact manner BUT
        #this is simply the most readable and intuative
        if econ_a.id == econ_b.id:
            return RelationType.IDENTICAL
        if econ_a.id in b_ancestors:
            return RelationType.ANCESTOR
        if econ_b.id in a_ancestors:
            return RelationType.DESCENDANT
        if len(set(a_ancestors) & set(b_ancestors)) > 0:
            return RelationType.COMMON_ANCESTOR
        return RelationType.NULL_RELATION
    
    def filterEventLogs(self) -> None:
        econ_a = self.economies[0]
        log_a = econ_a.change_log.copy()
        econ_b = self.economies[1]
        log_b = econ_b.change_log.copy()

        self.shared_events = [e for e in log_a if e in log_b]
        self.unique_events = {
            econ_a.id: [e for e in log_a if e not in log_b],
            econ_b.id: [e for e in log_b if e not in log_a],
        }
