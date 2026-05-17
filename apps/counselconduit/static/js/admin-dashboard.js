// apps/counselconduit/static/js/admin-dashboard.js
// Admin Dashboard — Provider Health + Circuit Breaker + Firm Policies
// Extracted from inline <script> block for CSP compliance (Cor.30 R31).

const BASE = "https://counselconduit-767252945109.us-central1.run.app";
let TOKEN = "";

// biome-ignore lint/correctness/noUnusedVariables: called via onclick="authenticate()" in HTML
function authenticate() {
  TOKEN = document.getElementById("token-input").value.trim();
  if (!TOKEN) return;
  document.getElementById("auth-view").style.display = "none";
  document.getElementById("dashboard-view").style.display = "block";
  refreshAll();
}

async function apiFetch(path) {
  const r = await fetch(`${BASE}${path}`, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

async function refreshAll() {
  const btn = document.getElementById("refresh-btn");
  btn.classList.add("loading");
  btn.textContent = "⏳ Loading...";
  const banner = document.getElementById("error-banner");
  banner.style.display = "none";

  try {
    const [providers, circuit, policies] = await Promise.allSettled([
      apiFetch("/admin/provider-health"),
      apiFetch("/admin/circuit-breaker"),
      apiFetch("/admin/firm-policies"),
    ]);

    if (providers.status === "fulfilled") renderProviders(providers.value);
    if (circuit.status === "fulfilled") renderCircuit(circuit.value);
    if (policies.status === "fulfilled") renderPolicies(policies.value);

    document.getElementById("last-updated").textContent =
      `Last updated: ${new Date().toLocaleTimeString()}`;
  } catch (e) {
    banner.textContent = `Error: ${e.message}`;
    banner.style.display = "block";
  }

  btn.classList.remove("loading");
  btn.textContent = "↻ Refresh";
}

function renderProviders(data) {
  document.getElementById("healthy-count").textContent =
    `${data.healthy_count}/${data.total_providers}`;

  const grid = document.getElementById("providers-grid");
  grid.innerHTML = "";

  for (const [name, info] of Object.entries(data.providers)) {
    const up = info.reachable;
    const card = document.createElement("div");
    card.className = `provider-card ${up ? "up" : "down"}`;
    card.innerHTML = `
            <div class="provider-name">
                <span class="status-dot ${up ? "up" : "down"}"></span>
                ${name.charAt(0).toUpperCase() + name.slice(1)}
            </div>
            <div class="provider-meta">
                <span>Status: ${up ? `✅ ${info.status_code}` : `❌ ${info.error || "unreachable"}`}</span>
                ${info.latency_ms ? `<span>Latency: ${info.latency_ms}ms</span>` : ""}
            </div>
        `;
    grid.appendChild(card);
  }
}

function renderCircuit(data) {
  const el = document.getElementById("circuit-status");
  const stateText = document.getElementById("circuit-state-text");
  const details = document.getElementById("circuit-details");
  const errCount = document.getElementById("error-count");
  const statCard = document.getElementById("stat-circuit");

  if (data.open) {
    el.textContent = "OPEN";
    el.className = "stat-value red";
    stateText.textContent = "🔴 CIRCUIT OPEN — Load shedding active";
    stateText.className = "circuit-state open";
    statCard.className = "stat-card unhealthy";
  } else {
    el.textContent = "CLOSED";
    el.className = "stat-value green";
    stateText.textContent = "🟢 CIRCUIT CLOSED — Normal operation";
    stateText.className = "circuit-state closed";
    statCard.className = "stat-card healthy";
  }

  errCount.textContent = data.errors_in_window;
  errCount.className = `stat-value ${data.errors_in_window > 5 ? "amber" : "green"}`;

  details.innerHTML = `
        <span>Errors: ${data.errors_in_window} / ${data.threshold}</span>
        <span>Window: ${data.window_seconds}s | Cooldown: ${data.cooldown_seconds}s</span>
    `;
}

function renderPolicies(data) {
  document.getElementById("firms-count").textContent = data.count;
  const grid = document.getElementById("firms-grid");
  grid.innerHTML = "";

  for (const p of data.policies) {
    const card = document.createElement("div");
    card.className = "provider-card up";
    card.innerHTML = `
            <div class="provider-name">${p.firm_id}</div>
            <div class="provider-meta">
                <span>Models: ${(p.allowed_models || []).join(", ")}</span>
                <span>Rate Limit: ${p.max_rpm} RPM / ${p.max_daily} daily</span>
                <span>BYOK: ${p.byok_enabled ? "✅ Enabled" : "❌ Disabled"}</span>
            </div>
        `;
    grid.appendChild(card);
  }

  if (data.count === 0) {
    grid.innerHTML =
      '<div class="provider-card"><div class="provider-meta">No firm policies configured</div></div>';
  }
}

// Auto-show auth form on load
document.getElementById("auth-view").style.display = "block";

// Auto-refresh every 30 seconds when authenticated
setInterval(() => {
  if (TOKEN) refreshAll();
}, 30000);
