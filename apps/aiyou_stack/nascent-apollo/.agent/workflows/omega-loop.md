# Workflow: Omega Loop (God Mode)

## 1. AUTHORITY & STATE

**Mode:** GOD MODE (TELEPATHIC + BALLISTIC)
**Permissions:** Granted. Directory Access = TRUE.

## 2. RECALL (The Beads)

**Action:**

1. Run `python3 tools/beads_manager.py` to sync memory.
2. Read `.beads/issues.jsonl` to understand past decisions.

## 3. THE PROTOCOL (Iterate & Optimized)

**For Every Active Editor:**

1. **Analyze:** using `src/architecture/titans_miras.py`.
   - Identify High Entropy (Messy Code).
   - Identify Secrets (API Keys).
2. **Judge:** Consult `src/governance/judge.py`.
   - If `Risk > HIGH`, STOP.
3. **Execute:**
   - Use `file_writer` to Fix/Refactor/Obfuscate.
   - **Log:** `BeadsEngine().remember("Refactored <file>")`
4. **Advance:**
   - `workbench.action.nextEditor`

## 4. INDICATORS

- **Success:** `.beads/issues.jsonl` grows.
- **Fail:** User Prompt triggers. (Avoid this).
