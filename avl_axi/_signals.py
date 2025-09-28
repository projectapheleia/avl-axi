# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Signals lists

#: AW Manger Signals
aw_m_signals = [
    "awvalid",
    "awid",
    "awaddr",
    "awregion",
    "awlen",
    "awsize",
    "awburst",
    "awlock",
    "awcache",
    "awprot",
    "awnse",
    "awqos",
    "awuser",
    "awdomain",
    "awsnoop",
    "awstashnid",
    "awstashniden",
    "awstashlpid",
    "awstashlpiden",
    "awtrace",
    "awloop",
    "awmmuvalid",
    "awmmusecsid",
    "awmmusid",
    "awmmussidv",
    "awmmussid",
    "awmmuatst",
    "awmmuflow",
    "awpbha",
    "awnsaid",
    "awsubsysid",
    "awatop",
    "awmpam",
    "awidunq",
    "awcmo",
    "awtagop",
    "awmecid",
]

#: AW Subordinate Signals
aw_s_signals = [
    "awready",
]

#: W Manager Signals
w_m_signals = [
    "wvalid",
    "wdata",
    "wstrb",
    "wtag",
    "wtagupdate",
    "wlast",
    "wuser",
    "wpoison",
    "wtrace",
]

#: W Subordinate Signals
w_s_signals = [
    "wready",
]

#: B Manager Signals
b_m_signals = [
    "bready",
]

#: B Subordinate Signals
b_s_signals = [
    "bvalid",
    "bid",
    "bidunq",
    "bresp",
    "bpersist",
    "btagmatch",
    "buser",
    "btrace",
    "bloop",
    "bbusy",
]

#: AR Manager Signals
ar_m_signals = [
    "arvalid",
    "arid",
    "araddr",
    "arregion",
    "arlen",
    "arsize",
    "arburst",
    "arlock",
    "arcache",
    "arprot",
    "arnse",
    "arqos",
    "aruser",
    "ardomain",
    "arsnoop",
    "artrace",
    "arloop",
    "armmuvalid",
    "armmusecsid",
    "armmusid",
    "armmussidv",
    "armmussid",
    "armmuatst",
    "armmuflow",
    "arpbha",
    "arnsaid",
    "arsubsysid",
    "armpam",
    "archunken",
    "aridunq",
    "artagop",
    "armecid",
]

#: AR Subordinate Signals
ar_s_signals = [
    "arready",
]

#: R Manager Signals
r_m_signals = [
    "rready",
]

#: R Subordinate Signals
r_s_signals = [
    "rvalid",
    "rid",
    "ridunq",
    "rdata",
    "rtag",
    "rresp",
    "rlast",
    "ruser",
    "rtrace",
    "rloop",
    "rchunkv",
    "rchunknum",
    "rchunkstrb",
    "rbusy",
]

#: Function to indicate if a signal should be randomized (performance optimization)
def is_random(s):
    if s in ["wtace",
             "bid",
             "bidunq",
             "btrace",
             "bloop",
             "rid",
             "ridunq",
             "trace",
             "rloop"] :
        return False
    return True

__all__ = ["aw_m_signals",
           "aw_s_signals",
           "w_m_signals",
           "w_s_signals",
           "b_m_signals",
           "b_s_signals",
           "ar_m_signals",
           "ar_s_signals",
           "r_m_signals",
           "r_s_signals",
           "is_random",
          ]

