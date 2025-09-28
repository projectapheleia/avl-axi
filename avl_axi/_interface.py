# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Interface

from typing import Any

from cocotb.handle import HierarchyObject


class Interface:
    def __init__(self, hdl : HierarchyObject) -> None: # noqa: C901
        """
        Create an interface
        Work around simulator specific issues with accessing signals inside generates.

        :param hdl: The handle to the interface
        :type hdl: HierarchyObject
        :return: None
        """
        # Parameters and Signals
        for child in list(hdl):
            # Parameters start with a capital letter
            if child._name[0].isupper():
                if isinstance(child.value, bytes):
                    setattr(self, child._name, str(child.value.decode("utf-8")))
                else:
                    setattr(self, child._name, int(child.value))
            else:
                setattr(self, child._name, child)

        if self.CLASSIFICATION != "AXI":
            raise TypeError(f"Expected AXI classification, got {self.CLASSIFICATION}")

        if self.VERSION not in [5]:
            raise ValueError(f"Unsupported AXI version: {self.VERSION}")

        # Remove un-configured signals
        if self.ID_W_WIDTH == 0:
            delattr(self, "awid")
            delattr(self, "bid")
            delattr(self, "arid")
            delattr(self, "rid")

        if self.REGION_Present == 0:
            delattr(self, "awregion")
            delattr(self, "arregion")

        if self.LEN_Present == 0:
            delattr(self, "awlen")
            delattr(self, "arlen")

        if self.SIZE_Present == 0:
            delattr(self, "awsize")
            delattr(self, "arsize")

        if self.BURST_Present == 0:
            delattr(self, "awburst")
            delattr(self, "arburst")

        if self.Exclusive_Accesses == 0:
            delattr(self, "awlock")
            delattr(self, "arlock")

        if self.CACHE_Present == 0:
            delattr(self, "awcache")
            delattr(self, "arcache")

        if self.PROT_Present == 0:
            delattr(self, "awprot")
            delattr(self, "arprot")

        if self.RME_Support == 0:
            delattr(self, "awnse")
            delattr(self, "arnse")

        if self.QOS_Present == 0:
            delattr(self, "awqos")
            delattr(self, "arqos")

        if self.USER_REQ_WIDTH == 0:
            delattr(self, "awuser")
            delattr(self, "aruser")

        if self.Shareable_Transactions == 0:
            delattr(self, "awdomain")
            delattr(self, "ardomain")

        if self.AWSNOOP_WIDTH == 0:
            delattr(self, "awsnoop")

        if self.ARSNOOP_WIDTH == 0:
            delattr(self, "arsnoop")

        if self.STASHNID_Present == 0:
            delattr(self, "awstashnid")
            delattr(self, "awstashniden")
            delattr(self, "awstashlpid")
            delattr(self, "awstashlpiden")

        if self.Trace_Signals == 0:
            delattr(self, "awtrace")
            delattr(self, "wtrace")
            delattr(self, "btrace")
            delattr(self, "artrace")
            delattr(self, "rtrace")

        if self.Loopback_Signals == 0 or self.LOOP_W_WIDTH == 0:
            delattr(self, "awloop")
            delattr(self, "bloop")

        if self.Loopback_Signals == 0 or self.LOOP_R_WIDTH == 0:
            delattr(self, "arloop")
            delattr(self, "rloop")

        if self.Untranslated_Transactions != "v3":
            delattr(self, "awmmuvalid")
            delattr(self, "armmuvalid")

        if self.Untranslated_Transactions == "False" or self.SECSID_WIDTH == 0:
            delattr(self, "awmmusecsid")
            delattr(self, "armmusecsid")

        if self.Untranslated_Transactions == "False" or self.SID_WIDTH == 0:
            delattr(self, "awmmusid")
            delattr(self, "armmusid")

        if self.Untranslated_Transactions == "False" or self.SSID_WIDTH == 0:
            delattr(self, "awmmussidv")
            delattr(self, "awmmussid")
            delattr(self, "armmussidv")
            delattr(self, "armmussid")

        if self.MMUFLOW_Present == 0 or (self.Untranslated_Transactions not in ["v1", "True"]):
            delattr(self, "awmmuatst")
            delattr(self, "armmuatst")

        if self.MMUFLOW_Present == 0 or (self.Untranslated_Transactions not in ["v2", "v3"]):
            delattr(self, "awmmuflow")
            delattr(self, "armmuflow")

        if self.PBHA_Support == 0:
            delattr(self, "awpbha")
            delattr(self, "arpbha")

        if self.MEC_Support == 0:
            delattr(self, "awmecid")
            delattr(self, "armecid")

        if self.NSAccess_Identifiers == 0:
            delattr(self, "awnsaid")
            delattr(self, "arnsaid")

        if self.SUBSYSID_WIDTH == 0:
            delattr(self, "awsubsysid")
            delattr(self, "arsubsysid")

        if self.Atomic_Transactions == 0:
            delattr(self, "awatop")

        if self.MPAM_Support == "False":
            delattr(self, "awmpam")
            delattr(self, "armpam")

        if self.Unique_ID_Support == 0 or self.ID_W_WIDTH == 0:
            delattr(self, "awidunq")
            delattr(self, "bidunq")

        if self.Unique_ID_Support == 0 or self.ID_R_WIDTH == 0:
            delattr(self, "aridunq")
            delattr(self, "ridunq")

        if self.CMO_On_Write == 0:
            delattr(self, "awcmo")

        if self.MTE_Support == "False":
            delattr(self, "awtagop")
            delattr(self, "wtag")
            delattr(self, "wtagupdate")
            delattr(self, "artagop")
            delattr(self, "rtag")

        if self.WSTRB_Present == 0:
            delattr(self, "wstrb")

        if self.WLAST_Present == 0:
            delattr(self, "wlast")

        if self.USER_DATA_WIDTH == 0:
            delattr(self, "wuser")

        if self.Poison == 0:
            delattr(self, "wpoison")
            delattr(self, "rpoison")

        if self.BRESP_WIDTH == 0:
            delattr(self, "bresp")

        if (self.Persist_CMO == 0 or self.CMO_On_Write == 0) and self.MTE_Support != "Standard":
            delattr(self, "bcomp")

        if self.Persist_CMO == 0 or self.CMO_On_Write == 0:
            delattr(self, "bpersist")

        if self.MTE_Support != "Standard":
            delattr(self, "btagmatch")

        if self.USER_RESP_WIDTH == 0:
            delattr(self, "buser")

        if self.Busy_Support == 0:
            delattr(self, "bbusy")
            delattr(self, "rbusy")

        if self.ID_R_WIDTH == 0:
            delattr(self, "arid")
            delattr(self, "rid")

        if self.RRESP_WIDTH == 0:
            delattr(self, "rresp")

        if self.RLAST_Present == 0:
            delattr(self, "rlast")

        if self.USER_DATA_WIDTH == 0 and self.USER_RESP_WIDTH == 0:
            delattr(self, "ruser")

        if self.Read_Data_Chunking == 0:
            delattr(self, "archunken")
            delattr(self, "rchunkv")

        if self.Read_Data_Chunking == 0 or self.RCHUNKNUM_WIDTH == 0:
            delattr(self, "rchunknum")

        if self.Read_Data_Chunking == 0 or self.RCHUNKSTRB_WIDTH == 0:
            delattr(self, "rchunkstrb")

        if self.DVM_Message_Support == "False":
            delattr(self, "acvalid")
            delattr(self, "acready")
            delattr(self, "acaddr")
            delattr(self, "acvmidext")
            delattr(self, "crvalid")
            delattr(self, "crready")

        if self.DVM_Message_Support == "False" or self.Trace_Signals == 0:
            delattr(self, "actrace")
            delattr(self, "crtrace")

        if self.Wakeup_Signals == 0:
            delattr(self, "awakeup")

        if self.Wakeup_Signals == 0 or self.DVM_Message_Support == "False":
            delattr(self, "acwakeup")

        if self.QoS_Accept == 0:
            delattr(self, "varqosaccept")
            delattr(self, "vawqosaccept")

        if self.Coherency_Connection_Signals == 0:
            delattr(self, "syscoreq")
            delattr(self, "syscoack")


        # Sanity checks
        if hasattr(self, "awlock"):
            if not hasattr(self, "rresp") or len(self.rresp) < 2:
                raise ValueError("AXI Exclusive accesses require RRESP to be 2 bits wide (minimum)")

            if not hasattr(self, "bresp") or len(self.bresp) < 2:
                raise ValueError("AXI Exclusive accesses require BRESP to be 2 bits wide (minimum)")

    def set(self, name : str, value : int) -> None:
        """
        Set the value of a signal (if signal exists)

        :param name: The name of the signal
        :type name: str
        :param value: The value to set
        :type value: int
        :return: None
        """
        signal = getattr(self, name, None)
        if signal is not None:
            signal.value = value

    def get(self, name : str, default : Any = None) -> int:
        """
        Get the value of a signal (if signal exists)

        :param name: The name of the signal
        :type name: str
        :param default: The default value to return if signal does not exist
        :type default: Any
        :return: The value of the signal or the default value
        :rtype: int
        """
        signal = getattr(self, name, None)
        if signal is not None:
            return signal.value
        return default

__all__ = ["Interface"]
