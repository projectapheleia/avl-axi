# Copyright 2024 Apheleia
#
# Description:
# Apheleia attributes example


import avl
import avl_axi
import cocotb
from avl_axi._types import axi_burst_t


class DirectedSequence(avl_axi.ManagerSequence):
    async def body(self) -> None:
        """
        Body of the sequence
        """

        self.info(f"Starting Directed Manager sequence {self.get_full_name()}")
        self.wait_for = "response"

        # Writes
        await self.write(awaddr=0x1000, awid=0, awlen=7, awsize=2, awburst=axi_burst_t.INCR, wdata=[0,1,2,3,4,5,6,7], wstrb=[0xF]*8)
        await self.write(awaddr=0x2020, awid=1, awlen=15, awsize=2, awburst=axi_burst_t.WRAP, wdata=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], wstrb=[0xF]*16)
        # Unaligned write burst
        await self.write(awaddr=0x2801, awid=1, awlen=15, awsize=2, awburst=axi_burst_t.INCR, wdata=[0xFFFF_FFFF,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], wstrb=[0xF]*16)

        # Check
        rsp = await self.read(araddr=0x1004, arid=1, arlen=7, arsize=2, arburst=axi_burst_t.FIXED)
        assert list(rsp.rdata.values()) == [1,1,1,1,1,1,1,1]

        rsp = await self.read(araddr=0x1000, arid=2, arlen=7, arsize=2, arburst=axi_burst_t.INCR)
        assert list(rsp.rdata.values()) == [0,1,2,3,4,5,6,7]

        rsp = await self.read(araddr=0x1010, arid=3, arlen=7, arsize=2, arburst=axi_burst_t.WRAP)
        assert list(rsp.rdata.values()) == [4,5,6,7,0,1,2,3]

        rsp = await self.read(araddr=0x2000, arid=2, arlen=15, arsize=2, arburst=axi_burst_t.WRAP)
        assert list(rsp.rdata.values()) == [0x08, 0x09, 0x0a, 0x0b,
                                            0x0c, 0x0d, 0x0e, 0x0f,
                                            0x00, 0x01, 0x02, 0x03,
                                            0x04, 0x05, 0x06, 0x07]

        # Only the first beat is affected by the unaligned address.
        rsp = await self.read(araddr=0x2800, arid=2, arlen=15, arsize=2, arburst=axi_burst_t.INCR)
        assert list(rsp.rdata.values()) == [0xFFFF_FF00,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

        # Same read as above, but unaligned, expect the same data.
        rsp = await self.read(araddr=0x2801, arid=2, arlen=15, arsize=2, arburst=axi_burst_t.INCR)
        assert list(rsp.rdata.values()) == [0xFFFF_FF00,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

        rsp = await self.read(araddr=0x2802, arid=2, arlen=15, arsize=2, arburst=axi_burst_t.INCR)
        assert list(rsp.rdata.values()) == [0xFFFF_FF00,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

        rsp = await self.read(araddr=0x2803, arid=2, arlen=15, arsize=2, arburst=axi_burst_t.INCR)
        assert list(rsp.rdata.values()) == [0xFFFF_FF00,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

        rsp = await self.read(araddr=0x2804, arid=2, arlen=15, arsize=2, arburst=axi_burst_t.INCR)
        assert list(rsp.rdata.values()) == [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0]

        rsp = await self.read(araddr=0x2805, arid=2, arlen=15, arsize=2, arburst=axi_burst_t.INCR)
        assert list(rsp.rdata.values()) == [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0]

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

