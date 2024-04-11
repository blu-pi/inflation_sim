from ...util.priority import Priority

class DemandWeight:

    def __init__(self, val : int, priority : Priority, name : str = None) -> None:
        self.val = val
        self.priority = priority
        self.name = name