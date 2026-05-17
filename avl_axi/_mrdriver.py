# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Driver


import avl
import cocotb
from cocotb.triggers import RisingEdge
import random

from ._driver import Driver
from ._signals import ar_m_signals, r_m_signals, r_s_signals
from ._types import axi_atomic_t
from ._utils import get_beat_byte_offset


class ManagerReadDriver(Driver):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the Manager Read Driver for the AXI agent.

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
        for i in range(1<<self.i_f.ID_R_WIDTH):
            self.responseQ[i] = []
        self.response_pending = 0

        # AXI A3.2.3 / A3.4.1 narrow-transfer byte-lane de-shift opt-in (via AgentCfg).
        _cfg_ = avl.Factory.get_variable(f"{self.get_full_name()}.cfg", None)
        self.narrow_transfer_lane_steering = bool(_cfg_.narrow_transfer_lane_steering) if _cfg_ is not None else False

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
            if s != "arpending":
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

            # Credit Control
            rp = [item.get("arrp", default=0)]
            if self.i_f.Shared_Credits_AR == 1:
                rp.append(self.i_f.Num_RP_AR)
            sel_rp = await self.wait_on_credit("ar", rp)

            # Rate Limiter
            await self.wait_on_rate(self.control_rate_limit())

            # Unique ID
            if item.get_idunq() or item.get("awatop", default=axi_atomic_t.NON_ATOMIC) != axi_atomic_t.NON_ATOMIC:
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

            # Pending
            if not bool(self.i_f.get("arpending", default=1)):
                self.i_f.set("arpending", 1)
                await RisingEdge(self.i_f.aclk)

            for s in ar_m_signals:
                if s == "arvalid":
                    self.i_f.set(s, 1)
                elif s == "arsharedcrd":
                    self.i_f.set(s, (sel_rp == self.i_f.Num_RP_AR))
                elif s == "arpending":
                    if random.random() > self.pending_rate_limit():
                        self.i_f.set(s, 0)
                else:
                    self.i_f.set(s, item.get(s, default=0))

            while True:
                await RisingEdge(self.i_f.aclk)
                if self.i_f.get("arready", default=1) and self.i_f.get("awakeup", default=1):
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

            # Narrow-transfer byte-lane sampling (AXI A3.2.3 / A3.4.1) is opt-in
            # via cfg.narrow_transfer_lane_steering: when enabled, rdata for this
            # beat lives on byte lanes [byte_offset .. byte_offset + (1<<size) - 1]
            # of the data bus and is de-shifted into a logical value. When disabled,
            # rdata is captured verbatim from the bus (legacy behaviour).
            if self.narrow_transfer_lane_steering:
                if hasattr(item, "awaddr"):
                    addr_key, size_key, burst_key = "awaddr", "awsize", "awburst"
                else:
                    addr_key, size_key, burst_key = "araddr", "arsize", "arburst"
                base_addr = int(item.get(addr_key,  default=0))
                asize     = int(item.get(size_key,  default=0))
                aburst    = int(item.get(burst_key, default=1))
                rlen      = item.get_rlen()
                byte_offset = get_beat_byte_offset(
                    base_addr, item._rcnt_, rlen, asize, aburst, self.i_f.STRB_WIDTH
                )
                num_bytes = 1 << asize
                data_mask = (1 << (num_bytes * 8)) - 1
            else:
                byte_offset = 0

            for s in r_s_signals:
                if s == "rdata" and byte_offset:
                    raw = int(self.i_f.get(s, default=0))
                    item.set(s, (raw >> (byte_offset * 8)) & data_mask, idx=item._rcnt_)
                else:
                    item.set(s, self.i_f.get(s, default=0), idx=item._rcnt_)

            item._rcnt_ += 1
            if item._rcnt_ == item.get_rlen()+1:
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

    async def drive_credits(self) -> None:
        """
        Drive credits
        """

        if self.i_f.AXI_Transport != "Credited":
            return

        while True:
            await RisingEdge(self.i_f.aclk)

            if self.i_f.get("aresetn") == 0:
                continue

            if int(self.i_f.get("rcredits", idx=0, default=0)) < self.i_f.NUM_CREDITS and random.random() <= self.credit_rate_limit():
                self.i_f.set("rcrdt", 1)
            else:
                self.i_f.set("rcrdt", 0)

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
