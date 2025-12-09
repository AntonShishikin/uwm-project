from model import Op, Instr


def encode_const(ins: Instr) -> int:
    val = 0
    val |= (ins.A & 0xF)
    val |= (ins.B & ((1 << 23) - 1)) << 4
    val |= (ins.C & ((1 << 26) - 1)) << 27
    return val


def encode_BC(ins: Instr) -> int:
    val = 0
    val |= (ins.A & 0xF)
    val |= (ins.B & ((1 << 26) - 1)) << 4
    val |= (ins.C & ((1 << 26) - 1)) << 30
    return val


def encode_bitreverse(ins: Instr) -> int:
    val = encode_BC(ins)
    val |= (ins.D & ((1 << 7) - 1)) << 56
    return val


def encode_instr(ins: Instr) -> bytes:
    if ins.op == Op.CONST:
        word = encode_const(ins)
    elif ins.op in (Op.LOAD, Op.STORE):
        word = encode_BC(ins)
    elif ins.op == Op.BITREV:
        word = encode_bitreverse(ins)
    else:
        raise ValueError("Invalid opcode")

    return bytes((word >> (8 * i)) & 0xFF for i in range(11))


def encode_program(program: list[Instr]) -> bytes:
    data = bytearray()
    for ins in program:
        data += encode_instr(ins)
    return bytes(data)
