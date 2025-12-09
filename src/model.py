from dataclasses import dataclass
from enum import Enum, auto


class Op(Enum):
    CONST = auto()      # A = 4
    LOAD = auto()       # A = 12
    STORE = auto()      # A = 3
    BITREV = auto()     # A = 9


@dataclass
class Instr:
    op: Op
    A: int
    B: int
    C: int
    D: int = 0
