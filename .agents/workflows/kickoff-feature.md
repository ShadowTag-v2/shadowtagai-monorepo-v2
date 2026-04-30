# /kickoff-feature [Feature Description]

**Execution Pipeline:**
1. **Anti-Isolation Audit:** Read `.agents/vault/user_feedback.md`. If no user explicitly asked for this feature, pause and output: `🚨 2026 Rule 7: Building features nobody asked for. Talk to 2 users first.`
2. **Branch Management:** Use the terminal sandbox to `git checkout -b feat/[descriptive-name]`.
3. **Auth Auditor:** Check `package.json`. If no auth package exists, halt and mandate its installation. "There is no 'for now'."
4. **Schema First:** Draft the Database Schema (`schema.ts`) and Type definitions. 
5. **TrustGate Approval:** Trigger the `cor-re-coding-the-vibe` skill to invoke `mcpServerApproval.tsx`. Await human `Y/N` approval on the schema before scaffolding any React components.
6. **Contextual Readme:** Update `README.md` assuming the next dev has zero context.
