---
name: Firebase MCP Recovery
description: >
  Standard Operating Procedure for recovering the Firebase MCP server from EOF crashes
  inside Electron-based IDEs (VS Code, Antigravity, Cursor, etc.). Covers root cause
  diagnosis, zombie cleanup, config hardening, and manual handshake tracing.
---

# Firebase MCP Recovery — SOP v1.0

## Trigger

This skill activates when:
- `firebase-mcp-server` tools return `connection closed: calling tools/call: client is closing: EOF`
- Firebase MCP is missing from the session's tool manifest after IDE restart
- Other MCP servers (Stitch, Chrome DevTools, DevKnowledge, Sequential Thinking) work fine but Firebase does not

## Root Causes (Gemini Deep Think Pro Diagnosis, 2026-04-25)

| # | Cause | Mechanism |
|---|-------|-----------|
| 1 | **Stdout Pollution** | Firebase CLI writes interactive prompts (analytics opt-in, npm update warnings) to stdout, corrupting the JSON-RPC stream |
| 2 | **Stale Command** | `experimental:mcp` was renamed to `mcp` in firebase-tools v15.x — old command fails silently |
| 3 | **Expired Auth** | CLI attempts browser redirect for re-auth, which deadlocks in headless Electron |
| 4 | **Missing Context** | No `--dir` flag → server starts in wrong directory without `firebase.json` |
| 5 | **Zombie Processes** | Previous MCP server instances hold the port/pipe, blocking reconnection |
| 6 | **Debug Log Lock** | Stale `firebase-debug.log` with wrong permissions causes write failure on startup |

## Recovery Procedure

### Phase 1: Zombie Cleanup (Terminal)

```bash
# Kill all firebase-tools and npx zombie processes
pkill -f "firebase-tools" 2>/dev/null
pkill -f "firebase.*mcp" 2>/dev/null

# Remove stale debug logs
rm -f firebase-debug.log

# Verify no lingering processes
ps aux | grep -i firebase | grep -v grep
```

### Phase 2: Config Hardening (antigravity-mcp-config.json)

The `firebase-mcp-server` entry MUST have these properties:

```json
"firebase-mcp-server": {
  "command": "npx",
  "args": [
    "-y",
    "firebase-tools@latest",
    "mcp",
    "--dir",
    "/absolute/path/to/project/root"
  ],
  "env": {
    "CI": "true",
    "FIREBASE_CLI_NONINTERACTIVE": "true",
    "NO_UPDATE_NOTIFIER": "1"
  }
}
```

**Critical env vars:**
- `CI=true` — Suppresses ALL interactive prompts (Inquirer.js, analytics, login redirects)
- `FIREBASE_CLI_NONINTERACTIVE=true` — Firebase-specific headless mode
- `NO_UPDATE_NOTIFIER=1` — Prevents npm update-notifier from writing to stdout

**Critical args:**
- `mcp` (NOT `experimental:mcp`) — The command was promoted in firebase-tools v15.x
- `--dir <path>` — Explicit project root so the server finds `firebase.json`

### Phase 3: CLI State Reset (Terminal)

If config hardening alone doesn't fix it:

```bash
# Force re-auth in terminal (saves preferences to disk)
CI=true firebase logout
CI=true firebase login --reauth --no-localhost

# Set active project context
CI=true firebase use shadowtag-omega-v4

# Verify CLI works
CI=true firebase projects:list
```

### Phase 4: Manual Handshake Trace (Terminal)

If the server still crashes, run it manually to see the raw error:

```bash
# Start the MCP server directly and send init handshake
CI=true FIREBASE_CLI_NONINTERACTIVE=true NO_UPDATE_NOTIFIER=1 \
  npx -y firebase-tools@latest mcp --dir /path/to/project 2>firebase-mcp-stderr.log &
MCP_PID=$!

# Send JSON-RPC initialize request
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | \
  kill -0 $MCP_PID 2>/dev/null && echo "Server alive" || echo "Server crashed"

# Check stderr for the real error
cat firebase-mcp-stderr.log
kill $MCP_PID 2>/dev/null
```

### Phase 5: IDE Restart

After applying config changes:
1. **Quit IDE completely** (Cmd+Q on macOS)
2. **Relaunch** — the MCP server will spawn with the corrected config
3. **Verify** — call `firebase_get_environment` MCP tool
4. If still failing, check the IDE's MCP output panel for startup errors

## Prevention Checklist

- [ ] `env.CI` = `"true"` in MCP config
- [ ] `env.FIREBASE_CLI_NONINTERACTIVE` = `"true"` in MCP config
- [ ] `env.NO_UPDATE_NOTIFIER` = `"1"` in MCP config
- [ ] Command is `mcp` not `experimental:mcp`
- [ ] `--dir` points to absolute project root with `firebase.json`
- [ ] No stale `firebase-debug.log` in project root
- [ ] CLI auth is current (`firebase login:list` shows active session)
- [ ] firebase-tools is latest (`npx firebase-tools@latest --version`)

## Gemini Deep Think Consultation Pattern

This skill was created using the **Gemini Deep Think Pro consultation pattern**:

1. Navigate to `https://gemini.google.com/`
2. Set LEFT tools menu → **Deep Think** (experimental reasoning)
3. Set RIGHT model picker → **Pro** (Gemini 2.5 Pro / 3.1 Pro)
4. Submit diagnostic prompt with full error context
5. **CRITICAL**: Keep scrolling/interacting with the page during generation — Deep Think requires active page engagement to complete
6. Wait 2-5 minutes for extended reasoning to complete
7. Extract the response and apply fixes

This pattern is useful for any complex diagnostic question where standard search fails. The key insight is that Deep Think mode produces significantly more thorough root-cause analysis than standard Gemini modes.

## References

- Gemini conversation: `https://gemini.google.com/app/1ab19b9a660086e0` (2026-04-25)
- Medium article: [Secure CI/CD with GitHub Apps Short-Lived Tokens](https://medium.com/@devopswithyoge/secure-ci-cd-with-github-apps-short-lived-tokens-227d6e05c5fa)
- Firebase MCP docs: `firebase mcp --help`
- Headless CLI doctrine: `GEMINI.md` → `headless_cli_doctrine`
