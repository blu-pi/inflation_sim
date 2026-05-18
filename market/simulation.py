
from market.economy import Economy
from market.input.sim_args import ArgDict


DEFAULT_GROUP_COLORS = [
    "#5c6bc0", "#26a69a", "#ef5350", "#ffb74d",
    "#ab47bc", "#66bb6a", "#ec407a", "#42a5f5",
]


class EconomyGroup:

    def __init__(self, id : int, name : str, members : list[Economy], color : str = "#5c6bc0"):
        self.id = id
        self.name = name
        self.members = members
        self.color = color

    def setName(self, new_name : str) -> None:
        self.name = new_name

    def setColor(self, color : str) -> None:
        self.color = color

    def addMember(self, new_member : Economy) -> None:
        self.members.append(new_member)

    def absorbGroup(self, other_group : 'EconomyGroup') -> None:
        self.members.extend(other_group.members)


class Simulation:
    """
    Responsible for running economies through time-steps. Holds every economy
    created in this session, organised into one or more EconomyGroup lanes.
    """

    def __init__(self, economies : list[Economy] = None, config : dict = None):
        self.config = config
        self.economies : list[Economy] = []
        self.economy_groups : list[EconomyGroup] = []
        self._next_economy_id : int = 0
        self._next_group_id : int = 0
        if economies:
            for econ in economies:
                self.registerEconomy(econ)
                self.createGroup([econ])

    def createEconomy(self, arg_dicts : dict[str,ArgDict], group_id : int = None) -> Economy:
        """Create a new Economy and register it. If group_id is provided, attach to that group; otherwise create a fresh group containing this economy."""
        economy = Economy(arg_dicts)
        self.registerEconomy(economy)
        if group_id is not None:
            group = self.getGroupById(group_id)
            if group is not None:
                group.addMember(economy)
                return economy
        self.createGroup([economy])
        return economy

    def registerEconomy(self, economy : Economy) -> None:
        economy.id = self._next_economy_id
        self._next_economy_id += 1
        self.economies.append(economy)

    def runNextGroupTimeStep(self, target_group : EconomyGroup) -> None:
        """
        Advance every economy in the given group by one time-step.
        """
        for economy in target_group.members:
            economy.runNextTimeStep()

    def forkEconomy(self, economy : Economy) -> Economy:
        common_group = self.getGroupForEconomy(economy)
        new_economy = economy.fork()
        self.registerEconomy(new_economy)
        common_group.addMember(new_economy)
        return new_economy

    def createGroup(self, members : list[Economy], name : str = None) -> EconomyGroup:
        if name is None:
            if len(members) == 1:
                name = f"{members[0].name}-based"
            else:
                name = f"group-{self._next_group_id}"
        color = DEFAULT_GROUP_COLORS[self._next_group_id % len(DEFAULT_GROUP_COLORS)]
        group = EconomyGroup(self._next_group_id, name, members, color)
        self._next_group_id += 1
        self.economy_groups.append(group)
        return group

    def getEconomyById(self, economy_id : int) -> Economy:
        for economy in self.economies:
            if economy.id == economy_id:
                return economy
        return None

    def getGroupById(self, group_id : int) -> EconomyGroup:
        for group in self.economy_groups:
            if group.id == group_id:
                return group
        return None

    def getGroupForEconomy(self, economy : Economy) -> EconomyGroup:
        for group in self.economy_groups:
            if economy in group.members:
                return group
        return None
