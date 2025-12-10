import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from assembler_ir import parse_program
from encode import encode_program


class AssemblerEncodingTests(unittest.TestCase):
    def assemble_bytes(self, source: str) -> bytes:
        program = parse_program(source)
        binary = encode_program(program)
        self.assertEqual(len(binary), 11 * len(program))
        return binary

    def test_const_encoding_matches_spec(self):
        expected = bytes(
            [0xE4, 0x35, 0x00, 0x48, 0x0E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        )
        result = self.assemble_bytes("CONST 862, 457")
        self.assertEqual(result, expected)

    def test_load_encoding_matches_spec(self):
        expected = bytes(
            [0xDC, 0x13, 0x00, 0x80, 0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        )
        result = self.assemble_bytes("LOAD 317, 486")
        self.assertEqual(result, expected)

    def test_store_encoding_matches_spec(self):
        expected = bytes(
            [0x23, 0x35, 0x00, 0xC0, 0xDB, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        )
        result = self.assemble_bytes("STORE 850, 879")
        self.assertEqual(result, expected)

    def test_bitreverse_encoding_matches_spec(self):
        expected = bytes(
            [0x59, 0x07, 0x00, 0x80, 0x64, 0x00, 0x00, 0x2B, 0x00, 0x00, 0x00]
        )
        result = self.assemble_bytes("BITREV 117, 43, 402")
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
