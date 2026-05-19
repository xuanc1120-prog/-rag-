const state = {
  history: [],
  lastMessages: [],
};

const refs = {
  chatFeed: document.getElementById("chatFeed"),
  traceOutput: document.getElementById("traceOutput"),
  healthStatus: document.getElementById("healthStatus"),
  healthProvider: document.getElementById("healthProvider"),
  healthModel: document.getElementById("healthModel"),
  healthStack: document.getElementById("healthStack"),
  questionInput: document.getElementById("questionInput"),
  chatForm: document.getElementById("chatForm"),
  chatFeedback: document.getElementById("chatFeedback"),
  sendBtn: document.getElementById("sendBtn"),
  refreshStatusBtn: document.getElementById("refreshStatusBtn"),
  clearChatBtn: document.getElementById("clearChatBtn"),
  quickPrompts: document.getElementById("quickPrompts"),
  ticketForm: document.getElementById("ticketForm"),
  ticketFeedback: document.getElementById("ticketFeedback"),
  ticketList: document.getElementById("ticketList"),
  refreshTicketsBtn: document.getElementById("refreshTicketsBtn"),
  toggleTraceBtn: document.getElementById("toggleTraceBtn"),
  traceContainer: document.getElementById("traceContainer"),
};

async function apiFetch(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;
  if (!response.ok) {
    throw new Error(payload?.detail || payload?.message || `Request failed (${response.status})`);
  }
  return payload;
}

function setFeedback(target, text = "", kind = "") {
  target.textContent = text;
  target.className = `feedback${kind ? ` ${kind}` : ""}`;
}

function renderHealth(data) {
  refs.healthStatus.textContent = data.status || "unknown";
  refs.healthProvider.textContent = data.provider || "-";
  refs.healthModel.textContent = data.model || "-";
  refs.healthStack.textContent = data.stack || "langchain";
}

function renderChat(messages) {
  refs.chatFeed.innerHTML = "";
  if (!messages.length) {
    refs.chatFeed.innerHTML = `
      <div class="empty-state">
        <h3>让 LangChain 版本先接一轮支持问题</h3>
        <p>你可以直接提问，也可以点击左侧快捷问题，观察它如何调工具、查知识库、推进工单。</p>
      </div>
    `;
    return;
  }

  for (const message of messages) {
    const card = document.createElement("article");
    const roleClass =
      message.role === "user" ? "user" : message.role === "assistant" ? "assistant" : "tool";
    card.className = `message ${roleClass}`;
    const meta = document.createElement("span");
    meta.className = "message-meta";
    const labels = {
      user: "用户问题",
      assistant: "LangChain Agent",
      tool: `工具结果 · ${message.name || "tool"}`,
      system: "系统消息",
    };
    meta.textContent = labels[message.role] || message.role;
    const body = document.createElement("div");
    body.textContent = message.content || "(无文本内容)";
    card.append(meta, body);
    refs.chatFeed.append(card);
  }

  refs.chatFeed.scrollTop = refs.chatFeed.scrollHeight;
}

function renderTrace(messages) {
  refs.traceOutput.textContent = JSON.stringify(messages, null, 2);
}

function renderTickets(tickets) {
  refs.ticketList.innerHTML = "";
  if (!tickets.length) {
    refs.ticketList.innerHTML = `<div class="muted">当前没有未关闭工单。</div>`;
    return;
  }

  for (const ticket of tickets) {
    const card = document.createElement("article");
    card.className = "ticket-card";
    card.innerHTML = `
      <header>
        <h3>${ticket.title}</h3>
        <span class="badge ${ticket.priority}">${ticket.priority}</span>
      </header>
      <div>${ticket.issue}</div>
      <div class="ticket-meta">
        <span>工单号：${ticket.ticket_id}</span>
        <span>状态：${ticket.status}</span>
        <span>邮箱：${ticket.customer_email}</span>
        <span>更新时间：${ticket.updated_at}</span>
      </div>
    `;
    refs.ticketList.append(card);
  }
}

async function loadHealth() {
  try {
    renderHealth(await apiFetch("/health"));
  } catch (error) {
    setFeedback(refs.chatFeedback, `健康检查失败：${error.message}`, "error");
  }
}

async function loadTickets() {
  try {
    renderTickets(await apiFetch("/tickets"));
  } catch (error) {
    refs.ticketList.innerHTML = `<div class="muted">工单加载失败：${error.message}</div>`;
  }
}

function buildConversationHistory(messages) {
  return messages
    .filter((message) => message.role === "user" || message.role === "assistant")
    .map((message) => ({
      role: message.role,
      content: message.content,
    }));
}

async function submitQuestion(question) {
  refs.sendBtn.disabled = true;
  setFeedback(refs.chatFeedback, "LangChain Agent 正在处理，请稍候…");
  try {
    const result = await apiFetch("/chat", {
      method: "POST",
      body: JSON.stringify({
        question,
        history: state.history,
      }),
    });
    state.lastMessages = result.messages || [];
    state.history = buildConversationHistory(state.lastMessages);
    renderChat(state.lastMessages);
    renderTrace(state.lastMessages);
    setFeedback(refs.chatFeedback, "已收到回复。", "success");
    await loadTickets();
  } catch (error) {
    setFeedback(refs.chatFeedback, error.message, "error");
  } finally {
    refs.sendBtn.disabled = false;
  }
}

refs.chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = refs.questionInput.value.trim();
  if (!question) {
    setFeedback(refs.chatFeedback, "先输入一个问题再发送。", "error");
    return;
  }
  await submitQuestion(question);
  refs.questionInput.value = "";
});

refs.quickPrompts.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-question]");
  if (!button) return;
  await submitQuestion(button.dataset.question || "");
});

refs.clearChatBtn.addEventListener("click", () => {
  state.history = [];
  state.lastMessages = [];
  renderChat([]);
  renderTrace([]);
  setFeedback(refs.chatFeedback, "会话已清空。", "success");
});

refs.refreshStatusBtn.addEventListener("click", loadHealth);
refs.refreshTicketsBtn.addEventListener("click", loadTickets);

refs.toggleTraceBtn.addEventListener("click", () => {
  const hidden = refs.traceContainer.hasAttribute("hidden");
  if (hidden) {
    refs.traceContainer.removeAttribute("hidden");
    refs.toggleTraceBtn.textContent = "▾";
  } else {
    refs.traceContainer.setAttribute("hidden", "hidden");
    refs.toggleTraceBtn.textContent = "▸";
  }
});

refs.ticketForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    title: document.getElementById("ticketTitle").value.trim(),
    issue: document.getElementById("ticketIssue").value.trim(),
    priority: document.getElementById("ticketPriority").value,
    customer_email: document.getElementById("ticketEmail").value.trim(),
  };

  if (!payload.title || !payload.issue || !payload.customer_email) {
    setFeedback(refs.ticketFeedback, "请把标题、描述和客户邮箱补完整。", "error");
    return;
  }

  try {
    const ticket = await apiFetch("/tickets", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    refs.ticketForm.reset();
    setFeedback(refs.ticketFeedback, `工单已创建：${ticket.ticket_id}`, "success");
    await loadTickets();
  } catch (error) {
    setFeedback(refs.ticketFeedback, error.message, "error");
  }
});

loadHealth();
loadTickets();
renderTrace([]);

