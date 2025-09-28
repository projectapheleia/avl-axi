// Copyright 2025 Apheleia
//
// Description:
// Apheleia Verification Library AXI5 Interface
// As defined in ARM AMBA AXI Protocol Specification (IHI0022K)

`define AVL_AXI5_IMPL_CHECK(cond, signal) \
if (``cond`` == 1) begin : ``signal``_cond \
    initial begin \
        #0.1; \
        @(``signal``) $error("%m: %s not supported in configuration", `"signal`");\
    end \
end : ``signal``_cond

`define AVL_AXI5_UNSUPPORTED(cond) \
initial begin \
    if (``cond``) $error("%m: Unsupported Configuration : contact avl@projectapheleia.net to discuss"); \
end


interface axi_if #(
    parameter string CLASSIFICATION                = "AXI",
    parameter int    VERSION                       = 5,

    // Widths
    parameter int ADDR_WIDTH                       = 32,
    parameter int ARSNOOP_WIDTH                    = 0,
    parameter int AWCMO_WIDTH                      = 0,
    parameter int AWSNOOP_WIDTH                    = 0,
    parameter int BRESP_WIDTH                      = 0,
    parameter int DATA_WIDTH                       = 32,
    parameter int ID_R_WIDTH                       = 0,
    parameter int ID_W_WIDTH                       = 0,
    parameter int LOOP_R_WIDTH                     = 0,
    parameter int LOOP_W_WIDTH                     = 0,
    parameter int MECID_WIDTH                      = 0,
    parameter int MPAM_WIDTH                       = 0,
    parameter int RCHUNKNUM_WIDTH                  = 0,
    parameter int RCHUNKSTRB_WIDTH                 = 0,
    parameter int RRESP_WIDTH                      = 0,
    parameter int SECSID_WIDTH                     = 0,
    parameter int SID_WIDTH                        = 0,
    parameter int SSID_WIDTH                       = 0,
    parameter int SUBSYSID_WIDTH                   = 0,
    parameter int USER_DATA_WIDTH                  = 0,
    parameter int USER_REQ_WIDTH                   = 0,
    parameter int USER_RESP_WIDTH                  = 0,

    // Feature enable parameters
    parameter bit Atomic_Transactions              = 0,    // True, False
    parameter bit Busy_Support                     = 0,    // True, False
    parameter bit BURST_Present                    = 0,    // True, False
    parameter bit CACHE_Present                    = 0,    // True, False
    parameter int Cache_Line_Size                  = 0,    // 0, 16, 32, 64, 128, 256, 512, 1024, 2048
    parameter string Cache_Stash_Transactions      = "False", // True, Basic, False
    parameter bit CMO_On_Read                      = 0,    // True, False
    parameter bit CMO_On_Write                     = 0,    // True, False
    parameter bit Coherency_Connection_Signals     = 0,    // True, False
    parameter bit Consistent_DECERR                = 0,    // True, False
    parameter bit DeAllocation_Transactions        = 0,    // True, False
    parameter bit Device_Normal_Independence       = 0,    // True, False
    parameter string DVM_Message_Support           = "False", // Receiver, False
    parameter bit DVM_v8                           = 0,    // True, False
    parameter bit DVM_v8_1                         = 0,    // True, False
    parameter bit DVM_v8_4                         = 0,    // True, False
    parameter bit DVM_v9_2                         = 0,    // True, False
    parameter bit Exclusive_Accesses               = 0,    // True, False
    parameter bit Fixed_Burst_Disable              = 0,    // True, False
    parameter bit InvalidateHint_Transaction       = 0,    // True, False
    parameter bit LEN_Present                      = 0,    // True, False
    parameter bit Loopback_Signals                 = 0,    // True, False
    parameter int Max_Transaction_Bytes            = 4096, // 64, 128, 256, 512, 1024, 2048, 4096
    parameter bit MEC_Support                      = 0,    // True, False
    parameter bit MMUFLOW_Present                  = 0,    // True, False
    parameter string MPAM_Support                  = "False", // MPAM_9_1, MPAM_12_1, False
    parameter string MTE_Support                   = "False", // Standard, Simplified, Basic, False
    parameter bit Multi_Copy_Atomicity             = 0,    // True, False
    parameter bit NSAccess_Identifiers             = 0,    // True, False
    parameter bit Ordered_Write_Observation        = 0,    // True, False
    parameter bit PBHA_Support                     = 0,    // True, False
    parameter bit Persist_CMO                      = 0,    // True, False
    parameter bit Poison                           = 0,    // True, False
    parameter bit Prefetch_Transaction             = 0,    // True, False
    parameter bit PROT_Present                     = 0,    // True, False
    parameter bit QoS_Accept                       = 0,    // True, False
    parameter bit QOS_Present                      = 0,    // True, False
    parameter bit Read_Data_Chunking               = 0,    // True, False
    parameter bit Read_Interleaving_Disabled       = 0,    // True, False
    parameter bit REGION_Present                   = 0,    // True, False
    parameter bit Regular_Transactions_Only        = 0,    // True, False
    parameter bit RLAST_Present                    = 0,    // True, False
    parameter bit RME_Support                      = 0,    // True, False
    parameter bit Shareable_Cache_Support          = 0,    // True, False
    parameter bit Shareable_Transactions           = 0,    // True, False
    parameter bit SIZE_Present                     = 0,    // True, False
    parameter bit STASHLPID_Present                = 0,    // True, False
    parameter bit STASHNID_Present                 = 0,    // True, False
    parameter bit Trace_Signals                    = 0,    // True, False
    parameter bit Unique_ID_Support                = 0,    // True, False
    parameter bit UnstashTranslation_Transaction   = 0,    // True, False
    parameter string Untranslated_Transactions     = "False", // v3, v2, v1, True, False
    parameter bit Wakeup_Signals                   = 0,    // True, False
    parameter bit WLAST_Present                    = 0,    // True, False
    parameter bit Write_Plus_CMO                   = 0,    // True, False
    parameter bit WriteDeferrable_Transaction      = 0,    // True, False
    parameter bit WriteNoSnoopFull_Transaction     = 0,    // True, False
    parameter bit WriteZero_Transaction            = 0,    // True, False
    parameter bit WSTRB_Present                    = 0     // True, False
    )();

    // Derived parameters
    localparam STRB_WIDTH = int'(DATA_WIDTH/8);
    localparam RUSER_WIDTH = int'(USER_DATA_WIDTH + USER_RESP_WIDTH);
    localparam CMO_WIDTH = (CMO_On_Write == 0) ? 0 : (RME_Support == 0) ? 2 : 3;
    localparam TAG_WIDTH = int'($ceil(DATA_WIDTH/128)*4);
    localparam TAGUPDATE_WIDTH = int'(TAG_WIDTH / 4);
    localparam POISON_WIDTH = int'($ceil(DATA_WIDTH/64));

    // Clock and Reset
    logic                                                    aclk;
    logic                                                    aresetn;

    // Write Address Channel (AW)
    logic                                                    awvalid;
    logic                                                    awready;
    logic [ID_W_WIDTH > 0 ? ID_W_WIDTH-1 : 0 :0]             awid;
    logic [ADDR_WIDTH-1:0]                                   awaddr;
    logic [3:0]                                              awregion;
    logic [7:0]                                              awlen;
    logic [2:0]                                              awsize;
    logic [1:0]                                              awburst;
    logic                                                    awlock;
    logic [3:0]                                              awcache;
    logic [2:0]                                              awprot;
    logic                                                    awnse;
    logic [3:0]                                              awqos;
    logic [USER_REQ_WIDTH > 0 ? USER_REQ_WIDTH-1 : 0 :0]     awuser;
    logic [1:0]                                              awdomain;
    logic [AWSNOOP_WIDTH > 0 ? AWSNOOP_WIDTH-1 : 0 :0]       awsnoop;
    logic [11:0]                                             awstashnid;
    logic                                                    awstashniden;
    logic [4:0]                                              awstashlpid;
    logic                                                    awstashlpiden;
    logic [3:0]                                              awtrace;
    logic [LOOP_W_WIDTH > 0 ? LOOP_W_WIDTH-1: 0 :0]          awloop;
    logic                                                    awmmuvalid;
    logic [SECSID_WIDTH > 0 ? SECSID_WIDTH-1 : 0 :0]         awmmusecsid;
    logic [SID_WIDTH > 0 ? SID_WIDTH-1 : 0 :0]               awmmusid;
    logic [SSID_WIDTH > 0 ? SSID_WIDTH-1 : 0 :0]             awmmussidv;
    logic [SSID_WIDTH > 0 ? SSID_WIDTH-1 : 0 :0]             awmmussid;
    logic [1:0]                                              awmmuatst;
    logic [2:0]                                              awmmuflow;
    logic [3:0]                                              awpbha;
    logic [15:0]                                             awmecid;
    logic [3:0]                                              awnsaid;
    logic [SUBSYSID_WIDTH > 0 ? SUBSYSID_WIDTH-1 : 0 :0]     awsubsysid;
    logic [5:0]                                              awatop;
    logic [MPAM_WIDTH > 0 ? MPAM_WIDTH-1 : 0 :0]             awmpam;
    logic                                                    awidunq;
    logic [CMO_WIDTH > 0 ? CMO_WIDTH-1 : 0 :0]               awcmo;
    logic [1:0]                                              awtagop;

    // Write Data Channel (W)
    logic                                                    wvalid;
    logic                                                    wready;
    logic [DATA_WIDTH-1:0]                                   wdata;
    logic [STRB_WIDTH > 0 ? STRB_WIDTH-1 : 0 :0]             wstrb;
    logic [TAG_WIDTH > 0 ? TAG_WIDTH-1 : 0 :0]               wtag;
    logic [TAGUPDATE_WIDTH > 0 ? TAGUPDATE_WIDTH-1 : 0 :0]   wtagupdate;
    logic                                                    wlast;
    logic [USER_DATA_WIDTH > 0 ? USER_DATA_WIDTH-1 : 0 :0]   wuser;
    logic [POISON_WIDTH > 0 ? POISON_WIDTH-1 :0 :0]          wpoison;
    logic [3:0]                                              wtrace;

    // Write Response Channel (B)
    logic                                                    bvalid;
    logic                                                    bready;
    logic [ID_W_WIDTH > 0 ? ID_W_WIDTH-1 : 0 :0]             bid;
    logic                                                    bidunq;
    logic [BRESP_WIDTH > 0 ? BRESP_WIDTH-1 : 0 :0]           bresp;
    logic                                                    bcomp;
    logic                                                    bpersist;
    logic [1:0]                                              btagmatch;
    logic [USER_RESP_WIDTH > 0 ? USER_RESP_WIDTH-1 : 0 :0]   buser;
    logic [3:0]                                              btrace;
    logic [LOOP_W_WIDTH > 0 ? LOOP_W_WIDTH-1 :0 :0]          bloop;
    logic                                                    bbusy;

    // Read Address Channel (AR)
    logic                                                    arvalid;
    logic                                                    arready;
    logic [ID_R_WIDTH > 0 ? ID_R_WIDTH-1 : 0 :0]             arid;
    logic [ADDR_WIDTH-1:0]                                   araddr;
    logic [3:0]                                              arregion;
    logic [7:0]                                              arlen;
    logic [2:0]                                              arsize;
    logic [1:0]                                              arburst;
    logic                                                    arlock;
    logic [3:0]                                              arcache;
    logic [2:0]                                              arprot;
    logic                                                    arnse;
    logic [3:0]                                              arqos;
    logic [USER_REQ_WIDTH > 0 ? USER_REQ_WIDTH-1 : 0 :0]     aruser;
    logic [1:0]                                              ardomain;
    logic [ARSNOOP_WIDTH > 0 ? ARSNOOP_WIDTH-1 : 0 :0]       arsnoop;
    logic [3:0]                                              artrace;
    logic [LOOP_R_WIDTH > 0 ? LOOP_R_WIDTH-1 : 0 :0]         arloop;
    logic                                                    armmuvalid;
    logic [SECSID_WIDTH > 0 ? SECSID_WIDTH-1 : 0 :0]         armmusecsid;
    logic [SID_WIDTH > 0 ? SID_WIDTH-1 : 0 :0]               armmusid;
    logic [SSID_WIDTH > 0 ? SSID_WIDTH-1 : 0 :0]             armmussidv;
    logic [SSID_WIDTH > 0 ? SSID_WIDTH-1 : 0 :0]             armmussid;
    logic [1:0]                                              armmuatst;
    logic [2:0]                                              armmuflow;
    logic [3:0]                                              arpbha;
    logic [15:0]                                             armecid;
    logic [3:0]                                              arnsaid;
    logic [SUBSYSID_WIDTH > 0 ? SUBSYSID_WIDTH-1 : 0 :0]     arsubsysid;
    logic [MPAM_WIDTH > 0 ? MPAM_WIDTH-1 : 0 :0]             armpam;
    logic                                                    archunken;
    logic                                                    aridunq;
    logic [1:0]                                              artagop;

    // Read Data Channel (R)
    logic                                                    rvalid;
    logic                                                    rready;
    logic [ID_R_WIDTH > 0 ? ID_R_WIDTH-1 : 0 :0]             rid;
    logic                                                    ridunq;
    logic [DATA_WIDTH-1:0]                                   rdata;
    logic [TAG_WIDTH > 0 ? TAG_WIDTH-1 : 0 :0]               rtag;
    logic [RRESP_WIDTH > 0 ? RRESP_WIDTH-1 : 0 :0]           rresp;
    logic                                                    rlast;
    logic [RUSER_WIDTH > 0 ? RUSER_WIDTH-1 : 0 :0]           ruser;
    logic [POISON_WIDTH > 0 ? POISON_WIDTH-1 :0 :0]          rpoison;
    logic [3:0]                                              rtrace;
    logic [LOOP_R_WIDTH > 0 ? LOOP_R_WIDTH-1 : 0 :0]         rloop;
    logic                                                    rchunkv;
    logic [RCHUNKNUM_WIDTH > 0 ? RCHUNKNUM_WIDTH-1 : 0 :0]   rchunknum;
    logic [RCHUNKSTRB_WIDTH > 0 ? RCHUNKSTRB_WIDTH-1 : 0 :0] rchunkstrb;
    logic                                                    rbusy;

    // Snoop channels
    logic                                                    acvalid;
    logic                                                    acready;
    logic [ADDR_WIDTH-1 :0]                                  acaddr;
    logic [3:0]                                              acvmidext;
    logic                                                    actrace;
    logic                                                    crvalid;
    logic                                                    crready;
    logic                                                    crtrace;

    // Other Signals
    logic                                                    awakeup;
    logic                                                    acwakeup;
    logic [3:0]                                              varqosaccept;
    logic [3:0]                                              vawqosaccept;
    logic                                                    syscoreq;
    logic                                                    syscoack;

    // Initial assertions
    // Sanity Checks on conflicting / mis-configured parameters
    initial begin
        assert (DATA_WIDTH % 8 == 0) else $error("DATA_WIDTH must be multiple of 8");
        assert (ADDR_WIDTH > 0) else $error("ADDR_WIDTH must be greater than 0");

        if (CACHE_Present)
            assert(Cache_Line_Size inside {16,32,64,128,256,512,1024,2048}) else $error("Cache_Line_Size must be a valid value");
        else
            assert(Cache_Line_Size == 0) else $error("Cache_Line_Size must be 0");

        if (Cache_Stash_Transactions != "False") begin
            assert(!(STASHNID_Present || STASHLPID_Present)) else $error("STASHNID_Present and STASHLPID_Present must be 0");
        end

        if (!(CMO_On_Read || CMO_On_Write))
            assert(!Persist_CMO) else $error("Persist_CMO must be 0");

        if (Consistent_DECERR)
            assert(RRESP_WIDTH > 0) else $error("RRESP_WIDTH must be > 0");

        assert(Max_Transaction_Bytes inside {64, 128, 256, 512, 1024, 2048, 4096}) else $error("Max_Transaction_Bytes must be valid value");

        if (MEC_Support)
            assert(RME_Support) else $error("RME_Support must be 1");

        if (MMUFLOW_Present) begin
            case(Untranslated_Transactions)
                "v2", "v3": ;
                default : $error("Untranslated_Transactions must be v2 or v3");
            endcase
        end

        case(MPAM_Support)
            "MPAM_9_1"  : assert(MPAM_WIDTH == 11) else $error("MPAM_WIDTH must be 11");
            "MPAM_12_1" : assert(MPAM_WIDTH == (14 + int'(RME_Support))) else $error("MPAM_WIDTH must be 14 + RME_Support");
            default     : assert(MPAM_WIDTH == 0) else $error("MPAM_WIDTH must be 0");
        endcase

        if (Prefetch_Transaction || Shareable_Cache_Support || Untranslated_Transactions inside {"v2", "v3"})
            assert(RRESP_WIDTH == 3) else $error("RRESP_WIDTH must be 3");

        if (WriteDeferrable_Transaction || Untranslated_Transactions inside {"v2", "v3"})
            assert(BRESP_WIDTH == 3) else $error("BRESP_WIDTH must be 3");

        if (WriteDeferrable_Transaction || UnstashTranslation_Transaction || InvalidateHint_Transaction)
            assert(AWSNOOP_WIDTH == 5) else $error("AWSNOOP_WIDTH must be 5");
        else if (Shareable_Cache_Support || WriteNoSnoopFull_Transaction || CMO_On_Write || WriteZero_Transaction || (Cache_Stash_Transactions != "False") || UnstashTranslation_Transaction || Prefetch_Transaction)
            assert(AWSNOOP_WIDTH == 4 || AWSNOOP_WIDTH == 5) else $error("AWSNOOP_WIDTH must be 4 or 5");
        else if (Shareable_Cache_Support || DeAllocation_Transactions || CMO_On_Read || (DVM_Message_Support != "False"))
            assert(AWSNOOP_WIDTH == 4) else $error("AWSNOOP_WIDTH must be 4");

        if (Untranslated_Transactions == "False")
            assert(SECSID_WIDTH == 0) else $error("SECSID_WIDTH must be 0");
        else if (!RME_Support)
            assert(SECSID_WIDTH == 1) else $error("SECSID_WIDTH must be 1");
        else
            assert(SECSID_WIDTH == 2) else $error("SECSID_WIDTH must be 2");

        if (Write_Plus_CMO)
            assert(CMO_On_Write == 1) else $error("CMO_On_Write must be 1");

        if (DATA_WIDTH < 32)
            assert(MTE_Support == "False") else $error("MTE_Support must be False");

        if (MTE_Support != "False")
            assert(CACHE_Present == 1) else $error("CACHE_Present must be 1");

        if (DVM_Message_Support != "False")
            assert(Shareable_Transactions) else $error("Shareable_Transactions must be 1");
    end

    // Generate configuration checks
    generate
        // Unsupported
        `AVL_AXI5_UNSUPPORTED((Coherency_Connection_Signals == 1))
        `AVL_AXI5_UNSUPPORTED((Device_Normal_Independence == 1))
        `AVL_AXI5_UNSUPPORTED((DVM_Message_Support != "False"))
        `AVL_AXI5_UNSUPPORTED((DVM_v8 == 1))
        `AVL_AXI5_UNSUPPORTED((DVM_v8_1 == 1))
        `AVL_AXI5_UNSUPPORTED((DVM_v8_4 == 1))
        `AVL_AXI5_UNSUPPORTED((DVM_v9_2 == 1))
        `AVL_AXI5_UNSUPPORTED((MTE_Support != "False"))
        `AVL_AXI5_UNSUPPORTED((Read_Data_Chunking == 1))

        // Write Address Channel
        `AVL_AXI5_IMPL_CHECK((ID_W_WIDTH == 0), awid)
        `AVL_AXI5_IMPL_CHECK((REGION_Present == 0), awregion)
        `AVL_AXI5_IMPL_CHECK((LEN_Present == 0), awlen)
        `AVL_AXI5_IMPL_CHECK((SIZE_Present == 0), awsize)
        `AVL_AXI5_IMPL_CHECK((BURST_Present == 0), awburst)
        `AVL_AXI5_IMPL_CHECK((Exclusive_Accesses == 0), awlock)
        `AVL_AXI5_IMPL_CHECK((CACHE_Present == 0), awcache)
        `AVL_AXI5_IMPL_CHECK((PROT_Present == 0), awprot)
        `AVL_AXI5_IMPL_CHECK((RME_Support == 0), awnse)
        `AVL_AXI5_IMPL_CHECK((QOS_Present == 0), awqos)
        `AVL_AXI5_IMPL_CHECK((USER_REQ_WIDTH == 0), awuser)
        `AVL_AXI5_IMPL_CHECK((Shareable_Transactions == 0), awdomain)
        `AVL_AXI5_IMPL_CHECK((AWSNOOP_WIDTH == 0), awsnoop)
        `AVL_AXI5_IMPL_CHECK((STASHNID_Present == 0), awstashnid)
        `AVL_AXI5_IMPL_CHECK((STASHNID_Present == 0), awstashniden)
        `AVL_AXI5_IMPL_CHECK((STASHLPID_Present == 0), awstashlpid)
        `AVL_AXI5_IMPL_CHECK((STASHLPID_Present == 0), awstashlpiden)
        `AVL_AXI5_IMPL_CHECK((Trace_Signals == 0), awtrace)
        `AVL_AXI5_IMPL_CHECK((Loopback_Signals == 0 || LOOP_W_WIDTH == 0), awloop)
        `AVL_AXI5_IMPL_CHECK((Untranslated_Transactions != "v3"), awmmuvalid)
        `AVL_AXI5_IMPL_CHECK((Untranslated_Transactions == "False" || SECSID_WIDTH == 0), awmmusecsid)
        `AVL_AXI5_IMPL_CHECK((Untranslated_Transactions == "False" || SID_WIDTH == 0), awmmusid)
        `AVL_AXI5_IMPL_CHECK((Untranslated_Transactions == "False" || SSID_WIDTH == 0), awmmussidv)
        `AVL_AXI5_IMPL_CHECK((Untranslated_Transactions == "False" || SSID_WIDTH == 0), awmmussid)
        `AVL_AXI5_IMPL_CHECK((MMUFLOW_Present == 0 || (Untranslated_Transactions != "v1" && Untranslated_Transactions != "True")), awmmuatst)
        `AVL_AXI5_IMPL_CHECK((MMUFLOW_Present == 0 || (Untranslated_Transactions != "v2" && Untranslated_Transactions != "v3")), awmmuflow)
        `AVL_AXI5_IMPL_CHECK((PBHA_Support == 0), awpbha)
        `AVL_AXI5_IMPL_CHECK((MEC_Support == 0), awmecid)
        `AVL_AXI5_IMPL_CHECK((NSAccess_Identifiers == 0), awnsaid)
        `AVL_AXI5_IMPL_CHECK((SUBSYSID_WIDTH == 0), awsubsysid)
        `AVL_AXI5_IMPL_CHECK((Atomic_Transactions == 0), awatop)
        `AVL_AXI5_IMPL_CHECK((MPAM_Support == "False"), awmpam)
        `AVL_AXI5_IMPL_CHECK((Unique_ID_Support == 0), awidunq)
        `AVL_AXI5_IMPL_CHECK((CMO_On_Write == 0), awcmo)
        `AVL_AXI5_IMPL_CHECK((MTE_Support == "False"), awtagop)

        // Write Data Channel
        `AVL_AXI5_IMPL_CHECK((WSTRB_Present == 0), wstrb)
        `AVL_AXI5_IMPL_CHECK((MTE_Support == "False"), wtag)
        `AVL_AXI5_IMPL_CHECK((MTE_Support == "False"), wtagupdate)
        `AVL_AXI5_IMPL_CHECK((WLAST_Present == 0), wlast)
        `AVL_AXI5_IMPL_CHECK((USER_DATA_WIDTH == 0), wuser)
        `AVL_AXI5_IMPL_CHECK((Poison == 0), wpoison)
        `AVL_AXI5_IMPL_CHECK((Trace_Signals == 0), wtrace)

        // Write Response Channel
        `AVL_AXI5_IMPL_CHECK((ID_W_WIDTH == 0), bid)
        `AVL_AXI5_IMPL_CHECK((Unique_ID_Support == 0), bidunq)
        `AVL_AXI5_IMPL_CHECK((BRESP_WIDTH == 0), bresp)
        `AVL_AXI5_IMPL_CHECK(((Persist_CMO == 0 || CMO_On_Write == 0) && MTE_Support != "Standard"), bcomp)
        `AVL_AXI5_IMPL_CHECK((Persist_CMO == 0 || CMO_On_Write == 0), bpersist)
        `AVL_AXI5_IMPL_CHECK((MTE_Support != "Standard"), btagmatch)
        `AVL_AXI5_IMPL_CHECK((USER_RESP_WIDTH == 0), buser)
        `AVL_AXI5_IMPL_CHECK((Trace_Signals == 0), btrace)
        `AVL_AXI5_IMPL_CHECK((Loopback_Signals == 0 || LOOP_W_WIDTH == 0), bloop)
        `AVL_AXI5_IMPL_CHECK((Busy_Support == 0), bbusy)

        // Read Address Channel
        `AVL_AXI5_IMPL_CHECK((ID_R_WIDTH == 0), arid)
        `AVL_AXI5_IMPL_CHECK((REGION_Present == 0), arregion)
        `AVL_AXI5_IMPL_CHECK((LEN_Present == 0), arlen)
        `AVL_AXI5_IMPL_CHECK((SIZE_Present == 0), arsize)
        `AVL_AXI5_IMPL_CHECK((BURST_Present == 0), arburst)
        `AVL_AXI5_IMPL_CHECK((Exclusive_Accesses == 0), arlock)
        `AVL_AXI5_IMPL_CHECK((CACHE_Present == 0), arcache)
        `AVL_AXI5_IMPL_CHECK((PROT_Present == 0), arprot)
        `AVL_AXI5_IMPL_CHECK((RME_Support == 0), arnse)
        `AVL_AXI5_IMPL_CHECK((QOS_Present == 0), arqos)
        `AVL_AXI5_IMPL_CHECK((RUSER_WIDTH == 0), aruser)
        `AVL_AXI5_IMPL_CHECK((Shareable_Transactions == 0), ardomain)
        `AVL_AXI5_IMPL_CHECK((ARSNOOP_WIDTH == 0), arsnoop)
        `AVL_AXI5_IMPL_CHECK((Trace_Signals == 0), artrace)
        `AVL_AXI5_IMPL_CHECK((Loopback_Signals == 0 || LOOP_R_WIDTH == 0), arloop)
        `AVL_AXI5_IMPL_CHECK((Untranslated_Transactions != "v3"), armmuvalid)
        `AVL_AXI5_IMPL_CHECK((Untranslated_Transactions == "False" || SECSID_WIDTH == 0), armmusecsid)
        `AVL_AXI5_IMPL_CHECK((Untranslated_Transactions == "False" || SID_WIDTH == 0), armmusid)
        `AVL_AXI5_IMPL_CHECK((Untranslated_Transactions == "False" || SSID_WIDTH == 0), armmussidv)
        `AVL_AXI5_IMPL_CHECK((Untranslated_Transactions == "False" || SSID_WIDTH == 0), armmussid)
        `AVL_AXI5_IMPL_CHECK((MMUFLOW_Present == 0 || (Untranslated_Transactions != "v1" && Untranslated_Transactions != "True")), armmuatst)
        `AVL_AXI5_IMPL_CHECK((MMUFLOW_Present == 0 || (Untranslated_Transactions != "v2" && Untranslated_Transactions != "v3")), armmuflow)
        `AVL_AXI5_IMPL_CHECK((PBHA_Support == 0), arpbha)
        `AVL_AXI5_IMPL_CHECK((MEC_Support == 0), armecid)
        `AVL_AXI5_IMPL_CHECK((NSAccess_Identifiers == 0), arnsaid)
        `AVL_AXI5_IMPL_CHECK((SUBSYSID_WIDTH == 0), arsubsysid)
        `AVL_AXI5_IMPL_CHECK((MPAM_Support == "False"), armpam)
        `AVL_AXI5_IMPL_CHECK((Read_Data_Chunking == 0), archunken)
        `AVL_AXI5_IMPL_CHECK((Unique_ID_Support == 0), aridunq)
        `AVL_AXI5_IMPL_CHECK((MTE_Support == "False"), artagop)

        // Read Data Channel
        `AVL_AXI5_IMPL_CHECK((ID_R_WIDTH == 0), rid)
        `AVL_AXI5_IMPL_CHECK((Unique_ID_Support == 0), ridunq)
        `AVL_AXI5_IMPL_CHECK((MTE_Support == "False"), rtag)
        `AVL_AXI5_IMPL_CHECK((RRESP_WIDTH == 0), rresp)
        `AVL_AXI5_IMPL_CHECK((RLAST_Present == 0), rlast)
        `AVL_AXI5_IMPL_CHECK((USER_DATA_WIDTH == 0 && USER_RESP_WIDTH == 0), ruser)
        `AVL_AXI5_IMPL_CHECK((Poison == 0), rpoison)
        `AVL_AXI5_IMPL_CHECK((Trace_Signals == 0), rtrace)
        `AVL_AXI5_IMPL_CHECK((Loopback_Signals == 0 || LOOP_R_WIDTH == 0), rloop)
        `AVL_AXI5_IMPL_CHECK((Read_Data_Chunking == 0), rchunkv)
        `AVL_AXI5_IMPL_CHECK((Read_Data_Chunking == 0 || RCHUNKNUM_WIDTH == 0), rchunknum)
        `AVL_AXI5_IMPL_CHECK((Read_Data_Chunking == 0 || RCHUNKSTRB_WIDTH == 0), rchunkstrb)
        `AVL_AXI5_IMPL_CHECK((Busy_Support == 0), rbusy)

        // Snoop Signals
        `AVL_AXI5_IMPL_CHECK((DVM_Message_Support == 0), acvalid)
        `AVL_AXI5_IMPL_CHECK((DVM_Message_Support == 0), acready)
        `AVL_AXI5_IMPL_CHECK((DVM_Message_Support == 0), acaddr)
        `AVL_AXI5_IMPL_CHECK((DVM_Message_Support == 0), acvmidext)
        `AVL_AXI5_IMPL_CHECK((DVM_Message_Support == 0 || Trace_Signals == 0), actrace)

        `AVL_AXI5_IMPL_CHECK((DVM_Message_Support == 0), crvalid)
        `AVL_AXI5_IMPL_CHECK((DVM_Message_Support == 0), crready)
        `AVL_AXI5_IMPL_CHECK((DVM_Message_Support == 0 || Trace_Signals == 0), crtrace)

        `AVL_AXI5_IMPL_CHECK((DVM_Message_Support == 0 || Wakeup_Signals == 0), acwakeup)

        // Other Signals
        `AVL_AXI5_IMPL_CHECK((Wakeup_Signals == 0), awakeup)
        `AVL_AXI5_IMPL_CHECK((QoS_Accept == 0), varqosaccept)
        `AVL_AXI5_IMPL_CHECK((QoS_Accept == 0), vawqosaccept)
        `AVL_AXI5_IMPL_CHECK((Coherency_Connection_Signals == 0), syscoreq)
        `AVL_AXI5_IMPL_CHECK((Coherency_Connection_Signals == 0), syscoack)

    endgenerate

endinterface : axi_if

`undef AVL_AXI5_IMPL_CHECK
