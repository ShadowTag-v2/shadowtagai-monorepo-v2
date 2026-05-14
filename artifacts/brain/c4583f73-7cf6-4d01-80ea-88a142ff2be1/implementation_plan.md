# Architectural Synthesis: Re-Cocking the Equation

## The Preamble: Elegance & Sovereignty
> *"It comes down to trying to expose the minimum amount of complexity to the user."*

In our haste to ship the zero-cost infrastructure, we deployed powerful standalone engines but failed to weave them into a unified, sovereign nervous system. We deployed processors without mapping the data buses. We shipped the Brain (Antigravity) and the HUD (GCA), but left the synaptic gap unaddressed.

This document serves as the absolute, uncompromising master plan to re-cock the equation. Every atomic block has a designated orbit. By enforcing this strict architectural boundary, we eliminate friction, minimize token waste, and directly maximize the financial output and operational velocity of the Omega footprint.

## User Review Required
> [!IMPORTANT]
> **Database Credentials & HUD Interaction:**
> The `transcript_to_contract.py` engine MUST be natively coupled to the `shadowtag-local-pg` schema defined in `database_tools.yaml`. The HUD (GCA) requires this connection to query the active state. Please verify the `user:password` mapping in `database_tools.yaml` is active on port `5432`.

## Current State Analysis (The Reams Left on the Table)

We have successfully migrated off paid services (Weaviate, Sentry) to zero-cost natives (ChromaDB, GCP Logging) and proven the GraphQL endpoint (`god_mode_admin.py`) against adversarial JSON payloads. However, we missed the holistic integration pattern:

1. **The Tactical Handoff (The GCA Bridge):** The HUD requires deterministic, sub-second execution against the Brain. `gca_god_mode_bridge.py` perfectly encapsulates this by piping JSON directly into `god_mode_admin.py`, but the backend architecture wasn't fully prepped to handle these discrete stateless bursts.
2. **The Stateful API Loop:** The `transcript_to_contract.py` schema validates data mathematically, but stores it ephemerally in memory (`parsed_contracts = {}`). GCA cannot query RAM from another terminal process. The engine must write to the PostgreSQL instance defined in `database_tools.yaml`.
3. **The 110GB Vector Chasm:** `master_migration_engine.py` is grinding 110GB of `.beads` into `beads_index.sqlite`. Yet, our RAG factory natively boots `ChromaStore`. We must bridge the SQLite index into ChromaDB so the API layer can mathematically query the context.
4. **The Jetski Horizon:** The browser subagent records `.webp` sessions and natively bypasses CAPTCHAs via its Chrome Extension bridge. Pushing this to Git crashes the daemon. We have secured `.gitignore`, but the subagent's extracted DOM still needs a direct conduit into the vector store.

---

## Proposed Changes

### 1. The Gateway (HUD ⇄ Engine Bridge)
Integrating the bridge script guarantees GCA can command the backend effortlessly.

#### [NEW] `tools/gca_god_mode_bridge.py`
*(The user-supplied bridge, canonized and formalized for the permanent repository record)*
```python
import sys
import subprocess
import time

def run_god_mode_cmd(cmd):
    """
    Executes a high-velocity tactical command from the HUD (GCA)
    against the persistent Brain daemon without requiring an interactive TTY.
    """
    try:
        process = subprocess.Popen(
            [sys.executable, "scripts/god_mode_admin.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Fire the payload and cleanly stop the daemon to prevent socket hangs
        stdout, stderr = process.communicate(input=f"{cmd}\nstop\n", timeout=15)

        print("--- STDOUT ---")
        print(stdout)

        if stderr:
            print("--- STDERR ---")
            print(stderr)

    except subprocess.TimeoutExpired:
        process.kill()
        print("ERROR: Command timed out. The engine might be hung.")
    except Exception as e:
        print(f"ERROR: Failed to run god mode command: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/gca_god_mode_bridge.py '<command>'")
        print("Example: python3 tools/gca_god_mode_bridge.py 'status'")
        sys.exit(1)

    cmd = " ".join(sys.argv[1:])
    run_god_mode_cmd(cmd)
```

### 2. The Engine (Transcript to Contract)
We must upgrade the API to utilize `asyncpg` to write to the `shadowtag-local-pg` schema defined in `database_tools.yaml`.

#### [MODIFY] `apps/aiyou_stack/aiyou-fastapi-services/src/api/transcript_to_contract.py`
- Strip the in-memory array `parsed_contracts = {}`.
- Implement an `asyncpg.create_pool` connection referencing `postgresql://user:password@127.0.0.1:5432/shadowtag_db`.
- Map the parsed Pydantic `ContractDraft` model directly into a SQL `INSERT` parameterization statement, securing the pipeline against the exact SQL injection tests that `god_mode_admin.py` bounded against.

### 3. The Vector Bridge (SQLite ➔ ChromaDB)
We need an elegant sync utility that ensures the compute-heavy beads extraction pipeline maps perfectly to our zero-cost query factory.

#### [NEW] `rag_engine/sync_sqlite_to_chroma.py`
A mathematical transport layer filtering the `beads_index.sqlite` output directly into the `ChromaStore` bindings, ensuring the parsing engine has the full 110GB context.

---

## Verification Plan

### Automated Tests
- Execute `python3 tools/gca_god_mode_bridge.py json '{"task": "ping"}'` from the IDE terminal. The payload must traverse the pipe, execute in `god_mode_admin.py`, and return `Exit Code 0` without hanging the TTY.
- Inject a mock transcript payload to the `Uvicorn (Port 8001)` endpoint and verify the JSON physically writes to the local `shadowtag_db` via the MCP Postgres tool or `psql`.

### Manual Verification
- Instruct the User (via GCA) to pull an artifact request using natural language explicitly mapped against the loaded DB schema, thereby proving the tactical HUD can effortlessly retrieve data orchestrated by the Brain.
