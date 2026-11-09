const assistantList = document.querySelector("#assistant-list");
const pluginList = document.querySelector("#plugin-list");
const title = document.querySelector("#assistant-title");
const conversation = document.querySelector("#conversation");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
let selectedAssistant = "general";
let assistants = [];
let history = [];

async function loadWorkspace() {
  try {
    const [assistantResponse, pluginResponse, healthResponse] = await Promise.all([
      fetch("/api/assistants"),
      fetch("/api/plugins"),
      fetch("/api/health"),
    ]);
    if (!assistantResponse.ok || !pluginResponse.ok || !healthResponse.ok) throw new Error("Could not load workspace");
    assistants = await assistantResponse.json();
    const plugins = await pluginResponse.json();
    const health = await healthResponse.json();
    renderAssistants();
    renderPlugins(plugins);
    const status = document.querySelector("#status-label");
    status.textContent = health.ai_configured ? "AI connected" : "Local mode";
    status.classList.toggle("connected", health.ai_configured);
    document.querySelector("#composer-hint").textContent = health.ai_configured
      ? "Your conversation is sent to the configured AI provider."
      : "Set OPENAI_API_KEY for AI chat · Tasks, calculator, and clock work locally";
  } catch (error) {
    addMessage("assistant", "I couldn't connect to the Open Jarvis server. Please refresh the page.");
    console.error(error);
  }
}

function renderAssistants() {
  assistantList.replaceChildren();
  assistants.forEach((assistant, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `assistant-item${assistant.id === selectedAssistant ? " active" : ""}`;
    button.setAttribute("aria-current", assistant.id === selectedAssistant ? "page" : "false");
    const icon = document.createElement("span");
    icon.className = "assistant-icon";
    icon.textContent = ["✦", "⌘", "◷"][index % 3];
    const details = document.createElement("span");
    details.className = "assistant-details";
    const name = document.createElement("strong");
    name.textContent = assistant.name;
    const description = document.createElement("small");
    description.textContent = assistant.description;
    details.append(name, description);
    button.append(icon, details);
    button.addEventListener("click", () => {
      selectedAssistant = assistant.id;
      title.textContent = assistant.name;
      renderAssistants();
      history = [];
      clearConversation();
    });
    assistantList.append(button);
  });
  const active = assistants.find((assistant) => assistant.id === selectedAssistant);
  if (active) title.textContent = active.name;
}

function renderPlugins(plugins) {
  pluginList.replaceChildren();
  plugins.forEach((plugin) => {
    const item = document.createElement("li");
    const dot = document.createElement("span");
    dot.className = "plugin-dot";
    const text = document.createElement("span");
    text.textContent = plugin.name;
    item.append(dot, text);
    pluginList.append(item);
  });
}

function clearConversation() {
  conversation.replaceChildren();
  const welcome = document.createElement("div");
  welcome.className = "welcome compact-welcome";
  const heading = document.createElement("h2");
  heading.textContent = `Chat with ${title.textContent}`;
  const copy = document.createElement("p");
  copy.textContent = "Your conversation starts here. Try a question or an enabled plugin.";
  welcome.append(heading, copy);
  conversation.append(welcome);
}

function addMessage(role, text, plugin) {
  document.querySelector("#welcome")?.remove();
  const row = document.createElement("article");
  row.className = `message ${role}`;
  const avatar = document.createElement("span");
  avatar.className = "message-avatar";
  avatar.textContent = role === "user" ? "Y" : "J";
  const content = document.createElement("div");
  content.className = "message-content";
  const label = document.createElement("div");
  label.className = "message-label";
  label.textContent = role === "user" ? "YOU" : title.textContent.toUpperCase();
  const body = document.createElement("p");
  body.textContent = text;
  content.append(label, body);
  if (plugin) {
    const badge = document.createElement("span");
    badge.className = "tool-badge";
    badge.textContent = `↳ ${plugin}`;
    content.append(badge);
  }
  row.append(avatar, content);
  conversation.append(row);
  conversation.scrollTop = conversation.scrollHeight;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || sendButton.disabled) return;
  addMessage("user", message);
  input.value = "";
  input.style.height = "auto";
  sendButton.disabled = true;
  sendButton.textContent = "…";
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assistant_id: selectedAssistant, message, history: history.slice(-20) }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "The request failed.");
    addMessage("assistant", data.reply, data.plugin_used);
    history.push({ role: "user", content: message }, { role: "assistant", content: data.reply });
    history = history.slice(-20);
  } catch (error) {
    addMessage("assistant", error.message || "Something went wrong. Please try again.");
  } finally {
    sendButton.disabled = false;
    sendButton.textContent = "↑";
    input.focus();
  }
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
});
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.prompt;
    form.requestSubmit();
  });
});

loadWorkspace();
