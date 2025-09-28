# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Monitor

import avl

from ._item import SequenceItem
from ._types import axi_resp_t


class ExclusivityMonitor(avl.Component):
    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the AXI Exclusivity Monitor

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

        # Handle to interface - defines capabilities and parameters
        i_f = avl.Factory.get_variable(f"{self.get_full_name()}.i_f", None)

        self.ranges = {}
        for i in range(2**i_f.ID_R_WIDTH):
            self.ranges[i] = None

    def _get_range_(self, item: SequenceItem) -> bool:
        """
        Return the address range of the item

        :param item: The sequence item to get the range for
        :type item: SequenceItem
        :return: The address range of the item, or None if not found
        """

        if hasattr(item, "awaddr"):
            lo = item.get("awaddr", default=0)
            hi = lo + (1 << item.get("awsize", default=0)) - 1
        else:
            lo = item.get("araddr", default=0)
            hi = lo + (1 << item.get("arsize", default=0)) - 1

        return (lo, hi)

    def _check_range_(self, r0: tuple[int, int], r1: tuple[int, int]) -> str:
        """
        Check if the given sequence item is within the monitored ranges.

        :param item: The sequence item to check
        :type item: SequenceItem
        :return: True if the item is within the ranges, False otherwise
        """
        # exact match
        if r0 == r1:
            return "exact"

        # overlap (if ranges intersect at all)
        if r0[0] <= r1[1] and r1[0] <= r0[1]:
            return "overlap"

        # otherwise, they miss
        return "miss"

    def process_write(self, item : SequenceItem) -> None:
        """
        Process a sequence item update for exclusivity

        :param item: The sequence item to process
        :type item: SequenceItem
        """

        if not isinstance(item, SequenceItem):
            raise TypeError("Item must be a SequenceItem")

        if not hasattr(item, "awlock"):
            return

        id = item.get_id()
        (lo, hi) = self._get_range_(item)

        if item.awlock:
            if self.ranges[id] is not None:
                # Genuine exclusive access
                #   - only returns EXOKAY on exact match
                #   - always clears exclusive
                if self._check_range_(self.ranges[id], (lo, hi)) == "exact":
                    item.set("bresp", axi_resp_t.EXOKAY)

                self.ranges[id] = None
                return

        # Check all ranges to clear
        for k,v in self.ranges.items():
            if v is not None:
                if self._check_range_(v, (lo, hi)) != "miss":
                    self.ranges[k] = None

    def process_read(self, item : SequenceItem) -> None:
        """
        Process a sequence item update for exclusivity

        :param item: The sequence item to process
        :type item: SequenceItem
        """

        if not isinstance(item, SequenceItem):
            raise TypeError("Item must be a SequenceItem")

        if not hasattr(item, "arlock"):
            return

        id = item.get_id()
        (lo, hi) = self._get_range_(item)

        if item.arlock:
            self.ranges[id] = (lo, hi)


__all__ = ["ExclusivityMonitor"]
