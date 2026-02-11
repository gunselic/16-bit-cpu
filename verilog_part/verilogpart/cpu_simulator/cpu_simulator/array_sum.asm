# Array Sum Iteration
# This program sums an array of 3 elements located at memory addresses 0, 1, 2.
# Demonstrates a realistic Load-Use hazard.

# Initialize Array in Memory (Simulated via code for simplicity)
ADDI $t0, $zero, 10
SW   $t0, 0($zero)   # Mem[0] = 10
ADDI $t0, $zero, 20
SW   $t0, 1($zero)   # Mem[1] = 20
ADDI $t0, $zero, 30
SW   $t0, 2($zero)   # Mem[2] = 30

# -- Start Logic --
ADDI $s0, $zero, 0   # Array Index Pointer
ADDI $s1, $zero, 3   # Loop Limit
ADDI $s2, $zero, 0   # Sum Accumulator

Loop:
    LW   $t3, 0($s0)     # Load Array[i] to $t3. (Cycle N)
    ADD  $s2, $s2, $t3   # Sum += Array[i]. HAZARD!! Must wait for $t3. (Cycle N+1)
    
    ADDI $s0, $s0, 1     # Increment Index
    BNE  $s0, $s1, Loop  # Continue if Index != 3

End:
    J End
