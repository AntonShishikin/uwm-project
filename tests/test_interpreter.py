import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from assembler_ir import parse_program
from bitutils import bitreverse64
from encode import encode_program
from interpreter import run_program


BITREV_PROGRAM = """
CONST 100, 10
CONST 200, 11
CONST 1,   100
CONST 2,   101
CONST 3,   102
CONST 4,   103
CONST 5,   104
CONST 6,   105
CONST 7,   106
CONST 8,   107
CONST 9,   108
BITREV 10, 0, 200
BITREV 10, 1, 201
BITREV 10, 2, 202
BITREV 10, 3, 203
BITREV 10, 4, 204
BITREV 10, 5, 205
BITREV 10, 6, 206
BITREV 10, 7, 207
BITREV 10, 8, 208
""".strip()


STORE_PROGRAM = """
CONST 300, 20
CONST 123, 300
CONST 500, 21
CONST 400, 500
STORE 20, 21
""".strip()


class InterpreterIntegrationTests(unittest.TestCase):
    def assemble_to_binary(self, asm_source: str) -> bytes:
        program = parse_program(asm_source)
        return encode_program(program)

    def run_and_dump(self, binary: bytes, start: int, end: int) -> list[int]:
        with tempfile.TemporaryDirectory() as tmpdir:
            bin_path = Path(tmpdir) / "program.bin"
            dump_path = Path(tmpdir) / "dump.json"
            bin_path.write_bytes(binary)

            buf = io.StringIO()
            with redirect_stdout(buf):
                run_program(str(bin_path), str(dump_path), start, end)

            with dump_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)

    def test_bitreverse_pipeline(self):
        binary = self.assemble_to_binary(BITREV_PROGRAM)
        dump = self.run_and_dump(binary, 200, 209)
        expected = [bitreverse64(i) for i in range(1, 10)]
        self.assertEqual(dump, expected)

    def test_store_instruction_moves_value(self):
        binary = self.assemble_to_binary(STORE_PROGRAM)
        dump = self.run_and_dump(binary, 398, 402)
        self.assertEqual(dump[2], 123)


if __name__ == "__main__":
    unittest.main()
