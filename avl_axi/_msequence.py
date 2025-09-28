# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Manager Sequence

import random

import avl

from ._item import ReadItem, SequenceItem, WriteItem


class ManagerSequence(avl.Sequence):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the sequence

        Sequence of independently randomized Manageractions

        :param name: Name of the sequence item
        :param parent: Parent component of the sequence item
        """
        super().__init__(name, parent)

        self.i_f = avl.Factory.get_variable(f"{self.get_full_name()}.i_f", None)
        """Handle to interface - defines capabilities and parameters"""

        self.n_items = avl.Factory.get_variable(f"{self.get_full_name()}.n_items", 1)
        """Number of items in the sequence (default 1)"""

        self.wait_for = avl.Factory.get_variable(f"{self.get_full_name}.wait_for", None)
        """Default phase to wait on after a item sent to driver before next item"""

    def done_cb(self, *args, **kwargs):
        """
        Callback on item done event

        :param args: Arguments
        :param kwargs: Keyword arguments
        """
        pass

    def control_cb(self, *args, **kwargs):
        """
        Callback on item control event

        :param args: Arguments
        :param kwargs: Keyword arguments
        """
        pass

    def data_cb(self, *args, **kwargs):
        """
        Callback on item data event

        :param args: Arguments
        :param kwargs: Keyword arguments
        """
        pass

    def response_cb(self, *args, **kwargs):
        """
        Callback on item response event

        :param args: Arguments
        :param kwargs: Keyword arguments
        """
        self.get_sequencer().drop_objection()

    async def _send_(self, item : SequenceItem, randomize : bool = True, wait_for : str = None) -> SequenceItem:
        """
        Send an item to the driver

        :param item: Item to send
        :param randomize: Randomize the item before sending (default True)
        :param wait_for: Phase to wait on after item sent to driver before next item (default None)
        :return: The item sent
        """
        self.get_sequencer().raise_objection()

        item.add_event("done", self.done_cb)
        item.add_event("control", self.control_cb)
        item.add_event("data", self.data_cb)
        item.add_event("response", self.response_cb)

        await self.start_item(item)
        if randomize:
            item.randomize()
        else:
            item.resize()
        await self.finish_item(item)

        if wait_for is not None:
            await item.wait_on_event(wait_for)
        return item

    async def next(self) -> SequenceItem:
        """
        Get the next item in the sequence
        """

        item = random.choice([WriteItem(f"from_{self.name}", self), ReadItem(f"from_{self.name}", self)])
        return await self._send_(item, wait_for=self.wait_for)

    async def write(self, **kwargs) -> WriteItem:
        """
        Send a write item to the driver

        :param kwargs: Keyword arguments to set on the item
        :return: The item sent
        """
        item = WriteItem(f"from_{self.name}", self)

        for k,v in kwargs.items():
            if hasattr(item, k):
                item.set(k, v)

        if "wait_for" in kwargs:
            wait_for = kwargs["wait_for"]
        else:
            wait_for = self.wait_for

        return await self._send_(item, randomize=False, wait_for=wait_for)

    async def read(self, **kwargs) -> ReadItem:
        """
        Send a read item to the driver

        :param kwargs: Keyword arguments to set on the item
        :return: The item sent
        """
        item = ReadItem(f"from_{self.name}", self)

        for k,v in kwargs.items():
            if hasattr(item, k):
                item.set(k, v)

        if "wait_for" in kwargs:
            wait_for = kwargs["wait_for"]
        else:
            wait_for = self.wait_for

        return await self._send_(item, randomize=False, wait_for=wait_for)

    async def body(self) -> None:
        """
        Body of the sequence
        """

        self.info(f"Starting Manager sequence {self.get_full_name()} with {self.n_items} items")
        for _ in range(self.n_items):
            item = await self.next()

        # Wait for response from final item
        await item.wait_on_event("response")

__all__ = ["ManagerSequence"]
