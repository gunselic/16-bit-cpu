class CPU:
    def __init__(self):
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
        # Reduced Register Set (8 Total)
        reg_names = [
            "$zero", # 0
            "$t0", "$t1", "$t2", "$t3", # 1-4
            "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7", # 16-23 (Mapped arbitrarily here)
            "$v0",   # 5
            "$sp",   # 6
            "$ra"    # 7
        ]
        self.registers = {name: 0 for name in reg_names}
        
        # Specific initializations
        self.registers["$sp"] = 0xFFF # Stack pointer
        
        self.pc = 0
        self.stack = []
