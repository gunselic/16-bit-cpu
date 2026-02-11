`timescale 1ns / 1ps

module tb_cpu;

    // Inputs
    reg clk;
    reg reset;

    // Instantiate the Unit Under Test (UUT)
    cpu uut (
        .clk(clk), 
        .reset(reset)
    );

    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // 10ns period -> 100MHz
    end

    initial begin
        // Initialize Inputs
        reset = 1;

        // VCD Dump for Waveforms
        $dumpfile("cpu_wave.vcd");
        $dumpvars(0, tb_cpu);

        // Wait 100 ns for global reset to finish
        #100;
        reset = 0;      
        
        // Let it run for 1000 ns
        #1000;
        
        $finish;
    end
    
    // Optional: Monitor PC changes
    always @(posedge clk) begin
        if (!reset)
            $display("Time: %d, PC: %h, Instr: %h", $time, uut.pc_current, uut.instruction);
    end

endmodule
