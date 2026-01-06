# Changelog

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
