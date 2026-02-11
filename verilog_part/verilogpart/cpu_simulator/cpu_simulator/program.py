from instruction import RType, IType, JType

# Comprehensive Demo Program
# 1. Initialize $s0 = 0 (Counter)
# 2. Initialize $s1 = 5 (Target)
# 3. Procedure Call: JAL to "AddFunction"
# 4. "AddFunction": Adds 1 to $s0.
# 5. Returns using JR $ra
# 6. Branch Check: If $s0 != $s1, jump back to Call (Loop)
# 7. End

# Addresses:
# 0: LOAD $s0, 0
# 1: LOAD $s1, 5
# 2: LOAD $s2, 1 (Increment step)
# 3: JAL 6 (Jump to AddFunction)
# 4: BNE $s0, $s1, 3 (If $s0 != $s1, jump back to JAL at 3)
# 5: J 9 (Jump to End)
# -- AddFunction --
# 6: ADD $s0, $s0, $s2  ($s0 = $s0 + 1)
# 7: JR $ra (Return)
# -- End --
# 8: LOAD $s7, 999 (Sentinel for success)

program = [
    # Init
    IType("LOAD", rd="$s0", imm=0, rs1=None),      # 0
    IType("LOAD", rd="$s1", imm=3, rs1=None),      # 1 (Loop 3 times)
    IType("LOAD", rd="$s2", imm=1, rs1=None),      # 2
    
    # Loop Start (Call Function)
    JType("JAL", address=6),                       # 3
    
    # Branch Check
    IType("BNE", rd="$s1", rs1="$s0", imm=3),      # 4 (Use rd as 2nd operand for comparison in our simplified logic)
    
    # Finished
    JType("J", address=8),                         # 5
    
    # Function: Add 1 to $s0
    RType("ADD", rd="$s0", rs1="$s0", rs2="$s2"),  # 6
    RType("JR", rd=None, rs1="$ra", rs2=None),     # 7
    
    # End
    IType("LOAD", rd="$s7", imm=999, rs1=None)     # 8
]
