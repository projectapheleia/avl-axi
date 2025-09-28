# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Subordinate Memory


import avl

from ._item import ReadItem, WriteItem
from ._types import axi_atomic_t, axi_resp_t
from ._utils import get_burst_addresses


class SubordinateMemory(avl.Memory):

    def __init__(self, width : int = 32) -> None:
        """
        Initialize the Memory for the AXI Subordinate Driver

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(width=width)

        # Misses return DECERR not assert
        self.miss = lambda address : None

        # Endianness Swap
        self._endianness_swap_ = False

    def read(self, address: int, num_bytes : int = None) -> int:
        """
        Read a value from the memory at the specified address.

        Calls miss() if the address is not found in memory.

        :param address: Address to read from.
        :type address: int
        :return: Value at the specified address.
        :rtype: int
        """
        if self._endianness_swap_:
            return self._convert_endianness_(super().read(address, num_bytes=num_bytes), num_bytes=num_bytes)
        else:
            return super().read(address, num_bytes=num_bytes)

    def write(self, address: int, value: int, num_bytes : int = None, strobe : int = None) -> None:
        """
        Write a value to the memory at the specified address.

        Calls miss() if the address is not found in memory.

        :param address: Address to write to.
        :type address: int
        :param value: Value to write.
        :type value: int
        :param num_bytes: Number of bytes to write (default is width // 8).
        :type num_bytes: int, optional
        :param strobe: Strobe signal
        :type strobe: int, optional
        """
        if self._endianness_swap_:
            value = self._convert_endianness_(value, num_bytes=num_bytes)

        # Apply mask
        value &= (1 << 8*num_bytes)-1

        # Write to memory
        super().write(address, value, num_bytes=num_bytes, strobe=strobe)

    def _convert_endianness_(self, value: int, num_bytes: int) -> int:
        """
        Convert the endianness of an integer represented in nbytes.

        :param value: Unsigned integer
        :param width: Bit width (e.g., 8, 16, 32)
        :return: Unsigned integer
        """
        b = value.to_bytes(num_bytes, byteorder="little", signed=False)
        return int.from_bytes(b[::-1], byteorder="little", signed=False)

    def _unsigned_to_signed_(self, value: int, width: int) -> int:
        """
        Convert an unsigned integer to a signed integer with given bit width.

        :param value: Unsigned integer
        :param width: Bit width (e.g., 8, 16, 32)
        :return: Signed integer
        """
        mask = 1 << (width - 1)
        if value & mask:
            return value - (1 << width)
        return value

    def _signed_to_unsigned_(self, value: int, width: int) -> int:
        """
        Convert an signed integer to a unsigned integer with given bit width.

        :param value: Unsigned integer
        :param width: Bit width (e.g., 8, 16, 32)
        :return: Signed integer
        """
        mask = (1 << width) - 1
        return value & mask

    def swap(self, address: int, value: int, num_bytes : int = None) -> int:
        """
        Swap values

        :param address: Address
        :type address: int
        :param value: Value to apply
        :type value: int
        :return: Original value at the specified address.
        :rtype: int
        """

        self.write(address, value, num_bytes = num_bytes)

    def compare(self, address: int, value: int, compare: int, num_bytes : int = None) -> int:
        """
        Compare Values

        :param address: Address
        :type address: int
        :param value: Value to apply
        :type value: int
        :return: Original value at the specified address.
        :rtype: int
        """

        old_value = self.read(address, num_bytes=num_bytes//2)
        if old_value == compare:
            self.write(address, value, num_bytes=num_bytes//2)

    def add(self, address: int, value: int, num_bytes : int = None) -> int:
        """
        Add Values

        :param address: Address
        :type address: int
        :param value: Value to apply
        :type value: int
        :return: Original value at the specified address.
        :rtype: int
        """

        old_value = self.read(address, num_bytes=num_bytes)
        self.write(address, value+old_value, num_bytes = num_bytes)

    def clr(self, address: int, value: int, num_bytes : int = None) -> int:
        """
        Bitwise Clear Value

        :param address: Address
        :type address: int
        :param value: Value to apply
        :type value: int
        :return: Original value at the specified address.
        :rtype: int
        """

        old_value = self.read(address, num_bytes=num_bytes)
        self.write(address, ~value&old_value, num_bytes = num_bytes)

    def xor(self, address: int, value: int, num_bytes : int = None) -> int:
        """
        Bitwise Exclusive Or Value

        :param address: Address
        :type address: int
        :param value: Value to apply
        :type value: int
        :return: Original value at the specified address.
        :rtype: int
        """

        old_value = self.read(address, num_bytes=num_bytes)
        self.write(address, value^old_value, num_bytes = num_bytes)

    def set(self, address: int, value: int, num_bytes : int = None) -> int:
        """
        Bitwise OR Value

        :param address: Address
        :type address: int
        :param value: Value to apply
        :type value: int
        :return: Original value at the specified address.
        :rtype: int
        """

        old_value = self.read(address, num_bytes=num_bytes)
        self.write(address, value|old_value, num_bytes = num_bytes)

    def smax(self, address: int, value: int, num_bytes : int = None) -> int:
        """
        Signed Max

        :param address: Address
        :type address: int
        :param value: Value to apply
        :type value: int
        :return: Original value at the specified address.
        :rtype: int
        """

        old_value = self._unsigned_to_signed_(self.read(address, num_bytes=num_bytes), 8*num_bytes)
        value     = self._unsigned_to_signed_(value, 8*num_bytes)
        self.write(address, self._signed_to_unsigned_(max(value,old_value),8*num_bytes), num_bytes = num_bytes)

    def smin(self, address: int, value: int, num_bytes : int = None) -> int:
        """
        Unsigned Min

        :param address: Address
        :type address: int
        :param value: Value to apply
        :type value: int
        :return: Original value at the specified address.
        :rtype: int
        """

        old_value = self._unsigned_to_signed_(self.read(address, num_bytes=num_bytes), 8*num_bytes)
        value     = self._unsigned_to_signed_(value, 8*num_bytes)
        self.write(address, self._signed_to_unsigned_(min(value,old_value), 8*num_bytes), num_bytes = num_bytes)

    def umax(self, address: int, value: int, num_bytes : int = None) -> int:
        """
        Unsigned Max

        :param address: Address
        :type address: int
        :param value: Value to apply
        :type value: int
        :return: Original value at the specified address.
        :rtype: int
        """

        old_value = self.read(address, num_bytes=num_bytes)
        self.write(address, max(value,old_value), num_bytes = num_bytes)

    def umin(self, address: int, value: int, num_bytes : int = None) -> int:
        """
        Unsigned Min

        :param address: Address
        :type address: int
        :param value: Value to apply
        :type value: int
        :return: Original value at the specified address.
        :rtype: int
        """

        old_value = self.read(address, num_bytes=num_bytes)
        self.write(address, min(value,old_value), num_bytes = num_bytes)

    def process_write(self, item : WriteItem) -> None:
        """
        Process a sequence item update for memory update

        :param item: The sequence item to process
        :type item: SequenceItem
        """

        if not isinstance(item, WriteItem):
            raise TypeError("Item must be a WriteItem")

        # Update memory contents
        for i,a in enumerate(get_burst_addresses(item.get("awaddr"),
                                                 item.get("awlen", default=0),
                                                 item.get("awsize", default=0),
                                                 item.get("awburst", default=1)
                                                )):

            if self._check_address_(a):
                num_bytes = 2**(item.get("awsize", default=0))
                wdata = item.get("wdata", idx=i, default=0)

                if hasattr(item, "awatop"):
                    # Return value is always original read
                    item.set("rdata", self.read(a, num_bytes=num_bytes), idx=i)

                    # Handle endianness
                    if item.awatop.endianness() != self.endianness:
                        self._endianness_swap_ = True

                    # Perform atomic update
                    if item.awatop == axi_atomic_t.NON_ATOMIC:
                        self.write(a, wdata, num_bytes=num_bytes, strobe=item.get("wstrb", idx=i, default=None))

                    elif item.awatop in [axi_atomic_t.STORE_LE_ADD, axi_atomic_t.LOAD_LE_ADD, axi_atomic_t.STORE_BE_ADD, axi_atomic_t.LOAD_BE_ADD]:
                        self.add(a, wdata, num_bytes=num_bytes)

                    elif item.awatop in [axi_atomic_t.STORE_LE_CLR, axi_atomic_t.LOAD_LE_CLR, axi_atomic_t.STORE_BE_CLR, axi_atomic_t.LOAD_BE_CLR]:
                        self.clr(a, wdata, num_bytes=num_bytes)

                    elif item.awatop in [axi_atomic_t.STORE_LE_EOR, axi_atomic_t.LOAD_LE_EOR, axi_atomic_t.STORE_BE_EOR, axi_atomic_t.LOAD_BE_EOR]:
                        self.xor(a, wdata, num_bytes=num_bytes)

                    elif item.awatop in [axi_atomic_t.STORE_LE_SET, axi_atomic_t.LOAD_LE_SET, axi_atomic_t.STORE_BE_SET, axi_atomic_t.LOAD_BE_SET]:
                        self.set(a, wdata, num_bytes=num_bytes)

                    elif item.awatop in [axi_atomic_t.STORE_LE_SMAX, axi_atomic_t.LOAD_LE_SMAX, axi_atomic_t.STORE_BE_SMAX, axi_atomic_t.LOAD_BE_SMAX]:
                        self.smax(a, wdata, num_bytes=num_bytes)

                    elif item.awatop in [axi_atomic_t.STORE_LE_SMIN, axi_atomic_t.LOAD_LE_SMIN, axi_atomic_t.STORE_BE_SMIN, axi_atomic_t.LOAD_BE_SMIN]:
                        self.smin(a, wdata, num_bytes=num_bytes)

                    elif item.awatop in [axi_atomic_t.STORE_LE_UMAX, axi_atomic_t.LOAD_LE_UMAX, axi_atomic_t.STORE_BE_UMAX, axi_atomic_t.LOAD_BE_UMAX]:
                        self.umax(a, wdata, num_bytes=num_bytes)

                    elif item.awatop in [axi_atomic_t.STORE_LE_UMIN, axi_atomic_t.LOAD_LE_UMIN, axi_atomic_t.STORE_BE_UMIN, axi_atomic_t.LOAD_BE_UMIN]:
                        self.umin(a, wdata, num_bytes=num_bytes)

                    elif item.awatop in [axi_atomic_t.SWAP]:
                        self.swap(a, wdata, num_bytes=num_bytes)

                    elif item.awatop in [axi_atomic_t.COMPARE]:
                        comp  = wdata
                        comp &= (1 << 8*num_bytes//2)-1
                        swap  = wdata >> (8*num_bytes//2)
                        swap &= (1 << 8*num_bytes//2)-1
                        self.compare(a, swap, comp, num_bytes=num_bytes)
                    else:
                        raise ValueError()

                    # No Endiannes Swap by default
                    self._endianness_swap_ = False

                else:
                    # Standard Write
                    self.write(a, item.get("wdata", idx=i, default=0), num_bytes=num_bytes, strobe=item.get("wstrb", idx=i, default=None))
            else:
                item.set("bresp", axi_resp_t.DECERR)

    def process_read(self, item : ReadItem) -> None:
        """
        Process a sequence item update for memory

        :param item: The sequence item to process
        :type item: SequenceItem
        """

        decerr = False
        if not isinstance(item, ReadItem):
            raise TypeError("Item must be a ReadItem")

        for i,a in enumerate(get_burst_addresses(item.get("araddr"),
                                                 item.get("arlen", default=0),
                                                 item.get("arsize", default=0),
                                                 item.get("arburst", default=1)
                                                )):

                if self._check_address_(a):
                    num_bytes = 2**(item.get("arsize", default=0))
                    item.set("rdata", self.read(a, num_bytes=num_bytes), idx=i)
                    item.set("rresp", axi_resp_t.OKAY, idx=i)
                else:
                    item.set("rdata", axi_resp_t.OKAY, idx=i)
                    item.set("rresp", axi_resp_t.DECERR, idx=i)
                    decerr = True

        # Consistent DECERR
        if item._Consistent_DECERR_ and decerr:
            for i in range(len(item.rresp)):
                item.set("rresp", axi_resp_t.DECERR, idx=i)

__all__ = ["SubordinateMemory"]
