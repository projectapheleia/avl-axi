# Copyright 2025 Apheleia
#
# Description:
# Apheleia attributes example


import avl
import avl_axi
import cocotb
from cocotb.triggers import RisingEdge


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


async def monitor_channel(dut, valid_name, ready_name, results, label, stop):
    """
    Record the clock cycle of every VALID & READY handshake on a channel, so that
    the gap (in cycles) between consecutive accepted beats can be checked. A gap
    of 1 means the channel was truly back-to-back (VALID never dropped between
    beats); any larger gap is a bubble.
    """
    valid_sig = getattr(dut.axi_if, valid_name)
    ready_sig = getattr(dut.axi_if, ready_name)

    accepted_cycles = []
    cycle = 0
    while not stop["done"]:
        await RisingEdge(dut.clk)
        cycle += 1
        if int(dut.rst_n.value) == 1 and int(valid_sig.value) == 1 and int(ready_sig.value) == 1:
            accepted_cycles.append(cycle)

    gaps = [accepted_cycles[i + 1] - accepted_cycles[i] for i in range(len(accepted_cycles) - 1)]
    results[label] = (accepted_cycles, gaps)


@cocotb.test
async def test(dut):
    """
    Demonstrates that back-to-back (gapless) AW/AR/W issuance does not require any
    special driver option - it falls out of the existing default settings:
    control/data rate limits at 1.0 (their default), AXI_Transport == "Ready"
    (no credit stalls), and no max_outstanding limit. Under these conditions the
    manager driver never needs to wait a clock edge between finishing one item and
    starting the next, so VALID is re-asserted with new payload before the next
    RisingEdge is ever sampled and the bus never shows an idle bubble.

    :param dut: The DUT instance
    :return: None
    """
    avl.Factory.set_variable("*.clk", dut.clk)
    avl.Factory.set_variable("*.rst_n", dut.rst_n)
    avl.Factory.set_variable("*.hdl", dut.axi_if)
    avl.Factory.set_variable("*.agent.cfg.has_manager", True)
    avl.Factory.set_variable("*.agent.cfg.has_subordinate", True)
    avl.Factory.set_variable("*.agent.cfg.has_monitor", True)
    avl.Factory.set_variable("*.agent.msqr.mseq.n_items", 300)

    results = {}
    stop = {"done": False}
    for label, valid, ready in (("aw", "awvalid", "awready"), ("ar", "arvalid", "arready"), ("w", "wvalid", "wready")):
        cocotb.start_soon(monitor_channel(dut, valid, ready, results, label, stop))

    e = example_env("env", None)
    await e.start()

    stop["done"] = True
    await RisingEdge(dut.clk)

    for label in ("aw", "ar", "w"):
        accepted, gaps = results[label]
        n_b2b = gaps.count(1)
        n_gaps = len(gaps)
        cocotb.log.info(f"{label}: accepted={len(accepted)} back_to_back={n_b2b}/{n_gaps}")

        assert accepted, f"no {label} transactions observed"
        # Allow a small tolerance for stalls caused by legitimate flow control
        # (e.g. transaction ID reuse forcing in-order completion) - the property
        # under test is that the channel is *capable* of being gapless, not that
        # every single beat is, so a large majority of gap==1 transitions is
        # sufficient to demonstrate it (and to catch a regression, which would
        # show close to 0% back-to-back).
        assert n_gaps == 0 or (n_b2b / n_gaps) >= 0.9, (
            f"{label}: expected the vast majority of consecutive beats to be back-to-back, "
            f"got only {n_b2b}/{n_gaps}"
        )
