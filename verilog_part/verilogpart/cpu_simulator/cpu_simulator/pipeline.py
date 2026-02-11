from instruction import RType, IType, JType

class Pipeline:
    def __init__(self, cpu, memory):
        self.cpu = cpu
        self.memory = memory
        self.IF = None
        self.ID = None
        self.EX = None
        self.MEM = None
        self.WB = None

    def step(self):
        stall = self._detect_hazard()

        self.WB = self.MEM
        if self.WB:
            self._execute_wb(self.WB)

        self.MEM = self.EX
        if self.MEM:
            self._execute_mem(self.MEM)

        if stall:
            self.EX = None
        else:
            self.EX = self.ID
            if self.EX:
                 self._execute_ex(self.EX)

        if not stall:
            self.ID = self.IF
            self.IF = None
            
        return stall

    def _detect_hazard(self):
        if self.EX and self.EX.opcode in ["LOAD", "LW"] and self.ID:
            load_dest = self.EX.rd
            
            id_rs1 = getattr(self.ID, 'rs1', None)
            id_rs2 = getattr(self.ID, 'rs2', None)
            
            # Special case for STORE: it reads from its 'rd' (which holds data source) and 'rs1' (base)
            if self.ID.opcode in ["STORE", "SW"]:
                 # STORE reads from rd (value) and rs1 (address base)
                 if load_dest == self.ID.rd or load_dest == id_rs1:
                      return True
            else:
                 # Normal case (R-Type, BEQ, etc.)
                 if load_dest and (load_dest == id_rs1 or load_dest == id_rs2):
                      return True
                      
        return False

    def _execute_ex(self, instruction):
        # Helper to get value with forwarding
        def get_val(reg_name):
            # Data Forwarding Check
            # If MEM stage writes to this register, grab the value before it hits WB

            if self.MEM and hasattr(self.MEM, 'rd') and self.MEM.rd == reg_name and reg_name is not None:
                return getattr(self.MEM, 'result', 0)
            
            # Otherwise read from register file (WB happened at start of step)

            return self.cpu.get_register(reg_name)

        # For R-Type, calculate result
        if isinstance(instruction, RType):
            if instruction.opcode == "ADD":
                val1 = get_val(instruction.rs1)
                val2 = get_val(instruction.rs2)
                instruction.result = val1 + val2
            elif instruction.opcode == "SUB":
                val1 = get_val(instruction.rs1)
                val2 = get_val(instruction.rs2)
                instruction.result = val1 - val2
            elif instruction.opcode == "AND":
                val1 = get_val(instruction.rs1)
                val2 = get_val(instruction.rs2)
                instruction.result = val1 & val2
            elif instruction.opcode == "OR":
                val1 = get_val(instruction.rs1)
                val2 = get_val(instruction.rs2)
                instruction.result = val1 | val2
            elif instruction.opcode == "SLT":
                val1 = get_val(instruction.rs1)
                val2 = get_val(instruction.rs2)
                instruction.result = 1 if val1 < val2 else 0
            elif instruction.opcode == "JR":
                # Jump Register: PC = $rs1
                target = get_val(instruction.rs1)
                self.cpu.pc = target
                self._flush_pipeline()
                print(f"JR to {target}")
            
        elif isinstance(instruction, IType):
            if instruction.opcode in ["LOAD", "LW"]:
                # Calculate Address: Base (rs1) + Offset (imm)
                base = get_val(instruction.rs1)
                instruction.effective_address = base + instruction.imm
                
            elif instruction.opcode in ["STORE", "SW"]:
                # Calculate Address: Base (rs1) + Offset (imm)
                base = get_val(instruction.rs1)
                instruction.effective_address = base + instruction.imm
                # Value to store is in rd (based on our assembler mapping)
                instruction.val_to_store = get_val(instruction.rd)

            elif instruction.opcode == "BEQ":
                # BEQ: Branch if Equal
                val1 = get_val(instruction.rs1)
                val2 = get_val(instruction.rd)
                
                if val1 == val2:
                     self.cpu.pc = instruction.imm # Using absolute address (simplified)
                     self._flush_pipeline()
                     print(f"BEQ taken to {instruction.imm}")
            elif instruction.opcode == "BNE":
                val1 = get_val(instruction.rs1)
                val2 = get_val(instruction.rd)
                if val1 != val2:
                     self.cpu.pc = instruction.imm
                     self._flush_pipeline()
                     print(f"BNE taken to {instruction.imm}")
            elif instruction.opcode == "ADDI":
                 val1 = get_val(instruction.rs1)
                 instruction.result = val1 + instruction.imm

        elif isinstance(instruction, JType):
            if instruction.opcode == "J":
                self.cpu.pc = instruction.address
                self._flush_pipeline()
                print(f"J to {instruction.address}")
            elif instruction.opcode == "JAL":
                # Jump and Link (JAL)
                # Save the return address (PC of next instruction).
                # Since PC increments at Fetch, current PC points to next instruction.
                # However, due to pipeline delay, we adjust to ensure correct return.

                self.cpu.set_register("$ra", self.cpu.pc - 2)
                self.cpu.pc = instruction.address
                self._flush_pipeline()
                print(f"JAL to {instruction.address}, return to {self.cpu.get_register('$ra')}")

    def _execute_mem(self, instruction):
        if instruction.opcode in ["LOAD", "LW"]:
             # Perform Read
             val = self.memory.load(instruction.effective_address)
             instruction.result = val
             
        elif instruction.opcode in ["STORE", "SW"]:
             # Perform Write
             self.memory.store(instruction.effective_address, instruction.val_to_store)
             print(f"MEM: Stored {instruction.val_to_store} to address {instruction.effective_address}")

    def _flush_pipeline(self):
        self.IF = None
        self.ID = None

    def _execute_wb(self, instruction):
        if isinstance(instruction, RType):
            if instruction.rd:
                self.cpu.set_register(instruction.rd, getattr(instruction, 'result', 0))
        elif isinstance(instruction, IType):
            if instruction.opcode in ["STORE", "SW"]:
                 # Already handled in MEM
                 pass
            elif instruction.rd:
                 # LOAD, ADDI, etc.
                 val = getattr(instruction, 'result', 0)
                 self.cpu.set_register(instruction.rd, val)

