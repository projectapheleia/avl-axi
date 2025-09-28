# Copyright 2024 Apheleia
#
# Description:
# Apheleia attributes example


import avl
import avl_axi
import cocotb
from avl_axi._types import axi_resp_t


class DirectedSequence(avl_axi.ManagerSequence):
    async def body(self) -> None:
        """
        Body of the sequence
        """

        self.info(f"Starting Directed Manager sequence {self.get_full_name()}")
        self.wait_for = "response"

        # Test : Normal operation
        await self.read(araddr=0x1000, arid=1, arsize=3, arlock=1)

        # Matching Exclusive Write - return EXOKAY
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.EXOKAY

        # Matching Exclusive Write - return OKAY
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Test : Clear by partial Match (smaller)
        await self.read(araddr=0x1000, arid=2, arsize=3, arlock=1)

        # Partial Matching Exclusive Write - return OKAY
        rsp = await self.write(awaddr=0x1000, awid=2, awsize=2, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Matching Exclusive Write - return OKAY
        rsp = await self.write(awaddr=0x1000, awid=2, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Test : Clear by artial Match (bigger)
        await self.read(araddr=0x1000, arid=3, arsize=0, arlock=1)

        # Partial Matching Exclusive Write - return OKAY
        rsp = await self.write(awaddr=0x1000, awid=3, awsize=2, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Matching Exclusive Write - return OKAY
        rsp = await self.write(awaddr=0x1000, awid=3, awsize=0, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Test : Clear by Miss
        await self.read(araddr=0x1000, arid=3, arsize=0, arlock=1)

        # Partial Matching Exclusive Write - return OKAY
        rsp = await self.write(awaddr=0x2000, awid=3, awsize=2, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Matching Exclusive Write - return OKAY
        rsp = await self.write(awaddr=0x1000, awid=3, awsize=0, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Test : Clear by exact match with other manager
        await self.read(araddr=0x1000, arid=4, arsize=3, arlock=1)

        # Partial Matching Exclusive Write - return OKAY
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Matching Exclusive Write - return OKAY
        rsp = await self.write(awaddr=0x1000, awid=4, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Test : Clear by partial match with other manager
        await self.read(araddr=0x1000, arid=5, arsize=3, arlock=1)

        # Partial Matching Exclusive Write - return OKAY
        rsp = await self.write(awaddr=0x1000, awid=2, awsize=1, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Matching Exclusive Write - return OKAY
        rsp = await self.write(awaddr=0x1000, awid=5, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Test : No clear by write to different range
        await self.read(araddr=0x1000, arid=0, arsize=3, arlock=1)

        # Miss (different master) - return OKAY
        rsp = await self.write(awaddr=0x1020, awid=1, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Matching Exclusive Write - return EXOKAY
        rsp = await self.write(awaddr=0x1000, awid=0, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.EXOKAY

        # Test : Update
        await self.read(araddr=0x1000, arid=0, arsize=3, arlock=1)
        await self.read(araddr=0x2000, arid=0, arsize=3, arlock=1)

        # Miss - would have hit first - return OK
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Matching Exclusive Write - return EXOKAY
        await self.read(araddr=0x1000, arid=0, arsize=3, arlock=1)
        await self.read(araddr=0x2000, arid=0, arsize=3, arlock=1)
        rsp = await self.write(awaddr=0x2000, awid=0, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.EXOKAY

        # Test : Read burst - Write single Match
        await self.read(araddr=0x1000, arid=1, arsize=3, arlen=2, awburst=1, arlock=1)

        # Matching Exclusive Write - return EXOKAY
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.EXOKAY

        # Test : Read Single - Write burst Match
        await self.read(araddr=0x1000, arid=1, arsize=3, arlock=1)

        # Matching Exclusive Write - return EXOKAY
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, awlen=1, awburst=2, wdata=[0xdeadbeef, 0xcafebabe], wstrb=[0xFF]*2, awlock=1)
        assert rsp.bresp == axi_resp_t.EXOKAY

        # Test : Read Burst - Write miss 0
        await self.read(araddr=0x1000, arid=1, arsize=3, arlen=1, awburst=1, arlock=1)

        # Matching Exclusive Write (wrong beat) - return OKAY
        rsp = await self.write(awaddr=0x1008, awid=1, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY


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
    Example AXI5 Interface with exclusive accesses

    :param dut: The DUT instance
    :return: None
    """
    avl.Factory.set_variable("*.clk", dut.clk)
    avl.Factory.set_variable("*.rst_n", dut.rst_n)
    avl.Factory.set_variable("*.hdl", dut.axi_if)
    avl.Factory.set_variable("*.agent.cfg.has_manager", True)
    avl.Factory.set_variable("*.agent.cfg.has_subordinate", True)
    avl.Factory.set_variable("*.agent.cfg.has_monitor", False)
    avl.Factory.set_variable("*.agent.cfg.has_trace", False)
    avl.Factory.set_variable("*.agent.msqr.mseq.n_items", 100)

    # Define memory range
    avl.Factory.set_variable("*.agent.cfg.subordinate_ranges", [(0x0000, 0x2FFF)])

    avl.Factory.set_override_by_type(avl_axi.SubordinateWriteDriver, avl_axi.SubordinateWriteMemoryDriver)
    avl.Factory.set_override_by_type(avl_axi.SubordinateReadDriver, avl_axi.SubordinateReadMemoryDriver)
    avl.Factory.set_override_by_type(avl_axi.ManagerSequence, DirectedSequence)

    e = example_env("env", None)
    await e.start()

