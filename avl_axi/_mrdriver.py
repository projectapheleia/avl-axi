# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Driver


import avl
import cocotb
from cocotb.triggers import RisingEdge

from ._driver import Driver
from ._signals import ar_m_signals, r_m_signals, r_s_signals


class ManagerReadDriver(Driver):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the Manager Read Driver for the AMBA agent.

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

        # Manager Write Driver
        self._mwdrv_ = None

        # Items Queues
        self.controlQ = []
        self.dataQ = []
        self.responseQ = {}
        for i in range(2**self.i_f.ID_R_WIDTH):
            self.responseQ[i] = []
        self.response_pending = 0

    async def reset(self) -> None:
        """
        Reset the driver by setting all signals to their default values.
        This method is called when the driver is reset.

        By default 0's all signals - can be overridden in subclasses to add randomization or other behavior.
        """

        # Write Signals
        for s in ar_m_signals + r_m_signals:
            self.i_f.set(s, 0)

    async def quiesce_control(self) -> None:
        """
        Quiesce the control signals by setting them to their default values.
        This method is called after driving the control signals.

        By default 0's all signals - can be overridden in subclasses to add randomization or other behavior.
        """
        for s in ar_m_signals:
            self.i_f.set(s, 0)

    async def drive_control(self) -> None:
        """
        Drive the control signals based on the items in the control queue.
        This method is called during the run phase of the simulation.
        It waits for items in the control queue and drives the corresponding signals.
        """
        self.controlQ = []
        while True:

            while not self.controlQ or self.i_f.get("aresetn") == 0:
                await RisingEdge(self.i_f.aclk)

            item = self.controlQ.pop(0)
            self.wake_export.write(item)

            self.i_f.set("arvalid", 0)

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

            for s in ar_m_signals:
                if s == "arvalid":
                    self.i_f.set(s, 1)
                else:
                    self.i_f.set(s, item.get(s, default=0))

            while True:
                await RisingEdge(self.i_f.aclk)
                if self.i_f.get("arready") and self.i_f.get("awakeup", default=1):
                    break

            # Clear the bus
            await self.quiesce_control()

            # Inform sequence control phase is completed
            item.set_event("control", item)

    async def quiesce_data(self) -> None:
        """
        Quiesce the data signals by setting them to their default values.
        This method is called after driving the data signals.
        """
        pass

    async def drive_data(self) -> None:
        """
        Drive the data signals based on the items in the data queue.
        This method is called during the run phase of the simulation.
        """
        pass

    async def quiesce_response(self) -> None:
        """
        Quiesce the response signals by setting them to their default values.
        This method is called after driving the response signals.
        By default 0's all signals - can be overridden in subclasses to add randomization or other behavior.
        """
        for s in r_m_signals:
            self.i_f.set(s, 0)

    async def drive_response(self):
        """
        Drive the response signals based on the items in the response queue.
        This method is called during the run phase of the simulation.
        It waits for items in the response queue and drives the corresponding signals.
        """
        for k in self.responseQ.keys():
            self.responseQ[k] = []
        while True:

            while self.response_pending == 0 or self.i_f.get("aresetn") == 0:
                await RisingEdge(self.i_f.aclk)

            # Rate Limiter
            await self.wait_on_rate(self.response_rate_limit())

            self.i_f.set("rready", 1)

            while True:
                await RisingEdge(self.i_f.aclk)
                if bool(self.i_f.get("rvalid", default=1)) and bool(self.i_f.get("rready", default=1)):
                    break

            rid = int(self.i_f.get("rid", default=0))
            item = self.responseQ[rid][0]
            if not hasattr(item, "_rcnt_"):
                item._rcnt_ = 0

            for s in r_s_signals:
                item.set(s, self.i_f.get(s, default=0), idx=item._rcnt_)

            item._rcnt_ += 1
            if item._rcnt_ == item.get_len()+1:
                # Inform sequence response phase is complete
                delattr(item, "_rcnt_")
                self.response_pending -= 1
                self.responseQ[rid].pop(0)

                # Inform sequence response phase is complete
                # Extra checks for items which have both r and b responses (atomics)
                # Only call response callback when all completed
                if not item.has_bresp():
                    item.set_event("response", item)
                else:
                    if hasattr(item, "_bresp_complete_"):
                        delattr(item, "_bresp_complete_")
                        item.set_event("response", item)
                    else:
                        setattr(item, "_rresp_complete_", True)

            await self.quiesce_response()

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

            if not hasattr(item, "araddr"):
                continue

            item.add_event("control", self._activate_)
            item.add_event("response", self._deactivate_)
            self.controlQ.append(item)

            rid = item.get_id()
            self.responseQ[rid].append(item)
            self.response_pending += 1

            item.set_event("done")

__all__ = ["ManagerReadDriver"]
