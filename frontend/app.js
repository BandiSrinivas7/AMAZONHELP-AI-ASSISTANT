const API_BASE = localStorage.getItem("amazonhelp_api") || "http://localhost:8000";

const form = document.getElementById("supportForm");
const message = document.getElementById("message");
const chat = document.getElementById("chat");
const apiState = document.getElementById("apiState");

function addMessage(text, cls) {
  const el = document.createElement("div");
  el.className = `msg ${cls}`;
  el.textContent = text;
  chat.appendChild(el);
  chat.scrollTop = chat.scrollHeight;
}

function addResult(data) {
  const el = document.createElement("div");
  el.className = "result";
  const decisionClass = data.decision === "ESCALATE" ? "badge warn" : "badge";
  const evidence = (data.evidence || []).slice(0, 3).map((x, i) =>
    `<div><b>${i + 1}.</b> ${escapeHtml(x.reply || x.text || "Historical support example")}</div>`
  ).join("");
  el.innerHTML = `
    <strong>AmazonHelp AI result</strong>
    <span class="${decisionClass}">${escapeHtml(data.decision)}</span>
    <div><b>Intent:</b> ${escapeHtml(data.intent)}</div>
    <div><b>Confidence:</b> ${(Number(data.intent_confidence || 0) * 100).toFixed(1)}%</div>
    <div style="margin-top:9px;line-height:1.45"><b>Draft reply</b><br>${escapeHtml(data.reply || "")}</div>
    ${data.reason ? `<div class="evidence"><b>Decision signals</b><br>${data.reason.map(escapeHtml).join("<br>")}</div>` : ""}
    ${evidence ? `<div class="evidence"><b>Retrieved evidence</b>${evidence}</div>` : ""}
  `;
  chat.appendChild(el);
  chat.scrollTop = chat.scrollHeight;
}

function escapeHtml(v) {
  return String(v).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
}

async function checkHealth() {
  try {
    const r = await fetch(`${API_BASE}/health`);
    const d = await r.json();
    apiState.textContent = d.status === "ok" ? "Backend: connected" : "Backend: unavailable";
  } catch {
    apiState.textContent = "Backend: offline";
  }
}

async function sendSupport(text) {
  const clean = text.trim();
  if (clean.length < 3) return;
  addMessage(clean, "user");
  message.value = "";
  addMessage("Analyzing intent and retrieving historical support evidence…", "bot");

  try {
    const r = await fetch(`${API_BASE}/api/support`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({message: clean, top_k: 5})
    });
    const data = await r.json();
    chat.lastElementChild.remove();
    if (!r.ok) throw new Error(data.detail || "Support request failed");
    addResult(data);
  } catch (err) {
    chat.lastElementChild.remove();
    addMessage(`I couldn't reach the support backend. ${err.message}. Start the FastAPI server on port 8000 and try again.`, "bot");
  }
}

form.addEventListener("submit", e => {
  e.preventDefault();
  sendSupport(message.value);
});

document.querySelectorAll(".suggestions button").forEach(btn => {
  btn.addEventListener("click", () => {
    message.value = btn.textContent;
    message.focus();
  });
});

document.getElementById("heroSupport").addEventListener("click", () => {
  document.getElementById("supportPanel").scrollIntoView({behavior:"smooth", block:"start"});
  message.focus();
});

document.getElementById("searchForm").addEventListener("submit", e => {
  e.preventDefault();
  const q = document.getElementById("siteSearch").value.trim();
  if (q) {
    message.value = `I need help with ${q}`;
    document.getElementById("supportPanel").scrollIntoView({behavior:"smooth"});
    message.focus();
  }
});

checkHealth();
