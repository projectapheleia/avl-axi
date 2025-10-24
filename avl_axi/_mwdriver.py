# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Driver


import avl
import cocotb
from cocotb.triggers import RisingEdge

from ._driver import Driver
from ._signals import aw_m_signals, b_m_signals, b_s_signals, w_m_signals


class ManagerWriteDriver(Driver):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the Manager Write Driver for the AMBA agent.

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

        # Manager Read Driver
        self._mrdrv_ = None

        # Items Queues
        self.controlQ = []
        self.dataQ = []
        self.responseQ = {}
        for i in range(2**self.i_f.ID_W_WIDTH):
            self.responseQ[i] = []
        self.response_pending = 0

        # Data before Control
        self.allow_early_data = avl.Factory.get_variable(f"{self.get_full_name()}.allow_early_data", False)
        """Allow data phase (W) to start before control phase (AW) is accepted"""

        if self.allow_early_data and self.max_outstanding is not None:
            raise ValueError("allow_early_data and max_outstanding are mutually exclusive")

    async def reset(self) -> None:
        """
        Reset the driver by setting all signals to their default values.
        This method is called when the driver is reset.

        By default 0's all signals - can be overridden in subclasses to add randomization or other behavior.
        """

        # Write Signals
        for s in aw_m_signals + w_m_signals + b_m_signals:
            self.i_f.set(s, 0)

    async def quiesce_control(self) -> None:
        """
        Quiesce the control signals by setting them to their default values.
        This method is called to ensure that the control signals are in a known state.

        By default 0's all signals - can be overridden in subclasses to add randomization or other behavior.
        """

        for s in aw_m_signals:
            self.i_f.set(s, 0)

    async def drive_control(self) -> None:
        """
        Drive the control signals based on the items in the control queue.
        This method is responsible for driving the control signals according to the protocol.
        """

        self.controlQ = []
        while True:

            while not self.controlQ or self.i_f.get("aresetn") == 0:
                await RisingEdge(self.i_f.aclk)

            item = self.controlQ.pop(0)
            self.wake_export.write(item)

            self.i_f.set("awvalid", 0)

            # Wake
            await item.wait_on_event("awake")

            # Rate Limiter
            await self.wait_on_rate(self.control_rate_limit())

            # Unique ID
            while self._unique_ids_[item.get_id()] > 0:
                await RisingEdge(self.i_f.aclk)

            # TAG Unique ID
            if item.get_tagop() != 0:
                while self._tag_ids_[item.get_id()] > 0:
                    await RisingEdge(self.i_f.aclk)

            # Max Outstanding
            while self.max_outstanding is not None and self._outstanding_transactions_ >= self.max_outstanding:
                await RisingEdge(self.i_f.aclk)
            self._outstanding_transactions_ += 1

            for s in aw_m_signals:
                if s == "awvalid":
                    self.i_f.set(s, 1)
                else:
                    self.i_f.set(s, item.get(s, default=0))

            # Start Data Phase
            if not self.allow_early_data:
                self.dataQ.append(item)

            while True:
                await RisingEdge(self.i_f.aclk)
                if self.i_f.get("awready") and self.i_f.get("awakeup", default=1):
                    break

            # Clear the bus
            await self.quiesce_control()

            # Inform sequence control phase is completed
            item.set_event("control", item)

    async def quiesce_data(self) -> None:
        """
        Quiesce the data signals by setting them to their default values.
        This method is called to ensure that the data signals are in a known state.
        By default 0's all signals - can be overridden in subclasses to add randomization or other behavior.
        """
        for s in w_m_signals:
            self.i_f.set(s, 0)

    async def drive_data(self) -> None:
        """
        Drive the data signals based on the items in the data queue.
        This method is responsible for driving the data signals according to the protocol.
        """
        self.dataQ = []
        while True:

            while not self.dataQ or self.i_f.get("aresetn") == 0:
                await RisingEdge(self.i_f.aclk)

            item = self.dataQ.pop(0)

            # Wake
            await item.wait_on_event("awake")

            for i in range(item.get_len()+1):
                self.i_f.set("wvalid", 0)

                # Rate Limiter
                await self.wait_on_rate(self.data_rate_limit())

                for s in w_m_signals:
                    if s == "wvalid":
                        self.i_f.set(s, 1)
                    elif s == "wlast":
                        self.i_f.set(s, i == item.get_len())
                    else:
                        self.i_f.set(s, item.get(s, idx=i, default=0))

                while True:
                    await RisingEdge(self.i_f.aclk)
                    if self.i_f.get("wready", default=1) and self.i_f.get("awakeup", default=1):
                        break

                # Clear the bus
                await self.quiesce_data()

            # Inform sequence data phase is complete
            item.set_event("data", item)

    async def quiesce_response(self) -> None:
        """
        Quiesce the response signals by setting them to their default values.
        This method is called to ensure that the response signals are in a known state.
        By default 0's all signals - can be overridden in subclasses to add randomization or
        other behavior.
        """
        for s in b_m_signals:
            self.i_f.set(s, 0)

    async def drive_response(self):
        """
        Drive the response signals based on the items in the response queue.
        This method is responsible for driving the response signals according to the protocol.
        """
        for k in self.responseQ.keys():
            self.responseQ[k] = []
        while True:
            while self.response_pending == 0 or self.i_f.get("aresetn") == 0:
                await RisingEdge(self.i_f.aclk)

            # Rate Limiter
            await self.wait_on_rate(self.response_rate_limit())

            self.i_f.set("bready", 1)

            while True:
                await RisingEdge(self.i_f.aclk)
                if bool(self.i_f.get("bvalid", default=1)) and bool(self.i_f.get("bready", default=1)):
                    break

            bid = int(self.i_f.get("bid", default=0))
            item = self.responseQ[bid].pop(0)

            for s in b_s_signals:
                if s != "bvalid":
                    item.set(s, self.i_f.get(s, default=0))

            await self.quiesce_response()

            # Decrement outstanding response counter
            self.response_pending -= 1

            # Inform sequence response phase is complete
            # Extra checks for items which have both r and b responses (atomics)
            # Only call response callback when all completed
            if not item.has_rresp():
                item.set_event("response", item)
            else:
                if hasattr(item, "_rresp_complete_"):
                    delattr(self, "_rresp_complete_")
                    item.set_event("response", item)
                else:
                    setattr(item, "_bresp_complete_", True)

    async def run_phase(self):
        """
        Run phase for the Requester Driver.
        This method is called during the run phase of the simulation.
        It is responsible for driving the request signals based on the sequencer's items.

        :raises NotImplementedError: If the run phase is not implemented.
        """
        item = None
        cocotb.start_soon(super().run_phase())

        while True:
            item = await self.get_next_item(item)

            if not hasattr(item, "awaddr"):
                continue

            item.add_event("control", self._activate_)
            item.add_event("response", self._deactivate_)
            self.controlQ.append(item)
            if self.allow_early_data:
                self.dataQ.append(item)

            id = item.get_id()

            if item.has_bresp():
                self.responseQ[id].append(item)
                self.response_pending += 1

            if item.has_rresp():
                self._mrdrv_.responseQ[id].append(item)
                self._mrdrv_.response_pending += 1

            item.set_event("done")

__all__ = ["ManagerWriteDriver"]
