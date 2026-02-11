module pipeline_reg #(parameter WIDTH = 32) (
    input clk,
    input reset,
    input flush,
    input enable, // 0 to stall (keep value), 1 to update
    input [WIDTH-1:0] in,
    output reg [WIDTH-1:0] out
);

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            out <= 0;
        end else if (flush) begin
            out <= 0;
        end else if (enable) begin
            out <= in;
        end
    end

endmodule
