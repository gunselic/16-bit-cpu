from assembler import Assembler

def test_assembler():
    asm = Assembler()
    
    code = """
    # This is a test
    ADDI $t0, $zero, 10
    ADDI $t1, $zero, 20
    Loop:
    ADD $t2, $t0, $t1
    BNE $t2, $t0, Loop
    J End
    End:
    LW $s0, 100
    """
    
    try:
        prog = asm.assemble(code)
        print("Assembly Successful!")
        for idx, instr in enumerate(prog):
            print(f"{idx}: {instr} -> {instr.to_binary()}")
            
    except Exception as e:
        print(f"Assembly Failed: {e}")

if __name__ == "__main__":
    test_assembler()
