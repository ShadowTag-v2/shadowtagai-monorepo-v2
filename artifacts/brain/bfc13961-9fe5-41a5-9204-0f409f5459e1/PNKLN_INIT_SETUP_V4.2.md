# PNKLN INIT SETUP (v4.2 - CONSOLIDATED)

**Objective**: Initialize the Sovereign Host (`shadowtag-omega-v2`) with the unified context of all 83 ingested resources.

## 1. Context & Definition
"v4.2" represents the **Post-Consolidation** state where:
- The **Host** is `ShadowTag-v2`.
- The **Memory** is the aggregation of local paths and remote repos.
- The **Engine** is `flying_monkeys.py` (Gemini 2.5).

## 2. Protocol Steps (The Script)
We will create `scripts/pnkln_init_setup_v4.2.sh` to execute the following:

### Step 1: Identity Verification
- Confirm `PROJECT_ID == shadowtag-omega-v2`.
- Confirm `Directory == /Users/pikeymickey/aiyou-stack/ShadowTag-v2`.
- Confirm `ShadowTagOmega.code-workspace` exists.

### Step 2: Governance Check (Judge 6)
- Verify `JudgeSix` class is importable.
- Verify `DANGEROUS_TOKENS` list is active.

### Step 3: Memory Indexing (The Consolidated 83)
- Scan `external_memory/local_links` (19 Paths).
- Scan `external_memory/repos` (64 Repos).
- Generate a `PNKLN_INDEX_V4.2.json` map.

### Step 4: Cortex Connection
- Test connection to `gemini-2.5-flash` (Speed).
- Test connection to `gemini-2.5-pro` (Reasoning).

## 3. Execution
Run `./scripts/pnkln_init_setup_v4.2.sh`.

**Success Criteria**:
- Output: `>>>  PNKLN V4.2 CORE ONLINE.`
