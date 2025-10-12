# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Base Driver


import asyncio
import random

import avl
import cocotb
from cocotb.triggers import FallingEdge, RisingEdge

from ._item import SequenceItem


class Driver(avl.Driver):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the Driver for the APB agent.

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

        self.i_f = avl.Factory.get_variable(f"{self.get_full_name()}.i_f", None)

        self.wake_export = avl.Port("wake_export", self)

        self.control_rate_limit = avl.Factory.get_variable(f"{self.get_full_name()}.control_rate_limit", lambda : 1.0)
        """Rate limit for driving control signals. lambda function (0.0 - 1.0)"""

        self.data_rate_limit = avl.Factory.get_variable(f"{self.get_full_name()}.data_rate_limit", lambda : 1.0)
        """Rate limit for driving data signals. lambda function (0.0 - 1.0)"""

        self.response_rate_limit = avl.Factory.get_variable(f"{self.get_full_name()}.response_rate_limit", lambda : 1.0)
        """Rate limit for driving accept signals. lambda function (0.0 - 1.0)"""

        self.max_outstanding = avl.Factory.get_variable(f"{self.get_full_name()}.max_outstanding", None)
        """Maximum number of outstanding transactions"""

        if not callable(self.control_rate_limit):
            raise TypeError("control rate_limit must be a callable (lambda function) that returns a float between 0.0 and 1.0")

        if not callable(self.data_rate_limit):
            raise TypeError("data rate_limit must be a callable (lambda function) that returns a float between 0.0 and 1.0")

        if not callable(self.response_rate_limit):
            raise TypeError("response rate_limit must be a callable (lambda function) that returns a float between 0.0 and 1.0")

        # Keep track of active ids
        self._unique_ids_ = {}
        self._tag_ids_ = {}
        for i in range(2**max(self.i_f.ID_R_WIDTH, self.i_f.ID_W_WIDTH)):
            self._unique_ids_[i] = 0
            self._tag_ids_[i] = 0

        # Keep track of outstanding transactions - dict to make atomic addition and removal easy
        self._outstanding_transactions_ = 0

        # Running tasks
        self.tasks = []

    def _deactivate_(self, item : SequenceItem) -> None:
        """
        Track Item

        :param item
        :type item: SequenceItem
        :return None
        """
        if item.get_idunq():
            self._unique_ids_[item.get_id()] -= 1
            assert self._unique_ids_[item.get_id()] >= 0

        if item.get_tagop() != 0:
            self._tag_ids_[item.get_id()] -= 1
            assert self._tag_ids_[item.get_id()] >= 0

        self._outstanding_transactions_ -= 1
        assert self._outstanding_transactions_ >= 0

    def _activate_(self, item : SequenceItem) -> None:
        """
        Track item

        :param item
        :type item: SequenceItem
        :return None
        """
        if item.get_idunq():
            self._unique_ids_[item.get_id()] += 1

        if item.get_tagop() != 0:
            self._tag_ids_[item.get_id()] += 1

    async def reset(self) -> None:
        """
        Reset the driver by setting all signals to their default values.
        This method is called when the driver is reset.

        By default 0's all signals - can be overridden in subclasses to add randomization or other behavior.
        """

        raise NotImplementedError("Reset method must be implemented in subclasses")

    async def wait_on_rate(self, rate : float) -> None:
        """
        Wait based on a rate

        :param rate
        :type rate: float
        :return: None
        """
        while random.random() > rate:
            await RisingEdge(self.i_f.aclk)

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

            for i in range(2**max(self.i_f.ID_R_WIDTH, self.i_f.ID_W_WIDTH)):
                self._unique_ids_[i] = 0
                self._tag_ids_[i] = 0

            self._outstanding_transactions_ = 0
        except asyncio.CancelledError:
            raise
        except Exception:
            pass

    async def quiesce_control(self) -> None:
        """
        Quiesce the control bus
        This method is called when the driver is quiesced.

        By default calls reset() to set all signals to their default values.
        Can be overridden in subclasses to add randomization or other behavior.
        """

        await self.reset()

    async def drive_control(self, item : SequenceItem) -> None:
        """
        Drive the control signals based on the provided sequence item.
        This method is called to drive the signals of the AXI interface.

        :param item: The sequence item containing the values to drive
        :type item: SequenceItem
        :return: None
        """
        raise NotImplementedError("Drive method must be implemented in subclasses")

    async def quiesce_data(self) -> None:
        """
        Quiesce the data bus
        This method is called when the driver is quiesced.

        By default calls reset() to set all signals to their default values.
        Can be overridden in subclasses to add randomization or other behavior.
        """

        await self.reset()

    async def drive_data(self, item : SequenceItem) -> None:
        """
        Drive the data signals based on the provided sequence item.
        This method is called to drive the signals of the AXI interface.

        :param item: The sequence item containing the values to drive
        :type item: SequenceItem
        :return: None
        """
        raise NotImplementedError("Drive method must be implemented in subclasses")

    async def quiesce_response(self) -> None:
        """
        Quiesce the response bus
        This method is called when the driver is quiesced.

        By default calls reset() to set all signals to their default values.
        Can be overridden in subclasses to add randomization or other behavior.
        """

        await self.reset()

    async def drive_response(self, item : SequenceItem) -> None:
        """
        Drive the response signals based on the provided sequence item.
        This method is called to drive the signals of the AXI interface.

        :param item: The sequence item containing the values to drive
        :type item: SequenceItem
        """
        raise NotImplementedError("Drive method must be implemented in subclasses")

    async def get_next_item(self, item : SequenceItem = None) -> SequenceItem:
        """
        Get the next sequence item.

        For the Request driver this method retrieves the next sequence item from the sequencer or
        the previously reset interrupted item.

        The implementation ensures items are driven on the rising edge of pclk, when not in reset,
        while allowing for back-to-back requests if the sequencer provides them.

        For the completion driver this method adjusts the completion side of the observed request.

        :param item: The sequence item to retrieve, defaults to None
        :type item: SequenceItem, optional
        :return: The next sequence item
        :rtype: SequenceItem
        """

        next_item = await self.seq_item_port.blocking_get()
        return next_item

    async def run_phase(self):
        """
        Run phase for the Driver.
        This method is called during the run phase of the simulation.
        It is responsible for driving the request signals based on the sequencer's items.

        """

        while True:
            await self.reset()

            self.tasks.clear()
            self.tasks.append(cocotb.start_soon(self.drive_control()))
            self.tasks.append(cocotb.start_soon(self.drive_data()))
            self.tasks.append(cocotb.start_soon(self.drive_response()))

            await self.wait_on_reset()

            for t in self.tasks:
                if not t.done():
                    t.cancel()

__all__ = ["Driver"]
