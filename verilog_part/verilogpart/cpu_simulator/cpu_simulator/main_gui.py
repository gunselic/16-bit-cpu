import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from cpu import CPU
from memory import Memory
from pipeline import Pipeline
from program import program
from assembler import Assembler

class CPUSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Simulator")
        self.root.geometry("1100x750")
        
        # Colors
        self.bg_color = "#FFF0F5" # Lavender Blush
        self.frame_bg = "#FFE4E1" # Misty Rose
        self.btn_bg = "#FF69B4"   # Hot Pink
        self.btn_fg = "white"
        self.text_color = "#4B0082" # Indigo
        
        self.root.configure(bg=self.bg_color)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", background=self.btn_bg, foreground=self.btn_fg, font=("Helvetica", 10, "bold"))
        style.map("TButton", background=[('active', "#FF1493")]) 
        style.configure("TNotebook", background=self.bg_color)
        style.configure("TNotebook.Tab", background="#FFB6C1", foreground=self.text_color, font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[('selected', self.btn_bg)], foreground=[('selected', "white")])

        self.cpu = CPU()
        self.mem = Memory()
        self.pipe = Pipeline(self.cpu, self.mem)
        self.assembler = Assembler()
        self.pc = 0
        self.program = program
        self.is_running = False

        self.setup_ui()
        self.update_display()

    def setup_ui(self):
        # Notebook for Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Execution
        self.tab_exec = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.tab_exec, text="  Execution  ")
        self.setup_execution_tab()
        
        # Tab 2: Editor
        self.tab_editor = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.tab_editor, text="  Code Editor  ")
        self.setup_editor_tab()

    def setup_execution_tab(self):
        # Top: Controls
        control_frame = tk.Frame(self.tab_exec, bg=self.bg_color, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        self.create_btn(control_frame, "Next Step", self.step).pack(side=tk.LEFT, padx=10)
        self.create_btn(control_frame, "Run All", self.run_all).pack(side=tk.LEFT, padx=10)
        self.create_btn(control_frame, "Pause", self.pause).pack(side=tk.LEFT, padx=10)
        self.create_btn(control_frame, "Reset", self.reset).pack(side=tk.LEFT, padx=10)

        # Content (Registers + Pipeline)
        content_frame = tk.Frame(self.tab_exec, bg=self.bg_color)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left: Registers (Scrollable)
        reg_outer_frame = tk.LabelFrame(content_frame, text="Registers (8)", bg=self.frame_bg, fg=self.text_color, font=("Segoe UI", 11, "bold"))
        reg_outer_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        canvas = tk.Canvas(reg_outer_frame, bg=self.frame_bg, width=220, highlightthickness=0)
        scrollbar = ttk.Scrollbar(reg_outer_frame, orient="vertical", command=canvas.yview)
        self.reg_frame = tk.Frame(canvas, bg=self.frame_bg)
        
        self.reg_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.reg_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.reg_labels = {}
        # Get all register names from CPU
        reg_names = list(self.cpu.registers.keys())
        # Sort reasonably if possible, or use list order
        # Specifically prioritize $s, $t, $a, $v for view
        # We'll just list them all in order of creation or key
        
        # Custom sort order:
        order = ["$zero", "$t0", "$t1", "$t2", "$t3", "$v0", "$sp", "$ra"]

        for name in order:
            lbl = tk.Label(self.reg_frame, text=f"{name}: 0", font=("Consolas", 10), bg=self.frame_bg, anchor="w")
            lbl.pack(fill=tk.X, padx=5, pady=1)
            self.reg_labels[name] = lbl

        # Right: Pipeline & Program
        right_panel = tk.Frame(content_frame, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Pipeline
        pipe_frame = tk.LabelFrame(right_panel, text="Pipeline Stages", bg=self.frame_bg, fg=self.text_color, font=("Segoe UI", 11, "bold"))
        pipe_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.pipe_labels = {}
        stages = ["IF", "ID", "EX", "MEM", "WB"]
        for stage in stages:
            frame = tk.Frame(pipe_frame, bg="white", bd=1, relief=tk.RAISED, height=40)
            frame.pack(fill=tk.X, padx=5, pady=3)
            frame.pack_propagate(False)
            
            tk.Label(frame, text=stage, font=("Segoe UI", 9, "bold"), bg="#FFB6C1", width=4).pack(side=tk.LEFT, fill=tk.Y)
            val = tk.Label(frame, text="-", font=("Consolas", 9), bg="white", anchor="w")
            val.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            self.pipe_labels[stage] = val

        # Program List (with Binary)
        prog_frame = tk.LabelFrame(right_panel, text="Program Memory", bg=self.frame_bg, fg=self.text_color, font=("Segoe UI", 11, "bold"))
        prog_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        
        # Columns: Addr | Binary | Assembly
        header_frame = tk.Frame(prog_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Addr", width=5, bg=self.bg_color, font=("Consolas", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(header_frame, text="Machine Code (Bin)", width=34, bg=self.bg_color, font=("Consolas", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(header_frame, text="Assembly", bg=self.bg_color, font=("Consolas", 9, "bold")).pack(side=tk.LEFT)

        self.prog_text = tk.Text(prog_frame, height=10, font=("Consolas", 9), bg="#FFF5EE", relief=tk.FLAT)
        self.prog_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._refresh_program_view()

    def setup_editor_tab(self):
        toolbar = tk.Frame(self.tab_editor, bg=self.bg_color, pady=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        self.create_btn(toolbar, "Load .asm", self.load_asm_file).pack(side=tk.LEFT, padx=10)
        self.create_btn(toolbar, "Save .asm", self.save_asm_file).pack(side=tk.LEFT, padx=10)
        self.create_btn(toolbar, "Assemble & Load", self.assemble_code).pack(side=tk.RIGHT, padx=10)

        self.editor = tk.Text(self.tab_editor, font=("Consolas", 11), bg="white", wrap=tk.NONE)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        ys = ttk.Scrollbar(self.editor, orient="vertical", command=self.editor.yview)
        xs = ttk.Scrollbar(self.editor, orient="horizontal", command=self.editor.xview)
        self.editor.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        ys.pack(side=tk.RIGHT, fill=tk.Y)
        xs.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Default text
        default_code = """# Example Program
ADDI $t0, $zero, 10
ADDI $t1, $zero, 20
ADD $t2, $t0, $t1
SW $t2, 100
"""
        self.editor.insert(tk.END, default_code)

    def create_btn(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd, bg=self.btn_bg, fg=self.btn_fg, 
                         font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=5, cursor="hand2")

    # --- Actions ---

    def load_asm_file(self):
        path = filedialog.askopenfilename(filetypes=[("Assembly Files", "*.asm"), ("All Files", "*.*")])
        if path:
            try:
                with open(path, "r") as f:
                    content = f.read()
                self.editor.delete(1.0, tk.END)
                self.editor.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def save_asm_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".asm", filetypes=[("Assembly Files", "*.asm")])
        if path:
            try:
                with open(path, "w") as f:
                    f.write(self.editor.get(1.0, tk.END))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def assemble_code(self):
        code = self.editor.get(1.0, tk.END)
        try:
            self.program = self.assembler.assemble(code)
            self.reset()
            self._refresh_program_view()
            self.notebook.select(self.tab_exec) # Switch to exec tab
            messagebox.showinfo("Success", "Assembly compiled and loaded successfully!")
        except Exception as e:
            messagebox.showerror("Assembly Error", str(e))

    def step(self):
        # Sync with CPU PC (Vital for Jumps/Branches)
        self.pc = self.cpu.pc
        
        if self.pc < len(self.program):
            self.pipe.IF = self.program[self.pc]
            # Increment PC for next cycle (and for JAL return address)
            self.cpu.pc += 1
            # Update local tracking
            self.pc = self.cpu.pc
        else:
            self.pipe.IF = None
        
        self.pipe.step()
        self.update_display()
        self._refresh_program_view() # Highlight current line

    def run_all(self):
        if self.is_running: return # Already running
        self.is_running = True
        self._run_loop()

    def pause(self):
        self.is_running = False

    def _run_loop(self):
        if not self.is_running: return

        if self.pc < len(self.program) or (self.pipe.WB or self.pipe.MEM or self.pipe.EX or self.pipe.ID):
            self.step()
            self.root.after(300, self._run_loop) # Faster run 300ms
        else:
            self.is_running = False

    def reset(self):
        self.cpu.reset()
        self.pc = 0
        self.pipe = Pipeline(self.cpu, self.mem)
        self.update_display()
        self._refresh_program_view()

    def update_display(self):
        # Registers
        for name, lbl in self.reg_labels.items():
            val = self.cpu.get_register(name)
            # Highlight if non-zero, but ignore default Stack Pointer (0xFFF)
            is_default_sp = (name == "$sp" and val == 0xFFF)
            color = "#800080" if (val != 0 and not is_default_sp) else "#333"
            lbl.config(text=f"{name}: {val}", fg=color)

        # Pipeline
        # Show stage + binary/hex info where possible
        def fmt_stage(val, stage):
            # Special visualization for Stall/Bubble in EX stage
            if stage == "EX" and val is None and self.pipe.ID is not None:
                return "⚠️ STALL (BUBBLE)"

            if not val: return "-"
            if stage == "ID" and hasattr(val, 'to_binary'):
                # Show BINARY & OPCODE
                return f"{val} \nbin: {val.to_binary()} \nhex: {hex(int(val.to_binary(), 2))}"
            elif stage == "EX" and hasattr(val, 'result'):
                return f"{val} [Res: {val.result}]"
            elif stage == "MEM" and hasattr(val, 'val_to_store'):
                return f"{val} [Store: {val.val_to_store}]"
            return str(val)

        self.pipe_labels["IF"].config(text=fmt_stage(self.pipe.IF, "IF"))
        self.pipe_labels["ID"].config(text=fmt_stage(self.pipe.ID, "ID"))
        self.pipe_labels["EX"].config(text=fmt_stage(self.pipe.EX, "EX"))
        self.pipe_labels["MEM"].config(text=fmt_stage(self.pipe.MEM, "MEM"))
        self.pipe_labels["WB"].config(text=fmt_stage(self.pipe.WB, "WB"))

    def _refresh_program_view(self):
        self.prog_text.config(state=tk.NORMAL)
        self.prog_text.delete(1.0, tk.END)
        for idx, instr in enumerate(self.program):
            prefix = " >" if idx == self.pc else "  "
            
            binary = instr.to_binary() if hasattr(instr, 'to_binary') else "?"
            line = f"{prefix} {idx:02d} | {binary} | {instr}\n"
            
            self.prog_text.insert(tk.END, line)
            
            if idx == self.pc:
                self.prog_text.tag_add("current", f"{idx+1}.0", f"{idx+1}.end")
                self.prog_text.tag_config("current", background="#FFB6C1", foreground="black")
                
        self.prog_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSimulatorGUI(root)
    root.mainloop()
