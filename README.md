# AVL-AXI - Apheleia Verification Library AMBA AXI Verification Component

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)


AVL-AXI has been developed by experienced, industry professional verification engineers to provide a simple, \
extensible verification component for the [AMBA AXI Bus](https://developer.arm.com/documentation/ihi0022/k/?lang=en) \
developed in [Python](https://www.python.org/) and the [AVL](https://avl-core.readthedocs.io/en/latest/index.html) library.

AVL is built on the [CocoTB](https://docs.cocotb.org/en/stable/) framework, but aims to combine the best elements of \
[UVM](https://accellera.org/community/uvm) in a more engineer friendly and efficient way.

## CocoTB 2.0

AVL-AXI supports CocoTB2.0 https://docs.cocotb.org/en/development/upgrade-2.0.html.

To upgrade follow the instructions given on the link above.

## Protocol Features

For full details see the docs. A few of the cache extensions are not supported in the initial release, but the bus features \
including most sidebands are supported.

If you are interested contact avl@projectapheleia.net to discuss.

Of the advanced features full support of exclusives and atomic operation are provided in the Subordinate memory model.

| Parameter Name | Supported |
|---|---|
| Atomic_Transactions | YES |
| BURST_Present | YES |
| Busy_Support | SIDEBAND |
| CACHE_Present | SIDEBAND |
| Cache_Line_Size | SIDEBAND |
| Cache_Stash_Transactions | SIDEBAND |
| Check_Type | NO |
| CMO_On_Read | SIDEBAND |
| CMO_On_Write | SIDEBAND |
| Coherency_Connection_Signals | NO |
| Consistent_DECERR | YES |
| DeAllocation_Transactions | SIDEBAND |
| Device_Normal_Independence | NO |
| DVM_Message_Support | NO |
| DVM_v8 | NO |
| DVM_v8_1 | NO |
| DVM_v8_4 | NO |
| DVM_v9_2 | NO |
| Exclusive_Accesses | YES |
| Fixed_Burst_Disable | YES |
| InvalidateHint_Transaction | SIDEBAND |
| LEN_Present | YES |
| Loopback_Signals | YES |
| Max_Transaction_Bytes | YES |
| MEC_Support | SIDEBAND |
| MMUFLOW_Present | SIDEBAND |
| MPAM_Support | SIDEBAND |
| MTE_Support | NO |
| Multi_Copy_Atomicity | SIDEBAND |
| NSAccess_Identifiers | SIDEBAND |
| Ordered_Write_Observation | YES |
| PBHA_Support | SIDEBAND |
| Persist_CMO | SIDEBAND |
| Poison | SIDEBAND |
| Prefetch_Transaction | SIDEBAND |
| PROT_Present | SIDEBAND |
| QoS_Accept | YES |
| QOS_Present | SIDEBAND |
| Read_Data_Chunking | NO |
| Read_Interleaving_Disabled | YES |
| REGION_Present | SIDEBAND |
| Regular_Transactions_Only | YES |
| RLAST_Present | YES |
| RME_Support | SIDEBAND |
| Shareable_Cache_Support | SIDEBAND |
| Shareable_Transactions | SIDEBAND |
| SIZE_Present | YES |
| STASHLPID_Present | SIDEBAND |
| STASHNID_Present | SIDEBAND |
| Trace_Signals | SIDEBAND |
| Unique_ID_Support | YES |
| UnstashTranslation_Transaction | SIDEBAND |
| Untranslated_Transactions | SIDEBAND |
| Wakeup_Signals | YES |
| WLAST_Present | YES |
| Write_Plus_CMO | SIDEBAND |
| WriteDeferrable_Transaction | SIDEBAND |
| WriteNoSnoopFull_Transaction | SIDEBAND |
| WriteZero_Transaction | SIDEBAND |
| WSTRB_Present | SIDEBAND |

## Component Features

- Majority of protocol features supported
- Simple RTL interface to interact with HDL and define parameter and configuration options
- Manager sequence, sequencer and driver with easy to control rate limiter and wakeup control
    - Support for pipelined sequence based on control, data or response acknowledge
- Subordinate driver with vanilla, random and memory response patterns (including exclusive and atomic operation support) and rate limiter
- Maximum outstanding transaction and maximum outstanding bytes suppport
- Parallel and independent read and write channels with support for early write data
- Monitor with configurable callbacks for control, data and response phases
- Bandwidth monitor generating bus activity plots over user defined windows during simulation
- Functional coverage including performance measurements
- Searchable trace file generation

---

## 📦 Installation

### Using `pip`
```sh
# Standard build
pip install avl-axi

# Development build
pip install avl-axi[dev]
```

### Install from Source
```sh
git clone https://github.com/projectapheleia/avl-axi.git
cd avl

# Standard build
pip install .

# Development build
pip install .[dev]
```

Alternatively if you want to create a [virtual environment](https://docs.python.org/3/library/venv.html) rather than install globally a script is provided. This will install, with edit privileges to local virtual environment.

This script assumes you have [Graphviz](https://graphviz.org/download/) and appropriate simulator installed, so all examples and documentation will build out of the box.


```sh
git clone https://github.com/projectapheleia/avl-axi.git
cd avl-axi
source avl-axi.sh
```

## 📖 Documentation

In order to build the documentation you must have installed the development build.

### Build from Source
```sh
cd doc
make html
<browser> build/html/index.html
```
## 🏃 Examples

In order to run all the examples you must have installed the development build.

To run all examples:

```sh
cd examples

# To run
make -j 8 sim

# To clean
make -j 8 clean
```

To run an individual example:

```sh
cd examples/THE EXAMPLE YOU WANT

# To run
make sim

# To clean
make clean
```

The examples use the [CocoTB Makefile](https://docs.cocotb.org/en/stable/building.html) and default to [Verilator](https://www.veripool.org/verilator/) with all waveforms generated. This can be modified using the standard CocoTB build system.

---


## 🧹 Code Style & Linting

This project uses [**Ruff**](https://docs.astral.sh/ruff/) for linting and formatting.

Check code for issues:

```sh
ruff check .
```

Automatically fix common issues:

```sh
ruff check . --fix
```



## 📧 Contact

- Email: avl@projectapheleia.net
- GitHub: [projectapheleia](https://github.com/projectapheleia)
