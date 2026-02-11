class CPU:
    def __init__(self):
        # Initialize 32 MIPS registers
        # Mapping names to indices for internal storage, but we will store by name for simplicity in this Python sim
        self.registers = {}
        self.reset()

    def get_register(self, name):
        if name == "$zero": return 0
        return self.registers.get(name, 0)

    def set_register(self, name, value):
        if name == "$zero": return # Read-only
        if name in self.registers:
            self.registers[name] = value & 0xFFFF # Enforce 16-bit for this sim data path
        else:
            print(f"Warning: Attempt to write to invalid register {name}")

    def reset(self):
        # Standard MIPS Register Set
        reg_names = [
            "$zero", "$at", "$v0", "$v1", "$a0", "$a1", "$a2", "$a3",
            "$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7",
            "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7",
            "$t8", "$t9", "$k0", "$k1", "$gp", "$sp", "$fp", "$ra"
        ]
        self.registers = {name: 0 for name in reg_names}
        
        # Specific initializations
        self.registers["$sp"] = 0xFFF # Stack pointer
        self.registers["$gp"] = 0x1000 # Global pointer (arbitrary)
        
        self.pc = 0
        self.stack = []
