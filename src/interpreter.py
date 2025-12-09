import argparse
import json
from vm import VM
from decode import decode_instr
from bitutils import bitreverse64
from model import Op


def run_program(
    bin_path: str,
    dump_path: str,
    dump_start: int,
    dump_end: int,
):
    vm = VM()

    with open(bin_path, "rb") as f:
        code = f.read()

    ip = 0

    while ip + 11 <= len(code):
        raw = code[ip : ip + 11]
        ip += 11

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
            src = base + instr.D
            value = vm.load_word(src)
            vm.store_word(instr.C, bitreverse64(value))

        else:
            raise RuntimeError("Unknown instruction")

    fragment = vm.mem[dump_start:dump_end]

    with open(dump_path, "w", encoding="utf-8") as f:
        json.dump(fragment, f, indent=2)

    print(f"Memory dumped to {dump_path}")


def main():
    parser = argparse.ArgumentParser(description="UVM Interpreter")
    parser.add_argument("bin", help="Program binary")
    parser.add_argument("dump", help="Output JSON memory dump")
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    args = parser.parse_args()

    run_program(args.bin, args.dump, args.start, args.end)


if __name__ == "__main__":
    main()
