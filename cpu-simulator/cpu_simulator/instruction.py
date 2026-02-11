# Opcode and Funct definitions
OPCODES = {
    "R-TYPE": 0,       # 000000
    "J": 2,            # 000010
    "JAL": 3,          # 000011
    "BEQ": 4,          # 000100
    "BNE": 5,          # 000101
    "ADDI": 8,         # 001000 (Treating simplified ADD with imm as ADDI)
    "LW": 35,          # 100011 (LOAD)
    "SW": 43,          # 101011 (STORE)
    # Mapping our simulator names to MIPS standard
    "LOAD": 35,
    "STORE": 43
}

FUNCT_CODES = {
    "ADD": 32,         # 100000
    "SUB": 34,         # 100010
    "JR": 8,           # 001000
}

REG_MAP = {
    "$zero": 0, "$at": 1, "$v0": 2, "$v1": 3,
    "$a0": 4, "$a1": 5, "$a2": 6, "$a3": 7,
    "$t0": 8, "$t1": 9, "$t2": 10, "$t3": 11, "$t4": 12, "$t5": 13, "$t6": 14, "$t7": 15,
    "$s0": 16, "$s1": 17, "$s2": 18, "$s3": 19, "$s4": 20, "$s5": 21, "$s6": 22, "$s7": 23,
    "$t8": 24, "$t9": 25, "$k0": 26, "$k1": 27,
    "$gp": 28, "$sp": 29, "$fp": 30, "$ra": 31
}

class Instruction:
    def __init__(self, opcode):
        self.opcode = opcode

    def __str__(self):
        return f"{self.opcode}"
    
    def to_binary(self):
        return "0" * 32

    def _reg_num(self, reg_name):
        return REG_MAP.get(reg_name, 0)

class RType(Instruction):
    def __init__(self, opcode, rd, rs1, rs2):
        super().__init__(opcode)
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2

    def __str__(self):
        return f"{self.opcode} {self.rd}, {self.rs1}, {self.rs2}"
    
    def to_binary(self):
        # R-Type: Opcode(6) | RS(5) | RT(5) | RD(5) | Shamt(5) | Funct(6)
        op = 0 # R-Type is always 0
        rs = self._reg_num(self.rs1)
        rt = self._reg_num(self.rs2)
        rd = self._reg_num(self.rd)
        shamt = 0
        funct = FUNCT_CODES.get(self.opcode, 0)
        
        val = (op << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (shamt << 6) | funct
        return f"{val:032b}"

class IType(Instruction):
    def __init__(self, opcode, rd, rs1, imm):
        super().__init__(opcode)
        self.rd = rd   # MIPS I-Type: rt is target/source
        self.rs1 = rs1 # MIPS I-Type: rs is base/source
        self.imm = imm

    def __str__(self):
        if self.rs1:
             return f"{self.opcode} {self.rd}, {self.rs1}, {self.imm}"
        else:
             return f"{self.opcode} {self.rd}, {self.imm}"
             
    def to_binary(self):
        # I-Type: Opcode(6) | RS(5) | RT(5) | Imm(16)
        op = OPCODES.get(self.opcode, 0)
        rs = self._reg_num(self.rs1) if self.rs1 else 0
        rt = self._reg_num(self.rd)
        imm = self.imm & 0xFFFF # Handle negative
        
        val = (op << 26) | (rs << 21) | (rt << 16) | imm
        return f"{val:032b}"

class JType(Instruction):
    def __init__(self, opcode, address):
        super().__init__(opcode)
        self.address = address

    def __str__(self):
        return f"{self.opcode} {self.address}"
        
    def to_binary(self):
        # J-Type: Opcode(6) | Address(26)
        op = OPCODES.get(self.opcode, 0)
        addr = self.address & 0x3FFFFFF
        
        val = (op << 26) | addr
        return f"{val:032b}"
