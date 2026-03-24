# Copyright 2024 Apheleia
#
# Description:
# Apheleia attributes example


import avl
import avl_axi
import cocotb
from avl_axi._types import axi_resp_t
from z3 import UGE, ULE, And, BitVecVal, Implies, Or, ZeroExt

class DirectedSequence(avl_axi.ManagerSequence):
    async def body(self) -> None:
        """
        Body of the sequence
        """

        self.info(f"Starting Directed Manager sequence {self.get_full_name()}")
        self.wait_for = "response"

        wdata = [0<<0,1<<8,2<<16,3<<24,4<<32,5<<40,6<<48,7<<56]
        await self.write(awaddr=0x1000, awcache=0, awid=0, awlen=7, awsize=0, awburst=1, wdata=wdata, wstrb=[1, 1<<1, 1<<2, 1<<3, 1<<4, 1<<5, 1<<6, 1<<7], awlock=0)
        rsp = await self.read (araddr=0x1000, arcache=0, arid=0, arlen=7, arsize=0, arburst=1, arlock=0)
        assert list(rsp.rresp.values()) == [axi_resp_t.OKAY]*8 and list(rsp.rdata.values()) == wdata

class example_env(avl.Env):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.hdl = avl.Factory.get_variable(f"{self.get_full_name()}.hdl", None)
        self.clk = avl.Factory.get_variable(f"{self.get_full_name()}.clk", None)
        self.rst_n = avl.Factory.get_variable(f"{self.get_full_name()}.rst_n", None)
        self.agent = avl_axi.Agent("agent", self)

    async def run_phase(self):
        self.raise_objection()

        cocotb.start_soon(self.timeout(1, units="ms"))
        cocotb.start_soon(self.clock(self.clk, 100))
        await self.async_reset(self.rst_n, duration=100, units="ns", active_high=False)

        self.drop_objection()

@cocotb.test
async def test(dut):
    """
    Example AXI5 Interface with bursts

    :param dut: The DUT instance
    :return: None
    """
    avl.Factory.set_variable("*.clk", dut.clk)
    avl.Factory.set_variable("*.rst_n", dut.rst_n)
    avl.Factory.set_variable("*.hdl", dut.axi_if)
    avl.Factory.set_variable("*.agent.cfg.has_manager", True)
    avl.Factory.set_variable("*.agent.cfg.has_subordinate", True)
    avl.Factory.set_variable("*.agent.cfg.has_monitor", True)
    avl.Factory.set_variable("*.agent.cfg.has_trace", True)
    avl.Factory.set_variable("*.agent.cfg.has_coverage", True)
    avl.Factory.set_variable("*.agent.msqr.mseq.n_items", 100)

    avl.Factory.set_variable("*.agent.swdrv.control_rate_limit", lambda: 0.5)
    avl.Factory.set_variable("*.agent.swdrv.data_rate_limit", lambda: 0.5)
    avl.Factory.set_variable("*.agent.mwdrv.response_rate_limit", lambda: 0.5)
    avl.Factory.set_variable("*.agent.srdrv.control_rate_limit", lambda: 0.1)
    avl.Factory.set_variable("*.agent.mrdrv.response_rate_limit", lambda: 0.1)

    # Define memory range
    avl.Factory.set_variable("*.agent.cfg.subordinate_ranges", [(0x0000, 0x2FFF)])

    avl.Factory.set_override_by_type(avl_axi.SubordinateWriteDriver, avl_axi.SubordinateWriteMemoryDriver)
    avl.Factory.set_override_by_type(avl_axi.SubordinateReadDriver, avl_axi.SubordinateReadMemoryDriver)
    avl.Factory.set_override_by_type(avl_axi.ManagerSequence, DirectedSequence)

    e = example_env("env", None)
    await e.start()

