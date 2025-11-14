# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Sequence Item

from typing import Any

import avl
from z3 import UGE, ULE, And, BitVecVal, Implies, Or, ZeroExt

from ._signals import ar_m_signals, aw_m_signals, b_s_signals, is_random, r_s_signals, w_m_signals
from ._types import axi_atomic_t, axi_burst_t, axi_resp_t, signal_to_type


class SequenceItem(avl.SequenceItem):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the sequence item

        :param name: Name of the sequence item
        :param parent: Parent component of the sequence item
        :return: None
        """
        super().__init__(name, parent)

        # Handle to interface - defines capabilities and parameters
        i_f = avl.Factory.get_variable(f"{self.get_full_name()}.i_f", None)

        # Add events for finer grained sequence control
        self.add_event("awake")
        self.add_event("control")
        self.add_event("data")

        # By default transpose to make more readable
        self.set_table_fmt(transpose=True)

        # Local / Hidden Parameters
        for k, v in vars(i_f).items():
            if isinstance(v, (int | str)):
                setattr(self, f"_{k}_", v)

    def resize(self, size : int = None) -> None:
        """
        Re-size transaction data fields based on len

        :param size: New size of the transaction (len+1) - if None use current len+1
        :type size: int
        :return: None

        """
        if size is None:
            n = self.get_len()+1
        else:
            n = size

        # Re-Size Write Data
        for s in w_m_signals + ["w_wait_cycles"]:
            if hasattr(self, s):
                lst = getattr(self, s)
                setattr(self, s, lst[:n])

        # Re-Size Read Data
        for s in r_s_signals + ["r_wait_cycles"]:
            if hasattr(self, s):
                if not self.has_rresp():
                    delattr(self, s)
                else:
                    lst = getattr(self, s)
                    setattr(self, s, lst[:n])

        # Force IDs, loop to match
        if hasattr(self, "bid") :
            self.set("bid", self.get("awid", default=0))
        if hasattr(self, "bloop") :
            self.set("bloop", self.get("awloop", default=0))
        if hasattr(self, "btrace"):
            self.set("btrace", self.get("awtrace", default=0))
        if hasattr(self, "bidunq"):
            self.set("bidunq", self.get("awidunq"))

        for i in range(n):
            if hasattr(self, "rid") :
                self.set("rid", self.get_id(), idx=i)
            if hasattr(self, "rloop") :
                self.set("rloop", self.get("arloop", default=0), idx=i)
            if hasattr(self, "rtrace") :
                self.set("rtrace", self.get("artrace", default=0), idx=i)
            if hasattr(self, "ridunq") :
                self.set("ridunq", self.get("aridunq", default=0), idx=i)

    def sanity(self) -> None:
        """
        Sanity Check fields vs. spec
        e.g.
        - command / response fields that should match
        - parameters that enforce values
        """

        # Fixed burst disable must be obeyed
        if self._Fixed_Burst_Disable_ or self._Regular_Transactions_Only_:
            assert self.get_burst() != axi_burst_t.FIXED

        # Max Transaction Bytes must be obeyed
        assert (self.get_len()+1)*self.get_size() <= self._Max_Transaction_Bytes_

        # Regular Transactions limitations must be obeyed
        if self._Regular_Transactions_Only_:

            # Limited Range of lengths
            assert self.get_len() in [0,1,3,7,15]

            # Bursts must used whole bus width
            if self.get_len() != 0:
                assert self.get_size() == self._DATA_WIDTH_/8

            # Address Alignment
            if self.get_burst() == axi_burst_t.INCR:
                assert self.get_addr() % ((self.get_len()+1)*self.get_size()) == 0
            elif self.get_burst() == axi_burst_t.WRAP:
                assert self.get_addr() % self.get_size() == 0
            else:
                raise ValueError("Unexpected burst type")

        if self.has_bresp():
            # Signals which must match command -> response
            assert self.get_id()    == self.get("bid", default=0)
            assert self.get_loop()  == self.get("bloop", default=0)
            assert self.get_trace() == self.get("btrace", default=0)
            assert self.get_idunq() == self.get("bidunq", default=0)

        if self.has_rresp():
            for i in range(self.get_len()+1):
                # Signals which must match command -> response
                assert self.get_id()    == self.get("rid", default=0, idx=i)
                assert self.get_loop()  == self.get("rloop", default=0, idx=i)
                assert self.get_trace() == self.get("rtrace", default=0, idx=i)
                assert self.get_idunq() == self.get("ridunq", default=0, idx=i)

                # Consistent DECERR - any decerr in responses must cause all decerr
                if self._Consistent_DECERR_:
                    assert self.get("rresp", default=axi_resp_t.OKAY, idx=i) == self.get("rresp", default=axi_resp_t.OKAY, idx=0)

    def post_randomize(self):
        """
        Post Randomize actions
        """
        super().post_randomize()

        self.resize()

        # Force alignment for Regular Transaction - quicker than constraint
        if self._Regular_Transactions_Only_:
            addr = self.get_addr()

            if self.get_burst() == axi_burst_t.INCR:
                mask = ((self.get_len()+1)*self.get_size()) -1
            elif self.get_burst() == axi_burst_t.WRAP:
                mask = self.get_size() -1
            else:
                raise ValueError(f"Unexpected burst_type_t {self.get('aw')}")

            self.set_addr(addr & ~mask)

    def set(self, name : str, value : int, idx : int = None) -> None:
        """
        Set the value of a field in the sequence item - if it exists.

        :param name: Name of the field to set
        :param value: Value to set for the field
        :return: None
        """
        signal = getattr(self, name, None)
        if isinstance(signal, list):
            if idx is not None:
                signal[idx].value = int(value)
            else:
                for i,v in enumerate(value):
                    signal[i].value = int(v)

        elif signal is not None:
            signal.value = int(value)

    def get(self, name : str, idx : int = None, default : Any = None) -> int:
        """
        Get the value of a field in the sequence item - if it exists.

        :param name: Name of the field to get
        :param default: Default value to return if the field does not exist
        :return: Value of the field or default value
        """
        signal = getattr(self, name, None)

        if isinstance(signal, list):
            if idx is not None:
                return signal[idx].value
            else:
                return signal
        elif signal is not None:
            return signal.value

        return default

    def get_addr(self) -> int:
        """
        Return the address

        :return: Addr (awaddr, araddr)
        """
        if hasattr(self, "awaddr"):
            return int(self.awaddr)
        else:
            return int(self.araddr)

    def set_addr(self, addr : int) -> None:
        """
        Set the address

        :return: Addr (awaddr, araddr)
        """
        if hasattr(self, "awaddr"):
            self.set("awaddr", addr)
        else:
            self.set("araddr", addr)

    def get_id(self) -> int:
        """
        Return ID

        :return: ID (awid, arid)
        """
        if hasattr(self, "awaddr"):
            return int(self.get("awid", default=0))
        else:
            return int(self.get("arid", default=0))

    def get_idunq(self) -> int:
        """
        Return ID Unique

        :return: ID Unique (awidunq, aridunq)
        """
        if hasattr(self, "awaddr"):
            return int(self.get("awidunq", default=0))
        else:
            return int(self.get("aridunq", default=0))

    def get_tagop(self) -> int:
        """
        Return TAG operation

        :return: TAG operation (awtagop, artagop)
        """
        if hasattr(self, "awaddr"):
            return int(self.get("awtagop", default=0))
        else:
            return int(self.get("artagop", default=0))

    def get_len(self) -> int:
        """
        Return Length

        :return: Length (arlen or awlen)
        """
        if hasattr(self, "awaddr"):
            return int(self.get("awlen", default=0))
        else:
            return int(self.get("arlen", default=0))

    def get_size(self) -> int:
        """
        Return Size (in bytes)

        :return: Size
        """
        if hasattr(self, "awaddr"):
            return int(2**self.get("awsize", default=0))
        else:
            return int(2**self.get("arsize", default=0))

    def get_burst(self) -> int:
        """
        Return Burst

        :return: Burst
        """
        if hasattr(self, "awaddr"):
            return int(self.get("awburst", default=axi_burst_t.INCR))
        else:
            return int(self.get("arburst", default=axi_burst_t.INCR))

    def get_loop(self) -> int:
        """
        Return Loop

        :return: Length (arloop or awloop)
        """
        if hasattr(self, "awaddr"):
            return int(self.get("awloop", default=0))
        else:
            return int(self.get("arloop", default=0))

    def get_trace(self) -> int:
        """
        Return Trace

        :return: Length (artrace or awtrace)
        """
        if hasattr(self, "awaddr"):
            return int(self.get("awtrace", default=0))
        else:
            return int(self.get("artrace", default=0))

    def has_bresp(self) -> bool:
        """
        Expect a response on bresp channel
        """

        if hasattr(self, "awatop"):
            return self.awatop.has_bresp()
        elif hasattr(self, "awaddr"):
            return True

        return False

    def has_rresp(self) -> bool:
        """
        Expect a response on resp channel
        """

        if hasattr(self, "awatop"):
            return self.awatop.has_rresp()
        elif hasattr(self, "araddr"):
            return True

        return False

class WriteItem(SequenceItem):
    def __init__(self, name: str, parent: avl.Component) -> None:  # noqa: C901
        """
        Initialize the sequence item

        :param name: Name of the sequence item
        :param parent: Parent component of the sequence item
        """
        super().__init__(name, parent)

        # Handle to interface - defines capabilities and parameters
        i_f = avl.Factory.get_variable(f"{self.get_full_name()}.i_f", None)

        if hasattr(i_f, "awakeup"):
            self.goto_sleep = avl.Logic(0, width=len(i_f.awakeup), fmt=str)

        # Write Control Signals
        for s in aw_m_signals:
            if s in ["awvalid"]:
                continue

            if hasattr(i_f, s):
                v = getattr(i_f, s)
                setattr(self, s, signal_to_type(s)(0, width=len(v), auto_random=is_random(s)))

        # Write Data Signals
        for s in w_m_signals:
            if s in ["wvalid", "wlast"]:
                continue

            if hasattr(i_f, s):
                v = getattr(i_f, s)
                setattr(self, s, [signal_to_type(s)(0, width=len(v), auto_random=is_random(s)) for _ in range(256)])

        # Read Response Signals - atomic loads
        for s in r_s_signals:
            if s in ["rvalid", "rlast"]:
                continue

            if hasattr(i_f, s):
                v = getattr(i_f, s)
                setattr(self, s, [signal_to_type(s)(0, width=len(v), auto_random=is_random(s)) for _ in range(256)])

        # Write Response Signals
        for s in b_s_signals:
            if s in ["bvalid"]:
                continue

            if hasattr(i_f, s):
                v = getattr(i_f, s)
                setattr(self, s, signal_to_type(s)(0, width=len(v), auto_random=is_random(s)))

        # Wait cycles
        self.aw_wait_cycles = avl.Uint8(0, auto_random=False)
        """Wait cycles between control awvalid and control awready"""
        self.set_field_attributes("aw_wait_cycles", compare=False)

        self.w_wait_cycles = [avl.Uint8(0, auto_random=False) for _ in range(256)]
        """Wait cycles between data wvalid and data wready"""
        self.set_field_attributes("w_wait_cycles", compare=False)

        self.b_wait_cycles = avl.Uint8(0, auto_random=False)
        """Wait cycles between data bvalid and data bready"""
        self.set_field_attributes("b_wait_cycles", compare=False)

        # Reduced signals used for coverage
        self._wdata_ = [avl.Logic(0, width=self.wdata[0].width), avl.Logic(-1, width=self.wdata[0].width)]

        if hasattr(self, "wstrb"):
            self._wstrb_ = [avl.Logic(0, width=self.wstrb[0].width), avl.Logic(-1, width=self.wstrb[0].width)]

        if hasattr(self, "wuser"):
            self._wuser_ = [avl.Logic(0, width=self.wuser[0].width), avl.Logic(-1, width=self.wuser[0].width)]

        if hasattr(self, "wpoison"):
            self._wpoison_ = [avl.Logic(0, width=self.wpoison[0].width), avl.Logic(-1, width=self.wpoison[0].width)]

        if hasattr(self, "wtrace"):
            self._wtrace_ = [avl.Logic(0, width=self.wtrace[0].width), avl.Logic(-1, width=self.wtrace[0].width)]

        # Constraints

        if hasattr(self, "awlen"):
            self.add_constraint("c_awlen", lambda x : ULE(x,len(self.wdata)-1), self.awlen)

            if hasattr(self, "awsize"):
                self.add_constraint("c_max_transaction_bytes",
                                     lambda x,y : ULE(((ZeroExt(8, x) + BitVecVal(1, 16)) << ZeroExt(13, y)), BitVecVal(i_f.Max_Transaction_Bytes,16)),
                                     self.awlen, self.awsize)
            else:
                self.add_constraint("c_max_transaction_bytes", lambda x : ULE((ZeroExt(8, x) + BitVecVal(1, 16)), BitVecVal(i_f.Max_Transaction_Bytes,16)), self.awlen)
        elif hasattr(self, "awsize"):
            self.add_constraint("c_max_transaction_bytes", lambda y : ULE(1 << ZeroExt(13, y), BitVecVal(i_f.Max_Transaction_Bytes,16)), self.awsize)

        if hasattr(self, "awatop"):
            self.add_constraint("c_awatop_legal", lambda x: Or(*(x == v for v in self.awatop.values())), self.awatop)
            self.add_constraint("c_awatop_size", lambda x,y : Implies(x != axi_atomic_t.NON_ATOMIC, ULE(y,5)), self.awatop, self.awsize)

        if hasattr(self, "swstashniden"):
            self.add_constraint("c_swstashnid", lambda x,y : Implies(y == 0, x == 0), self.awstashniden, self.awstashnid)

        if hasattr(self, "swstashlpiden"):
            self.add_constraint("c_swstashlpid", lambda x,y : Implies(y == 0, x == 0), self.awstashlpiden, self.awstashlpid)

        if hasattr(self, "awtagop"):
            self.add_constraint("c_awtagop_burst", lambda x,y : Implies(x != 0, y != axi_burst_t.FIXED), self.awtagop, self.awburst)
            self.add_constraint("c_awtagop_cache", lambda x,y : Implies(x != 0, y & 0b1111 == 0b0011), self.awtagop, self.awcache)
            if hasattr(self, "awidunq"):
                self.add_constraint("c_awtagop_cache", lambda x,y : Implies(x != 0, y == 1), self.awtagop, self.awidunq)

        if hasattr(self, "awburst") and i_f.Fixed_Burst_Disable:
            self.add_constraint("c_fixed_burst_disable", lambda x : x != axi_burst_t.FIXED, self.awburst)

        if i_f.Regular_Transactions_Only:
            if hasattr(self, "awlen"):
                self.add_constraint("c_regular_len", lambda x : Or(x==0, x==1, x==3, x==7, x==15), self.awlen)
                if hasattr(self, "awsize"):
                    self.add_constraint("c_regular_size", lambda x,y: Implies(y != 0, (1 << ZeroExt(8, x) == i_f.DATA_WIDTH/8)), self.awsize, self.awlen)
            if hasattr(self, "awburst"):
                self.add_constraint("c_regualr_burst", lambda x : x != axi_burst_t.FIXED, self.awburst)

class ReadItem(SequenceItem):
    def __init__(self, name: str, parent: avl.Component) -> None:  # noqa: C901
        """
        Initialize the sequence item

        :param name: Name of the sequence item
        :param parent: Parent component of the sequence item
        """
        super().__init__(name, parent)

        # Handle to interface - defines capabilities and parameters
        i_f = avl.Factory.get_variable(f"{self.get_full_name()}.i_f", None)

        if hasattr(i_f, "awakeup"):
            self.goto_sleep = avl.Logic(0, width=len(i_f.awakeup), fmt=str)

        # Read Control Signals
        for s in ar_m_signals:
            if s in ["arvalid"]:
                continue

            if hasattr(i_f, s):
                v = getattr(i_f, s)
                setattr(self, s, signal_to_type(s)(0, width=len(v), auto_random=is_random(s)))

        # Read Response Signals
        for s in r_s_signals:
            if s in ["rvalid", "rlast"]:
                continue

            if hasattr(i_f, s):
                v = getattr(i_f, s)
                setattr(self, s, [signal_to_type(s)(0, width=len(v), auto_random=is_random(s)) for _ in range(256)])

        # Wait cycles
        self.ar_wait_cycles = avl.Uint8(0, auto_random=False)
        """Wait cycles between control arvalid and control arready"""
        self.set_field_attributes("ar_wait_cycles", compare=False)

        self.r_wait_cycles = [avl.Uint8(0, auto_random=False) for _ in range(256)]
        """Wait cycles between data rvalid and data rready"""
        self.set_field_attributes("r_wait_cycles", compare=False)

        # Reduced signals used for coverage
        self._rdata_ = [avl.Logic(0, width=self.rdata[0].width), avl.Logic(-1, width=self.rdata[0].width)]

        if hasattr(self, "rresp"):
            self._rresp_ = [avl.Logic(0, width=self.rresp[0].width), avl.Logic(-1, width=self.rresp[0].width)]

        if hasattr(self, "ruser"):
            self._ruser_ = [avl.Logic(0, width=self.ruser[0].width), avl.Logic(-1, width=self.ruser[0].width)]

        if hasattr(self, "rpoison"):
            self._rpoison_ = [avl.Logic(0, width=self.rpoison[0].width), avl.Logic(-1, width=self.rpoison[0].width)]

        if hasattr(self, "rtrace"):
            self._rtrace_ = [avl.Logic(0, width=self.rtrace[0].width), avl.Logic(-1, width=self.rtrace[0].width)]

        if hasattr(self, "rloop"):
            self._rloop_ = [avl.Logic(0, width=self.rloop[0].width), avl.Logic(-1, width=self.rloop[0].width)]

        # Constraints
        if hasattr(self, "arlen"):
            self.add_constraint("c_arlen", lambda x : ULE(x, len(self.rdata)-1), self.arlen)

            if hasattr(self, "arsize"):
                self.add_constraint("c_max_transaction_bytes", lambda x,y : ULE(((ZeroExt(8, x) + 1) << ZeroExt(13, y)), BitVecVal(i_f.Max_Transaction_Bytes, 16)), self.arlen, self.arsize)
            else:
                self.add_constraint("c_max_transaction_bytes", lambda x : (ULE(ZeroExt(8, x) +1), BitVecVal(i_f.Max_Transaction_Bytes, 16)), self.arlen)
        elif hasattr(self, "arsize"):
            self.add_constraint("c_max_transaction_bytes", lambda y : ULE(1 << ZeroExt(13, y), BitVecVal(i_f.Max_Transaction_Bytes, 16)), self.arsize)

        if hasattr(self, "artagop"):
            self.add_constraint("c_artagop_reserved", lambda x : x != 0b10, self.artagop)
            self.add_constraint("c_artagop_rtag", lambda x,y : Implies(x == 0, y == 0), self.artagop, self.rtag)
            self.add_constraint("c_artagop_burst", lambda x,y : Implies(x != 0, y != axi_burst_t.FIXED), self.artagop, self.arburst)
            self.add_constraint("c_artagop_cache", lambda x,y : Implies(x != 0, y & 0b1111 == 0b0011), self.artagop, self.arcache)
            if hasattr(self, "aridunq"):
                self.add_constraint("c_artagop_cache", lambda x,y : Implies(x != 0, y == 1), self.artagop, self.aridunq)

        if hasattr(self, "arburst") and i_f.Fixed_Burst_Disable:
            self.add_constraint("c_fixed_burst_disable", lambda x : x != axi_burst_t.FIXED, self.arburst)

        if i_f.Regular_Transactions_Only:
            if hasattr(self, "arlen"):
                self.add_constraint("c_regular_len", lambda x : Or(x==0, x==1, x==3, x==7, x==15), self.arlen)
                if hasattr(self, "arsize"):
                    self.add_constraint("c_regular_size", lambda x,y: Implies(y != 0, (1 << ZeroExt(8, x) == i_f.DATA_WIDTH/8)), self.arsize, self.arlen)
            if hasattr(self, "arburst"):
                self.add_constraint("c_regualr_burst", lambda x : x != axi_burst_t.FIXED, self.arburst)

    def post_randomize(self):
        """
        """
        super().post_randomize()

        if self._Consistent_DECERR_:
            for i in range(len(self.resp)):
                if self.rresp[i] == axi_resp_t.DECERR:
                    for j in range(len(self.rresp)):
                        self.rresp[j] = axi_resp_t.DECERR
                        return

__all__ = ["SequenceItem", "WriteItem", "ReadItem"]
