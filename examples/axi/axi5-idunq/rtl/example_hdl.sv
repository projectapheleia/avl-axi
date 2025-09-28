module example_hdl();


    logic clk, rst_n;

    axi_if#(.ADDR_WIDTH(16),
            .DATA_WIDTH(32),
            .ID_W_WIDTH(4),
            .ID_R_WIDTH(4),
            .RRESP_WIDTH(2),
            .BRESP_WIDTH(2),
            .WSTRB_Present(1),
            .LEN_Present(1),
            .SIZE_Present(1),
            .BURST_Present(1),
            .WLAST_Present(1),
            .RLAST_Present(1),
            .Unique_ID_Support(1)) axi_if();

    assign axi_if.aclk = clk;
    assign axi_if.aresetn = rst_n;

endmodule : example_hdl
