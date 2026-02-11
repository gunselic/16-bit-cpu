from cpu import CPU
from pipeline import Pipeline
from instruction import RType, IType

def test_pipeline():
    print("Testing Pipeline Logic...")
    cpu = CPU()
    # Masking memory as None since we aren't testing STORE heavily yet or can mock if needed
    pipe = Pipeline(cpu, memory=None) 
    
    # Program:
    # LOAD $t0, 10
    # LOAD $t1, 20
    # ADD $t2, $t0, $t1
    
    prog = [
        IType("LOAD", rd="$t0", rs1=None, imm=10),
        IType("LOAD", rd="$t1", rs1=None, imm=20),
        RType("ADD", rd="$t2", rs1="$t0", rs2="$t1"),
    ]
    
    # Run pipeline manually
    # Cycle 1: IF Load 10
    pipe.IF = prog[0]
    pipe.step()
    
    # Cycle 2: IF Load 20, ID Load 10
    pipe.IF = prog[1]
    pipe.step()
    
    # Cycle 3: IF Add, ID Load 20, EX Load 10
    pipe.IF = prog[2]
    pipe.step()
    
    # Cycle 4: ID Add, EX Load 20, MEM Load 10
    pipe.step()
    
    # Cycle 5: EX Add, MEM Load 20, WB Load 10 -> $t0 should be 10 logic-wise (if WB happens here)
    pipe.step()
    print(f"Cycle 5 (WB Load 1): $t0={cpu.get_register('$t0')}") 
    
    # Cycle 6: MEM Add, WB Load 20 -> $t1 should be 20
    pipe.step()
    print(f"Cycle 6 (WB Load 2): $t1={cpu.get_register('$t1')}")
    
    # Cycle 7: WB Add -> $t2 should be 30
    pipe.step()
    print(f"Cycle 7 (WB Add): $t2={cpu.get_register('$t2')}")
    
    assert cpu.get_register("$t0") == 10, f"Expected $t0=10, got {cpu.get_register('$t0')}"
    assert cpu.get_register("$t1") == 20, f"Expected $t1=20, got {cpu.get_register('$t1')}"
    assert cpu.get_register("$t2") == 30, f"Expected $t2=30, got {cpu.get_register('$t2')}"
    
    print("Test Passed!")

if __name__ == "__main__":
    test_pipeline()
