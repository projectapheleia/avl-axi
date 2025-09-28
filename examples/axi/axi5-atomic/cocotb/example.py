# Copyright 2024 Apheleia
#
# Description:
# Apheleia attributes example


import avl
import avl_axi
import cocotb
from avl_axi._types import *

class DirectedSequence(avl_axi.ManagerSequence):
    async def body(self) -> None:
        """
        Body of the sequence
        """

        self.info(f"Starting Directed Manager sequence {self.get_full_name()}")
        self.wait_for = "response"

        # Test : Normal operation
        await self.write(awaddr=0x1000, awid=0, awsize=3, wdata=[0xaaaaaaaaaaaaaaaa], wstrb=[0xFF])

        rsp = await self.read(araddr=0x1000, arid=0, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xaaaaaaaaaaaaaaaa]

        # Test : Atomic load add
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, awatop=axi_atomic_t.LOAD_LE_ADD, wdata=[1])
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xaaaaaaaaaaaaaaaa]

        rsp = await self.read(araddr=0x1000, arid=0, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xaaaaaaaaaaaaaaab]

        # Test : Atomic store add
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, awatop=axi_atomic_t.STORE_LE_ADD, wdata=[2])
        assert rsp.bresp == 0

        rsp = await self.read(araddr=0x1000, arid=0, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xaaaaaaaaaaaaaaad]

        # Test : Atomic clr
        await self.write(awaddr=0x1000, awid=1, awsize=3, wdata=[0xffffffffffff], wstrb=[0xFF])
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, awatop=axi_atomic_t.LOAD_LE_CLR, wdata=[0xffff00000000ffff])
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xffffffffffff]

        rsp = await self.read(araddr=0x1000, arid=0, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0x0000ffffffff0000]

        # Test : Atomic Exclusive OR
        await self.write(awaddr=0x1000, awid=2, awsize=3, wdata=[0xaaaaaaaaaaaaaaaa], wstrb=[0xFF])
        rsp = await self.write(awaddr=0x1000, awid=2, awsize=3, awatop=axi_atomic_t.LOAD_LE_EOR, wdata=[0x5555555555555555])
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xaaaaaaaaaaaaaaaa]

        rsp = await self.read(araddr=0x1000, arid=0, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xffffffffffffffff]

        # Test : Atomic Set
        await self.write(awaddr=0x1000, awid=3, awsize=3, wdata=[0x1234567800000000], wstrb=[0xFF])
        rsp = await self.write(awaddr=0x1000, awid=3, awsize=3, awatop=axi_atomic_t.LOAD_LE_SET, wdata=[0xf000000055555555])
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0x1234567800000000]

        rsp = await self.read(araddr=0x1000, arid=1, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xf234567855555555]

        # Test : Atomic SMAX
        await self.write(awaddr=0x1000, awid=3, awsize=3, wdata=[10], wstrb=[0xFF])
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, awatop=axi_atomic_t.LOAD_LE_SMAX, wdata=[100])
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [10]

        rsp = await self.read(araddr=0x1000, arid=4, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [100]

        # Test : Atomic SMIN
        await self.write(awaddr=0x1000, awid=3, awsize=3, wdata=[20], wstrb=[0xFF])
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, awatop=axi_atomic_t.LOAD_LE_SMIN, wdata=[-100])
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [20]

        rsp = await self.read(araddr=0x1000, arid=4, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [-100&0xffffffffffffffff]

        # Test : Atomic UMAX
        await self.write(awaddr=0x1000, awid=3, awsize=3, wdata=[0x12345], wstrb=[0xFF])
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, awatop=axi_atomic_t.LOAD_LE_UMAX, wdata=[0xfffff])
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0x12345]

        rsp = await self.read(araddr=0x1000, arid=4, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xfffff]

        # Test : Atomic UMIN
        await self.write(awaddr=0x1000, awid=3, awsize=3, wdata=[0xfff], wstrb=[0xFF])
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, awatop=axi_atomic_t.LOAD_LE_UMIN, wdata=[0x23])
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xfff]

        rsp = await self.read(araddr=0x1000, arid=4, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0x23]

        # Test : Atomic SWAP
        await self.write(awaddr=0x1000, awid=3, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF])
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, awatop=axi_atomic_t.SWAP, wdata=[0xcafebabe])
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xdeadbeef]

        rsp = await self.read(araddr=0x1000, arid=4, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xcafebabe]

        # Test : Atomic COMPARE
        await self.write(awaddr=0x1000, awid=3, awsize=3, wdata=[0xcafebabedeadbeef], wstrb=[0xFF])
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, awatop=axi_atomic_t.COMPARE, wdata=[0xb00bf00ddeadbeef])
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xcafebabedeadbeef]

        rsp = await self.read(araddr=0x1000, arid=4, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0xcafebabeb00bf00d]

        # Test : Endianness - ADD
        await self.write(awaddr=0x1000, awid=0, awsize=3, wdata=[0x0001020304050607], wstrb=[0xFF])
        rsp = await self.write(awaddr=0x1000, awid=1, awsize=3, awatop=axi_atomic_t.LOAD_BE_ADD, wdata=[0x01])
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0x0001020304050607]

        rsp = await self.read(araddr=0x1000, arid=4, arsize=3)
        assert rsp.rresp == [axi_resp_t.OKAY] and rsp.rdata == [0x0101020304050607]

        # Test : BURST
        await self.write(awaddr=0x1000, awid=2, awsize=3, awlen=7, awburst=1, wdata=[0xaa00]*8, wstrb=[0xFF]*8)
        rsp = await self.write(awaddr=0x1000, awid=3, awsize=3, awlen=7, awburst=1, awatop=axi_atomic_t.LOAD_LE_SET, wdata=[0x01,0x2,0x3,0x4,0x5,0x6,0x7,0x8])
        assert rsp.rresp == [axi_resp_t.OKAY]*8 and rsp.rdata == [0xaa00]*8

        rsp = await self.read(araddr=0x1000, arid=4, arsize=3, arlen=7, arburst=1)
        assert rsp.rresp == [axi_resp_t.OKAY]*8 and rsp.rdata == [0xaa01,0xaa02,0xaa03,0xaa04,0xaa05,0xaa06,0xaa07,0xaa08]

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
        - Atomic Accesses
        - Memory semantics
        - All cmds wait for resposne
        - Directed atomic tests

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

