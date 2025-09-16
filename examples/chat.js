document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("chat-container");

  const API_URL = container.getAttribute("data-api");
  const client_id = container.getAttribute("data-client") || "defaultclient";
  const initial_greeting = container.getAttribute("data-greeting") || "Hello! How can I help you today?";

  const form = document.getElementById("query-form");
  const input = document.getElementById("user-input");
  const chatWindow = document.getElementById("chat-window");

  let session_id = sessionStorage.getItem("session_id");
  if (!session_id) {
    session_id = crypto.randomUUID();
    sessionStorage.setItem("session_id", session_id);
  }

  function addMessage(role, text) {
    const msg = document.createElement("div");
    msg.classList.add("message", role, "fade-in");
    msg.innerHTML = text.replace(/<a\b(?![^>]*\btarget=)/gi, '<a target="_blank" ');
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function createTypingIndicator() {
    const typing = document.createElement("div");
    typing.className = "assistant typing";
    typing.innerHTML = `<span>Typing</span><span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>`;
    return typing;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    addMessage("user", message);
    input.value = "";

    const typingIndicator = createTypingIndicator();
    chatWindow.appendChild(typingIndicator);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id, client_id, question: message }),
      });

      const data = await response.json();
      typingIndicator.remove();
      addMessage("assistant", data.answer || "No answer received.");
    } catch (err) {
      typingIndicator.remove();
      addMessage("assistant", "Error: Unable to connect to server.");
    }
  });

  addMessage("assistant", initial_greeting);

  function setAppHeight() {
    const doc = document.documentElement;
    doc.style.setProperty('--app-height', `${window.innerHeight}px`);
  }
  setAppHeight();
  window.addEventListener('resize', setAppHeight);
  window.addEventListener('orientationchange', setAppHeight);
});