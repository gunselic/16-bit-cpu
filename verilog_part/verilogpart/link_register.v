module link_register (
    input clk,
    input reset,
    input link_write,
    input [15:0] pc_in,
    output reg [15:0] link_addr
);

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            link_addr <= 16'd0;
        end else if (link_write) begin
            link_addr <= pc_in;
        end
    end

endmodule
