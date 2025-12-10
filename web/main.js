const form = document.getElementById("run-form");
const asmInput = document.getElementById("asm-source");
const dumpStartInput = document.getElementById("dump-start");
const dumpEndInput = document.getElementById("dump-end");
const statusEl = document.getElementById("status");
const programOut = document.getElementById("program-output");
const memoryOut = document.getElementById("memory-output");

const defaultStatus = "Готово.";
setStatus(defaultStatus);
renderProgram([]);
renderMemory([]);

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitBtn = form.querySelector("button");
  submitBtn.disabled = true;
  setStatus("Сборка и выполнение...", false);

  const payload = {
    source: asmInput.value,
    dumpStart: dumpStartInput.value,
    dumpEnd: dumpEndInput.value,
  };

  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Server error");
    }

    renderProgram(data.program);
    renderMemory(data.memory);
    setStatus(
      `Готово. Выведено ${data.memory.length} слов памяти (${data.dumpStart}..${data.dumpEnd}).`
    );
  } catch (err) {
    renderProgram([]);
    renderMemory([]);
    setStatus(err.message || "Неизвестная ошибка", true);
  } finally {
    submitBtn.disabled = false;
  }
});

function renderProgram(lines) {
  if (!Array.isArray(lines) || lines.length === 0) {
    programOut.textContent = "(нет данных)";
    return;
  }

  programOut.textContent = lines
    .map((line, idx) => `${String(idx).padStart(3, "0")}: ${line}`)
    .join("\n");
}

function renderMemory(cells) {
  memoryOut.innerHTML = "";

  if (!Array.isArray(cells) || cells.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 2;
    td.textContent = "(нет данных)";
    tr.appendChild(td);
    memoryOut.appendChild(tr);
    return;
  }

  for (const cell of cells) {
    const tr = document.createElement("tr");
    const addr = document.createElement("td");
    addr.textContent = cell.address;
    const val = document.createElement("td");
    val.textContent = cell.value;
    tr.append(addr, val);
    memoryOut.appendChild(tr);
  }
}

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", Boolean(isError));
}
