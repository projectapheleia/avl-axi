# Copyright 2024 Apheleia
#
# Description:
# Apheleia attributes example


import avl
import avl_axi
import cocotb

from z3 import ULE

class CustomWrite(avl_axi.WriteItem):

    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

        self.add_constraint("c_custom_write", lambda x : ULE(x, 8), self.awlen)

class CustomRead(avl_axi.ReadItem):

    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

        self.add_constraint("c_custom_read", lambda x : ULE(x, 8), self.arlen)

class example_env(avl.Env):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.hdl = avl.Factory.get_variable(f"{self.get_full_name()}.hdl", None)
        self.clk = avl.Factory.get_variable(f"{self.get_full_name()}.clk", None)
        self.rst_n = avl.Factory.get_variable(f"{self.get_full_name()}.rst_n", None)
        self.agent = avl_axi.Agent("agent", self)

    async def run_phase(self):
        self.raise_objection()

        cocotb.start_soon(self.timeout(10, units="ms"))
        cocotb.start_soon(self.clock(self.clk, 100))
        await self.async_reset(self.rst_n, duration=100, units="ns", active_high=False)

        self.drop_objection()

@cocotb.test
async def test(dut):
    """
    Example AXI5 Interface with bandwidth monitoring

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
    avl.Factory.set_variable("*.agent.cfg.has_bandwidth", True)

    avl.Factory.set_variable("*.agent.msqr.mseq.n_items", 200)

    avl.Factory.set_variable("*.agent.mwdrv.control_rate_limit", lambda: 0.3)
    avl.Factory.set_variable("*.agent.mwdrv.data_rate_limit", lambda: 0.6)
    avl.Factory.set_variable("*.agent.mrdrv.control_rate_limit", lambda: 0.7)

    avl.Factory.set_override_by_type(avl_axi.SubordinateReadDriver, avl_axi.SubordinateReadRandomDriver)
    avl.Factory.set_override_by_type(avl_axi.WriteItem, CustomWrite)
    avl.Factory.set_override_by_type(avl_axi.ReadItem, CustomRead)

    e = example_env("env", None)
    await e.start()

