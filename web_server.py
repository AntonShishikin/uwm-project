#!/usr/bin/env python3
"""Simple HTTP interface for the UVM assembler + VM."""

from __future__ import annotations

import argparse
import json
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import List, Tuple

BASE_DIR = Path(__file__).parent
SRC_DIR = BASE_DIR / "src"
WEB_DIR = BASE_DIR / "web"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from assembler_ir import parse_program
from bitutils import bitreverse64
from decode import decode_instr
from encode import encode_program
from model import Op
from vm import VM

INSTR_SIZE = 11


def assemble_and_run(
    asm_text: str, dump_start: int, dump_end: int
) -> Tuple[List[str], List[int]]:
    if dump_start < 0 or dump_end <= dump_start:
        raise ValueError("Dump start/end must satisfy 0 <= start < end.")

    program = parse_program(asm_text)
    binary = encode_program(program)

    vm = VM()
    ip = 0
    while ip + INSTR_SIZE <= len(binary):
        raw = binary[ip : ip + INSTR_SIZE]
        ip += INSTR_SIZE

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
            src_addr = base + instr.D
            value = vm.load_word(src_addr)
            vm.store_word(instr.C, bitreverse64(value))
        else:
            raise RuntimeError(f"Unknown op: {instr.op}")

    fragment = vm.mem[dump_start:dump_end]

    return [str(instr) for instr in program], fragment


class UVMRequestHandler(SimpleHTTPRequestHandler):
    """Rudimentary API + static file handler."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_POST(self):
        if self.path != "/api/run":
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid Content-Length header")
            return

        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body or b"{}")
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON payload"}, HTTPStatus.BAD_REQUEST)
            return

        asm_text = payload.get("source", "")
        dump_start = payload.get("dumpStart")
        dump_end = payload.get("dumpEnd")

        if not isinstance(asm_text, str):
            self._send_json({"error": "source must be a string"}, HTTPStatus.BAD_REQUEST)
            return

        try:
            dump_start = int(dump_start)
            dump_end = int(dump_end)
        except (TypeError, ValueError):
            self._send_json(
                {"error": "dumpStart and dumpEnd must be integers"},
                HTTPStatus.BAD_REQUEST,
            )
            return

        try:
            program_ir, memory_fragment = assemble_and_run(
                asm_text, dump_start, dump_end
            )
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return

        payload = {
            "program": program_ir,
            "dumpStart": dump_start,
            "dumpEnd": dump_end,
            "memory": [
                {"address": dump_start + idx, "value": value}
                for idx, value in enumerate(memory_fragment)
            ],
        }

        self._send_json(payload, HTTPStatus.OK)

    def _send_json(self, payload, status: HTTPStatus):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    parser = argparse.ArgumentParser(
        description="Run the browser-based interface for the UVM project."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Hostname to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    args = parser.parse_args()

    if not WEB_DIR.is_dir():
        raise SystemExit(f"Static directory '{WEB_DIR}' is missing.")

    server = ThreadingHTTPServer((args.host, args.port), UVMRequestHandler)
    print(f"Serving UI on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
