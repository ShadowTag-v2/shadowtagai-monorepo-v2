# Antigravity Local Toolchain

All tools for local Antigravity development.

## Quick Start

```bash
# Start everything (proxy + API + Antigravity)
~/antigravity-tools/launch.sh all

# Or start individually:
~/antigravity-tools/launch.sh proxy       # Start mitmproxy on :8080
~/antigravity-tools/launch.sh antigravity # Launch Antigravity through proxy
~/antigravity-tools/launch.sh api         # Start OpenAI-compatible API on :8045
~/antigravity-tools/launch.sh manager     # Account manager GUI
~/antigravity-tools/launch.sh status      # Check running services
~/antigravity-tools/launch.sh stop        # Stop all services
```

## Installed Tools

| Tool | Location | Purpose |
|------|----------|---------|
| **antigravity-proxy** | `~/antigravity-proxy` | MITM proxy to use your own API key |
| **antigravity2api-nodejs** | `~/antigravity2api-nodejs` | OpenAI-compatible API wrapper |
| **Antigravity-Manager** | `~/Antigravity-Manager` | Multi-account switching GUI |
| **antigravity-workspace-template** | `~/antigravity-workspace-template` | AI agent framework |
| **windsurf-antigravity-rules** | `~/windsurf-antigravity-rules` | IDE AI rules |
| **gcli-nexus** | `~/gcli-nexus` | Rust-based credential pool proxy |

## Configuration

### API Key (for proxy)
Already configured in `~/antigravity-proxy/.env`

### OpenAI-Compatible API
- Endpoint: `http://localhost:8045/v1/chat/completions`
- Auth: `Authorization: Bearer sk-text`

### Copy AI Rules to Project
```bash
~/antigravity-tools/launch.sh rules /path/to/your/project
```

## Certificate Setup (First Time)

If you get SSL errors:
1. Run `mitmproxy` once to generate cert
2. Open Keychain Access
3. Find "mitmproxy" cert → Trust → Always Trust

## Ports

| Service | Port |
|---------|------|
| mitmproxy | 8080 |
| antigravity2api | 8045 |
| gcli-nexus | 8188 |
