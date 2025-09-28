# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Driver

import asyncio
import random

import avl
import cocotb
from cocotb.triggers import FallingEdge, RisingEdge

from ._item import SequenceItem

ASLEEP = 0
PRE_WAKE = 1
AWAKE = 2
PRE_SLEEP = 3
class ManagerWakeDriver(avl.Driver):



    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the Manager Write Driver for the AMBA agent.

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

        self.i_f = avl.Factory.get_variable(f"{self.get_full_name()}.i_f", None)

        self.status = ASLEEP
        """Indication of current wake state"""

        self.pre_wakeup =  avl.Factory.get_variable(f"{self.get_full_name()}.pre_wakeup", lambda : 0.1)
        """Pre-wakeup delay - time to wait before driving the wakeup signal (0.0 - 1.0) (>= version 5)"""
        self.post_wakeup = avl.Factory.get_variable(f"{self.get_full_name()}.post_wakeup", lambda : 0.1)
        """Post-wakeup delay - time to wait after driving the wakeup signal (0.0 - 1.0) (>= version 5)"""

        # Keep track of outstanding transactions - dict to make atomic addition and removal easy
        self._outstanding_transactions_ = 0

    def _update_status_(self, new_status : int) -> None:
        """
        Update status

        :param new_status: New status to set
        :type new_status: int
        """
        if self.status != new_status:
            self.debug(f"_update_status_ {self.status} -> {new_status}")
        self.status = new_status

    async def reset(self) -> None:
        """
        Reset the driver by setting all signals to their default values.
        This method is called when the driver is reset.

        By default 0's all signals - can be overridden in subclasses to add randomization or other behavior.
        """

        self.i_f.set("awakeup", 0)

        if self.i_f.get("awakeup") is None:
            self._update_status_(AWAKE)

    async def wait_on_reset(self) -> None:
        """
        Wait for the reset signal to go low and then call the reset method.
        This method is called to ensure that the driver is reset before driving any signals.
        It waits for the presetn signal to go low, indicating that the reset is active,
        and then calls the reset method to set all signals to their default values.
        """

        try:
            await FallingEdge(self.i_f.aresetn)
            await self.reset()
        except asyncio.CancelledError:
            raise
        except Exception:
            pass

    async def assert_wake(self, item : SequenceItem) -> None:
        """
        Assert wake for the given item.
        This method is called to assert the wake signal for the given item.
        It waits for the pre-wakeup delay, asserts the wake signal, and then waits for
        the post-wakeup delay before setting the item event to "awake".

        :param item: The sequence item for which to assert wake
        :type item: SequenceItem
        """
        while self.status == PRE_SLEEP:
            await RisingEdge(self.i_f.aclk)

        # First item when asleep
        if self.status == ASLEEP:
            self._update_status_(PRE_WAKE)
            self.i_f.set("awakeup", 1)

            # Pre Wakeup delay
            delay = self.pre_wakeup()
            while random.random() > delay:
                await RisingEdge(self.i_f.aclk)

            if item.get("goto_sleep", default=False):
                self._update_status_(PRE_SLEEP)
            else:
                self._update_status_(AWAKE)

            # We're awake (even if we're already preparing to sleep)
            item.set_event("awake", item)
        else:
            # All items wait to be awake - block if we are preparing to sleep
            while self.status != AWAKE:
                await RisingEdge(self.i_f.aclk)
            item.set_event("awake", item)

        self._outstanding_transactions_ += 1

    async def deassert_wake(self, item : SequenceItem) -> None:
        """
        Deassert wake for the given item.
        This method is called to deassert the wake signal for the given item.
        It waits for the item event "response" to be set, indicating that the item has
        been processed, and then deasserts the wake signal if there are no outstanding transactions.

        :param item: The sequence item for which to deassert wake
        :type item: SequenceItem
        """

        if item.get("goto_sleep", default=False):
            self._update_status_(PRE_SLEEP)

        # Wait for response
        await item.wait_on_event("response")
        self._outstanding_transactions_ -= 1
        assert self._outstanding_transactions_ >= 0

        if self.status == PRE_SLEEP and self._outstanding_transactions_ == 0:
            # Post Wakeup delay
            delay = self.post_wakeup()
            while random.random() > delay:
                await RisingEdge(self.i_f.aclk)

            self.i_f.set("awakeup", 0)
            self._update_status_(ASLEEP)

    async def run_phase(self):
        """
        Run phase for the Requester Driver.
        This method is called during the run phase of the simulation.
        It is responsible for driving the request signals based on the sequencer's items.

        """
        async def wake_loop():
            item = None
            while True:
                item = await self.seq_item_port.blocking_get()

                if self.i_f.get("awakeup") is None:
                    item.set_event("awake")
                    continue

                cocotb.start_soon(self.assert_wake(item))
                cocotb.start_soon(self.deassert_wake(item))

        while True:
            await self.reset()

            tasks = []
            tasks.append(cocotb.start_soon(wake_loop()))

            await self.wait_on_reset()

            for t in tasks:
                if not t.done():
                    t.cancel()

__all__ = ["ManagerWakeDriver"]
