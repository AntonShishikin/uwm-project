; ==========================================================
; vec9.asm
; Bit-reverse each element of a 9-element vector
; ==========================================================

; ----------------------------------------------------------
; Base addresses
; ----------------------------------------------------------

; Address of input vector
CONST 100, 10

; Address of output vector
CONST 200, 11

; ----------------------------------------------------------
; Input vector values (9 elements)
; ----------------------------------------------------------

CONST 1,   100
CONST 2,   101
CONST 3,   102
CONST 4,   103
CONST 5,   104
CONST 6,   105
CONST 7,   106
CONST 8,   107
CONST 9,   108


; ----------------------------------------------------------
; Bit-reverse each element using BITREV instruction
; BITREV addrB, offset, output_addr
; ----------------------------------------------------------

; Vector[0]
BITREV 10, 0, 200

; Vector[1]
BITREV 10, 1, 201

; Vector[2]
BITREV 10, 2, 202

; Vector[3]
BITREV 10, 3, 203

; Vector[4]
BITREV 10, 4, 204

; Vector[5]
BITREV 10, 5, 205

; Vector[6]
BITREV 10, 6, 206

; Vector[7]
BITREV 10, 7, 207

; Vector[8]
BITREV 10, 8, 208
