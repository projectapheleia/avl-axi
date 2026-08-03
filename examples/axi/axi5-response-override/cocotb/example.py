# Copyright 2025 Apheleia
#
# Description:
# Apheleia response_overrides example


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

        # Test : basic override - matches on addr_range, forces SLVERR regardless
        # of the memory model's real (OKAY) response.
        rsp = await self.read(araddr=0x1000, arid=1, arsize=3, arlock=0)
        assert rsp.rresp[0] == axi_resp_t.SLVERR

        # Test : match_count budget exhausted - the rule above only fires once,
        # so this second read to the same address is unaffected.
        rsp = await self.read(araddr=0x1000, arid=1, arsize=3, arlock=0)
        assert rsp.rresp[0] == axi_resp_t.OKAY

        # Test : override_after_execution - the exclusivity monitor runs first and
        # would promote this OKAY exclusive read to EXOKAY, but the override rule
        # (flagged to apply "after") has the final say and forces it back to OKAY.
        rsp = await self.read(araddr=0x1100, arid=2, arsize=3, arlock=1)
        assert rsp.rresp[0] == axi_resp_t.OKAY

        # Test : override_before_execution - the override rule forces SLVERR before
        # the exclusivity monitor runs, so the monitor sees an error and correctly
        # withholds exclusivity. Nothing runs afterwards to re-stamp the response,
        # so SLVERR survives as the final wire value too.
        rsp = await self.read(araddr=0x1200, arid=3, arsize=3, arlock=1)
        assert rsp.rresp[0] == axi_resp_t.SLVERR

        # Confirm exclusivity was genuinely withheld: a matching exclusive write
        # to the same address gets OKAY, not EXOKAY.
        rsp = await self.write(awaddr=0x1200, awid=3, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.OKAY

        # Test : a rule with neither override_before_execution nor
        # override_after_execution set (both default to None) never applies,
        # at either call site - both flags must be exactly True to fire.
        rsp = await self.read(araddr=0x1500, arid=7, arsize=3, arlock=0)
        assert rsp.rresp[0] == axi_resp_t.OKAY

        # Test : write-side override_after_execution - forces SLVERR over what
        # would otherwise be a genuine EXOKAY exclusive-write match.
        rsp = await self.read(araddr=0x1300, arid=4, arsize=3, arlock=1)
        assert rsp.rresp[0] == axi_resp_t.EXOKAY

        rsp = await self.write(awaddr=0x1300, awid=4, awsize=3, wdata=[0xdeadbeef], wstrb=[0xFF], awlock=1)
        assert rsp.bresp == axi_resp_t.SLVERR


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
    Example AXI5 Interface demonstrating response_overrides on the Subordinate drivers

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

    # Response override rules for the Subordinate Read Driver
    avl.Factory.set_variable(
        "*.agent.srdrv.response_overrides",
        [
            # Forces SLVERR on the very first read to 0x1000, then never again
            {"resp": axi_resp_t.SLVERR, "addr_range": (0x1000, 0x1000), "match_count": 1,
             "override_after_execution": True},
            # Overrides the exclusivity monitor's own EXOKAY promotion
            {"resp": axi_resp_t.OKAY, "addr_range": (0x1100, 0x1100),
             "override_after_execution": True},
            # Seen by the exclusivity monitor - withholds exclusivity as a side effect
            {"resp": axi_resp_t.SLVERR, "addr_range": (0x1200, 0x1200),
             "override_before_execution": True},
            # Neither flag set - this rule is registered but never applies
            {"resp": axi_resp_t.DECERR, "addr_range": (0x1500, 0x1500)},
        ],
    )

    # Response override rules for the Subordinate Write Driver
    avl.Factory.set_variable(
        "*.agent.swdrv.response_overrides",
        [
            {"resp": axi_resp_t.SLVERR, "addr_range": (0x1300, 0x1300), "match_count": 1,
             "override_after_execution": True},
        ],
    )

    avl.Factory.set_override_by_type(avl_axi.SubordinateWriteDriver, avl_axi.SubordinateWriteMemoryDriver)
    avl.Factory.set_override_by_type(avl_axi.SubordinateReadDriver, avl_axi.SubordinateReadMemoryDriver)
    avl.Factory.set_override_by_type(avl_axi.ManagerSequence, DirectedSequence)

    e = example_env("env", None)
    await e.start()
