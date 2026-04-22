function addMessage(text, sender) {
  const chatBox = document.getElementById("chat-box");

  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.innerText = text;

  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
  const input = document.getElementById("user-input");
  const text = input.value.trim();

  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message: text })
  })
  .then(res => res.json())
  .then(data => {
    addMessage(data.response, "bot");
  })
  .catch(err => {
    addMessage("Server error. Check backend.", "bot");
    console.error(err);
  });
}

// ENTER KEY SUPPORT (CRITICAL)
document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("user-input");

  if (!input) {
    console.error("Input not found");
    return;
  }

  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });
});