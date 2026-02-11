module cpu (
    input clk,
    input reset
);

    // ===========================================
    // WIRE DEFINITIONS
    // ===========================================

    // --- IF Stage ---
    wire [15:0] pc_current;
    wire [15:0] pc_next, pc_next_seq; // pc_next_seq = pc + 1
    wire [31:0] instruction;
    wire pc_write; // From Hazard Detection
    wire if_id_write; // From Hazard Detection
    wire if_flush; // For Branch/Jump
    
    // --- IF/ID Pipeline Register Outputs ---
    wire [15:0] if_id_pc_plus_1;
    wire [31:0] if_id_instr;

    // --- ID Stage ---
    // Instruction Fields
    wire [5:0] opcode = if_id_instr[31:26];
    wire [4:0] rs = if_id_instr[25:21]; // Source 1
    wire [4:0] rt = if_id_instr[20:16]; // Source 2 / Dest (IType)
    wire [4:0] rd = if_id_instr[15:11]; // Dest (RType)
    wire [5:0] funct = if_id_instr[5:0];
    wire [15:0] immediate = if_id_instr[15:0];

    // Control Signals
    wire reg_dst, branch_eq, branch_ne, mem_read, mem_to_reg;
    wire [2:0] alu_op;
    wire mem_write, alu_src, reg_write, jump, jump_reg, LinkWrite;
    wire [15:0] link_reg_out; // Output from Link Register
    
    // Register File
    // MUX for Read Register 1 (For syscalls or normal? Standard MIPS uses rs)
    // Note: Our instruction format has 5-bit register indices. Register file takes 3-bit.
    // We will truncate or assume 3-bit LSBs are used if regs are 0-7.
    // Python code maps $t0=1, $sp=6, etc. Fits in 3 bits.
    wire [15:0] read_data1, read_data2;
    
    // Sign Extend
    wire [15:0] sign_ext_imm;

    // Hazard Detection
    wire stall;

    // Branch/Jump Logic (ID Stage resolution for Jump, EX for Branch)
    wire [15:0] jump_target_address; 
    
    // ID/EX Pipeline Register Inputs/Outputs
    // Control signals to pass
    // WB: RegWrite, MemToReg
    // M: BranchEQ, BranchNE, MemRead, MemWrite
    // EX: RegDst, ALUOp, ALUSrc
    
    // Outputs
    wire id_ex_reg_write, id_ex_mem_to_reg;
    wire id_ex_branch_eq, id_ex_branch_ne, id_ex_mem_read, id_ex_mem_write;
    wire id_ex_reg_dst, id_ex_alu_src;
    wire [2:0] id_ex_alu_op;
    wire [15:0] id_ex_pc_plus_1;
    wire [15:0] id_ex_read_data1, id_ex_read_data2;
    wire [15:0] id_ex_sign_ext_imm;
    wire [4:0] id_ex_rs, id_ex_rt, id_ex_rd;
    // JAL/JR handling signals might need passing if done in EX, but we try ID for Jump.
    // Spec says "Branch alındığında IF/ID flush". Wait, user says "Branch Donanımı: ALU zero + branch AND logic".
    // This implies Branch decision is in EX.
    
    // --- EX Stage ---
    wire [15:0] alu_in_a, alu_in_b;
    wire [15:0] alu_result;
    wire alu_zero;
    wire [4:0] write_reg_addr_ex; // Destination register address selected
    wire [1:0] forward_a, forward_b;
    wire [15:0] fwd_data_a, fwd_data_b; // Data after forwarding mux
    
    // Branch Target Calculation
    wire [15:0] branch_target_addr;
    
    // EX/MEM Pipeline Register
    wire ex_mem_reg_write, ex_mem_mem_to_reg;
    wire ex_mem_branch_eq, ex_mem_branch_ne, ex_mem_mem_read, ex_mem_mem_write;
    wire ex_mem_zero;
    wire [15:0] ex_mem_alu_result, ex_mem_write_data_mem; // data to write to mem
    wire [4:0] ex_mem_dest_reg;
    wire [15:0] ex_mem_branch_target; // Not strictly needed if branch applied in EX, but if MEM...
    // Requirement implies Branch is logic, usually applied to PC. Wiring back from EX to PC.

    // --- MEM Stage ---
    wire [15:0] mem_read_data;
    wire branch_taken;

    // MEM/WB Pipeline Register
    wire mem_wb_reg_write, mem_wb_mem_to_reg;
    wire [15:0] mem_wb_read_data, mem_wb_alu_result;
    wire [4:0] mem_wb_dest_reg;

    // --- WB Stage ---
    wire [15:0] write_back_data;


    // ===========================================
    // MODULE INSTANTIATIONS & LOGIC
    // ===========================================

    // --- 1. PC & Instruction Fetch ---
    
    // PC + 1
    assign pc_next_seq = pc_current + 16'd2;

    // PC Mux Logic
    // Priority: Reset > Branch > Jump > JAL > JR > Next
    // However, Jump/JAL/JR are control signals from ID. Branch is from EX.
    // If Branch matches in EX, it overwrites everything (because it happened earlier in instruction stream effectively? No, Branch is conditional).
    // Actually, if we are in EX and Branch is taken, we flush ID. Jumps in ID are for *later* instructions.
    // Wait, typical MIPS:
    // IF: Fetch
    // ID: Decode, Jump taken here (flush IF).
    // EX: Branch decision here (flush IF, ID).
    
    // PC Mux Logic
    // Priority: Reset > Branch > Jump > JAL > JR > Next
    
    assign jump_target_address = if_id_instr[15:0];

    assign pc_next = (branch_taken === 1'b1) ? branch_target_addr : // Branch from EX
                     (jump === 1'b1 || LinkWrite === 1'b1) ? jump_target_address :  // J/JAL from ID
                     (jump_reg === 1'b1)     ? read_data1 :         // JR from ID
                                               pc_next_seq;         // Next Sequential

    // PC Module
    pc pc_module (
        .clk(clk),
        .reset(reset),
        .pc_write(pc_write), // Hazard detection
        .new_pc(pc_next),
        .pc_out(pc_current)
    );

    // Instruction Memory
    instruction_memory instr_mem (
        .pc(pc_current),
        .instruction(instruction)
    );

    // Link Register
    link_register link_reg (
        .clk(clk),
        .reset(reset),
        .link_write(LinkWrite),
        .pc_in(pc_next_seq), // Capture PC+1 (or +2 per diagram, but +1 for logic)
        .link_addr(link_reg_out)
    );

    // Hazard Detection Unit
    // Detect Load-Use hazard to stall PC and IF/ID
    hazard_detection hazard_unit (
        .id_ex_rt(id_ex_rt[2:0]), // Truncating to 3 bits for RegFile
        .id_ex_mem_read(id_ex_mem_read),
        .if_id_rs(rs[2:0]),
        .if_id_rt(rt[2:0]),
        .stall(stall)
    );

    assign pc_write = !stall;
    assign if_id_write = !stall;
    
    // Flush Logic
    // Flush IF/ID if Branch Taken (EX) or Jump (ID)
    // Note: If Stall is active, we validly keep old IF/ID. 
    // If Branch is taken, we must Flush regardless.
    // If Jump is taken, we Flush IF/ID.
    assign if_flush = branch_taken || jump || LinkWrite || jump_reg;

    // IF/ID Pipeline Register
    // Using a custom instance or generic pipeline_reg. 
    // The existing pipeline_reg.v is generic single width. We need composite or multiple.
    // Let's instantiate multiple for PC and Instr.
    
    pipeline_reg #(.WIDTH(16)) if_id_pc_reg (
        .clk(clk), .reset(reset), .flush(if_flush), .enable(if_id_write),
        .in(pc_next_seq), .out(if_id_pc_plus_1)
    );
    pipeline_reg #(.WIDTH(32)) if_id_instr_reg (
        .clk(clk), .reset(reset), .flush(if_flush), .enable(if_id_write),
        .in(instruction), .out(if_id_instr)
    );


    // --- 2. Instruction Decode (ID) ---

    // Control Unit
    control_unit ctrl_unit (
        .opcode(opcode),
        .funct(funct),
        .reg_dst(reg_dst),
        .branch_eq(branch_eq),
        .branch_ne(branch_ne),
        .mem_read(mem_read),
        .mem_to_reg(mem_to_reg),
        .alu_op(alu_op),
        .mem_write(mem_write),
        .alu_src(alu_src),
        .reg_write(reg_write),
        .jump(jump),
        .jump_reg(jump_reg),
        .LinkWrite(LinkWrite)
    );

    // Register File Writes (from WB stage)
    // JAL Handling: If JAL, we write PC+1 to $ra (Reg 7).
    // This is often handled in WB, but JAL implies writing *now* or carrying PC+1 to WB.
    // Standard MIPS JAL writes in WB stage.
    // So we need to pass PC+1 down the pipeline or select it as WriteData in WB.
    
    // Register File
    register_file reg_file (
        .clk(clk),
        .reset(reset),
        .reg_write(mem_wb_reg_write), // Write enable from WB
        .read_reg1(rs[2:0]),
        .read_reg2(rt[2:0]),
        .write_reg(mem_wb_dest_reg[2:0]), // Write Addr from WB
        .write_data(write_back_data),    // Write Data from WB
        .read_data1(read_data1),
        .read_data2(read_data2)
    );

    // Sign Extend
    sign_extend sext (
        .in(immediate),
        .out(sign_ext_imm)
    );

    // ID Logic for Stall/Flush
    // If stall, we want to zero out control signals (bubble) to ID/EX
    wire id_flush_signals = stall || branch_taken; 
    // Note: Branch taken in EX flushes ID/EX too. Jump doesn't need to flush ID/EX because Jump IS in ID, 
    // but the instruction *after* jump (in IF) needs flushing (handled by if_flush).
    // Wait, if Jump is in ID, the current instruction is the Jump. It doesn't propagate execution to EX usually?
    // MIPS: Range of J is done. No EX/MEM action except for JAL reg write which goes through.
    // But simplistic CPU: Pass simplified NOPs if stall.

    // ID/EX Pipeline Register
    // We group signals or use multiple regs. Using a macro-like instantiation for brevity would be nice, 
    // but explicit is better here.

    // Control Signals Bubble Mux
    wire [15:0] cals_wb_m_ex; // Concatenated signals for debug/waveform visibility
    assign cals_wb_m_ex = {3'b0, reg_dst, alu_op, alu_src, branch_eq, branch_ne, mem_read, mem_write, reg_write, mem_to_reg};
    // Let's just mux input to pipeline reg.
    
    // EX Control
    pipeline_reg #(.WIDTH(1)) id_ex_reg_dst_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(reg_dst), .out(id_ex_reg_dst));
    pipeline_reg #(.WIDTH(3)) id_ex_alu_op_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(alu_op), .out(id_ex_alu_op));
    pipeline_reg #(.WIDTH(1)) id_ex_alu_src_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(alu_src), .out(id_ex_alu_src));
    
    // M Control
    pipeline_reg #(.WIDTH(1)) id_ex_branch_eq_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(branch_eq), .out(id_ex_branch_eq));
    pipeline_reg #(.WIDTH(1)) id_ex_branch_ne_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(branch_ne), .out(id_ex_branch_ne));
    pipeline_reg #(.WIDTH(1)) id_ex_mem_read_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(mem_read), .out(id_ex_mem_read));
    pipeline_reg #(.WIDTH(1)) id_ex_mem_write_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(mem_write), .out(id_ex_mem_write));
    
    // WB Control
    // Special handling for JAL: JAL sets RegWrite and RegDst=1? Or Link reg.
    // In ID, if JAL is high, we might want to flag downstream to write PC+1.
    // Let's pass 'link' signal or repurpose MemToReg/RegDst.
    // User request: "jal için $ra register'a PC+1 yazma... Write-back mux'ta JAL desteği".
    // So we pass 'jal' signal down.
    wire id_ex_LinkWrite;
    pipeline_reg #(.WIDTH(1)) id_ex_LinkWrite_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(LinkWrite), .out(id_ex_LinkWrite));
    wire [15:0] id_ex_link_reg_out;
    pipeline_reg #(.WIDTH(16)) id_ex_link_reg_out_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(link_reg_out), .out(id_ex_link_reg_out));
    pipeline_reg #(.WIDTH(1)) id_ex_reg_write_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(reg_write), .out(id_ex_reg_write));
    pipeline_reg #(.WIDTH(1)) id_ex_mem_to_reg_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(mem_to_reg), .out(id_ex_mem_to_reg));

    // Data
    pipeline_reg #(.WIDTH(16)) id_ex_pc_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(if_id_pc_plus_1), .out(id_ex_pc_plus_1));
    pipeline_reg #(.WIDTH(16)) id_ex_r1_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(read_data1), .out(id_ex_read_data1));
    pipeline_reg #(.WIDTH(16)) id_ex_r2_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(read_data2), .out(id_ex_read_data2));
    pipeline_reg #(.WIDTH(16)) id_ex_imm_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(sign_ext_imm), .out(id_ex_sign_ext_imm));
    pipeline_reg #(.WIDTH(5)) id_ex_rs_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(rs), .out(id_ex_rs));
    pipeline_reg #(.WIDTH(5)) id_ex_rt_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(rt), .out(id_ex_rt));
    pipeline_reg #(.WIDTH(5)) id_ex_rd_r (.clk(clk), .reset(reset), .flush(id_flush_signals), .enable(1'b1), .in(rd), .out(id_ex_rd));


    // --- 3. Execute (EX) ---

    // Forwarding Unit
    forwarding_unit fwd_unit (
        .id_ex_rs(id_ex_rs[2:0]),
        .id_ex_rt(id_ex_rt[2:0]),
        .ex_mem_rd(ex_mem_dest_reg[2:0]),
        .ex_mem_reg_write(ex_mem_reg_write),
        .mem_wb_rd(mem_wb_dest_reg[2:0]),
        .mem_wb_reg_write(mem_wb_reg_write),
        .forward_a(forward_a),
        .forward_b(forward_b)
    );

    // ALU Muxes
    // Forward A
    assign fwd_data_a = (forward_a == 2'b10) ? ex_mem_alu_result :
                        (forward_a == 2'b01) ? write_back_data : // Forward from WB stage (which is Mem/WB output logically or computed data)
                        (forward_a == 2'b11) ? 16'd0 : // Unused
                         id_ex_read_data1;

    // Forward B
    assign fwd_data_b = (forward_b == 2'b10) ? ex_mem_alu_result :
                        (forward_b == 2'b01) ? write_back_data :
                         id_ex_read_data2;

    // ALU Source Mux (Immediate or Register B)
    assign alu_in_a = fwd_data_a;
    assign alu_in_b = (id_ex_alu_src) ? id_ex_sign_ext_imm : fwd_data_b;

    // ALU
    alu alu_inst (
        .a(alu_in_a),
        .b(alu_in_b),
        .alu_control(id_ex_alu_op),
        .result(alu_result),
        .zero(alu_zero)
    );

    // Destination Register Mux
    // If JAL is active, we force dest to $ra (Reg 7).
    // Note: JAL is usually I or J type. If JAL was decoded in ID, we need to ensure write target is correct.
    // In control unit, JAL sets reg_write=1.
    // We can handle JAL dest selection here or in ID.
    // Let's assume standard R/I dest selection, and overrule if JAL.
    wire [4:0] dest_mux_out = (id_ex_reg_dst) ? id_ex_rd : id_ex_rt;
    assign write_reg_addr_ex = (id_ex_LinkWrite) ? 5'd7 : dest_mux_out; 

    // Branch Address Calculation
    // PC+1 is already in id_ex_pc_plus_1
    assign branch_target_addr = id_ex_pc_plus_1 + id_ex_sign_ext_imm;

    // Branch Decision (EX Stage)
    assign branch_taken = (id_ex_branch_eq && alu_zero) || (id_ex_branch_ne && !alu_zero);


    // EX/MEM Pipeline Register
    wire ex_flush = branch_taken; // If branch taken, flush EX/MEM? No, valid result needs to PROPAGATE?
    // Wait; if branch taken, next instructions (IF/ID, ID/EX) are wrong. The Branch instruction ITSELF is finishing EX.
    // It shouldn't write to memory or reg? Branches don't write.
    // So we don't flush EX/MEM. We flush IF/ID and ID/EX.

    // Signals passing
    pipeline_reg #(.WIDTH(1)) ex_mem_reg_write_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(id_ex_reg_write), .out(ex_mem_reg_write));
    pipeline_reg #(.WIDTH(1)) ex_mem_mem_to_reg_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(id_ex_mem_to_reg), .out(ex_mem_mem_to_reg));
    pipeline_reg #(.WIDTH(1)) ex_mem_mem_read_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(id_ex_mem_read), .out(ex_mem_mem_read));
    pipeline_reg #(.WIDTH(1)) ex_mem_mem_write_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(id_ex_mem_write), .out(ex_mem_mem_write));
    
    // Pass Branch Signals to MEM (even if logic is in EX_
    pipeline_reg #(.WIDTH(1)) ex_mem_branch_eq_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(id_ex_branch_eq), .out(ex_mem_branch_eq));
    pipeline_reg #(.WIDTH(1)) ex_mem_branch_ne_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(id_ex_branch_ne), .out(ex_mem_branch_ne));
    
    // Restore Zero and Branch Target for Waveform Visibility
    pipeline_reg #(.WIDTH(1)) ex_mem_zero_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(alu_zero), .out(ex_mem_zero));
    pipeline_reg #(.WIDTH(16)) ex_mem_branch_target_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(branch_target_addr), .out(ex_mem_branch_target));
    
    // JAL support: Pass PC+1 to MEM?
    // If JAL, we need to write PC+1.
    // We can mux ALU result with PC+1 here to save a pipeline reg width, or send separate.
    wire ex_mem_LinkWrite;
    pipeline_reg #(.WIDTH(1)) ex_mem_LinkWrite_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(id_ex_LinkWrite), .out(ex_mem_LinkWrite));
    wire [15:0] ex_result_to_mem = (id_ex_LinkWrite) ? id_ex_link_reg_out : alu_result; // Use Link Register output if LinkWrite

    pipeline_reg #(.WIDTH(16)) ex_mem_alu_res_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(ex_result_to_mem), .out(ex_mem_alu_result));
    pipeline_reg #(.WIDTH(16)) ex_mem_wdata_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(fwd_data_b), .out(ex_mem_write_data_mem)); // Store Value
    pipeline_reg #(.WIDTH(5)) ex_mem_dest_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(write_reg_addr_ex), .out(ex_mem_dest_reg));


    // --- 4. Memory (MEM) ---

    // Data Memory
    data_memory dmem (
        .clk(clk),
        .address(ex_mem_alu_result),
        .write_data(ex_mem_write_data_mem),
        .mem_write(ex_mem_mem_write),
        .mem_read(ex_mem_mem_read),
        .read_data(mem_read_data)
    );

    // MEM/WB Pipeline Register
    pipeline_reg #(.WIDTH(1)) mem_wb_reg_write_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(ex_mem_reg_write), .out(mem_wb_reg_write));
    pipeline_reg #(.WIDTH(1)) mem_wb_mem_to_reg_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(ex_mem_mem_to_reg), .out(mem_wb_mem_to_reg));
    
    pipeline_reg #(.WIDTH(16)) mem_wb_rdata_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(mem_read_data), .out(mem_wb_read_data));
    pipeline_reg #(.WIDTH(16)) mem_wb_alu_res_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(ex_mem_alu_result), .out(mem_wb_alu_result));
    pipeline_reg #(.WIDTH(5)) mem_wb_dest_r (.clk(clk), .reset(reset), .flush(1'b0), .enable(1'b1), .in(ex_mem_dest_reg), .out(mem_wb_dest_reg));


    // --- 5. Write Back (WB) ---

    // Mux for Write Data
    // Note: If JAL, we passed PC+1 via ALU Result path.
    // If MemToReg (LW), choose MemData. Else ALU Result.
    assign write_back_data = (mem_wb_mem_to_reg) ? mem_wb_read_data : mem_wb_alu_result;

endmodule
