import argparse
from assembler_ir import parse_program
from encode import encode_program


def main():
    parser = argparse.ArgumentParser(description="UVM Assembler")
    parser.add_argument("src", help="Assembly source file")
    parser.add_argument("outbin", help="Output binary file")
    parser.add_argument("--test", action="store_true", help="Print instruction dump")
    args = parser.parse_args()

    with open(args.src, "r", encoding="utf-8") as f:
        text = f.read()

    program = parse_program(text)

    if args.test:
        print("----- IR DUMP -----")
        for i, instr in enumerate(program):
            print(f"{i}: {instr}")

    binary = encode_program(program)

    with open(args.outbin, "wb") as f:
        f.write(binary)

    print(f"Compiled {len(program)} instructions into {args.outbin}")

    if args.test:
        print("\n----- BYTE DUMP -----")
        for i, b in enumerate(binary):
            if i % 11 == 0:
                print(f"\nInstr {i // 11}: ", end="")
            print(f"0x{b:02X} ", end="")
        print()


if __name__ == "__main__":
    main()
