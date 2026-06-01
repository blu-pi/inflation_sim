
from enum import Enum
from typing import TYPE_CHECKING

from market.simulation import Simulation

if TYPE_CHECKING:
    from market.economy import Economy


class EconomyComparison:

    def __init__(self,sim: Simulation, econ_a: 'Economy', econ_b: 'Economy'):
        self.sim = sim
        self.econ_a = econ_a
        self.econ_b = econ_b
        self.related : bool = self._validate_relationship()

    def _validate_relationship(self) -> bool:
        """Check for relationship between economies, if one exists return divergence step."""
        a_ancestors = self.sim.getAncestorIds(self.econ_a.id)
        b_ancestors = self.sim.getAncestorIds(self.econ_b.id)
        #I know the following can be written in a much more compact manner BUT
        #this is simply the most readable and intuative
        if self.econ_a.id == self.econ_b.id:
            return True
        if self.econ_a.id in b_ancestors:
            return True
        if self.econ_b.id in a_ancestors:
            return True
        if len(set(a_ancestors & set(b_ancestors))) > 0:
            return True
        return False
    
