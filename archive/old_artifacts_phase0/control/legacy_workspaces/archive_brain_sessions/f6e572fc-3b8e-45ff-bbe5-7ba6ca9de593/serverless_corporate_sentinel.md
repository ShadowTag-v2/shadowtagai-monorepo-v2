# Serverless Corporate Sentinel: The Internal Affairs Bureau

This architecture pivots the Autonomous IDE Agent from a "Wall Street Watchdog" into a "Corporate Counter-Espionage & Fraud (CEF) Sentinel." Designed for a manufacturing/widget business, it abandons persistent infrastructure (like Cloud Workstations) in favor of a **Pure Serverless Cloud Run** deployment.

## 1. The Serverless "Glass House" Architecture
By removing Cloud Workstations, we decouple the "Agent Triad" (Architect, Builder, Critic) from long-lived instances. Every component scales to zero and triggers purely on events.

### A. The Compute Layer (Cloud Run)
Instead of a Node.js process running inside a persistent IDE, the **Relay Server & Agent Manager** run on **Google Cloud Run**.
- **Execution:** Cloud Run handles WebSocket connections natively (enabled via HTTP/1.1 Upgrade headers in the GCP Load Balancer) or degrades to Server-Sent Events (SSE) for streaming Gemini 3 "Thoughts" to the frontend.
- **Concurrency:** A single Cloud Run container can multiplex up to 1000 concurrent agent evaluation loops, spinning up additional containers only when the corporate workforce triggers mass audits.

### B. Resolving the "Missing IDE Pieces"
To achieve the `Cor.Uphillsnowball.1` specification without a local VS Code instance, the Cloud Run Sentinel implements:
1. **Code/Data Search (The `ripgrep` Replacement):**
   - **Solution:** A serverless index. Instead of `ripgrep-js` scanning a local disk, git repositories and internal docs are continuously ingested into **Vertex AI Vector Search** and **BigQuery**.
   - **Execution:** The Kosmos Swarm executes BigQuery SQL or Vector Search queries to find exact matches across millions of HR/Log files in milliseconds.
2. **UI/UX States:**
   - **Solution:** A standalone React SPA hosted on **Firebase Hosting** or **Cloud Storage (GCS)**.
   - **Execution:** The UI connects to the Cloud Run backend via SSE for real-time visualization of the Agent's OODA loop and 17-Layer DOW CRSMC inspection alerts.
3. **Prompt Library (The Persona Files):**
   - **Solution:** Moved from `.antigravity/prompts` to **Google Secret Manager** or a dedicated **GCS Bucket**.
   - **Execution:** At container boot, Cloud Run fetches the latest "Safety Officer," "Architect," and "Critic" personas dynamically, ensuring the Agent is always operating on the latest compliance rules.

---

## 2. The Counter-Espionage & Fraud (CEF) Module

For a Widget CEO, the highest existential threats are internal (Mole) and external (Supply Chain Fraud). The Sentinel acts continuously in the background, analyzing disparate data sources.

### A. The "Ding Protocol" (Insider Threat & IP Theft)
*Reference: The Google / Linwei Ding Espionage Case.*

The goal is to detect a malicious actor attempting to exfiltrate proprietary widget blueprints while masking their physical location.

- **The Data Fusion (Ingestion Layer):**
  - **Physical:** Badge swipe logs stored in BigQuery (e.g., "Employee swiped into Building A").
  - **Digital:** Network accesses logged in Google Chronicle / Google Workspace Admin logs (e.g., "Employee IP is coming from Beijing via a VPN").
- **The Detection Loop (Kosmos Swarm):**
  - A scheduled **Eventarc Trigger** wakes the Kosmos Swarm every 5 minutes.
  - The Swarm runs a **"Presence Discrepancy"** check: `IF (Badge_Location != IP_Location) -> TRIGGER ALERT`.
- **The Critic (17-Layer Shield - Layer 1 & 10):**
  - Uses **Sensitive Data Protection (DLP)**. If the employee attempts to upload proprietary PDF schematics to an unauthorized Google Drive, the Critic (Gemini 3 Pro) intercepts the IAM request and forcefully revokes their access tokens in real-time.

### B. The "Ghost Ship Protocol" (Invoice & Supply Chain Fraud)
The goal is to prevent embezzlement via fake vendors / shell shipping companies.

- **The Data Fusion:**
  - **Financial:** Accounts Payable (AP) software emits a Pub/Sub event when a new vendor invoice is submitted.
  - **Geospatial:** The Kosmos Swarm invokes the **Google Maps Places API** and **Street View Static API**.
- **The Verification Loop:**
  - Upon receiving an invoice from "Acme Logistics LLC," the Architect (Gemini 3 Pro) dispatches a verification agent.
  - **Grounding Check:** The agent cross-references the invoice address via Google Maps.
  - **Analysis:** "The listed headquarters for Acme Logistics is a residential home or an empty dirt lot in Street View. There are no loading docks or trucks visible."
- **The Rejection (Layer 15 - Anti-Crime):**
  - The Critic flags the vendor as a "Ghost Ship." The invoice payment is blocked via API, and the internal CFO is alerted with visual evidence (satellite imagery) attached to the incident report.

---

## 3. Continual Background Scanning (The Daemon)

This Sentinel is an always-on entity. It operates on a **Variable Frequency OODA Loop**.

1. **Quiet State (Low Risk):**
   - Cloud Scheduler pings the Cloud Run instance every 15-30 minutes. The Kosmos Swarm checks macro-level data (public news about suppliers, standard badge logs). Cost is kept extremely low.
2. **Active State (High Risk):**
   - If a trigger is hit (e.g., a massive concurrent download of Git repos, or an invoice exceeding $5M), Pub/Sub instantly spins up the Cloud Run container.
   - The Swarm shifts into high-frequency mode, pulling real-time network logs and locking down access until the Critic (Gemini 3 Pro) manually clears the anomaly.

## Strategic Summary
By pivoting to **Pure Cloud Run** and integrating **Google Maps Grounding**, the AI is removed from the "Corder/IDE Assist" box and transformed into an **Autonomous Corporate Shield**. It doesn't just write code; it actively protects the company's IP and capital using geographic truth and behavioral disparity analysis.
