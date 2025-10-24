# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Monitor

import asyncio

import avl
import cocotb
from cocotb.triggers import FallingEdge, RisingEdge

from ._item import WriteItem
from ._signals import aw_m_signals, b_s_signals, w_m_signals


class WriteMonitor(avl.Monitor):
    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the Write Monitor for the AXI agent.

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

        self.i_f = avl.Factory.get_variable(f"{self.get_full_name()}.i_f", None)

        # Manager Read Monitor
        self._mrmon_ = None

        self.dataQ = avl.List()
        self.controlQ = avl.List()
        self.responseQ = {}
        for i in range(2**self.i_f.ID_W_WIDTH):
            self.responseQ[i] = avl.List()

    def reset(self) -> None:
        """
        Reset the monitor state
        """

        self.dataQ.clear()
        self.controlQ.clear()
        for i in range(2**self.i_f.ID_W_WIDTH):
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

                # Reduced data phase
                for s in ["wdata", "wstrb", "wuser", "wpoison", "wtrace"]:
                    if hasattr(item, s):
                        [_or_, _and_] = getattr(item, f"_{s}_")
                        _or_  |= item.get(s, idx=i)
                        _and_ &= item.get(s, idx=i)

            item.set_event("data")
            self.responseQ[item.get_id()].append(item)

    async def monitor_control(self) -> None:
        """
        Monitor the AXI Write Control Bus
        """

        self.controlQ.clear()
        while True:
            item = WriteItem("from_monitor", self)

            cnt = None
            while True:
                if self.i_f.get("awvalid", default=0) and self.i_f.get("awakeup", default=1):
                    if cnt is None:
                        cnt = 0
                    else:
                        cnt += 1
                    if self.i_f.get("awready", default=0):
                        break
                await RisingEdge(self.i_f.aclk)

            for s in aw_m_signals:
                item.set(s, self.i_f.get(s, default=0))
            item.set("aw_wait_cycles", cnt)

            item.resize()
            item.set_event("control")
            self.controlQ.append(item)
            if item.has_rresp():
                self._mrmon_.responseQ[item.get_id()].append(item)

            await RisingEdge(self.i_f.aclk)

    async def monitor_data(self) -> None:
        """
        Monitor the AXI Write Data Bus
        """

        self.dataQ.clear()
        cnt = None
        while True:
            if self.i_f.get("wvalid", default=0) and self.i_f.get("awakeup", default=1):
                if cnt is None:
                    cnt = 0
                else:
                    cnt += 1
                if self.i_f.get("wready", default=0):
                    data = {}
                    for s in w_m_signals:
                        data[s] = self.i_f.get(s, default=0)
                    data["w_wait_cycles"] = cnt
                    self.dataQ.append(data)
                    cnt = None
            await RisingEdge(self.i_f.aclk)


    async def monitor_response(self, id : int=0) -> None:
        """
        Monitor the AXI Write Response Bus

        :param id awid
        """

        self.responseQ[id].clear()
        while True:
            item = await self.responseQ[id].blocking_pop()

            while True:
                cnt = None
                if self.i_f.get("bvalid", default=0) and self.i_f.get("bid", default=0) == id:
                    if cnt is None:
                        cnt = 0
                    else:
                        cnt += 1
                    if self.i_f.get("bready", default=0):
                        break
                await RisingEdge(self.i_f.aclk)

            for s in b_s_signals:
                item.set(s, self.i_f.get(s, default=0))
            item.set("b_wait_cycles", cnt)

            # Sanity Checks
            item.sanity()

            # Export
            if not item.has_rresp():
                item.set_event("response")
                self.item_export.write(item)
            else:
                if hasattr(item, "_rresp_complete_"):
                    delattr(item, "_rresp_complete_")
                    item.set_event("response")
                    self.item_export.write(item)
                else:
                    setattr(item, "_bresp_complete_", True)

            # Wait for next edge
            await RisingEdge(self.i_f.aclk)

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
            tasks.append(cocotb.start_soon(self._wait_for_data_()))
            tasks.append(cocotb.start_soon(self.monitor_control()))
            tasks.append(cocotb.start_soon(self.monitor_data()))

            for i in range(2**self.i_f.ID_W_WIDTH):
                tasks.append(cocotb.start_soon(self.monitor_response(i)))

            await self.wait_on_reset()

            for t in tasks:
                if not t.done():
                    t.cancel()

__all__ = ["WriteMonitor"]
