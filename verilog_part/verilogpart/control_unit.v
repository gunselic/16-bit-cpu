module control_unit (
    input [5:0] opcode,
    input [5:0] funct,
    output reg reg_dst,
    output reg branch_eq, // BEQ
    output reg branch_ne, // BNE
    output reg mem_read,
    output reg mem_to_reg,
    output reg [2:0] alu_op,
    output reg mem_write,
    output reg alu_src,
    output reg reg_write,
    output reg jump,
    output reg jump_reg,
    output reg LinkWrite       // Formerly jal
);

    // Opcode definitions from instruction.py
    localparam OP_R_TYPE = 6'd0;
    localparam OP_J      = 6'd2;
    localparam OP_JAL    = 6'd3;
    localparam OP_BEQ    = 6'd4;
    localparam OP_BNE    = 6'd5;
    localparam OP_ADDI   = 6'd8;
    localparam OP_LW     = 6'd35;
    localparam OP_SW     = 6'd43;

    // Funct codes from instruction.py
    localparam FUNCT_ADD = 6'd32;
    localparam FUNCT_SUB = 6'd34;
    localparam FUNCT_JR  = 6'd8;

    always @(*) begin
        // Defaults
        reg_dst = 0;
        branch_eq = 0;
        branch_ne = 0;
        mem_read = 0;
        mem_to_reg = 0;
        alu_op = 3'b000;
        mem_write = 0;
        alu_src = 0;
        reg_write = 0;
        jump = 0;
        jump_reg = 0;
        LinkWrite = 0;

        case (opcode)
            OP_R_TYPE: begin
                if (funct == FUNCT_JR) begin
                    jump_reg = 1;
                end else begin
                    reg_dst = 1;
                    reg_write = 1;
                    // Decode ALU Op based on funct (Simplified ALU Control logic inside Control Unit)
                    case (funct)
                        FUNCT_ADD: alu_op = 3'b010; // ADD
                        FUNCT_SUB: alu_op = 3'b110; // SUB
                        default:   alu_op = 3'b000; // Default/AND?
                    endcase
                end
            end
            OP_J: begin
                jump = 1;
            end
            OP_JAL: begin
                jump = 1;
                LinkWrite = 1;
                reg_write = 1;
                // JAL writes to $ra (reg 31 in MIPS, but reg 7 here). 
                // We'll handle register index selection in Datapath.
            end
            OP_BEQ: begin
                branch_eq = 1;
                alu_op = 3'b110; // SUB comparison
            end
            OP_BNE: begin
                branch_ne = 1;
                alu_op = 3'b110; // SUB comparison
            end
            OP_ADDI: begin
                alu_src = 1;
                reg_write = 1;
                alu_op = 3'b010; // ADD
            end
            OP_LW: begin
                alu_src = 1;
                mem_read = 1;
                mem_to_reg = 1;
                reg_write = 1;
                alu_op = 3'b010; // ADD for address calc
            end
            OP_SW: begin
                alu_src = 1;
                mem_write = 1;
                alu_op = 3'b010; // ADD for address calc
            end
            default: begin
                reg_dst = 0;
                branch_eq = 0;
                branch_ne = 0;
                mem_read = 0;
                mem_to_reg = 0;
                alu_op = 3'b000;
                mem_write = 0;
                alu_src = 0;
                reg_write = 0;
                jump = 0;
                jump_reg = 0;
                LinkWrite = 0;
            end
        endcase
    end

endmodule
