# PROD-SPEC-005: Sentinel - Managed Agentic Workspaces

**Status**: DRAFT (Architecting)
**Objective**: Transform technical proofs-of-concept into a marketable Google Cloud Partner Solution.

## 1. Executive Summary
**Sentinel** is a turnkey platform that deploys secure, audited, and context-aware Antigravity environments. It bridges the gap between "experimental developer hack" and "Enterprise Managed Service" by adding Governance, Security, and Observability layers.

## 2. Core Modules (The "Add-Ons")

### Module A: The Compliance Sidecar (Observability)
**Source**: Bishoyi’s Reverse Engineering.
**Problem**: Enterprises fear "Black Box" AI agents.
**Solution**: A "Flight Recorder" Sidecar.
- **Port Listener**: Listens on `localhost:9222` (Chrome DevTools Protocol) to capture DOM interactions and URL visits.
- **Audit Trails**: Ships structured events to **Google Cloud Logging**.
- **Evidence**: Offloads `.webp` video artifacts to a WORM (Write Once, Read Many) GCS Bucket.
- **Value**: "Don't just run AI; *audit* it."

### Module B: The Hybrid Access Portal (Experience)
**Source**: Strebel (Performance) + Subatin (Portability).
**Problem**: Balancing performance (CRD/UDP) vs. Firewall compliance (HTTPS).
**Solution**: Smart-Routing Launch Script (`launch_sentinel.sh`).
- **Logic**: Detects network environment capabilities.
    - *High Bandwidth/UDP Open* -> Launches **Chrome Remote Desktop** (4K/60fps).
    - *Restricted/Corporate* -> Falls back to **noVNC** over HTTPS.
- **Security**: Wraps VNC in **Identity-Aware Proxy (IAP)** to enforce SSO and remove public IPs.

### Module C: The Secure Perimeter (Infrastructure)
**Source**: Hardening tutorial hacks.
**Problem**: Reliance on `--no-sandbox` and privileged containers.
**Solution**: Enterprise Governance Module.
- **Seccomp**: Custom Docker Seccomp profile (`infra/security/chrome-seccomp.json`) to whitelist necessary syscalls instead of disabling the sandbox.
- **VPC-SC**: Service Perimeter whitelisting only essential internal endpoints (e.g., `jetski-server.corp.goog`), blocking exfiltration to public GitHub/Pastebin.

### Module D: Agent Personas (Service Offering)
**Source**: Bishoyi’s `system_prompts` discovery.
**Problem**: Generic agents lack domain focus.
**Solution**: Specialized Workstation Images via System Prompt Injection.
- **The QA Bot**: Restricted to `browser_*` tools; prompted to find edge cases.
- **The Legacy Modernizer**: Prompted to prioritize explanation and microservice refactoring.

### Module E: Enterprise MCP Connectors (Integration)
**Source**: Extending MCP Architecture.
**Problem**: Lack of business context.
**Solution**: Pre-installed Context Servers.
- **BigQuery MCP**: Direct Data Warehouse query capability.
- **Internal Docs MCP**: Vertex AI Search connection for coding standards RAG.

## 3. Implementation Roadmap
1. **Architect**: Define directory structure and specs.
2. **Sidecar**: Implement `services/sentinel-sidecar` (Python + CDP/Websockets).
3. **Launcher**: Create `scripts/launch_sentinel.sh`.
4. **Security**: Author `infra/security/chrome-seccomp.json`.
5. **Personas**: Author `knowledge/personas/*.md`.
6. **Rollout**: Update `forge_sovereign.sh` to package Sentinel into the Sovereign Payload.
