# Copyright 2024 Apheleia
#
# Description:
# Apheleia attributes example


import avl
import avl_axi
import cocotb


class DirectedSequence(avl_axi.ManagerSequence):
    async def body(self) -> None:
        """
        Body of the sequence
        """

        self.info(f"Starting Directed Manager sequence {self.get_full_name()}")
        self.wait_for = "response"

        # Writes
        await self.write(awaddr=0x1000, awid=0, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF])
        await self.write(awaddr=0x1008, awid=1, awsize=3, wdata=[0xcafebabe], wstrb=[0xFF])
        await self.write(awaddr=0x1010, awid=2, awsize=3, wdata=[0xf00dfeed], wstrb=[0xFF])

        # Blocking Reads
        rsp = await self.read(araddr=0x1000, arsize=3, arid=0)
        assert rsp.get("rdata", default=0) == { 0 : 0xdeadbeef }

        rsp = await self.read(araddr=0x1008, arsize=3, arid=1)
        assert rsp.get("rdata", default=0) == { 0 : 0xcafebabe }

        rsp = await self.read(araddr=0x1010, arsize=3, arid=2)
        assert rsp.get("rdata", default=0) == { 0 : 0xf00dfeed }

        # Non-blocking reads
        t0 = cocotb.start_soon(self.read(araddr=0x1000, arsize=3, arid=3))
        t1 = cocotb.start_soon(self.read(araddr=0x1008, arsize=3, arid=4))
        t2 = cocotb.start_soon(self.read(araddr=0x1010, arsize=3, arid=5))

        rsp = await t0
        assert rsp.get("rdata", default=0) == { 0 : 0xdeadbeef }

        rsp = await t1
        assert rsp.get("rdata", default=0) == { 0 : 0xcafebabe }

        rsp = await t2
        assert rsp.get("rdata", default=0) == { 0 : 0xf00dfeed }

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
    Example AXI5 Interface directed sequence

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

    # Force a delay on responses
    avl.Factory.set_variable("*.agent.s*drv.response_rate_limit", lambda: 0.1)

    # Define memory range
    avl.Factory.set_variable("*.agent.cfg.subordinate_ranges", [(0x0000, 0x2FFF)])

    avl.Factory.set_override_by_type(avl_axi.SubordinateWriteDriver, avl_axi.SubordinateWriteMemoryDriver)
    avl.Factory.set_override_by_type(avl_axi.SubordinateReadDriver, avl_axi.SubordinateReadMemoryDriver)
    avl.Factory.set_override_by_type(avl_axi.ManagerSequence, DirectedSequence)
    e = example_env("env", None)
    await e.start()

