# Procedure Call Demo using CALL/RET
# Main Program

ADDI $t1, $zero, 10  # $t1 = 10
ADDI $t2, $zero, 20  # $t2 = 20

CALL SumFunc         # Call the procedure (JAL)
# When we return, $v0 should have 30.

ADDI $t0, $v0, 5     # $t0 = 30 + 5 = 35
SW   $t0, 100        # Store final result 35
J    End

# Procedure: SumFunc
# Input: $t1, $t2
# Output: $v0
SumFunc:
    ADD $v0, $t1, $t2 # $v0 = 10 + 20 = 30
    RET               # Return (JR $ra)

End:
    J End
