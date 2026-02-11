# Procedure Call Demo using CALL/RET
# Main Program

ADDI $s0, $zero, 10  # $s0 = 10
ADDI $s1, $zero, 20  # $s1 = 20

CALL SumFunc         # Call the procedure (JAL)
# When we return, $v0 should have 30.

ADDI $t0, $v0, 5     # $t0 = 30 + 5 = 35
SW   $t0, 100        # Store final result 35
J    End

# Procedure: SumFunc
# Input: $s0, $s1
# Output: $v0
SumFunc:
    ADD $v0, $s0, $s1 # $v0 = 10 + 20 = 30
    RET               # Return (JR $ra)

End:
    J End
