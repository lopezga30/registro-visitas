// La URL de la API se reemplaza automáticamente durante el deploy por GitHub Actions
const API_URL = "%%API_URL%%";

async function loadVisits() {
  const list = document.getElementById("visitsList");
  try {
    const res = await fetch(`${API_URL}/visits`);
    const data = await res.json();
    if (!data.visits || data.visits.length === 0) {
      list.innerHTML = '<p class="empty">Todavía no hay mensajes. ¡Sé el primero!</p>';
      return;
    }
    list.innerHTML = data.visits
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .map(v => `
        <div class="visit-card">
          <div class="visit-name">${escapeHtml(v.name)}</div>
          <div class="visit-message">${escapeHtml(v.message)}</div>
          <div class="visit-date">${formatDate(v.timestamp)}</div>
        </div>
      `).join("");
  } catch {
    list.innerHTML = '<p class="empty">Error al cargar los mensajes.</p>';
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
    status.textContent = "¡Mensaje enviado!";
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

function escapeHtml(str) {
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function formatDate(iso) {
  return new Date(iso).toLocaleString("es-AR", {
    day: "2-digit", month: "2-digit", year: "numeric",
    hour: "2-digit", minute: "2-digit"
  });
}

loadVisits();
