MEM_SIZE = 2048


class VM:
    def __init__(self):
        self.mem = [0] * MEM_SIZE

    def load_word(self, addr: int) -> int:
        return self.mem[addr]

    def store_word(self, addr: int, value: int):
        self.mem[addr] = value & ((1 << 64) - 1)
