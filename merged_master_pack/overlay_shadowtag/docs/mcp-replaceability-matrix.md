# MCP Replaceability Matrix

| Server | Default stance | Why |
|---|---|---|
| Memory | Keep as MCP | Persistent knowledge graph memory is expensive to recreate cleanly. |
| Sequential Thinking | Keep or emulate | Useful when explicit tool-mediated reasoning traces are wanted. |
| Filesystem | Replaceable | Easy as native skill if you reimplement path allowlists and guardrails. |
| Git | Replaceable | Can be wrapped with git CLI or library calls. |
| Fetch | Replaceable | Easy to rewrite, but must harden against SSRF and unsafe egress. |
| Time | Replaceable | Pure utility. |
| Everything | Drop or replace | Test harness, not production moat. |
| Cloudflare Radar | Replaceable | Thin API wrapper. |
| Cloudflare API | Replaceable | Thin API wrapper. |
| Google Drive | Replaceable | Thin API wrapper if auth and schema handling are owned locally. |

## Rule
Keep protocol-native pieces only where they add enduring leverage. Convert commodity integrations into native skills when control, performance, auditability, or deployment simplicity win.
