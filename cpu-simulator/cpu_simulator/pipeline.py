from instruction import RType, IType, JType

class Pipeline:
    def __init__(self, cpu, memory):
        self.cpu = cpu
        self.memory = memory  # Assuming memory module exists, or we might need to mock it if simplifed
        self.IF = None
        self.ID = None
        self.EX = None
        self.MEM = None
        self.WB = None

    def step(self):
        # 5. Write Back (WB)
        self.WB = self.MEM
        if self.WB:
            self._execute_wb(self.WB)

        # 4. Memory Access (MEM)
        self.MEM = self.EX
        # For this simple simulator, we might do memory ops here or in WB. 
        # But let's perform the "calculation" result passing here.

        # 3. Execute (EX)
        self.EX = self.ID
        # In a real pipeline, ALU happens here. We'll simulate result generation.
        if self.EX:
             self._execute_ex(self.EX)

        # 2. Decode (ID)
        self.ID = self.IF
        
        # 1. Fetch (IF) - This is usually pushed from outside (CPU PC), 
        # or we pull it here. The main loop usually feeds IF.
        # So we leave IF as is, to be set by the main loop.
        self.IF = None # Consumed

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
            elif instruction.opcode == "JR":
                # Jump Register: PC = $rs1
                target = get_val(instruction.rs1)
                self.cpu.pc = target
                self._flush_pipeline()
                print(f"JR to {target}")
            
        elif isinstance(instruction, IType):
            if instruction.opcode == "LOAD":
                instruction.result = instruction.imm
            elif instruction.opcode == "STORE":
                instruction.val_to_store = get_val(instruction.rs1)
            elif instruction.opcode == "BEQ":
                # BEQ: Branch if Equal
                # Logic: if val1 == val2, jump to new address


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
                # Jump and Link (JAL)
                # Save the return address (PC of next instruction).
                # Since PC increments at Fetch, current PC points to next instruction.
                # However, due to pipeline delay, we adjust to ensure correct return.


                self.cpu.set_register("$ra", self.cpu.pc - 2)
                self.cpu.pc = instruction.address
                self._flush_pipeline()
                print(f"JAL to {instruction.address}, return to {self.cpu.get_register('$ra')}")

    def _flush_pipeline(self):
        # Clear IF and ID stages as they contain instructions from the old path
        self.IF = None
        self.ID = None
        # EX is currently executing the branch/jump, so it finishes. 

    def _execute_wb(self, instruction):
        if isinstance(instruction, RType):
            if instruction.rd:
                self.cpu.set_register(instruction.rd, getattr(instruction, 'result', 0))
        elif isinstance(instruction, IType):
            if instruction.opcode == "STORE":
                 # Execute store to memory
                 val = self.cpu.get_register(instruction.rs1)
                 self.memory.store(instruction.imm, val) 
                 print(f"Memory Write: Address {instruction.imm} = {val}")
            elif instruction.rd:
                 # LOAD, ADDI, etc.
                 self.cpu.set_register(instruction.rd, getattr(instruction, 'result', 0))

