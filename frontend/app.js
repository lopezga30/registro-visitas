const API_URL = "%%API_URL%%";

const AVATAR_COLORS = [
  "linear-gradient(135deg,#7c3aed,#a78bfa)",
  "linear-gradient(135deg,#db2777,#f472b6)",
  "linear-gradient(135deg,#ea580c,#fb923c)",
  "linear-gradient(135deg,#0891b2,#22d3ee)",
  "linear-gradient(135deg,#16a34a,#4ade80)",
  "linear-gradient(135deg,#ca8a04,#fbbf24)",
];

function avatarColor(name) {
  let hash = 0;
  for (const c of name) hash = (hash * 31 + c.charCodeAt(0)) & 0xffff;
  return AVATAR_COLORS[hash % AVATAR_COLORS.length];
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function formatDate(iso) {
  return new Date(iso).toLocaleString("es-AR", {
    day: "2-digit", month: "2-digit", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

async function loadVisits() {
  const list = document.getElementById("visitsList");
  const badge = document.getElementById("countBadge");
  try {
    const res = await fetch(`${API_URL}/visits`);
    const data = await res.json();
    const visits = (data.visits || []).sort(
      (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
    );
    badge.textContent = visits.length;
    if (visits.length === 0) {
      list.innerHTML = `
        <div class="state-message">
          <div class="icon">💬</div>
          <p>Todavía no hay mensajes. ¡Sé el primero!</p>
        </div>`;
      return;
    }
    list.innerHTML = visits.map(v => {
      const initial = escapeHtml(v.name.charAt(0).toUpperCase());
      const color = avatarColor(v.name);
      return `
        <div class="visit-card">
          <div class="visit-card-top">
            <div class="avatar" style="background:${color}">${initial}</div>
            <span class="visit-name">${escapeHtml(v.name)}</span>
            <span class="visit-date">${formatDate(v.timestamp)}</span>
          </div>
          <div class="visit-message">${escapeHtml(v.message)}</div>
        </div>`;
    }).join("");
  } catch {
    list.innerHTML = `
      <div class="state-message">
        <div class="icon">⚠️</div>
        <p>Error al cargar los mensajes.</p>
      </div>`;
  }
}

document.getElementById("visitForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = document.getElementById("submitBtn");
  const status = document.getElementById("formStatus");
  const name = document.getElementById("name").value.trim();
  const message = document.getElementById("message").value.trim();

  btn.disabled = true;
  status.textContent = "Enviando...";
  status.className = "status";

  try {
    const res = await fetch(`${API_URL}/visits`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, message }),
    });
    if (!res.ok) throw new Error();
    status.textContent = "✓ ¡Mensaje publicado!";
    status.className = "status success";
    document.getElementById("visitForm").reset();
    await loadVisits();
  } catch {
    status.textContent = "Error al enviar. Intentá de nuevo.";
    status.className = "status error";
  } finally {
    btn.disabled = false;
  }
});

loadVisits();
