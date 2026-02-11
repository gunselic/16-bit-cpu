from cpu import CPU
from memory import Memory
from pipeline import Pipeline
from program import program

cpu = CPU()
mem = Memory()
pipe = Pipeline(cpu, mem)

while cpu.pc < len(program):
    pipe.IF = program[cpu.pc]
    cpu.pc += 1
    pipe.step()

    print("Pipeline State:")
    print("IF:", pipe.IF)
    print("ID:", pipe.ID)
    print("EX:", pipe.EX)
    print("MEM:", pipe.MEM)
    print("WB:", pipe.WB)
    print("------")
