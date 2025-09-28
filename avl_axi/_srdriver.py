# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Driver

import random

import avl
from cocotb.triggers import RisingEdge

from ._driver import Driver
from ._item import ReadItem, SequenceItem
from ._signals import ar_m_signals, ar_s_signals, r_s_signals


class SubordinateReadDriver(Driver):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the Subordinate Read Driver for the AMBA agent.

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

        # Subordinate Write Driver
        self._swdrv_ = None

        # Memory Mode
        self.memory = None

        # Items Queues
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
        for s in ar_s_signals + r_s_signals:
            self.i_f.set(s, 0)

        # QOS Accept
        self.i_f.set("varqosaccept", self.qosaccept)

    async def quiesce_control(self) -> None:
        """
        Quiesce the control channel by setting all control signals to their default values.
        This method is called after a control transaction is completed.

        By default 0's all control signals - can be overridden in subclasses to add randomization or other behavior.
        """
        for s in ar_s_signals:
            self.i_f.set(s, 0)

    async def drive_control(self) -> None:
        """
        Drive the control channel by sending read address transactions.
        This method runs in a loop, waiting for the appropriate conditions to send transactions.
        """
        while True:

            self.i_f.set("arready", 0)

            while self.i_f.get("aresetn") == 0 or self.i_f.get("awakeup", default=1) == 0:
                await RisingEdge(self.i_f.aclk)

            item = ReadItem("from_sdriver", self)

            # Rate Limiter
            await self.wait_on_rate(self.control_rate_limit())

            self.i_f.set("arready", 1)

            while True:
                await RisingEdge(self.i_f.aclk)
                if self.i_f.get("arvalid"):
                    break

            await self.quiesce_control()

            # Send item to response phase
            for s in ar_m_signals:
                item.set(s, self.i_f.get(s, default=0))
            item.resize()

            # Handle Memory Access
            if self.memory is not None:
                self.memory.process_read(item)

            # Send item to write response phase
            self.responseQ.append(item)

    async def quiesce_data(self) -> None:
        """
        Quiesce the data channel by setting all data signals to their default values.
        This method is empty as reads have no data channel.
        """
        pass

    async def drive_data(self) -> None:
        """
        Drive the data channel by sending read data transactions.
        This method is empty as reads have no data channel.
        """
        pass

    async def quiesce_response(self) -> None:
        """
        Quiesce the response channel by setting all response signals to their default values.
        This method is called after a response transaction is completed.
        By default 0's all response signals - can be overridden in subclasses to add randomization or other behavior.
        """
        for s in r_s_signals:
            self.i_f.set(s, 0)

    async def drive_response(self) -> None:
        """
        Drive the response channel by sending read data transactions.
        This method runs in a loop, waiting for the appropriate conditions to send transactions.
        """
        self.responseQ = avl.List()
        while True:
            while not self.responseQ or self.i_f.get("aresetn") == 0 or self.i_f.get("awakeup", default=1) == 0:
                await RisingEdge(self.i_f.aclk)

            if self.in_order or self.i_f.Read_Interleaving_Disabled:
                idx = 0
            else:
                idx = random.randrange(len(self.responseQ))

            item = await self.get_next_item(self.responseQ[idx])

            # Rate Limiter
            await self.wait_on_rate(self.response_rate_limit())

            for s in r_s_signals:
                if s == "rvalid":
                    self.i_f.set(s, 1)
                elif s == "rlast":
                    self.i_f.set(s, item._rcnt_ == item.get_len())
                else:
                    self.i_f.set(s, item.get(s, idx=item._rcnt_, default=0))

            while True:
                await RisingEdge(self.i_f.aclk)
                if self.i_f.get("rready"):
                    break

            # Exclusive monitor
            self.emonitor.process_read(item)

            item._rcnt_ += 1
            if item._rcnt_ == item.get_len()+1:
                delattr(item, "_rcnt_")
                self.responseQ.pop(idx)

            await self. quiesce_response()

    async def get_next_item(self, item : SequenceItem = None) -> SequenceItem:
        """
        Get the next item to be sent on the response channel.
        This method can be overridden in subclasses to modify the item before it is sent.
        By default, it initializes the read count if not already set.

        :param item: The item to be sent on the response channel
        :type item: SequenceItem
        :return: The item to be sent on the response channel
        :rtype: SequenceItem
        """
        if not isinstance(item, SequenceItem):
            raise ValueError("get_next_item() - expected type SequenceItem")

        if not hasattr(item, "_rcnt_"):
            item._rcnt_ = 0

        return item

class SubordinateReadRandomDriver(SubordinateReadDriver):

    async def get_next_item(self, item : SequenceItem = None) -> SequenceItem:
        """
        Get the next item to be sent on the response channel.
        This method randomizes the item if it has not been sent before.

        :param item: The item to be sent on the response channel
        :type item: SequenceItem
        :return: The item to be sent on the response channel
        :rtype: SequenceItem
        """

        if not isinstance(item, SequenceItem):
            raise ValueError("get_next_item() - expected type SequenceItem")

        if not hasattr(item, "_rcnt_"):
            item._rcnt_ = 0

            # Randomize
            for s in ar_m_signals:
                if hasattr(item, s):
                    v = getattr(item, s)
                    item.add_constraint(f"_c_{s}_temp", lambda x,val=v.value: x == val, v)
            item.randomize()

        return item

class SubordinateReadMemoryDriver(SubordinateReadDriver):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the Subordinate Write Driver for the AXI agent.

        This agent behaves as a memory

        Memory operations are performed at the end of the ar phase
        as responses can be delayed

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

        self.memory = parent.smem


__all__ = ["SubordinateReadDriver", "SubordinateReadRandomDriver", "SubordinateReadMemoryDriver"]
