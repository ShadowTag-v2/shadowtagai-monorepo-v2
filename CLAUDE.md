# CLAUDE.md
## Developer Instructions
- A developer who reads every generated file before accepting it
- Auth that was designed before it was prompted
- DB schemas that considered relationships, indexes, and migrations
- Error handling that actually does something
- At least one test for the critical paths

## Orthogonal Edits Rule
- STRICT MINIMAL EDIT: You must avoid editing unrelated lines or helper files to mask context. Prevent polluting the attention mechanism. Do not add hallucinated dependencies to justify changes made in previous turns. Keep the context window focused on the actual task instead of an ever-expanding web of side effects.

## Firebase MCP-First Deployment (see GEMINI.md §firebase_mcp_doctrine)
- Firebase MCP server is the ONLY authorized deployment path.
- Deploy is an MCP Resource/Prompt (`firebase://guides/init/hosting`), not a Tool.
- Terminal CLI does NOT inherit MCP session credentials.
- Full doctrine: `skills/firebase-mcp-deploy-doctrine/SKILL.md`

## GitHub Doctrine
- GitHub Apps ONLY. Deploy keys are NOT acceptable.
- SSH is mandatory transport. HTTPS is last-resort fallback.
