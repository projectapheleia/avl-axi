module example_hdl();


    logic clk, rst_n;

    axi_if#(.ADDR_WIDTH(16),
            .DATA_WIDTH(32),
            .ID_W_WIDTH(4),
            .ID_R_WIDTH(4),
            .RRESP_WIDTH(3),
            .BRESP_WIDTH(3),
            .WSTRB_Present(1),
            .LEN_Present(1),
            .SIZE_Present(1),
            .BURST_Present(1),
            .WLAST_Present(1),
            .RLAST_Present(1),
            .Untranslated_Transactions("v3"),
            .SECSID_WIDTH(1),
            .SID_WIDTH(3),
            .SSID_WIDTH(6)) axi_if();

    assign axi_if.aclk = clk;
    assign axi_if.aresetn = rst_n;

endmodule : example_hdl
