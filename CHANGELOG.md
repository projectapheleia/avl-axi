# Changelog

## [Unreleased]

### Fixed
 - [PR #51](https://github.com/projectapheleia/avl-axi/pull/51) Subordinate Write/Read Drivers: `drive_control` sampled the AW/AR request payload into its item *after* calling `quiesce_control()`, which since [PR #41](https://github.com/projectapheleia/avl-axi/pull/41) begins with `await NextTimeStep()` - so the capture landed a full timestep past the handshake edge. Against a manager driving back-to-back transfers, edge N's non-blocking updates are visible by then and the item recorded the *next* transfer's address and control, and the sample also raced the peer manager driver's own `quiesce_control()`, which resumes on that same `NextTimeStep`. The sample now happens immediately after the handshake edge, before quiescing, matching `_rmonitor`/`_wmonitor` (which already read at exactly that point) so driver and monitor items agree. Await counts are unchanged, so `back_to_back` timing and PR #41's ready-pulse hold are unaffected. Introduced by PR #41; the equivalent data/response sites were already correctly ordered.
 - [#49](https://github.com/projectapheleia/avl-axi/issues/49) Subordinate Write Driver: `drive_response`'s reset guard tested a misspelled signal name (`arestn` instead of `aresetn`), so `Interface.get()` found no such signal and returned its `None` default; `None == 0` is `False`, leaving the B channel with no reset guard at all - silently, with no exception or warning. Impact is limited because `Driver.run_phase` cancels and restarts the drive tasks on each `FallingEdge(aresetn)` and `drive_response` clears `responseQ` on entry, but two gaps remained: the initial reset window (where `aresetn` may be asserted at time 0 with no falling edge to trigger a restart) ran wholly unguarded, and any item reaching `responseQ` while reset was asserted would drive `BVALID` and its payload during reset. The `awakeup` half of the guard was unaffected. The line now matches its read-side counterpart in `_srdriver.py`. Present since the first commit.

## [v1.0.0] - 2026-08-08

First stable release. From this point on the public API follows semantic versioning.

### Changed

**BREAKING** - [PR #43](https://github.com/projectapheleia/avl-axi/pull/43) `SequenceItem.get_id()` is renamed to `get_bus_id()`, with a matching `set_bus_id()`. Any caller using `item.get_id()` to read the AXI protocol ID (`awid`/`arid`) must migrate to `item.get_bus_id()`.

 - Note that this change is silent, not a hard error: `get_id()` still resolves via `avl-core`'s `Transaction.get_id()` and returns `_id_` - the sequence's own item index - so affected code keeps running while reading the wrong number. Grep your testbench for `.get_id()` on AXI items before upgrading.
 - Rationale: `get_id()` read the AXI protocol ID but `set_id()` was never overridden to match, so it silently wrote to `avl-core`'s unrelated `Transaction._id_` bookkeeping instead - a getter/setter imbalance. Overriding `set_id()` directly (as originally proposed) is unsafe: `avl-core`'s `Sequence.start_item()` calls `item.set_id()` with the sequence's own item index on every item sent, which would clobber any caller-specified `awid`/`arid`. Renaming the pair matches the existing `get_addr()`/`set_addr()` convention and removes the collision with base sequencer bookkeeping.

### Added
 - [PR #47](https://github.com/projectapheleia/avl-axi/pull/47) Subordinate Write/Read Drivers: Factory-driven `response_overrides` hook to force a chosen response (optionally address-ranged, budget-limited via `match_count`) onto the B/R channel. Shared implementation lives in `Driver._apply_response_overrides_()`; each rule independently opts in to running before and/or after the exclusivity monitor via `override_before_execution`/`override_after_execution` (must be exactly `True`; `None`/`False` means it doesn't apply at that call site). See `examples/axi/axi5-response-override` and `doc/source/components/subordinate.rst`

### Fixed
 - [PR #41](https://github.com/projectapheleia/avl-axi/pull/41) Manager/Subordinate Write/Read Drivers: on a comb-generated ready/valid, a driver's `quiesce_control`/`quiesce_data`/`quiesce_response` retracted the just-completed handshake signal (e.g. `arvalid`) immediately on the same `RisingEdge` callback that detected it, with no ordering guarantee relative to other coroutines woken on that same edge (e.g. `_rmonitor`/`_wmonitor`'s `monitor_control`/`monitor_response`, which read the same signals right after their own `RisingEdge`). If the driver's write happened to run first, the monitor observed the signal already retracted and never recorded the beat, permanently blocking `monitor_response`'s `blocking_pop()` - reproducible on Verilator, masked on simulators whose internal scheduling happens to run the monitor first. PR #41 proposed wrapping every read in `ReadOnly()`/`NextTimeStep()`, but per cocotb's Verilator-specific scheduling (`RisingEdge` already resumes after the cycle settles), the reads were never the problem; only the retracting write needed to be deferred. Each driver's `quiesce_*` now does a single `await NextTimeStep()` before clearing signals, so no retraction can land before every coroutine scheduled on that edge has read - fixing PR #41's own acknowledged `wready` gap and the equivalent subordinate-driver sites for free, with no change to any read site.
 - [#45](https://github.com/projectapheleia/avl-axi/issues/45) Manager Write Driver: `awpending`/`wpending` flow-control checks lacked the "signal absent" default (and the W-beat check tested the wrong signal, `arpending`), forcing a spurious 1-cycle bubble before every AW assertion and W beat even with `control_rate_limit`/`data_rate_limit` at 1.0 and no `max_outstanding` (AR was unaffected - its equivalent check already had the correct default). Also adds an opt-in `back_to_back` option on `Driver` that overrides `control_rate_limit`/`data_rate_limit`/`max_outstanding` on a driver instance to force gapless issuance regardless of other Factory settings. See `examples/axi/axi5-back-to-back(-override)` and `doc/source/components/manager.rst`
 - [PR #44](https://github.com/projectapheleia/avl-axi/pull/44) Exclusives: EXOKAY incorrectly overwriting SLVERR/DECERR on read, and exclusivity granted despite an errored beat
 - [PR #42](https://github.com/projectapheleia/avl-axi/pull/42) Manager Write/Read Drivers: response_pending not cleared on mid-sim reset, causing hangs or IndexError

## [v0.7.1] - 2026-06-14

### Fixed
 - [#40](https://github.com/projectapheleia/avl-axi/issues/40) Exclusives: Incorrect rresp behaviour

## [v0.7.0] - 2026-06-07

### Fixed
 - [#35](https://github.com/projectapheleia/avl-axi/issues/35) Allow_Early_Data: Awake condition limited use
 - [#36](https://github.com/projectapheleia/avl-axi/issues/36) Item(): Post randomize() not applying constraints to Write Strobe Correctly
 - [#37](https://github.com/projectapheleia/avl-axi/issues/37) Types(): Issues with randomization and atomics not constrained for all values

## [v0.6.2] - 2026-05-17

### Fixed
 - [#30](https://github.com/projectapheleia/avl-axi/issues/30) ATOMIC COMPARE: R channel length should be halved AXI A6.2
 - [#31](https://github.com/projectapheleia/avl-axi/issues/31) Support narrow-transfer lane steering AXI A3.2.3 and AXI A3.4.1

## [v0.6.1] - 2026-04-09

### Fixed
 - [#25](https://github.com/projectapheleia/avl-axi/issues/25) Most examples fail in VCS due to failure to cast X to bool

## [v0.6.0] - 2026-03-27

### Fixed
 - [#24](https://github.com/projectapheleia/avl-axi/issues/24) Examples fail in VCS - Interface signal enumeration not working
 - Changed power of 2 to left shift for performance

## [v0.5.0] - 2026-03-05

### Added
 - [#21](https://github.com/projectapheleia/avl-axi/issues/21) Support AXI_Transport == "Credited"

## [v0.4.2] - 2026-01-27

### Fixed

 - [#17](https://github.com/projectapheleia/avl-axi/issues/17) get_burst_addresses doesn't handle unaligned accesses for incrementing bursts
 - [#19](https://github.com/projectapheleia/avl-axi/issues/19) Unaligned reads return unexpected data

## [v0.4.1] - 2026-01-18

### Added

 - (https://github.com/projectapheleia/avl-axi/pull/16) feat: write()/read() wait for response by default

## [v0.4.0] - 2026-01-06

### Fixed
 - [#14](https://github.com/projectapheleia/avl-axi/issues/14) Performance: Using 256 entry list has large overhead on object creation
    - Requires v0.4.1 of avl-core to support defaultdicts - v0.4.1(https://github.com/projectapheleia/avl/commit/1a6b63a35e1c4f0b963123136dadd5ed093bf395)

## [v0.3.0] - 2025-12-19

### Fixed
 - [#7] (https://github.com/projectapheleia/avl-axi/issues/7) Sequence: Sequence only waits on last item. Can complete early on out-of-order responses
 - [#8] (https://github.com/projectapheleia/avl-axi/issues/8) Atomics: Randomization of atomics can break single outstanding ID requirements
 - [#9] (https://github.com/projectapheleia/avl-axi/issues/9) SMemory : Endianness swap can overflow
 - [#11](https://github.com/projectapheleia/avl-axi/issues/11) item: resize() called before awatop is assigned removes all r_ signals. Slave driver doesn't populate causing protocol error
 - [#10](https://github.com/projectapheleia/avl-axi/issues/10) smemory: read/write data is not shifted on misaligned accesses #10
    - Requires newer version of avl-core that supports rotation in memory model - v0.4.0(https://github.com/projectapheleia/avl/commit/e524043490677997a35b20244c206ac809733b0a)

## [v0.2.2] - 2025-11-14

### Fixed
 - [#6] (https://github.com/projectapheleia/avl-axi/issues/6) [item] c_awatop_size constraint issue

## [v0.2.1] - 2025-10-25

### Fixed
 - [#3] (https://github.com/projectapheleia/avl-axi/issues/3) AVL_AXI coverage init issue
 - [#4] (https://github.com/projectapheleia/avl-axi/issues/4) AXI5 ATOPs should always respond on the B channel
 - [#5] (https://github.com/projectapheleia/avl-axi/issues/5) Monitors blocked awiting on reset

## [v0.2.0] - 2025-10-12

### Fixed
 - [#2](https://github.com/projectapheleia/avl-axi/issues/2) Unique IDs and Tag ID create new dict instead of clearing class dict
 - [#1](https://github.com/projectapheleia/avl-axi/issues/1) Modelsim does not support detecting parameters through VPI

## [v0.1.0] - 2025-09-28

### Added
- First version
