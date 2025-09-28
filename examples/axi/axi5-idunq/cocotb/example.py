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
        Body of the sequence - no waiting from sequence
        """

        self.info(f"Starting Directed Manager sequence {self.get_full_name()}")

        # Writes
        await self.write(awaddr=0x1000, awid=0, awidunq=1, awlen=7, awsize=3, awburst=1, wdata=[0,1,2,3,4,5,6,7], wstrb=[0xFF]*8)
        await self.write(awaddr=0x1100, awid=1, awidunq=1, awlen=15, awsize=0, awburst=2, wdata=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], wstrb=[0x1]*16)
        await self.write(awaddr=0x1200, awid=0, awidunq=0, awlen=3, awsize=2, awburst=1, wdata=[20,30,40,50], wstrb=[0xFF]*4) # Should block
        await self.write(awaddr=0x1300, awid=2, awidunq=0, awlen=0, awsize=3, awburst=1, wdata=[0xcafebabe], wstrb=[0xFF])

        # Reads
        await self.read(araddr=0x2000, arid=0, aridunq=1, arlen=1, arsize=2, arburst=2)
        await self.read(araddr=0x2100, arid=1, aridunq=1, arlen=2, arsize=1, arburst=1)
        await self.read(araddr=0x2200, arid=0, aridunq=0, arlen=4, arsize=3, arburst=1) # Should block
        await self.read(araddr=0x2300, arid=2, aridunq=0, arlen=3, arsize=2, arburst=2)


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
    Example Simple interface
        - AXI5 (burst with wlast/rlast)
        - 3 bit read and write ids
        - Memory semantics
        - All zero delay
        - 100 items mix of read and write

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

    avl.Factory.set_variable("*.agent.swdrv.response_rate_limit", lambda: 0.05)
    avl.Factory.set_variable("*.agent.srdrv.response_rate_limit", lambda: 0.05)

    # Define memory range
    avl.Factory.set_variable("*.agent.cfg.subordinate_ranges", [(0x0000, 0x2FFF)])

    avl.Factory.set_override_by_type(avl_axi.SubordinateWriteDriver, avl_axi.SubordinateWriteMemoryDriver)
    avl.Factory.set_override_by_type(avl_axi.SubordinateReadDriver, avl_axi.SubordinateReadMemoryDriver)
    avl.Factory.set_override_by_type(avl_axi.ManagerSequence, DirectedSequence)

    e = example_env("env", None)
    await e.start()

