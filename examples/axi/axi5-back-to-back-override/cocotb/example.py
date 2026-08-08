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
    Demonstrates back_to_back=True forcing gapless issuance by overriding the
    settings that would otherwise introduce delay, using two driver instances in
    one simulation to show the effect and its absence side by side:

     - Write driver (mwdrv, AW/W channels): control_rate_limit and
       data_rate_limit throttled to 0.3 and max_outstanding capped at 1 - all
       settings that would normally introduce a bubble between consecutive
       beats - with back_to_back=True on top. Expect near-gapless AW/W issuance:
       back_to_back overrides these settings back to control_rate_limit=1.0,
       data_rate_limit=1.0 and max_outstanding=None.

     - Read driver (mrdrv, AR channel): the same throttled control_rate_limit
       and max_outstanding, left alone (back_to_back defaults to False). Expect
       bubbly AR issuance - this is the baseline proving the throttled settings
       really do introduce delay when not overridden, i.e. that the write
       channel's gapless result above is due to back_to_back and not because
       the throttled settings are toothless.

    :param dut: The DUT instance
    :return: None
    """
    avl.Factory.set_variable("*.clk", dut.clk)
    avl.Factory.set_variable("*.rst_n", dut.rst_n)
    avl.Factory.set_variable("*.hdl", dut.axi_if)
    avl.Factory.set_variable("*.agent.cfg.has_manager", True)
    avl.Factory.set_variable("*.agent.cfg.has_subordinate", True)
    avl.Factory.set_variable("*.agent.cfg.has_monitor", True)
    avl.Factory.set_variable("*.agent.msqr.mseq.n_items", 150)

    # Write channel: throttled settings, overridden back to gapless via back_to_back
    avl.Factory.set_variable("*.agent.mwdrv.control_rate_limit", lambda: 0.3)
    avl.Factory.set_variable("*.agent.mwdrv.data_rate_limit", lambda: 0.3)
    avl.Factory.set_variable("*.agent.mwdrv.max_outstanding", 1)
    avl.Factory.set_variable("*.agent.mwdrv.back_to_back", True)

    # Read channel: the same throttled settings, left as a baseline (no override)
    avl.Factory.set_variable("*.agent.mrdrv.control_rate_limit", lambda: 0.3)
    avl.Factory.set_variable("*.agent.mrdrv.max_outstanding", 1)

    results = {}
    stop = {"done": False}
    for label, valid, ready in (("aw", "awvalid", "awready"), ("ar", "arvalid", "arready"), ("w", "wvalid", "wready")):
        cocotb.start_soon(monitor_channel(dut, valid, ready, results, label, stop))

    e = example_env("env", None)
    await e.start()

    stop["done"] = True
    await RisingEdge(dut.clk)

    # aw/w: back_to_back=True should override the throttling -> mostly gapless
    # ar: no back_to_back -> throttling should show through as bubbles
    expect_back_to_back = {"aw": True, "w": True, "ar": False}

    for label, expect in expect_back_to_back.items():
        accepted, gaps = results[label]
        n_b2b = gaps.count(1)
        n_gaps = len(gaps)
        fraction = 1.0 if n_gaps == 0 else n_b2b / n_gaps
        cocotb.log.info(f"{label}: accepted={len(accepted)} back_to_back={n_b2b}/{n_gaps} ({fraction:.0%})")

        assert accepted, f"no {label} transactions observed"
        if expect:
            assert n_gaps == 0 or fraction >= 0.9, (
                f"{label}: expected back_to_back=True to override the throttled settings and "
                f"produce mostly gapless beats, got only {n_b2b}/{n_gaps}"
            )
        else:
            assert fraction < 0.5, (
                f"{label}: expected the throttled settings to introduce bubbles without "
                f"back_to_back, but {n_b2b}/{n_gaps} consecutive beats were back-to-back anyway"
            )
