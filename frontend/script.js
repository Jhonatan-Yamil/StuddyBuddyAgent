const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

const API_URL = "/generate"; 

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const userMessage = input.value.trim();
  if (!userMessage) return;

  addMessage(userMessage, "user");
  input.value = "";

  const loadingMsg = addMessage("Escribiendo...", "bot");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: userMessage }),
    });

    const data = await response.json();

    chatBox.removeChild(loadingMsg);

    addMessage(data.response, "bot");
  } catch (error) {
    console.error("Error:", error);
    chatBox.removeChild(loadingMsg);
    addMessage("Error al conectar con el servidor.", "bot");
  }
});

function addMessage(text, sender) {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.innerText = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
  return msg;
}
