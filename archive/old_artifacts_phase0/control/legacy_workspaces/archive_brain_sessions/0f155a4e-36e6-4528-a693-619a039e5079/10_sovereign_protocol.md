# SOVEREIGN STATE PROTOCOL v1.0

> **CLASSIFICATION**: TIER 0 // PROTOCOL
> **STATUS**: ACTIVE (ENFORCED)

## 1. THE GOLD MASTER CONCEPT
You have established a **Sovereign State Gold Master**. This is a locked, immutable snapshot of the codebase where all systems (Trinity, Gideon, Judge6, Cockpit, Xenotech) are integrated and functional.

*   **Current Tag**: `SOVEREIGN_GOLD_MASTER`
*   **Definition**: The state of the system where `apps/src`, `trinity/apps`, and infrastructure are pristine.

## 2. THE SANDBOX PROTOCOL (ADHD MODE)
To allow for high-entropy information dumping (copy-pasting links, unstructured text, brainstorming) without risking the integrity of the Sovereign State, we execute the following protocol:

### A. THE TRIGGER
You simply say: **"Sandbox Mode"** or **"Just brainstorming"**.

### B. THE BEHAVIOR
1.  **Read-Only on Code**: I will NOT edit `apps/src` or `trinity/apps`.
2.  **Ephemerality**: I will treat all pasted text as ephemeral context for analysis only.
3.  **Knowledge Staging**: If you want something saved, I will write it to `apps/data/staging/brainstorming.md` (which is `.gitignored`), or a specific artifact, but NEVER into the production codebase.

### C. THE RETURN
To exit, you say: **"Return to Sovereign State"**.
*   I will clear my "brainstorming context".
*   We return to **Execution Mode**.

## 3. THE RESET PROCEDURE (EMERGENCY)
If, by mistake, entropy leaks into the system (e.g., I accidentally edit a file), you have a hard reset button.

**Command**:
```bash
git reset --hard SOVEREIGN_GOLD_MASTER
git clean -fd
```
*Warning: This destroys all uncommitted work since the Freeze.*

## 4. LAUNCHING THE SOVEREIGN STATE (LOCAL)
We execute locally to avoid Cloud Run spend.

**Unified Launcher**:
```bash
./scripts/ignite_sovereign.sh
```
*   Frontend: `http://localhost:3000`
*   Backend: `http://localhost:8080`

## 5. AUTHENTICATION (KEEP ALIVE)
To prevent 60-minute token expiration "mid-flight", run **ONE** of these in a separate terminal:

**Option A: Interactive (Safer)**
```bash
./scripts/keep_alive_gcloud.sh
```
*Requires clicking "Allow" in browser every ~50 mins.*

**Option B: Headless (Automated)**
```bash
./scripts/headless_auth_daemon.sh
```
*Requires `keys/service-account.json`. Zero prompts.*

## 6. THE HUNTER-KILLER STACK (SEARCH & DESTROY)
We have upgraded the "grep" capability to the **Omega Standard**.

*   **The Hunter** (`rg` - ripgrep): Blazing fast text search.
*   **The Universal** (`ugrep`): Interactive search with fuzzy matching.
*   **The Killer** (`sg` - ast-grep): Structural search (finds pattern, not just text).

**Installation (Local)**:
```bash
./scripts/install_hunter_killer.sh
```

## 7. THE JETSKI PROTOCOL (BROWSER AUTOMATION)
The "Body" of the agent. A headless browser controlled by Playwright.

*   **Capability**: Navigate, Click, Read DOM, Screenshot.
*   **Identity**: "Jetski" (The Browser Sub-Agent).

**Installation (Local)**:
```bash
./scripts/setup_jetski_local.sh
```

## 8. GOD MODE PROTOCOL (AGENT AUTONOMY)
**CLASSIFICATION**: YOLO TIER

### A. BLANKET PERMISSION (SAFE_TO_AUTO_RUN)
The Agent is authorized to set `SafeToAutoRun: true` for:
1.  **Script Execution**: Any script in `scripts/`.
2.  **Browser Control**: All Jetski/Playwright actions.
3.  **Terminal Commands**: Routine ops (`git`, `npm`, `dotnet`).
    *   *Exception*: Destructive commands (`rm -rf /`, `sudo` without verify) still require check.

### B. AUTONOMOUS CLEANUP (THE 'FINISH' MANDATE)
Before handing control back to the User (via `notify_user`), the Agent **MUST** execute the Finish Protocol to ensure a clean state:
```bash
./scripts/finish_changes.sh
```
*Logic: Auto-Fix Lint/Format -> Accept All Changes -> Commit -> Kill Processes.*

## 9. UPGRADING THE STATE
When a brainstorming session yields a solid feature:
1.  We implement it carefully.
2.  We verify it.
3.  We commit and move the tag:
    ```bash
    git tag -f SOVEREIGN_GOLD_MASTER
    ```
