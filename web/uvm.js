const OP_INFO = {
  CONST: { a: 4, enumValue: 1, argCount: 2 },
  LOAD: { a: 12, enumValue: 2, argCount: 2 },
  STORE: { a: 3, enumValue: 3, argCount: 2 },
  BITREV: { a: 9, enumValue: 4, argCount: 3 },
};

const MEM_SIZE = 2048;
const MASK64 = (1n << 64n) - 1n;

export function assembleAndRun(source, dumpStart, dumpEnd) {
  if (typeof source !== "string") {
    throw new Error("Исходный код должен быть строкой.");
  }

  const start = toInteger(dumpStart, "dumpStart");
  const end = toInteger(dumpEnd, "dumpEnd");
  if (start < 0 || end <= start) {
    throw new Error("Диапазон дампа должен удовлетворять 0 <= start < end.");
  }
  if (end > MEM_SIZE) {
    throw new Error(`Конец дампа (${end}) выходит за пределы памяти (${MEM_SIZE}).`);
  }

  const program = parseProgram(source);
  const vm = new VM();

  for (const instr of program) {
    executeInstruction(vm, instr);
  }

  const fragment = [];
  for (let addr = start; addr < end; addr++) {
    fragment.push({
      address: addr,
      value: vm.read(addr).toString(),
    });
  }

  return {
    program: program.map(formatInstr),
    dumpStart: start,
    dumpEnd: end,
    memory: fragment,
  };
}

export function parseProgram(text) {
  const program = [];
  for (const line of text.split(/\r?\n/)) {
    const instr = parseLine(line);
    if (instr) {
      program.push(instr);
    }
  }
  return program;
}

function parseLine(line) {
  const withoutComment = line.split(";", 1)[0].trim();
  if (!withoutComment) {
    return null;
  }

  const match = withoutComment.match(/^([A-Za-z]+)\s*(.*)$/);
  if (!match) {
    throw new Error(`Неверная строка: "${line}"`);
  }

  const mnemonic = match[1].toUpperCase();
  const argsRaw = match[2];
  const args = argsRaw
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean)
    .map((value) => toInteger(value, `аргумент ${mnemonic}`));

  const info = OP_INFO[mnemonic];
  if (!info) {
    throw new Error(`Неизвестная инструкция ${mnemonic}`);
  }
  if (args.length !== info.argCount) {
    throw new Error(`Инструкция ${mnemonic} принимает ${info.argCount} арг.`);
  }

  if (mnemonic === "CONST") {
    const [value, addr] = args;
    return { op: mnemonic, A: info.a, B: value, C: addr, D: 0 };
  }

  if (mnemonic === "BITREV") {
    const [addrB, offset, addrC] = args;
    return { op: mnemonic, A: info.a, B: addrB, C: addrC, D: offset };
  }

  const [addrB, addrC] = args;
  return { op: mnemonic, A: info.a, B: addrB, C: addrC, D: 0 };
}

class VM {
  constructor() {
    this.mem = new Array(MEM_SIZE).fill(0n);
  }

  read(addr) {
    this.#checkAddr(addr);
    return this.mem[addr];
  }

  write(addr, value) {
    this.#checkAddr(addr);
    const big = typeof value === "bigint" ? value : BigInt(value);
    this.mem[addr] = big & MASK64;
  }

  resolvePointer(value) {
    const big = typeof value === "bigint" ? value : BigInt(value);
    if (big < 0n || big >= BigInt(MEM_SIZE)) {
      throw new Error(`Адрес ${big} вне диапазона памяти`);
    }
    return Number(big);
  }

  #checkAddr(addr) {
    if (addr < 0 || addr >= MEM_SIZE) {
      throw new Error(`Адрес ${addr} вне диапазона памяти`);
    }
  }
}

function executeInstruction(vm, instr) {
  switch (instr.op) {
    case "CONST":
      vm.write(instr.C, instr.B);
      break;

    case "LOAD": {
      const ptr = vm.read(instr.B);
      const addr = vm.resolvePointer(ptr);
      const value = vm.read(addr);
      vm.write(instr.C, value);
      break;
    }

    case "STORE": {
      const ptrToValue = vm.read(instr.B);
      const valueAddr = vm.resolvePointer(ptrToValue);
      const value = vm.read(valueAddr);

      const ptrToPtr = vm.read(instr.C);
      const ptrAddr = vm.resolvePointer(ptrToPtr);
      const finalAddrBig = vm.read(ptrAddr);
      const finalAddr = vm.resolvePointer(finalAddrBig);

      vm.write(finalAddr, value);
      break;
    }

    case "BITREV": {
      const basePtr = vm.read(instr.B);
      const base = vm.resolvePointer(basePtr);
      const srcAddr = base + instr.D;
      vm.resolvePointer(srcAddr); // bounds check
      const value = vm.read(srcAddr);
      vm.write(instr.C, bitreverse64(value));
      break;
    }

    default:
      throw new Error(`Неизвестная операция ${instr.op}`);
  }
}

function bitreverse64(x) {
  let value = x;
  if (typeof value !== "bigint") {
    value = BigInt(value);
  }

  let result = 0n;
  for (let i = 0n; i < 64n; i++) {
    if ((value >> i) & 1n) {
      result |= 1n << (63n - i);
    }
  }
  return result;
}

function toInteger(value, label) {
  const num = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(num) || !Number.isInteger(num)) {
    throw new Error(`${label} должен быть целым числом`);
  }
  return num;
}

function formatInstr(instr) {
  const info = OP_INFO[instr.op];
  return `Instr(op=<Op.${instr.op}: ${info.enumValue}>, A=${instr.A}, B=${instr.B}, C=${instr.C}, D=${instr.D})`;
}
