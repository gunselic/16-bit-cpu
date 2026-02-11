module pc (
    input clk,
    input reset,
    input pc_write, // Hazard detection'dan gelen stall sinyali ile kontrol edilir (stall varsa 0)
    input [15:0] new_pc,
    output reg [15:0] pc_out
);

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            pc_out <= 16'd0;
        end else if (pc_write) begin
            pc_out <= new_pc;
        end
    end

endmodule
