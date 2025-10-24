# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Coverage

from typing import Any

import avl

from ._item import ReadItem, WriteItem
from ._types import axi_atomic_t, axi_burst_t, axi_domain_t, axi_resp_t, axi_secsid_t


class Coverage(avl.Component):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize Coverage

        :param name: Name of the coverage class.
        :type name: str
        :param parent: Parent component.
        :type parent: Component
        """
        super().__init__(name, parent)

        self.item_port = avl.List()

        # Define Write coverage
        self.item = WriteItem("coverage_item", self)
        self.cg = avl.Covergroup("axi", self)
        self.cg.set_comment("AXI Coverage")

        #AWID
        self.add_coverpoint(self.cg, "awid")

        # AWADDR
        self.add_coverpoint(self.cg, "awaddr")

        # AWREGION
        self.add_coverpoint(self.cg, "awregion")

        # AWLEN
        self.add_coverpoint(self.cg, "awlen")

        # Simplified AWLEN for crosses
        if hasattr(self.item, "awlen"):
            self.cg.add_coverpoint("w_is_burst", lambda: self.item.get("awlen", default=None))
            self.cg._cps_["w_is_burst"].add_bin("0", lambda x : x == 0)
            self.cg._cps_["w_is_burst"].add_bin("1", lambda x : x != 0)

        # AWSIZE
        self.add_coverpoint(self.cg, "awsize")

        # AWLEN X AWSIZE
        self.add_covercross(self.cg, "awlen==0 X awsize", "w_is_burst", "awsize")

        # AWBURST
        self.add_coverpoint(self.cg, "awburst", signal_type=axi_burst_t)

        # AWLEN X AWBURST
        self.add_covercross(self.cg, "awlen==0 X awburst", "w_is_burst", "awburst")

        # AWLOCK
        self.add_coverpoint(self.cg, "awlock")

        # AWLEN X AWLOCK
        self.add_covercross(self.cg, "awlen==0 X awlock", "w_is_burst", "awlock")

        # AWPROT
        self.add_coverpoint(self.cg, "awprot")

        # AWNSE
        self.add_coverpoint(self.cg, "awnse")

        # AWQOS
        self.add_coverpoint(self.cg, "awqos")

        # AWUSER
        self.add_coverpoint(self.cg, "awuser")

        # AWDOMAIN
        self.add_coverpoint(self.cg, "awdomain", signal_type=axi_domain_t)

        # AWSNOOP
        self.add_coverpoint(self.cg, "awsnoop")

        # AWSSTASHNID
        self.add_coverpoint(self.cg, "awstashnid")

        # AWSSTASHNIDEN
        self.add_coverpoint(self.cg, "awstashniden")

        # AWSSTASHLPID
        self.add_coverpoint(self.cg, "awstashlpid")

        # AWSSTASHLPIDEN
        self.add_coverpoint(self.cg, "awstashlpiden")

        # AWTRACE
        self.add_coverpoint(self.cg, "awtrace")

        # AWLOOP
        self.add_coverpoint(self.cg, "awloop")

        # AWMMUVLAID
        self.add_coverpoint(self.cg, "awmmuvalid")

        # AWMMUSECSID
        self.add_coverpoint(self.cg, "awmmusecsid", signal_type=axi_secsid_t)

        # AWMMUSID
        self.add_coverpoint(self.cg, "awmmusid")

        # AWMMUSSIDV
        self.add_coverpoint(self.cg, "awmmussidv")

        # AWMMUSSID
        self.add_coverpoint(self.cg, "awmmussid")

        # AWMMUATST
        self.add_coverpoint(self.cg, "awmmuatst")

        # AWMMFLOW
        self.add_coverpoint(self.cg, "awmmflow")

        # AWPBHA
        self.add_coverpoint(self.cg, "awpbha")

        # AWMECID
        self.add_coverpoint(self.cg, "awmecid")

        # AWNSAID
        self.add_coverpoint(self.cg, "awnsaid")

        # AWSUBSYSID
        self.add_coverpoint(self.cg, "awsubsysid")

        # AWATOP
        self.add_coverpoint(self.cg, "awatop", signal_type=axi_atomic_t)

        # AWLEN X AWATOP
        self.add_covercross(self.cg, "awlen==0 X awatop", "w_is_burst", "awatop")

        # AWMPAM
        self.add_coverpoint(self.cg, "awmpam")

        # AWIDUNQ
        self.add_coverpoint(self.cg, "awidunq")

        # AWCMO
        self.add_coverpoint(self.cg, "awcmo")

        # AWTAGOP
        self.add_coverpoint(self.cg, "awtagop")

        # AWTAG
        self.add_coverpoint(self.cg, "awtag")

        # AWTAGUPDATE
        self.add_coverpoint(self.cg, "awtagupdate")

        # AW Wait
        self.cg.add_coverpoint("aw_wait", lambda: self.item.get("aw_wait_cycles", default=None))
        self.cg._cps_["aw_wait"].set_comment("AW WAIT CYCLES")
        for i in range(3):
            self.cg._cps_["aw_wait"].add_bin(f"{i}", i)
        self.cg._cps_["aw_wait"].add_bin("wait_cycles", range(0,256), stats=True)

        # WDATA
        self.add_coverpoint(self.cg, "wdata")

        # WSTRB
        self.add_coverpoint(self.cg, "wstrb")

        # WUSER
        self.add_coverpoint(self.cg, "wuser")

        # WPOISON
        self.add_coverpoint(self.cg, "wpoison")

        # WTRACE
        self.add_coverpoint(self.cg, "wtrace")

        # W Wait
        self.cg.add_coverpoint("w_wait[0]", lambda: self.item.get("w_wait_cycles", idx=0, default=None))
        self.cg._cps_["w_wait[0]"].set_comment("W WAIT CYCLES (1st beat)")
        for i in range(3):
            self.cg._cps_["w_wait[0]"].add_bin(f"{i}", i)
        self.cg._cps_["w_wait[0]"].add_bin("wait_cycles", range(0,256), stats=True)

        # BRESP
        self.add_coverpoint(self.cg, "bresp", signal_type=axi_resp_t)

        # BCOMP
        self.add_coverpoint(self.cg, "bcomp")

        # BPERSIST
        self.add_coverpoint(self.cg, "bpersist")

        # BUSER
        self.add_coverpoint(self.cg, "buser")

        # BTRACE
        self.add_coverpoint(self.cg, "btrace")

        # BLOOP
        self.add_coverpoint(self.cg, "bloop")

        # BTAGMATCH
        self.add_coverpoint(self.cg, "btagmatch")

        # BWait
        self.cg.add_coverpoint("b_wait", lambda: self.item.get("b_wait_cycles", default=None))
        self.cg._cps_["b_wait"].set_comment("B WAIT CYCLES")
        for i in range(3):
            self.cg._cps_["b_wait"].add_bin(f"{i}", i)
        self.cg._cps_["b_wait"].add_bin("wait_cycles", range(0,256), stats=True)

        # Define Read coverage
        self.item = ReadItem("coverage_item", self)

        #ARID
        self.add_coverpoint(self.cg, "arid")

        # ARADDR
        self.add_coverpoint(self.cg, "araddr")

        # ARREGION
        self.add_coverpoint(self.cg, "arregion")

        # ARLEN
        self.add_coverpoint(self.cg, "arlen")

        # Simplified ARLEN for crosses
        if hasattr(self.item, "arlen"):
            self.cg.add_coverpoint("r_is_burst", lambda: self.item.get("arlen", default=None))
            self.cg._cps_["r_is_burst"].add_bin("0", lambda x : x == 0)
            self.cg._cps_["r_is_burst"].add_bin("1", lambda x : x != 0)

        # ARSIZE
        self.add_coverpoint(self.cg, "arsize")

        # ARLEN X ARSIZE
        self.add_covercross(self.cg, "arlen==0 X arsize", "r_is_burst", "arsize")

        # ARBURST
        self.add_coverpoint(self.cg, "arburst", signal_type=axi_burst_t)

        # ARLEN X ARBURST
        self.add_covercross(self.cg, "arlen==0 X arburst", "r_is_burst", "arburst")

        # ARLOCK
        self.add_coverpoint(self.cg, "arlock")

        # ARLEN X ARLOCK
        self.add_covercross(self.cg, "arlen==0 X arlock", "r_is_burst", "arlock")

        # ARPROT
        self.add_coverpoint(self.cg, "arprot")

        # ARNSE
        self.add_coverpoint(self.cg, "arnse")

        # ARQOS
        self.add_coverpoint(self.cg, "arqos")

        # ARUSER
        self.add_coverpoint(self.cg, "aruser")

        # ARDOMAIN
        self.add_coverpoint(self.cg, "ardomain", signal_type=axi_domain_t)

        # ARSNOOP
        self.add_coverpoint(self.cg, "arsnoop")

        # ARTRACE
        self.add_coverpoint(self.cg, "artrace")

        # ARLOOP
        self.add_coverpoint(self.cg, "arloop")

        # ARMMUVLAID
        self.add_coverpoint(self.cg, "armmuvalid")

        # ARMMUSECSID
        self.add_coverpoint(self.cg, "armmusecsid", signal_type=axi_secsid_t)

        # ARMMUSID
        self.add_coverpoint(self.cg, "armmusid")

        # ARMMUSSIDV
        self.add_coverpoint(self.cg, "armmussidv")

        # ARMMUSSID
        self.add_coverpoint(self.cg, "armmussid")

        # ARMMUATST
        self.add_coverpoint(self.cg, "armmuatst")

        # ARMMFLOW
        self.add_coverpoint(self.cg, "armmflow")

        # ARPBHA
        self.add_coverpoint(self.cg, "arpbha")

        # ARMECID
        self.add_coverpoint(self.cg, "armecid")

        # ARNSAID
        self.add_coverpoint(self.cg, "arnsaid")

        # ARSUBSYSID
        self.add_coverpoint(self.cg, "arsubsysid")

        # ARMPAM
        self.add_coverpoint(self.cg, "armpam")

        # ARIDUNQ
        self.add_coverpoint(self.cg, "aridunq")

        # ARTAGOP
        self.add_coverpoint(self.cg, "artagop")

        # ARTAG
        self.add_coverpoint(self.cg, "artag")

        # AR Wait
        self.cg.add_coverpoint("ar_wait", lambda: self.item.get("ar_wait_cycles", default=None))
        self.cg._cps_["ar_wait"].set_comment("AR WAIT CYCLES")
        for i in range(3):
            self.cg._cps_["ar_wait"].add_bin(f"{i}", i)
        self.cg._cps_["ar_wait"].add_bin("wait_cycles", range(0,256), stats=True)

        # RDATA
        self.add_coverpoint(self.cg, "rdata")

        # RUSER
        self.add_coverpoint(self.cg, "ruser")

        # RPOISON
        self.add_coverpoint(self.cg, "rpoison")

        # RTRACE
        self.add_coverpoint(self.cg, "rtrace")

        # RRESP
        self.add_coverpoint(self.cg, "rresp") # Use bitwise as a list

        # RLOOP
        self.add_coverpoint(self.cg, "rloop")

        # R Wait
        self.cg.add_coverpoint("r_wait[0]", lambda: self.item.get("r_wait_cycles", idx=0, default=None))
        self.cg._cps_["r_wait[0]"].set_comment("R WAIT CYCLES (1st beat)")
        for i in range(3):
            self.cg._cps_["r_wait[0]"].add_bin(f"{i}", i)
        self.cg._cps_["r_wait[0]"].add_bin("wait_cycles", range(0,256), stats=True)

    def add_coverpoint(self, cg : avl.Covergroup, signal : str, signal_type : [Any]=None, comment : str=None) -> avl.Coverpoint:
        """
        Wrapper around adding coverage point
        Lists are reduced to bit checks across all beats

        :param cg
        :param signal: Signal to add coverage point
        :param signal_type: Type of signal to add
        :returns: None
        """
        if not hasattr(self.item, signal):
            return

        if comment is None:
            comment = signal.upper()

        attr_name = f"_{signal}_" if isinstance(getattr(self.item, signal), list) else signal
        var = getattr(self.item, attr_name)

        cg.add_coverpoint(signal, lambda: getattr(self.item, attr_name, None))
        cg._cps_[signal].set_comment(comment)

        if isinstance(var, list):
            for i in range(var[0].width):
                cg._cps_[signal].add_bin(f"[{i}] == 0", lambda x, y=i : 0 == (x[1] & (1<<y)))
                cg._cps_[signal].add_bin(f"[{i}] == 1", lambda x, y=i : 0 != (x[0] & (1<<y)))
        elif signal_type is not None:
            for k,v in var.values().items():
                cg._cps_[signal].add_bin(v, k)
        elif var.width <= 8:
            for i in range(2**var.width):
                cg._cps_[signal].add_bin(f"{i}", i)
        else:
            for i in range(var.width):
                cg._cps_[signal].add_bin(f"[{i}] == 0", lambda x, y=i : 0 == (x & (1<<y)))
                cg._cps_[signal].add_bin(f"[{i}] == 1", lambda x, y=i : 0 != (x & (1<<y)))

        return cg._cps_[signal]

    def add_covercross(self, cg : avl.Covergroup, name : str, *args, comment : str=None) -> avl.Covercross:
        """
        Wrapper around adding coverage cross

        :param cg
        :param str names of coverpoints
        :returns: None
        """
        cps = []
        for a in args:
            if a not in cg._cps_:
                return
            cps.append(cg._cps_[a])
        cg.add_covercross(name, *cps)

    async def run_phase(self) -> None:
        """
        Run phase for the coverage component.

        """

        while True:
            # Wait for an item to be available
            self.item = await self.item_port.blocking_get()

            # Sample
            self.cg.sample()

__all__ = ["Coverage"]
