

from market.products.types import AnyProduct
from util.priority import Priority


class DemandMap:
    """
    Data structure representing priority-ordered 'shopping list' of Products for consumer use.
    Somewhat mirrors componentDict
    """

    def __init__(self, target_products: list[AnyProduct], make_nulls: bool = False):
        self.target_products = set(target_products)
        self.priority_mapping: dict[Priority,set[AnyProduct]] = {}
        self.percieved_utilities: dict[AnyProduct, list[float,Priority]] = {}
        #list[float,Priority] could be a namedtuple but it does not support type hinting

        if make_nulls:
            self._initNullMap()
        
    def _initNullMap(self) -> None:
        """
        No bias demand mapping.
        Useful if sim can determine it's own priorities over time.
        Poor way to begin init for more complex mapping. (inefficient)
        """
        self.priority_mapping[Priority.NONE] = self.target_products
        self.percieved_utilities = {p: [0, Priority.NONE] for p in self.target_products}

    def updatePriority(self, target: AnyProduct, new_prio: Priority) -> None:
        """Update priority of given Product. This must already exist in general mapping to apply."""
        entry = self.percieved_utilities.get(target)
        if entry is None:
            raise KeyError(f"Target {target} not found in perceived_utilities.")
        old_prio: Priority = entry[1]
        entry[1] = new_prio
        if old_prio in self.priority_mapping:
            self.priority_mapping[old_prio].discard(target)
        self.priority_mapping.setdefault(new_prio, set()).add(target)

    def updateUtility(self, target: AnyProduct, util: float) -> None:
        entry = self.percieved_utilities.get(target)
        if entry is None:
            raise KeyError(f"Target {target} not found in perceived_utilities.")
        entry[0] = util

    def populatePriority(self, prio: Priority, targets: list[AnyProduct], utilities: list[float] = None) -> None:
        """
        Overwrite exisitng entries at current priority level with targets input.
        Target products do not have to be in ampping already (honestly ideal if they aren't)
        If member of targets already in priority mapping at different priority level, it will be duplicated.
        Such duplication does not necessarily cause errors but results in unwanted behaviour regarding demand allocation.
        This duplication does not occur in percieved util dict as it's keyed by target's hash.
        This method does not warn or check for duplications of this kind. syncConts solves this in O(N) time.
        Use with caution.
        """
        if utilities is None or len(utilities) != len(targets):
            utilities = [0] * len(targets)

        self.priority_mapping[prio] = set(targets)
        for util, product in zip(utilities,targets):
            self.percieved_utilities[product] = [util, prio] 

    def syncConts(self) -> bool:
        """
        Utility method. Checks if percied util conts match priority mapping
        If there are differences, percieved util is always treated as truth.
        Returns bool(was corrective action taked? t/f)
        """
        resynced: bool = False

        # Build reverse lookup: product → current priority in mapping
        product_to_mapped_prio: dict[AnyProduct, Priority] = {}
        for prio, products_set in self.priority_mapping.items():
            for product in products_set:
                product_to_mapped_prio[product] = prio

        perceived_set: set[AnyProduct] = set(self.percieved_utilities.keys())

        # Correct: ensure each perceived product is in the right priority set
        for product, (util, true_prio) in self.percieved_utilities.items():
            if true_prio not in self.priority_mapping:
                self.priority_mapping[true_prio] = set()
            if product not in self.priority_mapping[true_prio]:
                # Remove from old (wrong) priority set
                old_prio = product_to_mapped_prio.get(product)
                if old_prio is not None and old_prio in self.priority_mapping:
                    self.priority_mapping[old_prio].discard(product)
                self.priority_mapping[true_prio].add(product)
                resynced = True

        # Remove any products in priority_mapping not present in perceived_utilities
        for prio, products_set in list(self.priority_mapping.items()):
            orphans = products_set - perceived_set
            if orphans:
                products_set.difference_update(orphans)
                resynced = True

        return resynced