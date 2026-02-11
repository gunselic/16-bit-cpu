module data_memory (
    input clk,
    input mem_write,
    input mem_read,
    input [15:0] address,
    input [15:0] write_data,
    output reg [15:0] read_data
);

    reg [15:0] memory [255:0];

    always @(posedge clk) begin
        if (mem_write) begin
            memory[address[7:0]] <= write_data;
        end
    end

    always @(*) begin
        if (mem_read) begin
            read_data = memory[address[7:0]];
        end else begin
            read_data = 16'd0;
        end
    end

endmodule
