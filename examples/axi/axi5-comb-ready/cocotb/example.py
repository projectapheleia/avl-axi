# Copyright 2024 Apheleia
#
# PR #41 reproducer: one write + read against a subordinate with a comb ready
# loop on every channel the fix touches (rtl/example_hdl.sv). A watcher records
# whether each RTL-driven ready reached the wire. Gate: AW/AR ready must be
# observed high.
#
#                 Verilator stock  Verilator fixed  Questa stock/fixed
#   awready/arready  collapsed        visible          visible
#   wready           collapsed        collapsed(GAP)   visible
#   example.test     FAIL             PASS             PASS
#
# On stock Verilator the AW/AR comb pulses collapse to a zero-duration glitch;
# the fix holds them one settle-delta -> observable. wready stays collapsed even
# with the fix (drive_data unpatched). Questa has no collapse, so no regression.
# Questa on a login node lacking X11: `make SIM=questa-compat TOPLEVEL_LANG=verilog`.

import avl
import avl_axi
import cocotb
from cocotb.triggers import Timer


class WriteReadSeq(avl_axi.ManagerSequence):
    """One write then one read, so AW/W/B and AR/R are all exercised."""

    async def body(self):
        self.info("WriteReadSeq: sending 1 write")
        await self.write(awaddr=0x100)
        self.info("WriteReadSeq: write complete, sending 1 read")
        await self.read(araddr=0x200)
        self.info("WriteReadSeq: read complete")


class example_env(avl.Env):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.hdl = avl.Factory.get_variable(f"{self.get_full_name()}.hdl", None)
        self.clk = avl.Factory.get_variable(f"{self.get_full_name()}.clk", None)
        self.rst_n = avl.Factory.get_variable(f"{self.get_full_name()}.rst_n", None)
        self.agent = avl_axi.Agent("agent", self)

    async def run_phase(self):
        self.raise_objection()

        # Short timeout so a stock-buggy run that wedges terminates rather than
        # hanging indefinitely.
        cocotb.start_soon(self.timeout(20, units="us"))
        cocotb.start_soon(self.clock(self.clk, 100))
        await self.async_reset(self.rst_n, duration=100, units="ns", active_high=False)

        self.drop_objection()


async def wire_watcher(sigs):
    """Poll each signal every 1 ns; record whether it was ever high on the wire."""
    seen = {name: False for name in sigs}
    while True:
        await Timer(1, units="ns")
        for name, handle in sigs.items():
            try:
                if int(handle.value) == 1:
                    seen[name] = True
            except ValueError:
                pass  # x/z during reset
        wire_watcher.seen = seen


wire_watcher.seen = {}


@cocotb.test
async def test(dut):
    """One AVL write + one read against the all-channel comb/registered subordinate."""
    avl.Factory.set_variable("*.clk", dut.clk)
    avl.Factory.set_variable("*.rst_n", dut.rst_n)
    avl.Factory.set_variable("*.hdl", dut.axi_if)
    avl.Factory.set_variable("*.agent.cfg.has_manager", True)
    # Subordinate off: readies/valids come from pure RTL (example_hdl.sv).
    avl.Factory.set_variable("*.agent.cfg.has_subordinate", False)
    avl.Factory.set_variable("*.agent.cfg.has_monitor", True)
    avl.Factory.set_variable("*.agent.msqr.mseq.n_items", 1)

    avl.Factory.set_override_by_type(avl_axi.ManagerSequence, WriteReadSeq)

    watcher = cocotb.start_soon(wire_watcher({
        "awready": dut.axi_if.awready,
        "wready":  dut.axi_if.wready,
        "arready": dut.axi_if.arready,
        "bvalid":  dut.axi_if.bvalid,
        "rvalid":  dut.axi_if.rvalid,
    }))

    e = example_env("env", None)
    await e.start()

    watcher.cancel()
    seen = wire_watcher.seen
    dut._log.info("WIRE " + " ".join(f"{k}_high={v}" for k, v in seen.items()))

    # Gate: AW/AR ready (drive_control sample, patched) must reach the wire.
    assert seen["awready"], "awready never observed high (AW comb pulse collapsed)"
    assert seen["arready"], "arready never observed high (AR comb pulse collapsed)"

    # W is unpatched (drive_data), so wready stays collapsed even with the fix: log only.
    if not seen["wready"]:
        dut._log.warning("KNOWN GAP: wready never observed high (drive_data unpatched)")
