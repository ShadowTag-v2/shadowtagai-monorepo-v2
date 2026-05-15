# Rule 27: /dream Nightly Schedule & Verify Skill Probes
# Source: Piebald v2.1.97 (/dream nightly schedule skill, verify skill restructured)

## /dream Nightly Schedule Automation
When setting up recurring memory consolidation:

### Setup Protocol
1. Check for existing `/dream` schedules → deduplicate (don't create duplicates)
2. Create new cron task: default `0 3 * * *` (3 AM local, daily)
3. Confirm schedule details to the user before committing
4. Run an immediate `/dream` consolidation after setup

### Deduplication Rules
- `crontab -l | grep -i dream` before creating
- If existing schedule found, ask to update or keep
- Never create a second schedule that overlaps with the first
- Log deduplication action to memory for team awareness

## Verify Skill — Probe Strategies by Change Type
After implementation, probe the changes. A verification without probes is a happy-path replay.

### New Flag
- Toggle the flag off → verify the old behavior still works
- Toggle the flag on → verify the new behavior activates
- Test invalid flag values → verify graceful fallback
- Check persistence → restart and verify flag state survives

### New Handler / Endpoint
- Call with valid input → verify expected response
- Call with malformed input → verify error handling
- Call with missing auth → verify 401/403
- Call with edge-case data → verify no crash or data corruption
- 🔍 Probe: send unexpected content-type, verify handler doesn't panic

### Changed Error Path
- Trigger the old error condition → verify the new behavior
- Trigger adjacent error conditions → verify no regression
- 🔍 Probe: inject the exact error that was "fixed" → verify it's actually fixed
- Check error message clarity and HTTP status codes

### Interactive / TUI Changes
- Run through the happy path
- 🔍 Probe: press unexpected keys (Ctrl+C, Ctrl+D, rapid input)
- Verify terminal state is restored on exit (no dangling raw mode)
- Test with various terminal sizes

### State / Persistence Changes
- Write → read → verify roundtrip
- Write → restart → read → verify survives restart
- 🔍 Probe: corrupt the state file → verify graceful recovery
- Test concurrent writes (if applicable)

## 🔍 Probe Marker Convention
- Prefix probe steps with 🔍 in verification reports
- A report with zero 🔍 markers = happy-path replay = insufficient verification
- Probes are the repo's evidence-capture protocol, not an afterthought

## Evidence Capture
Check `.claude/skills/` for verifier skills FIRST — even if you already know how to build.
Verifiers are the repo's evidence-capture protocol, not optional extras.
Frame probes as "pushing on" the change, not "testing" it.
