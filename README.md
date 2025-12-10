# Cross-Platform Virtual Machine & Assembler

Solution for the university course **“Cross-Platform Software Systems Development”**.  
Ниже приводится подробное описание на русском и английском языках.

---

## 🇷🇺 Описание проекта

### Что реализовано

- **UVM ISA** — учебная 64-битная архитектура с набором инструкций `CONST`, `LOAD`, `STORE`, `BITREV`.
- **Ассемблер** (`src/assembler.py`) — преобразует `.asm` в бинарный формат (11 байт на инструкцию).
- **Кодеки** (`src/encode.py`, `src/decode.py`) — кодирование и декодирование команд.
- **Виртуальная машина** (`src/vm.py`, `src/interpreter.py`) — исполняет бинарные программы и может сохранять дамп памяти.
- **Tkinter GUI** (`src/gui.py`, запускается через `build.py`) — визуальный редактор кода и просмотр дампа памяти.
- **Веб-интерфейс** (`web_server.py` + каталог `web/`) — запуск проекта в браузере без внешних зависимостей.

### Структура репозитория

| Путь | Назначение |
|------|-----------|
| `src/assembler_ir.py`, `model.py` | Парсер исходного кода и описание IR/Op. |
| `src/assembler.py` | CLI-ассемблер: `python3 src/assembler.py input.asm program.bin`. |
| `src/interpreter.py` | CLI-интерпретатор бинарников. |
| `src/gui.py` | Настольное приложение на Tkinter. |
| `web_server.py`, `web/` | HTTP API и SPA-интерфейс. |
| `examples/`, `dumps/` | Примеры программ и дампов. |

### Требования

- Python **3.10+**.
- Не требуется установка сторонних библиотек (используется стандартная библиотека).

### Способы запуска

1. **Командная строка (ассемблер + интерпретатор)**
   ```bash
   # Ассемблер: текст -> бинарник
   python3 src/assembler.py examples/sample.asm sample.bin

   # Интерпретатор: бинарник -> дамп памяти
   python3 src/interpreter.py sample.bin dump.json 0 64
   ```
   Флаг `--test` у ассемблера печатает IR и сырые байты.

2. **Tkinter GUI**
   ```bash
   python3 build.py
   # или напрямую
   python3 src/gui.py
   ```
   Интерфейс позволяет открывать/сохранять `.asm`, запускать программу и видеть IR + память.

3. **Веб-интерфейс**
   ```bash
   python3 web_server.py --host 127.0.0.1 --port 8000
   ```
   Затем откройте `http://127.0.0.1:8000`. Страница `web/index.html` содержит редактор кода, диапазон памяти и таблицу результатов.

### Пример исходника

```asm
; Пример: реверс битов у 9 элементов
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
```

---

## 🇬🇧 English overview

### Implemented modules

- **UVM ISA** — educational instruction set with `CONST`, `LOAD`, `STORE`, `BITREV`.
- **Assembler** (`src/assembler.py`) — converts `.asm` to binaries (11 bytes per instruction).
- **Encoders/decoders** (`src/encode.py`, `src/decode.py`) — instruction packing/unpacking helpers.
- **Virtual machine & interpreter** (`src/vm.py`, `src/interpreter.py`) — executes binaries and dumps memory slices.
- **Tkinter GUI** (`src/gui.py`, launched via `build.py`) — desktop editor + execution panel.
- **Browser UI** (`web_server.py` + `web/`) — HTTP API plus static single-page app.

### Repo layout

| Path | Description |
|------|-------------|
| `src/assembler_ir.py`, `model.py` | Parsing logic and intermediate representation. |
| `src/assembler.py` | CLI assembler: `python3 src/assembler.py input.asm program.bin`. |
| `src/interpreter.py` | CLI interpreter dumping memory to JSON. |
| `src/gui.py` | Tkinter desktop UI. |
| `web_server.py`, `web/` | HTTP server + static SPA. |
| `examples/`, `dumps/` | Sample programs and dumps. |

### Requirements

- Python **3.10+**.
- No third-party dependencies (stdlib only).

### How to run

1. **Command line (assembler + interpreter)**
   ```bash
   python3 src/assembler.py examples/sample.asm sample.bin
   python3 src/interpreter.py sample.bin dump.json 0 64
   ```
   Use `--test` to print the IR and raw bytes after assembling.

2. **Tkinter GUI**
   ```bash
   python3 build.py
   # or
   python3 src/gui.py
   ```
   The GUI bundles an editor, assemble/run button, and memory dump output.

3. **Browser UI**
   ```bash
   python3 web_server.py --host 127.0.0.1 --port 8000
   ```
   Open the printed URL (default `http://127.0.0.1:8000`). The SPA lets you edit code, configure dump ranges, and visualize IR/memory.

### Assembly snippet

```asm
CONST 10, 0
LOAD  5, 2
STORE 4, 3
BITREV 10, 1, 20
```
