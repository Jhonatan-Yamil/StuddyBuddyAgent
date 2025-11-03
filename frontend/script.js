const API_BASE = ""; 
const chatBox = document.getElementById("chat-box");
const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  addMessage(text, "user");
  input.value = "";

  const loading = addMessage("Escribiendo...", "bot");

  try {
    const res = await fetch(`${API_BASE}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: text }),
    });
    const data = await res.json();
    chatBox.removeChild(loading);
    addMessage(data.response || "Sin respuesta", "bot");
  } catch (err) {
    console.error(err);
    chatBox.removeChild(loading);
    addMessage("Error al conectar con el servidor", "bot");
  }
});

document.getElementById("pdf-upload").addEventListener("change", async (e) => {
  const files = e.target.files;
  if (!files.length) return;
  addMessage("Subiendo PDF...", "bot");

  const formData = new FormData();
  for (const file of files) formData.append("files", file);

  const res = await fetch(`${API_BASE}/upload-pdf`, { method: "POST", body: formData });
  const data = await res.json();

  addMessage("Ya puedes hacer preguntas sobre el contenido de los PDFs.", "bot");
});

document.getElementById("image-upload").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  addMessage("Analizando imagen...", "bot");

  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload-image`, { method: "POST", body: formData });
  const data = await res.json();

  addMessage("Ya puedes hacer preguntas sobre el contenido de la imagen.", "bot");
});

document.getElementById("audio-upload").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  addMessage("Escuchando audio...", "bot");

  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/speech-to-text`, { method: "POST", body: formData });
  const data = await res.json();

  addMessage("Ya puedes hacer preguntas sobre el contenido del audio.", "bot");
});

function addMessage(text, sender) {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.innerText = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
  return msg;
}
