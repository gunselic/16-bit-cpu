# Fibonacci Sequence Demo (Example 2)
# Calculates numbers: 0, 1, 1, 2, 3, 5, 8...

ADDI $t0, $zero, 0   # $t0 = 0 (Privious 1)
ADDI $t1, $zero, 1   # $t1 = 1 (Previous 2 / Current)
ADDI $t2, $zero, 10  # $t2 = 10 (Loop Counter)

Loop:
    ADD  $t3, $t0, $t1   # New = Prev1 + Prev2
    ADD  $t0, $zero, $t1 # Prev1 = Prev2 (Shift)
    ADD  $t1, $zero, $t3 # Prev2 = New (Shift)
    
    ADDI $t2, $t2, -1    # Decrement Counter
    BNE  $t2, $zero, Loop # Check if loop done

    SW   $t1, 500        # Store final result (89 for 11th number step, or similar)
    J    End             # End program

End:
    J    End
