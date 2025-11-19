let mediaRecorder;
let chunks = [];
let blob;

const recBtn = document.getElementById("btnRec");
const stopBtn = document.getElementById("btnStop");
const sendBtn = document.getElementById("btnSend");
const player = document.getElementById("player");
const statusEl = document.getElementById("status");
const output = document.getElementById("output");

recBtn.onclick = async () => {
  chunks = [];
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.onstop = () => {
      blob = new Blob(chunks, { type: "audio/webm" });
      player.src = URL.createObjectURL(blob);
      sendBtn.disabled = false;
    };
    mediaRecorder.start();
    statusEl.textContent = "Gravando…";
    recBtn.disabled = true;
    stopBtn.disabled = false;
  } catch (e) {
    statusEl.textContent = "Erro ao acessar microfone: " + e.message;
  }
};

stopBtn.onclick = () => {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    statusEl.textContent = "Gravação finalizada.";
    recBtn.disabled = false;
    stopBtn.disabled = true;
  }
};

sendBtn.onclick = async () => {
  if (!blob) return;
  statusEl.textContent = "Enviando para transcrever…";
  sendBtn.disabled = true;

  const form = new FormData();
  form.append("file", blob, "gravacao.webm");

  const res = await fetch("/transcribe", { method: "POST", body: form });
  const data = await res.json();

  statusEl.textContent = data.ok ? "Transcrição concluída." : "Falhou.";
  output.textContent = JSON.stringify(data, null, 2);
  sendBtn.disabled = false;
};
