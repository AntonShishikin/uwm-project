; ==========================================================
; tests.asm
; Sample assembly program for testing all instructions
; ==========================================================

; Load constant values into memory
CONST 862, 457
CONST 317, 100
CONST 850, 200
CONST 117, 300

; Demonstrate LOAD instruction
; mem[486] = mem[mem[100]]    -> will read value from mem[317]
LOAD 100, 486

; Demonstrate STORE instruction
; mem[mem[mem[879]]] = mem[mem[200]]
CONST 879, 400
CONST 123, 500
STORE 200, 400

; Demonstrate BITREV instruction
; mem[402] = bitreverse( mem[mem[300] + 43] )
BITREV 300, 43, 402
