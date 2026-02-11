module alu (
    input [15:0] a,
    input [15:0] b,
    input [2:0] alu_control,
    output reg [15:0] result,
    output zero
);

    // ALU Control Signals (based on standard MIPS conventions usually, but adapted)
    // 000: AND
    // 001: OR
    // 010: ADD
    // 110: SUB
    // 111: SLT
    // (We will map these in Control Unit)

    always @(*) begin
        case (alu_control)
            3'b000: result = a & b;       // AND
            3'b001: result = a | b;       // OR
            3'b010: result = a + b;       // ADD
            3'b110: result = a - b;       // SUB
            3'b111: result = (a < b) ? 16'd1 : 16'd0; // SLT
            default: result = 16'd0;
        endcase
    end

    assign zero = (result == 16'd0);

endmodule
