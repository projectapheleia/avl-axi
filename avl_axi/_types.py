# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Types

from collections.abc import Callable
from typing import Any

import avl


class axi_burst_t(avl.Logic):

    FIXED = 0
    INCR = 1
    WRAP = 2
    RESERVED = 3

    def __init__(self, value : Any, width : int = 1, auto_random : bool=False, fmt: Callable[..., int] = None) -> None:
        """
        Enumeration for the AXI Burst type
            - 0 : FIXED
            - 1 : INCR
            - 2 : WRAP
            - 3 : RESERVED

        :param value: The value to assign to the AXI Burst type.
        :param auto_random: Whether to use automatic randomization.
        :param fmt: The format string for the AXI Burst type.
        :return: None
        """
        super().__init__(value, width=width, auto_random=auto_random, fmt=fmt)

        # Avoid randomizing to reserve value
        self.add_constraint("c_reserved", lambda x: x != axi_burst_t.RESERVED)

        if self._fmt_ is None:
            self._fmt_ = self.fmt

    def fmt(self, value : int) -> str:
        """
        Custom format

        :param value: The value to format.
        :return: The formatted string.
        """
        return self.values()[value]

    def values(self) -> dict[str, int]:
        """
        Return a dictionary of types

        :return dict
        :rtype: dict[str, int]
        """
        d = {
                axi_burst_t.FIXED    : "FIXED",
                axi_burst_t.INCR     : "INCR",
                axi_burst_t.WRAP     : "WRAP",
                axi_burst_t.RESERVED : "RESERVED",
            }

        for i in range(axi_burst_t.FIXED, axi_burst_t.RESERVED, 1):
            if i > (2**self.width)-1:
                del d[i]
        return d

    def _cast_(self, other : Any) -> bool:
        """
        Casts the given value to the AXI Burst type.

        :param other: The value to cast.
        :return: True if the cast was successful, False otherwise.
        """
        if int(other) == axi_burst_t.RESERVED:
            raise ValueError("Cannot assign RESERVED value to axi_burst_t")

        return super()._cast_(other)

class axi_resp_t(avl.Logic):

    OKAY = 0
    EXOKAY = 1
    SLVERR = 2
    DECERR = 3
    DEFER = 4
    TRANSFAULT = 5
    RESERVED = 6
    UNSUPPORTED = 7

    def __init__(self, value : Any, width : int = 1, auto_random : bool=False, fmt: Callable[..., int] = None) -> None:
        """
        Enumeration for the AXI Response type
            - 0 : OKAY
            - 1 : EXOKAY
            - 2 : SLVERR
            - 3 : DECERR
            - 4 : DEFER
            - 5 : TRANSFAULT
            - 6 : RESERVED
            - 7 : UNSUPPORTED

        :param value: The value to assign to the AXI Burst type.
        :param auto_random: Whether to use automatic randomization.
        :param fmt: The format string for the AXI Burst type.
        :return: None
        """

        super().__init__(value, width=width, auto_random=auto_random, fmt=fmt)

        # Avoid randomizing to reserve value
        self.add_constraint("c_reserved", lambda x: x != axi_resp_t.RESERVED)

        if self._fmt_ is None:
            self._fmt_ = self.fmt

    def fmt(self, value : int) -> str:
        """
        Custom format

        :param value: The value to format.
        :return: The formatted string.
        """
        return self.values()[value]

    def values(self) -> dict[str, int]:
        """
        Return a dictionary of types

        :return dict
        :rtype: dict[str, int]
        """
        d = {
                axi_resp_t.OKAY        : "OKAY",
                axi_resp_t.EXOKAY      : "EXOKAY",
                axi_resp_t.SLVERR      : "SLVERR",
                axi_resp_t.DECERR      : "DECERR",
                axi_resp_t.DEFER       : "DEFER",
                axi_resp_t.TRANSFAULT  : "TRANSFAULT",
                axi_resp_t.RESERVED    : "RESERVED",
                axi_resp_t.UNSUPPORTED : "UNSUPPORTED",
            }

        for i in range(axi_resp_t.OKAY, axi_resp_t.UNSUPPORTED, 1):
            if i > (2**self.width)-1:
                del d[i]
        return d

    def _cast_(self, other : Any) -> bool:
        """
        Casts the given value to the AXI Burst type.

        :param other: The value to cast.
        :return: True if the cast was successful, False otherwise.
        """
        if int(other) == axi_resp_t.RESERVED:
            raise ValueError("Cannot assign RESERVED value to axi_resp_t")

        return super()._cast_(other)

class axi_domain_t(avl.Logic):

    NON_SHAREABLE = 0
    INNER_SHAREABLE = 1
    OUTER_SHAREABLE = 2
    SYSTEM = 3

    def __init__(self, value : Any, width : int = 1, auto_random : bool=False, fmt: Callable[..., int] = None) -> None:
        """
        Enumeration for the AXI domain type
            - 0 : NON_SHAREABLE
            - 1 : SHAREABLE (INNER)
            - 2 : SHAREABLE (OUTER)
            - 3 : SYSTEM

        :param value: The value to assign to the AXI domain type.
        :param auto_random: Whether to use automatic randomization.
        :param fmt: The format string for the AXI domain type.
        :return: None
        """
        super().__init__(value, width=width, auto_random=auto_random, fmt=fmt)

        if self._fmt_ is None:
            self._fmt_ = self.fmt

    def fmt(self, value : int) -> str:
        """
        Custom format

        :param value: The value to format.
        :return: The formatted string.
        """
        return self.values()[value]

    def values(self) -> dict[str, int]:
        """
        Return a dictionary of types

        :return dict
        :rtype: dict[str, int]
        """
        d = {
                axi_domain_t.NON_SHAREABLE   : "NON_SHAREABLE",
                axi_domain_t.INNER_SHAREABLE : "INNER_SHAREABLE",
                axi_domain_t.OUTER_SHAREABLE : "OUTER_SHAREABLE",
                axi_domain_t.SYSTEM          : "SYSTEM",
            }

        for i in range(axi_domain_t.NON_SHAREABLE, axi_domain_t.SYSTEM, 1):
            if i > (2**self.width)-1:
                del d[i]

        return d



class axi_atomic_t(avl.Logic):

    NON_ATOMIC    = 0b000000
    STORE_LE_ADD  = 0b010000
    STORE_LE_CLR  = 0b010001
    STORE_LE_EOR  = 0b010010
    STORE_LE_SET  = 0b010011
    STORE_LE_SMAX = 0b010100
    STORE_LE_SMIN = 0b010101
    STORE_LE_UMAX = 0b010110
    STORE_LE_UMIN = 0b010111
    LOAD_LE_ADD   = 0b100000
    LOAD_LE_CLR   = 0b100001
    LOAD_LE_EOR   = 0b100010
    LOAD_LE_SET   = 0b100011
    LOAD_LE_SMAX  = 0b100100
    LOAD_LE_SMIN  = 0b100101
    LOAD_LE_UMAX  = 0b100110
    LOAD_LE_UMIN  = 0b100111
    SWAP          = 0b110000
    COMPARE       = 0b110001
    STORE_BE_ADD  = 0b011000
    STORE_BE_CLR  = 0b011001
    STORE_BE_EOR  = 0b011010
    STORE_BE_SET  = 0b011011
    STORE_BE_SMAX = 0b011100
    STORE_BE_SMIN = 0b011101
    STORE_BE_UMAX = 0b011110
    STORE_BE_UMIN = 0b011111
    LOAD_BE_ADD   = 0b101000
    LOAD_BE_CLR   = 0b101001
    LOAD_BE_EOR   = 0b101010
    LOAD_BE_SET   = 0b101011
    LOAD_BE_SMAX  = 0b101100
    LOAD_BE_SMIN  = 0b101101
    LOAD_BE_UMAX  = 0b101110
    LOAD_BE_UMIN  = 0b101111

    def __init__(self, value : Any, width : int = 1, auto_random : bool=False, fmt: Callable[..., int] = None) -> None:
        """
        Enumeration for the AXI Atomic type

        :param value: The value to assign to the AXI Burst type.
        :param auto_random: Whether to use automatic randomization.
        :param fmt: The format string for the AXI Burst type.
        :return: None
        """

        super().__init__(value, width=width, auto_random=auto_random, fmt=fmt)

        if self._fmt_ is None:
            self._fmt_ = self.fmt

    def fmt(self, value : int) -> str:
        """
        Custom format

        :param value: The value to format.
        :return: The formatted string.
        """
        return self.values()[value]

    def values(self) -> dict[str, int]:
        """
        Return a dictionary of types

        :return dict
        :rtype: dict[str, int]
        """
        d = {
                axi_atomic_t.NON_ATOMIC    : "NON_ATOMIC",
                axi_atomic_t.STORE_LE_ADD  : "STORE_LE_ADD",
                axi_atomic_t.STORE_LE_CLR  : "STORE_LE_CLR",
                axi_atomic_t.STORE_LE_EOR  : "STORE_LE_EOR",
                axi_atomic_t.STORE_LE_SET  : "STORE_LE_SET",
                axi_atomic_t.STORE_LE_SMAX : "STORE_LE_SMAX",
                axi_atomic_t.STORE_LE_SMIN : "STORE_LE_SMIN",
                axi_atomic_t.STORE_LE_UMAX : "STORE_LE_UMAX",
                axi_atomic_t.STORE_LE_UMIN : "STORE_LE_UMIN",
                axi_atomic_t.LOAD_LE_ADD   : "LOAD_LE_ADD",
                axi_atomic_t.LOAD_LE_CLR   : "LOAD_LE_CLR",
                axi_atomic_t.LOAD_LE_EOR   : "LOAD_LE_EOR",
                axi_atomic_t.LOAD_LE_SET   : "LOAD_LE_SET",
                axi_atomic_t.LOAD_LE_SMAX  : "LOAD_LE_SMAX",
                axi_atomic_t.LOAD_LE_SMIN  : "LOAD_LE_SMIN",
                axi_atomic_t.LOAD_LE_UMAX  : "LOAD_LE_UMAX",
                axi_atomic_t.LOAD_LE_UMIN  : "LOAD_LE_UMIN",
                axi_atomic_t.SWAP          : "SWAP",
                axi_atomic_t.COMPARE       : "COMPARE",
                axi_atomic_t.STORE_BE_ADD  : "STORE_BE_ADD",
                axi_atomic_t.STORE_BE_CLR  : "STORE_BE_CLR",
                axi_atomic_t.STORE_BE_EOR  : "STORE_BE_EOR",
                axi_atomic_t.STORE_BE_SET  : "STORE_BE_SET",
                axi_atomic_t.STORE_BE_SMAX : "STORE_BE_SMAX",
                axi_atomic_t.STORE_BE_SMIN : "STORE_BE_SMIN",
                axi_atomic_t.STORE_BE_UMAX : "STORE_BE_UMAX",
                axi_atomic_t.STORE_BE_UMIN : "STORE_BE_UMIN",
                axi_atomic_t.LOAD_BE_ADD   : "LOAD_BE_ADD",
                axi_atomic_t.LOAD_BE_CLR   : "LOAD_BE_CLR",
                axi_atomic_t.LOAD_BE_EOR   : "LOAD_BE_EOR",
                axi_atomic_t.LOAD_BE_SET   : "LOAD_BE_SET",
                axi_atomic_t.LOAD_BE_SMAX  : "LOAD_BE_SMAX",
                axi_atomic_t.LOAD_BE_SMIN  : "LOAD_BE_SMIN",
                axi_atomic_t.LOAD_BE_UMAX  : "LOAD_BE_UMAX",
                axi_atomic_t.LOAD_BE_UMIN  : "LOAD_BE_UMIN",
            }

        for i in range(axi_atomic_t.NON_ATOMIC, axi_atomic_t.LOAD_BE_UMIN, 1):
            if i > (2**self.width)-1:
                del d[i]

        return d

    def has_bresp(self) -> bool:
        """
        Returns True if the operation generates a BRESP response, False otherwise.

        Currently all atomic operations return bresp - however implementing explicitly
        for symmetry and future proofing

        :return: bool
        :rtype: bool
        """
        return True

    def has_rresp(self) -> bool:
        """
        Returns True if the operation generates a RRESP response, False otherwise.

        :return: bool
        :rtype: bool
        """
        if self.value & 0b100000 != 0:
            return True

        return False

    def endianness(self) -> str:
        """
        Returns the endianness of the operation.

        :return: "little" or "big"
        :rtype: str
        """
        if self.value & 0b001000 == 0:
            return "little"
        else:
            return "big"



class axi_secsid_t(avl.Logic):

    NON_SECURE = 0
    SECURE = 1
    REALM = 2
    RESERVED = 3

    def __init__(self, value : Any, width : int = 1, auto_random : bool=False, fmt: Callable[..., int] = None) -> None:
        """
        Enumeration for the AXI secure stream identifier type
            - 0 : NON_SECURE
            - 1 : SECURE
            - 2 : REALM
            - 3 : RESERVED

        :param value: The value to assign to the AXI domain type.
        :param auto_random: Whether to use automatic randomization.
        :param fmt: The format string for the AXI domain type.
        :return: None
        """
        super().__init__(value, width=width, auto_random=auto_random, fmt=fmt)

        # Avoid randomizing to reserve value
        self.add_constraint("c_reserved", lambda x: x != axi_secsid_t.RESERVED)

        if self._fmt_ is None:
            self._fmt_ = self.fmt

    def fmt(self, value : int) -> str:
        """
        Custom format

        :param value: The value to format.
        :return: The formatted string.
        """
        return self.values()[value]

    def values(self) -> dict[str, int]:
        """
        Return a dictionary of types

        :return dict
        :rtype: dict[str, int]
        """
        d = {
                axi_secsid_t.NON_SECURE   : "NON_SECURE",
                axi_secsid_t.SECURE       : "SECURE",
                axi_secsid_t.REALM        : "REALM",
                axi_secsid_t.RESERVED     : "RESERVED",
            }

        for i in range(axi_secsid_t.NON_SECURE, axi_secsid_t.RESERVED, 1):
            if i > (2**self.width)-1:
                del d[i]

        return d

def signal_to_type(signal : str) -> Any:
    """
    Converts a signal string to the corresponding type class instance.

    :param signal: The signal string to convert.
    :param type_class: The type class to use for conversion.
    :return: An instance of the type class corresponding to the signal.
    """
    if signal.endswith("burst"):
        return axi_burst_t
    elif signal.endswith("resp"):
       return axi_resp_t
    elif signal == "awatop":
        return axi_atomic_t
    elif signal.endswith("mmusecsid"):
        return axi_secsid_t
    else:
        return avl.Logic

__all__ =   [
            "axi_burst_t",
            "axi_resp_t",
            "axi_domain_t",
            "axi_atomic_t",
            "axi_secsid_t",
            "signal_to_type",
            ]
