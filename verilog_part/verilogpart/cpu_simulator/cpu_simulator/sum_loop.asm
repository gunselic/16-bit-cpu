# Sum Loop Demo
# Calculates sum of numbers from 5 down to 1 (5+4+3+2+1 = 15)

ADDI $t0, $zero, 5   # $t0 = 5 (Counter N)
ADD  $t1, $zero, $zero # $t1 = 0 (Result Sum)

Loop:
    ADD  $t1, $t1, $t0   # Sum = Sum + N
    ADDI $t0, $t0, -1    # N = N - 1
    BNE  $t0, $zero, Loop # If N != 0, go back to Loop

End:
    SW   $t1, 200        # Store Result (15) to Memory Address 200
    J    End             # Infinite jump to stay here
