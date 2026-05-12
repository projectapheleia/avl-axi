# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Signals lists

def get_burst_addresses(base, length, size, burst):
    """
    Calculate addresses for an AXI transaction.

    Args:
        base (int): Starting address (ARADDR/AWADDR)
        length (int): ARLEN/AWLEN - number of transfers minus 1 (0-255)
        size (int): ARSIZE/AWSIZE - size of each transfer as power of 2
                   0=1 byte, 1=2 bytes, 2=4 bytes, 3=8 bytes, etc.
        burst (int): ARBURST/AWBURST - burst type
                    0=FIXED, 1=INCR, 2=WRAP

    Returns:
        list: List of addresses for all transfers in the transaction
    """
    addresses = []
    num_transfers = length + 1  # ARLEN/AWLEN is number of transfers - 1
    transfer_size = 1<<size   # Convert size encoding to actual bytes

    if burst == 0:  # FIXED burst
        # All transfers use the same address
        addresses = [base] * num_transfers

    elif burst == 1:  # INCR (incrementing) burst
        # Each transfer increments by transfer_size
        for i in range(num_transfers):
            burst_address = base + (i * transfer_size)
            # For unaligned bursts, align the address starting from the 2nd beat.
            if (i!=0):
                burst_address = burst_address & ~(transfer_size-1)
            addresses.append(burst_address)

    elif burst == 2:  # WRAP burst
        # Calculate wrap boundary
        wrap_boundary = transfer_size * num_transfers

        # Align the base address to the wrap boundary
        aligned_base = (base // wrap_boundary) * wrap_boundary

        for i in range(num_transfers):
            addr = base + (i * transfer_size)
            # Wrap around within the boundary
            wrapped_addr = aligned_base + ((addr - aligned_base) % wrap_boundary)
            addresses.append(wrapped_addr)

    else:
        raise ValueError(f"Invalid burst type: {burst}. Must be 0 (FIXED), 1 (INCR), or 2 (WRAP)")

    return addresses

def get_beat_byte_offset(base, beat, length, size, burst, strb_width):
    """
    Byte-lane offset of a single beat within the data channel for an AXI burst.

    Implements the narrow-transfer placement defined by AMBA AXI A3.2.3 and the
    address structure in A3.4.1: each beat's `1 << size` payload bytes live on
    byte lanes `[offset .. offset + (1 << size) - 1]` of the data bus, where
    `offset = beat_address mod data_bus_bytes`. For INCR the first beat may be
    unaligned; subsequent beats are aligned to `1 << size`. For WRAP the address
    wraps at `(1 << size) * (length + 1)`. For FIXED every beat reuses the
    Start_Address lanes.

    Args:
        base (int):       Start_Address (AWADDR/ARADDR).
        beat (int):       0-indexed beat number within the burst.
        length (int):     AWLEN/ARLEN (number of beats - 1).
        size (int):       AWSIZE/ARSIZE (log2 of bytes per beat).
        burst (int):      0=FIXED, 1=INCR, 2=WRAP.
        strb_width (int): Data-bus width in bytes.

    Returns:
        int: Byte-lane offset for `beat` within the data bus.
    """
    return get_burst_addresses(base, length, size, burst)[beat] & (strb_width - 1)


def get_burst_byte_count(strb, length, size, burst):
    """
    Calculate total bytes transferred for an AXI burst.

    Parameters:
        strb (int): Byte strobe width (number of valid bytes in a beat)
        length (int): Burst length (ARLEN/AWLEN) = number of beats - 1
        size (int): log2(bytes per beat)
        burst (str): "FIXED", "INCR", or "WRAP"

    Returns:
        int: Total number of bytes transferred
    """
    # Bytes per beat from size
    bytes_per_beat = 1 << size

    # Mask with strb if given
    if strb is not None and strb > 0:
        bytes_per_beat = min(bytes_per_beat, strb)

    # Number of beats
    num_beats = length + 1

    # Total bytes
    total_bytes = num_beats * bytes_per_beat

    return total_bytes

__all__ = ["get_burst_addresses", "get_beat_byte_offset", "get_burst_byte_count"]
