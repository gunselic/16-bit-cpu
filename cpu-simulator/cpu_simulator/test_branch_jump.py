from cpu import CPU
from pipeline import Pipeline
from instruction import RType, IType, JType

def test_branches():
    print("Testing Branches & Jumps...")
    cpu = CPU()
    pipe = Pipeline(cpu, memory=None)
    
    # Program:
    # 0: LOAD $s0, 5
    # 1: LOAD $s1, 5
    # 2: BEQ $s0, $s1, 5 (Jump to addr 5)
    # 3: ADD $s2, $s0, $s1 (Should be skipped/flushed)
    # 4: LOAD $s2, 999 (Should be skipped)
    # 5: LOAD $s3, 10 (Target)
    
    prog = [
        IType("LOAD", rd="$s0", imm=5, rs1=None),
        IType("LOAD", rd="$s1", imm=5, rs1=None),
        IType("BEQ", rd="$s1", rs1="$s0", imm=5),
        RType("ADD", rd="$s2", rs1="$s0", rs2="$s1"),
        IType("LOAD", rd="$s2", imm=999, rs1=None), # If executed, s2=999
        IType("LOAD", rd="$s3", imm=10, rs1=None)
    ]
    
    # We need to simulate fetching mechanism roughly or manually feed
    # Let's manually feed, checking PC updates
    
    # 1. Fetch LOAD 5
    pipe.IF = prog[0]
    cpu.pc = 1
    pipe.step() # WB:- MEM:- EX:- ID:Load0 IF:-
    
    # 2. Fetch LOAD 5
    pipe.IF = prog[1]
    cpu.pc = 2
    pipe.step() # ...
    
    # 3. Fetch BEQ
    pipe.IF = prog[2]
    cpu.pc = 3
    pipe.step() 
    
    # 4. Fetch ADD (Instruction at 3) - This is speculatively fetched
    pipe.IF = prog[3]
    cpu.pc = 4
    pipe.step()
    # At end of Cycle 4:
    # EX has BEQ. 
    # BEQ executes -> Logic sees equal. Sets PC to 5. Flushes ID, IF.
    # So ID (which would have been ADD) -> None. 
    
    print(f"Cycle 4 Post-BEQ PC: {cpu.pc}")
    assert cpu.pc == 5, f"PC should be 5, got {cpu.pc}"
    assert pipe.ID is None, "ID should be flushed in Cycle 4"
    assert pipe.IF is None, "IF should be flushed in Cycle 4"
    
    # 5. Fetch TARGET (Instruction at 5) - Correct path
    pipe.IF = prog[5]
    cpu.pc = 6 # Target fetched, next PC 6
    pipe.step() 
    # At end of Cycle 5:
    # ID has Target (Load 10).
    
    # 6. Run a few more to finish WB
    pipe.step() # EX=Target
    pipe.step() # MEM=Target
    pipe.step() # WB=Target
 
    
    # Run a few more to finish WB
    pipe.step()
    pipe.step()
    pipe.step()
    
    print(f"$s3: {cpu.get_register('$s3')}")
    assert cpu.get_register("$s3") == 10, "$s3 should be 10 (Target executed)"
    assert cpu.get_register("$s2") == 0, "$s2 should be 0 (ADD skipped)"
    
    print("Branch Test Passed!")

def test_jal():
    print("Testing JAL...")
    cpu = CPU()
    pipe = Pipeline(cpu, memory=None)
    
    # 0: JAL 10
    # ...
    # 10: JR $ra
    
    # Fetch JAL
    cpu.pc = 0
    instruction = JType("JAL", address=10)
    
    # Manually execute EX stage logic (skipping pipeline fill for unit test of logic)
    # But let's use pipeline to be safe
    # Cycle 1: Fetch
    pipe.IF = instruction
    cpu.pc = 1 # Fetched 0, next is 1
    pipe.step()
    
    # Cycle 2: ID
    pipe.step()
    
    # Cycle 3: EX (JAL executes)
    pipe.step()
    
    print(f"Post-JAL PC: {cpu.pc}")
    print(f"Post-JAL $ra: {cpu.get_register('$ra')}")
    
    assert cpu.pc == 10, "PC should be 10"
    assert cpu.get_register("$ra") == 1, f"RA should be 1 (Next PC), got {cpu.get_register('$ra')}"
    
    print("JAL Test Passed!")

if __name__ == "__main__":
    test_branches()
    test_jal()
