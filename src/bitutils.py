def bitreverse64(x: int) -> int:
    result = 0
    for i in range(64):
        if (x >> i) & 1:
            result |= 1 << (63 - i)
    return result
