# 16-bit CPU Design in Verilog

## Project Overview

This project presents the design and implementation of a custom 16-bit CPU using Verilog HDL.  
The processor includes a complete datapath architecture, control unit, ALU, register file, and memory interface.

In addition to the hardware implementation, a Python-based simulation and GUI were developed to visualize instruction execution and CPU state changes.

This project demonstrates a strong understanding of computer architecture, digital system design, and hardware-software integration.

---

## Architecture

The CPU is composed of the following components:

- 16-bit Datapath
- Arithmetic Logic Unit (ALU)
- Register File
- Control Unit
- Instruction Decoder
- Memory Interface
- Testbench for simulation

Waveform simulations were used to verify correct instruction execution and control signal transitions.

---

## Verilog Implementation

The CPU was implemented using modular Verilog design:

- `alu.v`
- `control_unit.v`
- `register_file.v`
- `cpu_top.v`
- `testbench.v`

Each module was designed independently and then integrated into the top-level CPU architecture.

Waveform analysis confirms proper datapath behavior and control logic timing.

---

## Python Simulation & GUI

A Python-based simulator was developed to:

- Simulate instruction execution
- Visualize register values
- Display CPU state changes
- Provide a simple graphical interface for interaction

This allowed software-level validation alongside hardware simulation.

---

## Instruction Set (Example)

| Instruction | Description |
|------------|------------|
| ADD        | Adds two registers |
| SUB        | Subtracts two registers |
| LOAD       | Loads data from memory |
| STORE      | Stores data to memory |
| AND        | Bitwise AND operation |
| OR         | Bitwise OR operation |

*(Modify according to your actual instruction set.)*

---

## Screenshots

### Datapath Design
(Add datapath image here)

### Waveform Simulation
(Add waveform image here)

### Python GUI
(Add GUI screenshot here)

---

## How to Run

### Verilog Simulation
Run the `testbench.v` file using ModelSim / Vivado (or your preferred simulator).

### Python Simulation
Navigate to the python simulation folder and run:

