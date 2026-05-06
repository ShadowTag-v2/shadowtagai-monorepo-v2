# HeadFade Truth Oracle MCP Server

**Official Model Context Protocol (MCP) Server** for the HeadFade cognitive forensics platform.

Part of the **Antigravity Dark Factory** — zero-OpEx, self-healing, enterprise-grade infrastructure.

---

## Features

- **verify_synthetic_video** — Returns Human Deception Index (HDI), AI model stack, and full Remix Family Tree
- **purchase_workflow_license** — Agent-to-Agent $2.99 micro-license purchases for ComfyUI workflows
- **Enterprise Authentication** — Uses Google Cloud Workload Identity Federation (no long-lived API keys)
- **Direct Cloud SQL Access** — Powered by Firebase Data Connect (zero middleware)

---

## Quick Start

```bash
cd antigravity-core/mcp
npm install
npm run build
npm start
```

---

## Architecture

- Built on official `@modelcontextprotocol/sdk`
- Authenticated via Google Workload Identity Federation
- Queries Firebase Data Connect → Cloud SQL (Postgres)
- Designed for Jules, Claude, Gemini, and external agent consumption

---

## Security

- No API keys in code or environment
- All access controlled via short-lived OAuth tokens
- SOC2 / enterprise ready

---

**Status**: Production Ready (Stealth Mode)

Part of Project Antigravity v11.0
