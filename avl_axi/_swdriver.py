# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Driver

import random

import avl
import cocotb
from cocotb.triggers import RisingEdge

from ._driver import Driver
from ._item import SequenceItem, WriteItem
from ._signals import aw_m_signals, aw_s_signals, b_s_signals, w_m_signals, w_s_signals


class SubordinateWriteDriver(Driver):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the Subordinate Write Driver for the AMBA agent.

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

        self.in_order = avl.Factory.get_variable(f"{self.get_full_name}.in_order", True)
        """Responses return in order of control"""

        self.qosaccept = avl.Factory.get_variable(f"{self.get_full_name}.qosaccept", 0)
        """QOS Accept hint value"""

        # Subordinate Read Driver - required for atomic loads
        self._srdrv_ = None

        # Memory Mode
        self.memory = None

        # Items Queues
        self.controlQ = avl.List()
        self.dataQ = avl.List()
        self.responseQ = avl.List()

        # Exclusive Monitor
        self.emonitor = None

    async def reset(self) -> None:
        """
        Reset the driver by setting all signals to their default values.
        This method is called when the driver is reset.

        By default 0's all signals - can be overridden in subclasses to add randomization or other behavior.
        """

        # Write Signals
        for s in aw_s_signals + w_s_signals + b_s_signals:
            self.i_f.set(s, 0)

        # QOS Accept
        self.i_f.set("vawqosaccept", self.qosaccept)

    async def _wait_for_data_(self) -> None:
        """
        Wait for  the wdata to populate control items
        This way the data phase can be ahead of control phase
        """

        while True:
            item = await self.controlQ.blocking_pop()

            for i in range(item.get_len()+1):
                d = await self.dataQ.blocking_pop()

                for k,v in d.items():
                    if hasattr(item, k):
                        item.set(k, v, idx=i)

            # Handle Memory Access
            if self.memory is not None:
                self.memory.process_write(item)

            # Send item to response phases
            if item.has_bresp():
                self.responseQ.append(item)

            if item.has_rresp():
                self._srdrv_.responseQ.append(item)

    async def quiesce_control(self) -> None:
        """
        Quiesce the control signals by setting them to their default values.
        This method is called after a control transaction is completed.

        By default 0's all signals - can be overridden in subclasses to add randomization or other behavior.
        """
        for s in aw_s_signals:
            self.i_f.set(s, 0)

    async def drive_control(self) -> None:
        """
        Drive the control signals by waiting for valid signals and then setting the ready signals.
        This method runs in an infinite loop and should be started as a separate coroutine.
        """
        self.controlQ.clear()
        self.tasks.append(cocotb.start_soon(self._wait_for_data_()))
        while True:
            self.i_f.set("awready", 0)

            while self.i_f.get("aresetn") == 0 or self.i_f.get("awakeup", default=1) == 0:
                await RisingEdge(self.i_f.aclk)

            item = WriteItem("from_sdriver", self)

            # Rate Limiter
            await self.wait_on_rate(self.control_rate_limit())

            self.i_f.set("awready", 1)

            while True:
                await RisingEdge(self.i_f.aclk)
                if self.i_f.get("awvalid"):
                    break

            await self.quiesce_control()

            # Populate Item with control data
            for s in aw_m_signals:
                item.set(s, self.i_f.get(s, default=0))
            item.resize()

            self.controlQ.append(item)

    async def quiesce_data(self) -> None:
        """
        Quiesce the data signals by setting them to their default values.
        This method is called after a data transaction is completed.

        By default 0's all signals - can be overridden in subclasses to add randomization or other behavior.
        """
        for s in w_s_signals:
            self.i_f.set(s, 0)

    async def drive_data(self) -> None:
        """
        Drive the data signals by waiting for valid signals and then setting the ready signals.
        This method runs in an infinite loop and should be started as a separate coroutine.
        """
        self.dataQ.clear()
        while True:
            self.i_f.set("wready", 0)

            while self.i_f.get("aresetn") == 0 or self.i_f.get("awakeup", default=1) == 0:
                await RisingEdge(self.i_f.aclk)

            # Rate Limiter
            await self.wait_on_rate(self.control_rate_limit())

            self.i_f.set("wready", 1)

            while True:
                await RisingEdge(self.i_f.aclk)
                if self.i_f.get("wvalid"):
                    break

            data = {}
            for s in w_m_signals:
                data[s] = self.i_f.get(s, default=0)
            self.dataQ.append(data)

            await self.quiesce_data()

    async def quiesce_response(self) -> None:
        """
        Quiesce the response signals by setting them to their default values.
        This method is called after a response transaction is completed.
        By default 0's all signals - can be overridden in subclasses to add randomization or other behavior.
        """
        for s in b_s_signals:
            self.i_f.set(s, 0)

    async def drive_response(self) -> None:
        """
        Drive the response signals by waiting for valid signals and then setting the ready signals.
        This method runs in an infinite loop and should be started as a separate coroutine.
        """
        self.responseQ.clear()
        while True:
            while not self.responseQ or self.i_f.get("arestn") == 0 or self.i_f.get("awakeup", default=1) == 0:
                await RisingEdge(self.i_f.aclk)

            if self.in_order or self.i_f.Ordered_Write_Observation:
                idx = 0
            else:
                idx = random.randrange(len(self.responseQ))

            item = await self.get_next_item(self.responseQ.pop(idx))

            # Exclusive monitor
            self.emonitor.process_write(item)

            # Rate Limiter
            await self.wait_on_rate(self.response_rate_limit())

            for s in b_s_signals:
                if s in ["bvalid"]:
                    self.i_f.set(s, 1)
                else:
                    self.i_f.set(s, item.get(s, default=0))

            while True:
                await RisingEdge(self.i_f.aclk)
                if self.i_f.get("bready"):
                    break

            await self. quiesce_response()

    async def get_next_item(self, item : SequenceItem = None) -> SequenceItem:
        """
        Get the next item to be processed.
        This method can be overridden in subclasses to modify the item before it is processed.

        :param item: The item to be processed
        :type item: SequenceItem
        :return: The item to be processed
        :rtype: SequenceItem
        """
        if not isinstance(item, WriteItem):
            raise ValueError("get_next_item() - expected type WriteItem")

        return item

class SubordinateWriteMemoryDriver(SubordinateWriteDriver):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the Subordinate Write Driver for the AXI agent.

        This agent behaves as a memory

        Memory operations are performed at the end of the aw/w phase
        as responses can be delayed

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

        # Assign the memory
        self.memory = parent.smem

__all__ = ["SubordinateWriteDriver", "SubordinateWriteMemoryDriver"]
