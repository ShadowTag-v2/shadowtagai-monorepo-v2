# CONFLICT RESOLUTION LEDGER (The Canon)

**Objective**: Resolve version conflicts among the 83 ingested resources and define the "Single Source of Truth."

## 1. THE SOVEREIGN HOST (Tier 1 - ACTIVE)
**Role**: The Operating System. All *new* code and *active* agents live here.
- **Project**: `ShadowTag-v2`
- **Location**: `/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2`
- **Status**: **LIVE WRITING**
- **Action**: All terminal commands and file edits target this root.

## 2. PRIMARY REFERENCE (Tier 2 - READ ONLY)
**Role**: The immediate predecessor / "Previous Life". High-value context.
- **Criteria**: Paths located in `/Users/pikeymickey/` (non-deleted).
- **Projects**:
  - `ShadowTag-v2-fastapi-services` (Direct User Path)
  - `.antigravity` (Config)
- **Action**: Use for **Reference Only**. Do not edit. Copy useful code *into* Tier 1.

## 3. DEEP ARCHIVE (Tier 3 - FROZEN)
**Role**: Forensic evidence and backup. "Deleted Users" paths.
- **Criteria**: Paths located in `/Users/Deleted Users/`.
- **Projects**:
  - `ShadowTag-v2-fastapi-services` (legacy versions)
  - `judge6-mcp` (legacy)
  - `google-cloud-sdk` (legacy)
- **Action**: **IGNORE** unless explicitly mining for lost artifacts.

## 4. EXTERNAL TOOLS (Tier 4 - LIBRARY)
**Role**: The "Belt". Third-party tools and repos.
- **Location**: `external_memory/repos/`
- **Projects**: `Antigravity-Manager`, `Awesome-Antigravity`, etc.
- **Action**: Use as **Libraries/Dependencies**. Do not modify source.

---

## DECISION MATRIX: "Which are we using?"

| Component | **WINNER (Use This)** | LOSER (Ignore/Ref) |
| :--- | :--- | :--- |
| **Agent Core** | `ShadowTag-v2/agents/autoresearch.py` | `antigravity-agent` (repo) |
| **Memory** | `ShadowTag-v2/.gemini/` | `erik-hancock-llm-memory` |
| **Backend** | `ShadowTag-v2/src/libs/ShadowTag-v2` | `ShadowTag-v2-fastapi-services` (old) |
| **Infrastructure** | `ShadowTag-v2/infrastructure` | `google-cloud-sdk` (old) |
| **Governance** | `ShadowTag-v2/agents/autoresearch.py` (Judge6) | `judge6-mcp` (old) |

**VERDICT**:
You are using **ShadowTag-v2**.
Everything else is just **Memory**.
