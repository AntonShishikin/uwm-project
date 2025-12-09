import re
from typing import List
from model import Op, Instr


def parse_line(line: str) -> Instr | None:
    # Remove comments
    line = line.split(";", 1)[0].strip()

    if not line:
        return None

    match = re.match(r"([A-Za-z]+)\s*(.*)", line)
    if not match:
        raise ValueError(f"Invalid line: {line}")

    mnemonic = match.group(1).upper()
    args_raw = match.group(2)

    args = [a.strip() for a in args_raw.split(",") if a.strip()]
    nums = [int(a) for a in args]

    if mnemonic == "CONST":
        if len(nums) != 2:
            raise ValueError("CONST requires 2 arguments")
        value, addr = nums
        return Instr(Op.CONST, 4, value, addr)

    if mnemonic == "LOAD":
        if len(nums) != 2:
            raise ValueError("LOAD requires 2 arguments")
        addrB, addrC = nums
        return Instr(Op.LOAD, 12, addrB, addrC)

    if mnemonic == "STORE":
        if len(nums) != 2:
            raise ValueError("STORE requires 2 arguments")
        addrB, addrC = nums
        return Instr(Op.STORE, 3, addrB, addrC)

    if mnemonic == "BITREV":
        if len(nums) != 3:
            raise ValueError("BITREV requires 3 arguments")
        addrB, offset, addrC = nums
        return Instr(Op.BITREV, 9, addrB, addrC, offset)

    raise ValueError(f"Unknown instruction {mnemonic}")


def parse_program(text: str) -> List[Instr]:
    program = []
    for line in text.splitlines():
        instr = parse_line(line)
        if instr:
            program.append(instr)
    return program
