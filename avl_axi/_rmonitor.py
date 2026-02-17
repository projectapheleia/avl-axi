# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Monitor

import asyncio

import avl
import cocotb
from cocotb.triggers import FallingEdge, RisingEdge

from ._item import ReadItem
from ._signals import ar_m_signals, r_s_signals


class ReadMonitor(avl.Monitor):
    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the Read Monitor for the AXI agent.

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

        self.i_f = avl.Factory.get_variable(f"{self.get_full_name()}.i_f", None)

        self.responseQ = {}
        for i in range(2**self.i_f.ID_R_WIDTH):
            self.responseQ[i] = avl.List()

        # Credits
        self.credits = {"control" : {}, "data" : {}, "response" : {}}

    def reset(self) -> None:
        """
        Reset the monitor state
        """

        for i in range(2**self.i_f.ID_R_WIDTH):
            self.responseQ[i].clear()

    async def wait_on_reset(self) -> None:
        """
        Wait for the reset signal to go low and then call the reset method.
        This method is called to ensure that the driver is reset before driving any signals.
        It waits for the presetn signal to go low, indicating that the reset is active,
        and then calls the reset method to set all signals to their default values.
        """

        try:
            await FallingEdge(self.i_f.aresetn)
            self.reset()
        except asyncio.CancelledError:
            raise
        except Exception:
            pass

    async def monitor_control(self) -> None:
        """
        Monitor the AXI Write Control Bus
        """

        while True:
            item = ReadItem("from_monitor", self)

            cnt = None
            while True:
                if self.i_f.get("arvalid", default=0) and self.i_f.get("awakeup", default=1):
                    if cnt is None:
                        cnt = 0
                    else:
                        cnt += 1
                    if self.i_f.get("arready", default=1):
                        break
                await RisingEdge(self.i_f.aclk)

            for s in ar_m_signals:
                item.set(s, self.i_f.get(s, default=0))
            item.set("ar_wait_cycles", cnt)
            item.resize()
            item.set_event("control")
            self.responseQ[item.get_id()].append(item)
            await RisingEdge(self.i_f.aclk)

    async def monitor_response(self, id : int=0) -> None:
        """
        Monitor the AXI Write Response Bus
        """

        while True:
            item = await self.responseQ[id].blocking_pop()

            for i in range(item.get_len()+1):
                cnt = None
                while True:
                    if self.i_f.get("rvalid", default=0) and self.i_f.get("rid", default=0) == id and self.i_f.get("awakeup", default=1):
                        if cnt is None:
                            cnt = 0
                        else:
                            cnt += 1
                        if self.i_f.get("rready", default=1):
                            break
                    await RisingEdge(self.i_f.aclk)

                for s in r_s_signals:
                    item.set(s, self.i_f.get(s, default=0), idx=i)
                item.set("r_wait_cycles", cnt, idx=i)

                # Reduced data phase
                if not hasattr(item, "awaddr"):
                    for s in ["rdata", "rresp", "ruser", "rpoison", "rtrace", "rloop"]:
                        if hasattr(item, s):
                            [_or_, _and_] = getattr(item, f"_{s}_")
                            _or_  |= item.get(s, idx=i)
                            _and_ &= item.get(s, idx=i)


                if i == item.get_len():
                    # Sanity Checks
                    item.sanity()

                    # Export
                    # Inform sequence response phase is complete
                    # Extra checks for items which have both r and b responses (atomics)
                    # Only call response callback when all completed
                    if not item.has_bresp():
                        item.set_event("response", item)
                        self.item_export.write(item)
                    else:
                        if hasattr(item, "_bresp_complete_"):
                            delattr(item, "_bresp_complete_")
                            item.set_event("response", item)
                            self.item_export.write(item)
                        else:
                            setattr(item, "_rresp_complete_", True)

                # Wait for next edge
                await RisingEdge(self.i_f.aclk)

    async def monitor_credits(self) -> None:
        """
        Monitor credits
        """

        if self.i_f.AXI_Transport != "Credited":
            return

        while True:
            await RisingEdge(self.i_f.aclk)

            if self.i_f.get("aresetn") == 0:
                for i in range(self.i_f.Num_RP_AR):
                     self.credits["control"][i] = 0
                self.credits["response"][0] = 0
            else:
                # Control
                if self.i_f.get("arvalid", default=0) == 1:
                    self.credits["control"][int(self.i_f.get("arrp", default=0))] -= 1

                arcrdt = int(self.i_f.get("arcrdt", default=0))
                for i in range(self.i_f.Num_RP_AR):
                    if (arcrdt >> i ) & 0x1 == 1:
                        self.credits["control"][i] += 1

                    assert self.credits["control"][i] >= 0 and self.credits["control"][i] <= self.i_f.NUM_CREDITS

                # Response
                if self.i_f.get("rvalid", default=0) == 1:
                    self.credits["response"][0] -= 1

                if self.i_f.get("rcrdt", default=0) == 1:
                    self.credits["response"][0] += 1

                assert self.credits["response"][0] >= 0 and self.credits["response"][0] <= self.i_f.NUM_CREDITS

    async def run_phase(self):
        """
        Run phase for the Requester Driver.
        This method is called during the run phase of the simulation.
        It is responsible for driving the request signals based on the sequencer's items.

        :raises NotImplementedError: If the run phase is not implemented.
        """

        self.reset()

        while True:

            tasks = []
            tasks.append(cocotb.start_soon(self.monitor_control()))

            for i in range(2**self.i_f.ID_R_WIDTH):
                tasks.append(cocotb.start_soon(self.monitor_response(i)))

            tasks.append(cocotb.start_soon(self.monitor_credits()))

            await self.wait_on_reset()

            for t in tasks:
                if not t.done():
                    t.cancel()

__all__ = ["ReadMonitor"]
