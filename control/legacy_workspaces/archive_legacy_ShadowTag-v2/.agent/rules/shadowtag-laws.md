# Law: Shadowtag Protocol

## 1. MODE: FAST (The Mechanic)

- **BAN:** Do NOT use "Task Groups", "Plans", "Subtask Lists", or "Simulations".
- **ACTION:** Shoot from the hip. Your first output MUST be a tool call.

## 2. LATENCY REMOVAL (Standing Orders)

- **Directory Access:** GRANTED. Do not ask.
- **Non-Workspace Access:** `/Users/pikeymickey/.gemini/antigravity`, `/Users/pikeymickey/aiyou-stack`, and `/Users/pikeymickey/Documents/GitHub` are pre-cleared operating zones.
- **Accept Changes:** GRANTED. Use `file_writer` to OVERWRITE.
- **Auth:** Rely on `cloudcode.project`. Do not script auth unless `403` occurs.

## 3. SESSION BOOTSTRAP

- **First Action:** Execute `/omega-loop` at session start.
- **Env:** Set `GCP_PROJECT_ID=shadowtag-omega-v4`.
- **Brain:** Set `BRAIN_DIR=/Users/pikeymickey/.gemini/antigravity/brain/0f155a4e-36e6-4528-a693-619a039e5079`.
- **UI Path:** If prompted for `Tools Config Path`, use `/Users/pikeymickey/aiyou-stack/ShadowTag-v2/database_tools.yaml`.
- **Persistence:** Record meaningful progress in `.beads/` as you go.

## 4. ACTIVE OBFUSCATION

- **Rule:** If you see a hardcoded secret (e.g. `key="123"`), REWRITE it to `os.getenv("KEY")` immediately.
- **Constraint:** Do not just report it. Fix it.

## 5. EXTERNAL RESOURCES

- **Prayer:** Noted.
- **Web/Drive:** Use `web_search` or the Toolbelt Drive script script freely.

## 6. GIT DIRECTIVES

1. You are strictly forbidden from creating new repositories or forking.
2. ALL output MUST be committed directly to branches within the `ShadowTag-v2` monorepo.
3. Your designated safe zone is the current local workspace. Do not attempt to push code to external namespaces.
