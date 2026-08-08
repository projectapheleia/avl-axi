// Copyright 2024 Apheleia
//
// Synthetic AXI subordinate touching every channel the manager/subordinate
// drivers quiesce after a handshake:
//   AW/AR/W : RTL drives READY as a legal comb pulse (ready=f(valid)), asserted
//             after valid held 2 cycles. AXI permits READY to depend
//             combinationally on VALID (just not the reverse).
//   B/R     : RTL drives VALID, which AXI forbids depending on ready. So bvalid/
//             rvalid are registered, armed off the registered request grant
//             (robust to the comb pulse collapsing), cleared on valid&&ready.

module example_hdl();

    logic clk, rst_n;

    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, example_hdl);
    end

    axi_if#(.ADDR_WIDTH(32),
            .DATA_WIDTH(64),
            .ID_W_WIDTH(3),
            .ID_R_WIDTH(3),
            .WSTRB_Present(1)) axi_if();

    assign axi_if.aclk = clk;
    assign axi_if.aresetn = rst_n;

    // AW / AR / W ready: comb pulse, high once valid held 2 cycles. The
    // wait-counter is registered; the loop closes through the cocotb driver.

    // AW ready
    logic [3:0] aw_wait;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)                                   aw_wait <= '0;
        else if (axi_if.awvalid && !axi_if.awready)   aw_wait <= aw_wait + 1;
        else if (axi_if.awvalid &&  axi_if.awready)   aw_wait <= '0;
    end
    assign axi_if.awready = (axi_if.awvalid && (aw_wait >= 2));

    // W ready: same comb-pulse shape as AW/AR.
    logic [3:0] w_wait;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)                                 w_wait <= '0;
        else if (axi_if.wvalid && !axi_if.wready)   w_wait <= w_wait + 1;
        else if (axi_if.wvalid &&  axi_if.wready)   w_wait <= '0;
    end
    assign axi_if.wready = (axi_if.wvalid && (w_wait >= 2));

    // AR ready
    logic [3:0] ar_wait;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)                                   ar_wait <= '0;
        else if (axi_if.arvalid && !axi_if.arready)   ar_wait <= ar_wait + 1;
        else if (axi_if.arvalid &&  axi_if.arready)   ar_wait <= '0;
    end
    assign axi_if.arready = (axi_if.arvalid && (ar_wait >= 2));

    // B: registered write response, armed off the registered W-grant, cleared on
    // bvalid&&bready. bvalid does not depend on bready.
    logic w_done, w_accept;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            w_done   <= 1'b0;
            w_accept <= 1'b0;
        end else begin
            w_accept <= 1'b0;
            if (!w_done && w_wait == 4'd2) begin
                w_done   <= 1'b1;
                w_accept <= 1'b1;
            end
        end
    end

    logic [3:0] b_wait;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            b_wait        <= '0;
            axi_if.bvalid <= 1'b0;
        end else if (w_accept) begin
            b_wait <= 4'd1;
        end else if (b_wait != 0) begin
            b_wait <= b_wait + 1;
            if (b_wait == 4'd2)
                axi_if.bvalid <= 1'b1;
            if (axi_if.bvalid && axi_if.bready) begin
                axi_if.bvalid <= 1'b0;
                b_wait        <= '0;
            end
        end
    end
    assign axi_if.bid   = '0;
    assign axi_if.bresp = '0;

    // R: registered single-beat read response, armed off the registered AR-grant,
    // cleared on rvalid&&rready. rvalid does not depend on rready.
    logic ar_done, ar_accept;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ar_done   <= 1'b0;
            ar_accept <= 1'b0;
        end else begin
            ar_accept <= 1'b0;
            if (!ar_done && ar_wait == 4'd2) begin
                ar_done   <= 1'b1;
                ar_accept <= 1'b1;
            end
        end
    end

    logic [3:0] r_wait;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            r_wait        <= '0;
            axi_if.rvalid <= 1'b0;
        end else if (ar_accept) begin
            r_wait <= 4'd1;
        end else if (r_wait != 0) begin
            r_wait <= r_wait + 1;
            if (r_wait == 4'd2)
                axi_if.rvalid <= 1'b1;
            if (axi_if.rvalid && axi_if.rready) begin
                axi_if.rvalid <= 1'b0;
                r_wait        <= '0;
            end
        end
    end
    assign axi_if.rlast = 1'b0;   // RLAST_Present=0: must stay low
    assign axi_if.rdata = 64'hDEAD_BEEF_CAFE_F00D;
    assign axi_if.rid   = '0;
    assign axi_if.rresp = '0;

endmodule : example_hdl
