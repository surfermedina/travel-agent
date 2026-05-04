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

  const formatText = (text) =>
    text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>")
      .replace(/<a\b(?![^>]*\btarget=)/gi, '<a target="_blank" ');

  // const streamUrl = new URL(API_URL, window.location.href);
  // streamUrl.pathname = streamUrl.pathname.replace(/\/ask$/, "/ask_stream");
  const streamUrl = new URL("/ask_stream", API_URL);

  function addMessage(role, text) {
    const msg = document.createElement("div");
    msg.classList.add("message", role, "fade-in");
    msg.innerHTML = formatText(text);
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function createTypingIndicator() {
    const typing = document.createElement("div");
    typing.className = "assistant typing";
    typing.innerHTML = `Thinking<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>`;
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
      const res = await fetch(streamUrl.toString(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: message, client_id, session_id })
      });

      if (!res.ok || !res.body) {
        throw new Error(`Streaming request failed: ${res.status} ${res.statusText}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      let buf = "";
      let fullText = "";
      let msg = null;
      let lastFlush = 0;
      const FLUSH_MS = 50;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buf += decoder.decode(value, { stream: true });

        let idx;
        while ((idx = buf.indexOf("\n")) >= 0) {
          const line = buf.slice(0, idx).trim();
          buf = buf.slice(idx + 1);
          if (!line) continue;

          const evt = JSON.parse(line);

          if (evt.type === "delta") {
            if (typingIndicator.isConnected) typingIndicator.remove();

            if (!msg) {
              msg = document.createElement("div");
              msg.classList.add("message", "assistant", "fade-in");
              chatWindow.appendChild(msg);
            }

            fullText += evt.text;

            const now = Date.now();
            if (now - lastFlush > FLUSH_MS) {
              msg.innerHTML = formatText(fullText) + '<span class="cursor">|</span>';
              chatWindow.scrollTop = chatWindow.scrollHeight;
              lastFlush = now;
            }
          }

          if (evt.type === "final") {
            if (typingIndicator.isConnected) typingIndicator.remove();

            if (!msg) {
              msg = document.createElement("div");
              msg.classList.add("message", "assistant", "fade-in");
              chatWindow.appendChild(msg);
            }

            msg.innerHTML = formatText(fullText);
            chatWindow.scrollTop = chatWindow.scrollHeight;
            return;
          }
        }
      }
    } catch (err) {
      if (typingIndicator.isConnected) typingIndicator.remove();
      addMessage("assistant", "Error: Unable to connect to server.");
    }
  });

  document.querySelectorAll(".prompt-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      input.value = btn.innerText;
      form.dispatchEvent(new Event("submit"));
    });
  });

  addMessage("assistant", initial_greeting);

  function setAppHeight() {
    document.documentElement.style.setProperty("--app-height", `${window.innerHeight}px`);
  }

  // Refresh session on "new chat"
  const newChatBtn = document.getElementById("new-chat-btn");
  if (newChatBtn) {
    newChatBtn.addEventListener("click", () => {
      // reset session
      session_id = crypto.randomUUID();
      sessionStorage.setItem("session_id", session_id);

      // fade out
      chatWindow.style.opacity = 0;

      setTimeout(() => {
        // clear + reset
        chatWindow.innerHTML = "";
        addMessage("assistant", initial_greeting);

        // fade back in
        chatWindow.style.opacity = 1;
      }, 100);
    });
  }

  setAppHeight();
  window.addEventListener("resize", setAppHeight);
  window.addEventListener("orientationchange", setAppHeight);
});

