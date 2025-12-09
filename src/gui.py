import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from assembler_ir import parse_program
from encode import encode_program
from decode import decode_instr
from vm import VM
from bitutils import bitreverse64
from model import Op


INSTR_SIZE = 11  # 11 bytes per instruction


class UVMGui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("UVM Assembler & Interpreter")
        self.geometry("1000x600")

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Верхняя панель с настройками
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Dump start
        ttk.Label(top_frame, text="Dump start:").pack(side=tk.LEFT)
        self.dump_start_var = tk.StringVar(value="0")
        ttk.Entry(top_frame, textvariable=self.dump_start_var, width=8).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        # Dump end
        ttk.Label(top_frame, text="Dump end:").pack(side=tk.LEFT)
        self.dump_end_var = tk.StringVar(value="64")
        ttk.Entry(top_frame, textvariable=self.dump_end_var, width=8).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        # Кнопки
        ttk.Button(
            top_frame, text="Open .asm", command=self.on_open_asm
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            top_frame, text="Save .asm", command=self.on_save_asm
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            top_frame, text="Assemble & Run", command=self.on_assemble_and_run
        ).pack(side=tk.RIGHT, padx=5)

        # Основная область: слева код, справа результат
        main_frame = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Левое окно – редактор кода
        left_frame = ttk.Frame(main_frame)
        main_frame.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Assembly source").pack(anchor=tk.W)
        self.text_asm = tk.Text(left_frame, wrap=tk.NONE, undo=True)
        self.text_asm.pack(fill=tk.BOTH, expand=True)

        # Скроллбары для левого окна
        y_scroll_left = ttk.Scrollbar(
            left_frame, orient=tk.VERTICAL, command=self.text_asm.yview
        )
        y_scroll_left.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_asm.configure(yscrollcommand=y_scroll_left.set)

        x_scroll_left = ttk.Scrollbar(
            left_frame, orient=tk.HORIZONTAL, command=self.text_asm.xview
        )
        x_scroll_left.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_asm.configure(xscrollcommand=x_scroll_left.set)

        # Правое окно – вывод памяти / лог
        right_frame = ttk.Frame(main_frame)
        main_frame.add(right_frame, weight=1)

        ttk.Label(right_frame, text="Execution result (memory dump)").pack(anchor=tk.W)
        self.text_output = tk.Text(right_frame, wrap=tk.NONE, state=tk.NORMAL)
        self.text_output.pack(fill=tk.BOTH, expand=True)

        # Скроллбары для правого окна
        y_scroll_right = ttk.Scrollbar(
            right_frame, orient=tk.VERTICAL, command=self.text_output.yview
        )
        y_scroll_right.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_output.configure(yscrollcommand=y_scroll_right.set)

        x_scroll_right = ttk.Scrollbar(
            right_frame, orient=tk.HORIZONTAL, command=self.text_output.xview
        )
        x_scroll_right.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_output.configure(xscrollcommand=x_scroll_right.set)

        # Заполним редактор примером по умолчанию
        self._insert_default_example()

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------
    def on_open_asm(self):
        path = filedialog.askopenfilename(
            title="Open assembly file",
            filetypes=[("Assembly files", "*.asm"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_asm.delete("1.0", tk.END)
            self.text_asm.insert("1.0", content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def on_save_asm(self):
        path = filedialog.asksaveasfilename(
            title="Save assembly file",
            defaultextension=".asm",
            filetypes=[("Assembly files", "*.asm"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            content = self.text_asm.get("1.0", tk.END)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    # ------------------------------------------------------------------
    # Core action: assemble & run
    # ------------------------------------------------------------------
    def on_assemble_and_run(self):
        asm_text = self.text_asm.get("1.0", tk.END)

        try:
            dump_start = int(self.dump_start_var.get())
            dump_end = int(self.dump_end_var.get())
            if dump_start < 0 or dump_end <= dump_start:
                raise ValueError("Invalid dump range")
        except ValueError:
            messagebox.showerror(
                "Invalid input", "Dump start/end must be valid integers and start < end."
            )
            return

        try:
            # 1) parse assembly
            program = parse_program(asm_text)

            # 2) encode to machine code (in memory)
            binary = encode_program(program)

            # 3) run interpreter logic in memory
            vm = VM()
            self._execute_binary_on_vm(binary, vm)

            # 4) dump memory range
            fragment = vm.mem[dump_start:dump_end]

            # 5) show result
            self._show_dump(program, fragment, dump_start)

        except Exception as e:
            messagebox.showerror("Error", f"Error during assemble/run:\n{e}")

    # ------------------------------------------------------------------
    # VM execution (same semantics as interpreter.py)
    # ------------------------------------------------------------------
    def _execute_binary_on_vm(self, binary: bytes, vm: VM):
        ip = 0
        while ip + INSTR_SIZE <= len(binary):
            raw = binary[ip : ip + INSTR_SIZE]
            ip += INSTR_SIZE

            instr = decode_instr(raw)

            if instr.op == Op.CONST:
                vm.store_word(instr.C, instr.B)

            elif instr.op == Op.LOAD:
                addr = vm.load_word(instr.B)
                value = vm.load_word(addr)
                vm.store_word(instr.C, value)

            elif instr.op == Op.STORE:
                addrB = vm.load_word(instr.B)
                value = vm.load_word(addrB)
                a1 = vm.load_word(instr.C)
                a2 = vm.load_word(a1)
                vm.store_word(a2, value)

            elif instr.op == Op.BITREV:
                base = vm.load_word(instr.B)
                src_addr = base + instr.D
                value = vm.load_word(src_addr)
                vm.store_word(instr.C, bitreverse64(value))

            else:
                raise RuntimeError(f"Unknown op: {instr.op}")

    # ------------------------------------------------------------------
    # Output formatting
    # ------------------------------------------------------------------
    def _show_dump(self, program, fragment, start_addr: int):
        self.text_output.configure(state=tk.NORMAL)
        self.text_output.delete("1.0", tk.END)

        self.text_output.insert(tk.END, "=== Program (IR) ===\n")
        for i, instr in enumerate(program):
            self.text_output.insert(tk.END, f"{i:3d}: {instr}\n")

        self.text_output.insert(tk.END, "\n=== Memory dump ===\n")
        for i, val in enumerate(fragment):
            addr = start_addr + i
            self.text_output.insert(tk.END, f"[{addr:4d}] = {val}\n")

        self.text_output.configure(state=tk.NORMAL)

    # ------------------------------------------------------------------
    # Default example program
    # ------------------------------------------------------------------
    def _insert_default_example(self):
        example = """; Example program: bit-reverse 9-element vector

; Base address of input vector
CONST 100, 10

; Base address of output vector
CONST 200, 11

; Input vector (9 elements)
CONST 1,   100
CONST 2,   101
CONST 3,   102
CONST 4,   103
CONST 5,   104
CONST 6,   105
CONST 7,   106
CONST 8,   107
CONST 9,   108

; Bit-reverse each element
BITREV 10, 0, 200
BITREV 10, 1, 201
BITREV 10, 2, 202
BITREV 10, 3, 203
BITREV 10, 4, 204
BITREV 10, 5, 205
BITREV 10, 6, 206
BITREV 10, 7, 207
BITREV 10, 8, 208
"""
        self.text_asm.insert("1.0", example)


def main():
    app = UVMGui()
    app.mainloop()


if __name__ == "__main__":
    main()
