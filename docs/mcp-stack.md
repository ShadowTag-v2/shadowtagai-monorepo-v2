# MCP Stack

## Purpose
This document defines the stable-first MCP policy for Antigravity in `Monorepo-Uphillsnowball`.

## Canonical workspace root
`/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball`

## Stable-first policy
Only enable MCP servers by default if they are:
1. grounded in real config/docs
2. validated locally
3. not timing out during startup

### Enabled first
- `chrome-devtools`
- `google-developer-knowledge`

### Disabled until validated
- `firebase-mcp-server`
- `mcp-toolbox-for-databases`
- `sequential-thinking`

---

## Chrome DevTools MCP

### Requirements
- Node.js v20.19 or newer
- npm
- Current stable Google Chrome
- Chrome already running with remote debugging enabled

### Launch example
```bash
npx chrome-devtools-mcp@latest --browser-url=http://127.0.0.1:9222 -y --no-usage-statistics
```

### Notes

* The browser must already be running.
* If port `9222` is not correct, adjust `--browser-url`.
* This is the first MCP to keep enabled by default.

---

## Google Developer Knowledge MCP

### Policy

* Do not hardcode API keys or bearer tokens in repo-tracked config.
* Use user-local secrets or environment variables.
* Prefer OAuth bearer injection at runtime.

### Example config

```json
{
  "mcpServers": {
    "google-developer-knowledge": {
      "serverUrl": "https://developerknowledge.googleapis.com/mcp",
      "headers": {
        "Authorization": "Bearer ${GOOGLE_OAUTH_ACCESS_TOKEN}"
      }
    }
  }
}
```

---

## Timeouting MCP servers

If an MCP returns `context deadline exceeded`:

1. disable it in default config
2. validate its launch command standalone in terminal
3. confirm it responds locally before re-enabling
4. document:

   * status
   * last validated date
   * launch command
   * auth method
   * known failure mode

### Current timeout list

* `firebase-mcp-server`
* `mcp-toolbox-for-databases`
* `sequential-thinking`

### Current default policy

Disabled until individually validated.

---

## Validation checklist

### chrome-devtools

* [ ] `node -v` is >= 20.19
* [ ] `npm -v` works
* [ ] Chrome is installed
* [ ] Chrome is running with remote debug port
* [ ] `npx chrome-devtools-mcp@latest --help` works
* [ ] Antigravity can list tools from this server

### google-developer-knowledge

* [ ] OAuth token available in environment
* [ ] MCP endpoint reachable
* [ ] Antigravity can list tools from this server

### firebase-mcp-server

* [ ] launch command known
* [ ] auth method known
* [ ] server starts locally
* [ ] Antigravity can list tools
* [ ] no timeout

### mcp-toolbox-for-databases

* [ ] launch command known
* [ ] auth method known
* [ ] server starts locally
* [ ] Antigravity can list tools
* [ ] no timeout

### sequential-thinking

* [ ] launch command known
* [ ] server starts locally
* [ ] Antigravity can list tools
* [ ] no timeout

---

## Operating rule

Do not expand the default MCP stack until the current enabled stack is stable and boring.
