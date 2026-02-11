from cpu import CPU
from pipeline import Pipeline
from instruction import RType, IType

def test_pipeline():
    print("Testing Pipeline Logic...")
    cpu = CPU()
    # Masking memory as None since we aren't testing STORE heavily yet or can mock if needed
    pipe = Pipeline(cpu, memory=None) 
    
    # Program:
    # LOAD $s1, 10
    # LOAD $s2, 20
    # ADD $s3, $s1, $s2
    
    prog = [
        IType("LOAD", rd="$s1", rs1=None, imm=10),
        IType("LOAD", rd="$s2", rs1=None, imm=20),
        RType("ADD", rd="$s3", rs1="$s1", rs2="$s2"),
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
    
    # Cycle 5: EX Add, MEM Load 20, WB Load 10 -> $s1 should be 10 logic-wise (if WB happens here)
    pipe.step()
    print(f"Cycle 5 (WB Load 1): $s1={cpu.get_register('$s1')}") 
    
    # Cycle 6: MEM Add, WB Load 20 -> $s2 should be 20
    pipe.step()
    print(f"Cycle 6 (WB Load 2): $s2={cpu.get_register('$s2')}")
    
    # Cycle 7: WB Add -> $s3 should be 30
    pipe.step()
    print(f"Cycle 7 (WB Add): $s3={cpu.get_register('$s3')}")
    
    assert cpu.get_register("$s1") == 10, f"Expected $s1=10, got {cpu.get_register('$s1')}"
    assert cpu.get_register("$s2") == 20, f"Expected $s2=20, got {cpu.get_register('$s2')}"
    assert cpu.get_register("$s3") == 30, f"Expected $s3=30, got {cpu.get_register('$s3')}"
    
    print("Test Passed!")

if __name__ == "__main__":
    test_pipeline()
