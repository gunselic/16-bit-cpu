import re
from instruction import RType, IType, JType

class Assembler:
    def __init__(self):
        # Regex patterns for parsing
        self.label_pattern = re.compile(r"^(\w+):")
        self.comment_pattern = re.compile(r"#.*$")
        
        # Instruction mappings
        self.r_type_ops = ["ADD", "SUB", "AND", "OR", "SLT", "JR"]
        self.i_type_ops = ["ADDI", "LW", "SW", "BEQ", "BNE", "LOAD", "STORE"] # LOAD/STORE as aliases
        self.j_type_ops = ["J", "JAL"]
        # Pseudo-ops map
        self.pseudo_ops = ["CALL", "RET"]

    def assemble(self, source_code):
        lines = source_code.splitlines()
        clean_lines = []
        labels = {}
        instruction_list = []
        
        # Pass 1: Clean code and find labels
        inst_idx = 0
        for line in lines:
            line = self.comment_pattern.sub("", line).strip()
            if not line:
                continue
                
            # Check for label
            label_match = self.label_pattern.match(line)
            if label_match:
                label = label_match.group(1)
                labels[label] = inst_idx
                # Remove label from line
                line = line[len(label)+1:].strip()
            
            if line:
                clean_lines.append(line)
                inst_idx += 1
                
        # Pass 2: Parse instructions
        for idx, line in enumerate(clean_lines):
            try:
                instr = self._parse_line(line, labels, idx)
                instruction_list.append(instr)
            except Exception as e:
                print(f"Error parsing line {idx+1}: {line} -> {e}")
                raise e
                
        return instruction_list

    def _parse_line(self, line, labels, current_addr):
        # Normalize commas
        parts = line.replace(",", " ").split()
        opcode = parts[0].upper()
        args = parts[1:]
        
        if opcode in self.r_type_ops:
            return self._parse_rtype(opcode, args)
        elif opcode in self.i_type_ops:
            return self._parse_itype(opcode, args, labels, current_addr)
        elif opcode in self.j_type_ops:
            return self._parse_jtype(opcode, args, labels)
        elif opcode == "CALL":
            # CALL Label -> JAL Label
            return self._parse_jtype("JAL", args, labels)
        elif opcode == "RET":
            # RET -> JR $ra
            return RType("JR", rd=None, rs1="$ra", rs2=None)
        else:
            raise ValueError(f"Unknown opcode: {opcode}")

    def _parse_rtype(self, opcode, args):
        # R-Type: ADD rd, rs, rt -> rd, rs1, rs2
        # JR rs -> rs1 (rd=None, rs2=None)
        if opcode == "JR":
             return RType(opcode, rd=None, rs1=args[0], rs2=None)
        
        return RType(opcode, rd=args[0], rs1=args[1], rs2=args[2])

    def _parse_itype(self, opcode, args, labels, current_addr):
        # I-Type: 
        # ADDI rt, rs, imm
        # LW rt, offset(rs) -> Not supporting offset(rs) syntax yet, using simplified: LW rt, imm (rs implicit/ignored or fixed)
        # BEQ rs, rt, label
        
        if opcode in ["BEQ", "BNE"]:
            # BEQ rs, rt, label
            rs1 = args[0]
            rd = args[1] # Treat 2nd reg as rd/rt field
            label_or_imm = args[2]
            
            if label_or_imm in labels:
                 imm = labels[label_or_imm] # Absolute address of label
            else:
                 imm = int(label_or_imm)
                 
            return IType(opcode, rd=rd, rs1=rs1, imm=imm)
            
        elif opcode in ["LOAD", "LW", "STORE", "SW"]:
            # LOAD rd, imm
            # OR SW rs, imm (Source is in rd field for IType usually? No, SW uses rt as source to store)
            # Let's map args strictly to what Instruction expects
            # Simulator expects: LOAD rd, imm (rs1=None)
            # Simulator expects: STORE rs1, imm (rd=None/Ignored) -> Check pipeline.py usage
            
            # Update to match pipeline.py logic:
            # LOAD: rd=dest
            # STORE: rs1=val_to_store
            
             if opcode in ["STORE", "SW"]:
                 # SW $t0, 100 -> store content of $t0 to address 100
                 return IType(opcode, rd=None, rs1=args[0], imm=int(args[1]))
             else:
                 # LW $t0, 100
                 return IType(opcode, rd=args[0], rs1=None, imm=int(args[1]))

        else:
            # ADDI rt, rs, imm
            return IType(opcode, rd=args[0], rs1=args[1], imm=int(args[2]))

    def _parse_jtype(self, opcode, args, labels):
        # J label
        target = args[0]
        if target in labels:
            addr = labels[target]
        else:
            addr = int(target)
            
        return JType(opcode, address=addr)
