# Copyright 2024 Apheleia
#
# Description:
# Apheleia types example

import cocotb
from avl_axi._types import axi_burst_t, axi_resp_t, axi_domain_t, axi_atomic_t, axi_secsid_t

@cocotb.test
async def test(dut):
    """
    Example of working with the various AXI types
    """
    # axi_burst_t
    print("=== axi_burst_t ===")
    print(axi_burst_t(1))           # → INCR
    print(axi_burst_t.WRAP)         # → 2

    # axi_resp_t
    print("=== axi_resp_t ===")
    print(axi_resp_t(3))            # → DECERR
    print(axi_resp_t.TRANSFAULT)    # → 5

    # axi_domain_t
    print("=== axi_domain_t ===")
    print(axi_domain_t(2))          # → OUTER_SHAREABLE
    print(axi_domain_t.SYSTEM)      # → 3

    # axi_atomic_t
    print("=== axi_atomic_t ===")
    print(axi_atomic_t(17))         # → STORE_LE_CLR
    print(axi_atomic_t.STORE_LE_CLR)  # → 17

    # axi_secsid_t
    print("=== axi_secsid_t ===")
    print(axi_secsid_t(1))          # → SECURE
    print(axi_secsid_t.REALM)       # → 2


