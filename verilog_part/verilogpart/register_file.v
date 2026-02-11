module register_file (
    input clk,
    input reset,
    input reg_write,
    input [2:0] read_reg1,
    input [2:0] read_reg2,
    input [2:0] write_reg,
    input [15:0] write_data,
    output [15:0] read_data1,
    output [15:0] read_data2
);

    reg [15:0] registers [7:0];
    integer i;

    // Initialize/Reset
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            for (i = 0; i < 8; i = i + 1) begin
                registers[i] <= 16'd0;
            end
            // Specific initialization if needed per python spec:
            // $sp (reg 6) = 0xFFF
            registers[6] <= 16'h0FFF; 
        end else if (reg_write && (write_reg != 3'd0)) begin
            // Write only if RegWrite is high and not writing to $zero (Reg 0)
            registers[write_reg] <= write_data;
        end
    end

    // Asynchronous Read
    // If reading Reg 0, always return 0 (Hardwired $zero)
    // Note: Python spec says $t0 is reg 1, $zero is reg 0.
    assign read_data1 = (read_reg1 == 3'd0) ? 16'd0 : registers[read_reg1];
    assign read_data2 = (read_reg2 == 3'd0) ? 16'd0 : registers[read_reg2];

endmodule
