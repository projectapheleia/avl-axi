# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Agent

import avl
from cocotb.handle import HierarchyObject
from cocotb.triggers import NextTimeStep, RisingEdge

from ._agent_cfg import AgentCfg
from ._bandwidth import Bandwidth
from ._coverage import Coverage
from ._emonitor import ExclusivityMonitor
from ._interface import Interface
from ._mrdriver import ManagerReadDriver
from ._msequence import ManagerSequence
from ._mwakedriver import ManagerWakeDriver
from ._mwdriver import ManagerWriteDriver
from ._rmonitor import ReadMonitor
from ._smemory import SubordinateMemory
from ._srdriver import SubordinateReadDriver
from ._swdriver import SubordinateWriteDriver
from ._wmonitor import WriteMonitor


class Agent(avl.Agent):
    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the avl-apb Agent

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

        # Create configuration and export to children
        self.cfg = avl.Factory.get_variable(f"{self.get_full_name()}.cfg", AgentCfg("cfg", self))
        avl.Factory.set_variable(f"{self.get_full_name()}.*.cfg", self.cfg)

        # Bind HDL to establish parameters and configuration
        self._bind_(avl.Factory.get_variable(f"{self.get_full_name()}.hdl", None))

        # Create sequencer and driver if manager is enabled
        if self.cfg.has_manager:
            self.msqr = avl.Sequencer("msqr", self)
            self.mseq = ManagerSequence("mseq",self.msqr)
            self.mwdrv = ManagerWriteDriver("mwdrv", self)
            self.mrdrv = ManagerReadDriver("mrdrv", self)
            self.mwakedrv = ManagerWakeDriver("mwakedrv", self)
            self.mwdrv._mrdrv_ = self.mrdrv
            self.mrdrv._mwsrv_ = self.mwdrv


            self.msqr.seq_item_export.connect(self.mwdrv.seq_item_port)
            self.msqr.seq_item_export.connect(self.mrdrv.seq_item_port)
            self.mwdrv.wake_export.connect(self.mwakedrv.seq_item_port)
            self.mrdrv.wake_export.connect(self.mwakedrv.seq_item_port)

        if self.cfg.has_subordinate:
            self.smem  = SubordinateMemory(width=self.i_f.DATA_WIDTH)

            if self.cfg.subordinate_ranges is not None:
                for r in self.cfg.subordinate_ranges:
                    self.smem.add_range(r[0], r[1])

            self.swdrv = SubordinateWriteDriver("swdrv", self)
            self.srdrv = SubordinateReadDriver("srdrv", self)
            self.swdrv._srdrv_ = self.srdrv
            self.srdrv._swsrv_ = self.swdrv

            # Shared exclusive monitor
            self.emonitor = ExclusivityMonitor("emonitor", self)
            self.swdrv.emonitor = self.emonitor
            self.srdrv.emonitor = self.emonitor

            # Ensure common memory
            if hasattr(self.srdrv, "memory"):
                self.swdrv.memory = self.srdrv.memory

        # Create monitor if enabled
        if self.cfg.has_monitor:
            self.wmonitor = WriteMonitor("wmonitor", self)
            self.rmonitor = ReadMonitor("rmonitor", self)
            self.wmonitor._mrmon_ = self.rmonitor


            if self.cfg.has_coverage:
                self.coverage = Coverage("coverage", self)
                self.wmonitor.item_export.connect(self.coverage.item_port)
                self.rmonitor.item_export.connect(self.coverage.item_port)

            if self.cfg.has_bandwidth:
                self.wbandwidth = Bandwidth("wbandwidth", self)
                self.wmonitor.item_export.connect(self.wbandwidth.item_port)

                self.rbandwidth = Bandwidth("rbandwidth", self)
                self.wmonitor.item_export.connect(self.rbandwidth.item_port) # For atomics
                self.rmonitor.item_export.connect(self.rbandwidth.item_port)

            if self.cfg.has_trace:
                self.wtrace = avl.Trace("wtrace", self)
                self.wmonitor.item_export.connect(self.wtrace.item_port)
                self.rtrace = avl.Trace("rtrace", self)
                self.rmonitor.item_export.connect(self.rtrace.item_port)

    def _bind_(self, hdl) -> None:
        """
        Bind the agent to a hardware description language (HDL) interface.
        This method is used to associate the agent with a specific HDL interface,
        allowing it to interact with the hardware model.

        :param hdl: The HDL interface to bind to the agent
        :type hdl: HierarchyObject
        :raises TypeError: If `hdl` is not an instance of HierarchyObject
        """
        if not isinstance(hdl, HierarchyObject):
            raise TypeError(f"Expected HierarchyObject, got {type(hdl)}")

        # Assign Interface
        self.i_f = Interface(hdl)
        avl.Factory.set_variable(f"{self.get_full_name()}.*.i_f", self.i_f)

    async def run_phase(self) -> None:
        """
        Run the agent's phase. This method is called to start the agent's operation.
        It initializes the agent and starts the manager and subordinate if they are active.
        """

        self.raise_objection()
        await NextTimeStep()

        if self.cfg.has_manager:
            await self.mseq.start()

        # Run-off
        for _ in range(10):
            await RisingEdge(self.i_f.aclk)

        self.drop_objection()

__all__ = ["Agent"]
