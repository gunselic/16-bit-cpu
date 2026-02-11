module hazard_detection (
    input [2:0] id_ex_rt,
    input id_ex_mem_read,
    input [2:0] if_id_rs,
    input [2:0] if_id_rt,
    output reg stall
);

    always @(*) begin
        // Load-Use Hazard Detection
        // If ID/EX is a Load (MemRead=1) and destination (rt) matches IF/ID source (rs or rt)
        if (id_ex_mem_read && ((id_ex_rt == if_id_rs) || (id_ex_rt == if_id_rt))) begin
            stall = 1;
        end else begin
            stall = 0;
        end
    end

endmodule
