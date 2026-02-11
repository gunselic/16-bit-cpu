
import sys
import os

# Add specific path to find the package
sys.path.append(os.path.join(os.getcwd(), "cpu_simulator"))
from cpu_simulator.instruction import Instruction
from cpu_simulator.program import program

def main():
    with open("program.hex", "w") as f:
        for i, instr in enumerate(program):
            # to_binary returns 32-bit binary string
            bin_str = instr.to_binary()
            # Convert to hex
            hex_val = f"{int(bin_str, 2):08x}"
            f.write(f"{hex_val}\n")
            print(f"Instr {i}: {instr} -> {hex_val}")
        
        # Fill rest with NOPs (0)
        for _ in range(len(program), 256):
             f.write("00000000\n")

if __name__ == "__main__":
    main()
