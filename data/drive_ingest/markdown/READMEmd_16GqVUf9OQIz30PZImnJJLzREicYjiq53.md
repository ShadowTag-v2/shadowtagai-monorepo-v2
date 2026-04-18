# PNKLN Dev Environment Tools

Development enhancement tools for the PNKLN/ShadowTag stack.

## Tools

### 1. Antigravity Proxy
Intercepts Antigravity Studio API calls and redirects to your own Gemini API key.
- **Purpose**: $0 marginal cost vs Studio token limits
- **Security**: HTTPS MITM - DEV ONLY, cert is revocable

### 2. CACI (Claude Code Config Interface)
AI-powered Claude Code configuration optimizer.
- **Purpose**: Optimal agent/MCP/command setup in minutes vs hours
- **Engine**: Gemini 2.5 Pro for component recommendations

## Quick Start

```bash
# One-command setup
./scripts/setup-dev-tools.sh

# Or manual:
cd tools/dev-environment/antigravity-proxy && ./pnkln/enable.sh
cd tools/dev-environment/claude-code-config && npx caci
```

## Security Warnings

- **antigravity-proxy**: Intercepts ALL HTTPS traffic when enabled
- Run `./pnkln/disable.sh` to revoke cert when done
- Never use in production environments
- API keys stored in `.env` files (gitignored)

## PNKLN-Specific Components

Custom Claude Code components for the stack are defined in:
- `claude-code-config/pnkln/pnkln-components.json`

These include:
- Judge#6 governance agent
- JR Engine validation agent
- ATP 5-19 risk assessment agent
- Vertex AI MCP integration
- GKE cluster management MCP
- ShadowTag watermarking MCP
