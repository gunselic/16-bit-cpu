module forwarding_unit (
    input [2:0] id_ex_rs,
    input [2:0] id_ex_rt,
    input [2:0] ex_mem_rd,
    input ex_mem_reg_write,
    input [2:0] mem_wb_rd,
    input mem_wb_reg_write,
    output reg [1:0] forward_a,
    output reg [1:0] forward_b
);

    always @(*) begin
        // Forward A (ALU input 1 / Rs)
        forward_a = 2'b00; // Default: from ID/EX register

        // EX Hazard
        if (ex_mem_reg_write && (ex_mem_rd != 0) && (ex_mem_rd == id_ex_rs)) begin
            forward_a = 2'b10; // Forward from EX/MEM
        end
        // MEM Hazard
        else if (mem_wb_reg_write && (mem_wb_rd != 0) && (mem_wb_rd == id_ex_rs)) begin
            forward_a = 2'b01; // Forward from MEM/WB
        end


        // Forward B (ALU input 2 / Rt)
        forward_b = 2'b00; // Default: from ID/EX register

        // EX Hazard
        if (ex_mem_reg_write && (ex_mem_rd != 0) && (ex_mem_rd == id_ex_rt)) begin
            forward_b = 2'b10; // Forward from EX/MEM
        end
        // MEM Hazard
        else if (mem_wb_reg_write && (mem_wb_rd != 0) && (mem_wb_rd == id_ex_rt)) begin
             forward_b = 2'b01; // Forward from MEM/WB
        end
    end

endmodule
