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
    transfer_size = 2 ** size   # Convert size encoding to actual bytes

    if burst == 0:  # FIXED burst
        # All transfers use the same address
        addresses = [base] * num_transfers

    elif burst == 1:  # INCR (incrementing) burst
        # Each transfer increments by transfer_size
        for i in range(num_transfers):
            addresses.append(base + (i * transfer_size))

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

__all__ = ["get_burst_addresses", "get_burst_byte_count"]
