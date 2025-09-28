module example_hdl();


    logic clk, rst_n;

    axi_if#(.ADDR_WIDTH(32),
            .DATA_WIDTH(64),
            .ID_W_WIDTH(3),
            .ID_R_WIDTH(3),
            .WSTRB_Present(1),
            .SIZE_Present(1)) axi_if();

    assign axi_if.aclk = clk;
    assign axi_if.aresetn = rst_n;

endmodule : example_hdl
