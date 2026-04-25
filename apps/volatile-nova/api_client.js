/**
 * Omega Protocol: Ingestion API Client
 * Binds frontend playground to local ASGI FastAPI Node
 */

const OMEGA_ENDPOINT = 'http://127.0.0.1:8000';

// UI Elements
const statusIndicator = document.getElementById('connection-status');
const pulseRing = document.querySelector('.pulse-ring');
const healthMetricsGrid = document.getElementById('health-metrics');
const apiResponseWindow = document.getElementById('api-response-window');
const btnPing = document.getElementById('btn-ping');
const btnFetchJobs = document.getElementById('btn-fetch-jobs');

// JSON Syntax Highlighter
function syntaxHighlight(json) {
  if (typeof json !== 'string') {
    json = JSON.stringify(json, undefined, 2);
  }
  json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return json.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g,
    (match) => {
      let cls = 'number';
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'key';
        } else {
          cls = 'string';
        }
      } else if (/true|false/.test(match)) {
        cls = 'boolean';
      } else if (/null/.test(match)) {
        cls = 'null';
      }
      return `<span class="${cls}">${match}</span>`;
    },
  );
}

// Update Global Status
function setConnectionStatus(isConnected) {
  if (isConnected) {
    pulseRing.classList.add('connected');
    statusIndicator.textContent = 'Ingestion Pipeline: ONLINE';
    statusIndicator.style.color = 'var(--success)';
  } else {
    pulseRing.classList.remove('connected');
    statusIndicator.textContent = 'Ingestion Pipeline: OFFLINE';
    statusIndicator.style.color = 'var(--warning)';
  }
}

// Fetch Health/Root Telemetry
async function pingServer() {
  try {
    const response = await fetch(`${OMEGA_ENDPOINT}/`);
    if (!response.ok) throw new Error('Network response was not ok');

    const data = await response.json();
    setConnectionStatus(true);

    // Render Metric Cards
    healthMetricsGrid.innerHTML = `
            <div class="metric-card">
                <span class="metric-label">Service</span>
                <span class="metric-value" style="font-size: 1.1rem">${data.service}</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">Version</span>
                <span class="metric-value">${data.version}</span>
            </div>
        `;
  } catch (_error) {
    setConnectionStatus(false);
    healthMetricsGrid.innerHTML = `
            <div class="metric-card" style="grid-column: span 2; border-color: var(--warning);">
                <span class="metric-label" style="color: var(--warning)">CONNECTION ERROR</span>
                <span class="metric-value" style="font-size: 1rem">Failed to handshake with ${OMEGA_ENDPOINT}</span>
            </div>
        `;
  }
}

// Fetch Latest Job Status
async function fetchJobStatus() {
  apiResponseWindow.innerHTML = 'Fetching latest timeline...';
  try {
    const response = await fetch(`${OMEGA_ENDPOINT}/ingestion/status`);
    if (!response.ok) throw new Error('Endpoint failed');

    const data = await response.json();
    apiResponseWindow.innerHTML = syntaxHighlight(data);
  } catch (error) {
    apiResponseWindow.innerHTML = `<span style="color: #ff5f56">Failed to retrieve job status.\nEnsure Uvicorn is active and CORS allows origin.</span>\n\nError: ${error.message}`;
  }
}

// Event Listeners
btnPing.addEventListener('click', pingServer);
btnFetchJobs.addEventListener('click', fetchJobStatus);

// Initial Boot Sequence
document.addEventListener('DOMContentLoaded', () => {
  pingServer();
});
