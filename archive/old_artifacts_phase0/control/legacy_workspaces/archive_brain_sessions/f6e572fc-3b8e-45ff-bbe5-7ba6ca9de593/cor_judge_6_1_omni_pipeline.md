# Cor.Judge 6.1: The Omni-Pipeline Architecture

This document outlines the synthesis of the "Yay Compiled" AntiGravity capabilities with the overarching Sovereign Research & Defense system. By defocusing on isolated counter-espionage protocols, this architecture integrates the full pipeline of Research Agents (Kosmos Swarm), Military-Grade Compliance (DOW CRSMC), and the ultimate GCP Knowledge Citadel.

---

## 1. The Core Components (The "Yay" Harvest)
To elevate the cloud workstation beyond basic tool execution, the Omni-Pipeline integrates three missing IDE components deeply into the backend.

### A. The Virtual File System (VFS) & Watcher
- **Function:** Instead of allowing the agent to write raw code to the active disk, the backend maintains a **Shadow File System**.
- **Execution:** The Builder agent writes to this VFS. The Critic (Safety Officer) inspects the "staged" files in isolation before they are merged into the user's workspace, preventing aggressive, unverified overwrites.

### B. The Context "Pruning" Engine (The Sieve)
- **Function:** Solves token bloat for large monorepos.
- **Execution:** A pre-processor uses `Tree-sitter` to dynamically feed the Architect agent:
  - *Level 0:* Project Folder Structure (Always sent).
  - *Level 1:* File Headers & Signatures (Sent for related files).
  - *Level 2:* Full Code Body (Sent only for the file being actively edited).

### C. Atomic Orchestration & The AG-UI Firewall
- **Function:** Replaces brittle custom WebSocket relays with a deterministic central nervous system (Atomic Threads).
- **Execution:** Every task is decomposed into an `AtomicThread` (`purpose`, `reasons`, `brakes`, `risk_level`, `dependencies`, `budget`). The orchestrator intercepts the event stream, logging internal telemetry (`TOOL_CALL_STARTED`, `AGENT_THOUGHT_CHUNK`) to the Google Confidential Ledger while mathematically **DROPPING** it before reaching the edge. The client only receives safe outcomes (`RUN_STARTED`, `UI_RENDER_COMPONENT`, `RUN_COMPLETED`).

---

## 2. The Command-and-Control Intelligence Layer
The pipeline replaces a linear 1-to-1 processing flow with a highly orchestrated Multi-Agent Swarm logic.

### A. The High-Thinking Triad (Gemini 3)
1. **The Architect (Gemini 3 Pro + High Thinking):** Acts as the Strategist. Emits real-time `AGENT_THOUGHT_CHUNK` events over WebSocket to the UI before drafting plans. Uses the **Kosmos Swarm** protocol to spawn parallel research agents.
2. **The Builder (Gemini 3 Flash + Medium Thinking):** Fast execution. Trapped in the VFS "Sandbox" with zero trusted write permissions.
3. **The Critic (Gemini 3 Pro + Low Thinking):** The 17-Layer DOW CRSMC Firewall. Physically placed between the Builder and the File System to act as a strict authorization gate.

### B. Modular Premium Packs (The Dispatcher)
The 17-Layer Shield is dynamically applied by Kosmos based on the operating environment.
- **Law Firm Profile:** Activates Layer 13 (Privilege/VPN) and Layer 6 (EU AI Act - Confidentiality). Puts Layer 16 (Kinetic/Drone protocols) to sleep to save compute.
- **Accounting Firm Profile:** Activates Layer 7 (Financial Risk). Kosmos generates rigorous BigQuery Monte Carlo simulations for any algorithmic change.

---

## 3. The Continuous Sentinel (Variable OODA Loop)
The Agent evolves into an *Always-Looping Daemon*. It no longer requires a user trigger.

### A. Variable Frequency Control
- **Low Volatility (Slow Mode):** The Cosmos Swarm wakes every 15 minutes to check RSS feeds or standard market metrics.
- **High Volatility (Fast Mode):** Upon detecting breaking news or massive anomalies, the loop accelerates to a 100ms real-time tick rate, executing tactical transaction scripts via the Terminal.

### B. The "Hybrid Browser" (Eyes of the Swarm)
- **Jetski Layer:** Gives Kosmos raw capability to click, type, and navigate complex SPAs.
- **Gemini Native DOM Extraction:** Pulls the high-fidelity accessibility tree and hidden JSON data from web pages natively through a Google Kubernetes Engine (GKE) CDP cluster, providing mathematically precise data extraction without OCR errors or reliance on open-source browser wrappers.

---

## 4. The GCP Knowledge Citadel (Enterprise Data Fabric)
Replacing localized storage ("Ice Lake"), the Omni-Pipeline utilizes native Google Cloud data primitives for massively scalable, sovereign intelligence.

### A. The Three-Tier Data Mesh
1. **The Vault (Google Cloud Storage):** Immutable storage for scraped PDFs (Scholarly Sources, Medical Journals, Court Dockets). Enforced with WORM (Write Once Read Many) policies.
2. **The Cortex (Vertex AI Vector Search):** Stores semantic embeddings of every paragraph in the Vault, empowering the Agent to find abstract technical/legal precedents.
3. **The Truth (BigQuery):** Relational linking. Connects Artifact IDs to their real-time "Shepardizing" status.

### B. In-Database Risk Models (Compute-to-Data)
To execute Layer 7 (Financial Risk), Kosmos does not pull data to Python.
- **Execution:** Kosmos triggers **BigQuery ML (BQML)** and SQL-based Monte Carlo procedures *inside* the data warehouse.
- **Benefit:** Massive parallel array generation across thousands of Serverless BigQuery slots allows 10,000-scenario risk simulations in seconds with zero data egress.

### C. Continuous Shepardizing (Cloud Functions)
- **Execution:** Eventarc and Cloud Scheduler trigger bots that constantly query APIs (e.g., CourtListener, FDA databases).
- **Action:** If a paper is retracted or a legal case is overturned, the function instantly updates the `status` flag in BigQuery. The Artifact API actively blocks the Architect from referencing invalidated knowledge, eliminating AI hallucinations in mission-critical environments.

### D. Grounding via Google Universe
- **Pattern of Life Analysis:** Correlates structured intelligence (Credit, Socials) with Geospatial Truth (Google Maps Places API & Aerial View).
- **Result:** Provides the Kosmos Swarm with undeniable "Ground Truth" to verify supply chains or evaluate executive leverage, generating alpha / intel beyond standard NLP.
