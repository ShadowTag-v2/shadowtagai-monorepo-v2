# ShadowTag Omega - Master Technical Specification
**Status:** Final Commit (Forensic Precision)
**Date:** 2026-01-18

This document is the **Master Technical Specification**, reintegrating "lost" forensic data into a single operational view. It distinguishes the "Jetski" (Local) architecture from the "Omega" (Cloud) architecture.

## I. The "Jetski" Architecture (Local/Shell)
*The "Wild" Agent. Lives on the metal, owns the browser, runs as the User.*

This is a **compiled Go binary** acting as a local Language Server. It bypasses standard cloud discovery in favor of direct, hard-coded piping into a local Chrome instance.

### 1. The Forensic Footprint
- **Orchestrator:** `language_server_macos_arm` (Running locally, PID 15440).
- **Communication Layer:**
    - **Extension Server:** Port `53410` (Direct bridge to Chrome Extension).
    - **LSP Ports:** `53412-13` (Standard Language Server Protocol for IDE integration).
    - **Debug:** `remote-debugging-port=9222` (The Chrome DevTools Protocol "God Mode" port).
- **Security:**
    - **CSRF Token:** `--csrf_token [REDACTED]` (Local validation to prevent drive-by attacks on the agent).
    - **User Profile:** `--user-data-dir=/Users/[USER]/.gemini/antigravity-browser-profile` (A sandboxed, agent-specific browser profile).

### 2. The Cognitive Stack (Dynamic Prompting)
The agent's "brain" is not a single prompt, but a JIT (Just-In-Time) assembly of templates from `google3/third_party/jetski/prompt/template_provider/templates/system_prompts/`.

- **Cognitive Boundaries:**
    - `task_boundary_tool.tmpl`: Defines what the sub-agent *cannot* do.
    - `mode_descriptions.tmpl`: Handles context switching (e.g., "Coding Mode" vs. "Browsing Mode").
- **Output Formatting:**
    - `file_diffs_artifact.tmpl`: The blueprint for generating precise code patches.
    - `knowledge_discovery.tmpl`: The protocol for RAG/Information Retrieval.
    - `notify_user_tool.tmpl`: The interrupt logic for asking the human for help.

### 3. The "Hands" (Binary Tool Converters)
The agent uses **Strict Typing** to bridge the gap between LLM hallucination and Go execution.
- **Input:** `ToolsConverter` ensures the LLM sends valid JSON for `browser_click_element(index: int)`.
- **Output:** `BrowserGetDomStringConverter` drastically simplifies the HTML DOM into a "chat-friendly" string, stripping noise so the context window doesn't overflow.
- **The Bridge:** Extension ID `eeijfnjmjelapkebgockoeaadonbchdd` listening on local port `3025`.

---

## II. The "Omega" Architecture (Cloud/MCP)
*The "Civilized" Agent. Lives in the Cloud, governed by IAM, speaks universal protocols.*

This is the standardization of the "Jetski" prototype into an enterprise-ready platform using the **Model Context Protocol (MCP)**.

### 1. The Connection Layer
- **Protocol:** MCP over SSE (Server-Sent Events).
- **Discovery:** Dynamic. The agent does not have hardcoded tools; it queries the **Cloud API Registry** to ask "What can I do?"
- **Security:** **Google Cloud IAM**. The agent is an authenticated Principal (Service Account) with specific permissions (e.g., `bigquery.jobs.create`).

### 2. The Toolset (Enterprise Scale)
- **Grounding:** Uses "Maps Grounding Lite" for spatial reasoning, not just raw text.
- **Infrastructure:** Native integration with GKE and Compute Engine. It calls the API directly.
- **Data:** In-situ SQL execution via BigQuery. It runs query jobs directly.

---

## III. The Apigee "Dark Matter" Bridge
*The Governance Layer. How the Cloud Agent touches internal corporate data safely.*

The "Omega" agent cannot just curl internal databases. It must pass through the **Apigee Gateway**, which acts as a "No-Code Proxy".

1. **Ingest:** Upload an **OpenAPI (Swagger)** spec of a legacy internal API.
2. **Transform:** Apigee automatically generates an **MCP-compliant endpoint**.
3. **Govern:**
    - **Rate Limiting:** Prevents the AI from accidentally DDoS-ing the internal payroll server.
    - **Audit Logging:** Logs every single SQL query or API call the AI attempts.
    - **OAuth Scopes:** Passes the *human user's* token to the internal service, ensuring the AI can only see what the human is allowed to see.

---

## Final System Status Summary

| Feature | "Jetski" (Local V1) | "Omega" (Cloud V2) |
| :--- | :--- | :--- |
| **Philosophy** | "Move fast, break DOMs" | "governed, scalable, standard" |
| **Orchestration** | Local Binary (`language_server`) | Cloud Run / Vertex AI Agent Engine |
| **Tool Definition** | Hardcoded Go Structs | Dynamic Discovery (MCP) |
| **Context Source** | Local Files / Browser Tabs | BigQuery / Drive / Slack |
| **Auth** | CSRF Token / Process Owner | IAM Principal / OAuth |
| **Primary Use** | Coding / Web Tasks | Enterprise Workflows / Data Ops |

---

## IV. Operational Implementation (Code-on-Disk)
*Current state of the repository as of Jan 18, 2026.*

### 1. RLM Implementation (Kosmos)
**File:** `src/agents/flyingmonkeys7.py`
The Recursive Language Model architecture (arXiv:2512.24601) is active.
- **KosmosREPL:** A simulated Python REPL injected into the agent to hold "Large Context" (`large_context_store`).
- **Standard:** Omega/Cloud (uses `re.search` for programmatic context navigation).
- **Recursion:** Implements `recursive_think(goal, depth)` to self-correct before answering.

### 2. Doctrine & Protocols
**File:** `GEMINI.md`
- **Tegu Protocol:** Visual Agent logic (Reasoning about layout before OCR).
- **Slash Commands:** `/risk`, `/ui`, `/scan` are reserved for Agentic operations.
- **Zero Deviation:** strict adherence to `google.generativeai` namespace.

### 3. Toolchain Status
- **Chrome DevTools MCP:** Present in `tools/chrome-devtools-mcp`.
- **Antigravity Proxy:** Active in `tools/antigravity-proxy`.

---

## V. Environmental Doctrine (The 4 Corners)
*Meta-Cognitive Re-Punch (Jan 18, 2026)*

### 1. Identity Gap (The Pilot vs The Plane)
- **Problem:** User credentials work locally but fail in Cloud Run (MFA/Zero Trust).
- **Doctrine:** The Agent runs as **Service Account** (`agent-runtime@shadowtag-omega-v2.iam.gserviceaccount.com`).
- **Action:** Grant this principal GCS and Vertex AI permissions.

### 2. Data Gravity Gap (Network Egress)
- **Problem:** Public internet routing is slow and insecure.
- **Doctrine:** **Google Private Access** must be enabled on the subnet. Traffic stays on the backbone.

### 3. The ADK Gap (Definition)
- **Problem:** "ADK" implies Android/Nest hardware agents.
- **Doctrine:** Use **Vertex AI Agent Builder** for the Enterprise Brain. Avoid "ADK" unless shipping binary apps to phones.

### 4. Observability Gap (Blind Flying)
- **Problem:** Serverless = No Logs/SSH.
- **Doctrine:** Enable **Cloud Trace** and **Error Reporting** to debug "Zero Ops" latency and failures.

