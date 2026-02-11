module instruction_memory (
    input [15:0] pc,
    output [31:0] instruction
);

    parameter PROGRAM_FILE = "C:/Users/sevvalguni/Desktop/verilogpart/program.mem";

    reg [31:0] memory [0:255];

    integer i;
    initial begin
        for (i = 0; i < 256; i = i + 1) begin
            memory[i] = 32'b0;
        end

        $display("----------------------------------------------------------------");
        $display("MEMORY: Loading instruction memory from file: %s", PROGRAM_FILE);
        
        $readmemh(PROGRAM_FILE, memory);

        if (memory[0] === 32'bx) begin
            $display("MEMORY ERROR: memory[0] is X. Loading probably failed!");
        end else if (memory[0] == 32'b0) begin
            $display("MEMORY WARNING: memory[0] is 0. File might be empty, missing, or start with NOPs.");
        end else begin
            $display("MEMORY SUCCESS: Loaded successfully. First instruction: %h", memory[0]);
        end
        $display("----------------------------------------------------------------");
    end

    assign instruction = memory[pc[8:1]]; 

endmodule