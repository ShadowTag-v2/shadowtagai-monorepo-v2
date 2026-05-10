# LSP Passive Feedback

## Overview
Harvested from `lsp/` (LSPServerManager, passiveFeedback.ts). This skill enhances the `post-edit-validation-loop`.

## Protocol
1. Instead of waiting for a manual `npm run lint` or `tsc` command, the agent should assume the IDE's LSP is generating diagnostics in real-time.
2. If available, read the `.lint-results/` or LSP dump files.
3. Preemptively auto-fix errors (e.g., missing imports, type mismatches) BEFORE reporting task completion to the user.
