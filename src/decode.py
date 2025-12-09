from model import Op, Instr


def read_u63_from_11(data: bytes) -> int:
    val = 0
    for i in range(11):
        val |= data[i] << (8 * i)
    return val


def decode_instr(data: bytes) -> Instr:
    if len(data) != 11:
        raise ValueError("Instruction must be exactly 11 bytes")

    v = read_u63_from_11(data)
    A = v & 0xF

    if A == 4:
        B = (v >> 4) & ((1 << 23) - 1)
        C = (v >> 27) & ((1 << 26) - 1)
        return Instr(Op.CONST, A, B, C)

    if A in (12, 3, 9):
        B = (v >> 4) & ((1 << 26) - 1)
        C = (v >> 30) & ((1 << 26) - 1)
        D = (v >> 56) & ((1 << 7) - 1)

        if A == 12:
            return Instr(Op.LOAD, A, B, C)
        if A == 3:
            return Instr(Op.STORE, A, B, C)
        if A == 9:
            return Instr(Op.BITREV, A, B, C, D)

    raise ValueError(f"Unknown opcode A={A}")
