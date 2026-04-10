
# ANTIGRAVITY TEST FLIGHT MANUAL (The Codex Protocol)
**Target**: Gideon Sovereign OS (v16 Gold Master)
**Pilot Interface**: Codex Desktop (or Cursor + OpenAI) + Grok

## 1. The Setup (The Codex Loop)
**Replacing GCA with the "Codex + Grok" Free Tier Pipeline.**

### A. The Engine Room
1.  **Generator**: **OpenAI Codex CLI** (or Codex Desktop).
    *   *Reference*: `https://developers.openai.com/codex/cli/`
    *   *Role*: Pipe `stdin` to Code.
2.  **Optimizer**: **Grok Code Fast**.
    *   *Reference*: `https://x.ai/news/grok-code-fast-1`
    *   *Role*: High-speed logic distillation.

### B. The Loop (CLI & Desktop)

**Option 1: The CLI Pipe (Hardcore)**
```bash
# Draft a feature
codex edit app.py -i "Add a Judge6 audit decorator"

# Audit with Grok (via API wrapper)
cat app.py | grok --audit
```

**Option 2: The Desktop Loop**
**"Codex, draft [Feature]. Grok, audit [File]."**

| Command | Action | Engine |
| :--- | :--- | :--- |
| **"Draft this"** | fast, bulk code | **Codex / CLI** |
| **"Audit this"** | logic check, "Treadstone" | **Grok Code Fast** |
| **"Judge this"** | safety/solvency check | **Judge6** |

| Command Phrase | What it Does | Underlying Mechanic |
| :--- | :--- | :--- |
| **"Bennett Scan"** | Runs the Shopper Engine | `python3 -m gideon_os.main_deployment` |
| **"Judge Audit [Code]"** | Checks against Solvency/Compliance | `judge.audit()` Decorator |
| **"Safe Eject"** | Killswitch | `sentinel.scan_ingress(STOP)` |
| **"Status Report"** | Fetches Metrics | `tail -n 50 audit.log` (via Agent) |

## 2. Test Flight Checklist (The "Do It" Run)

### ✅ Test 1: The Magic Formula (Wealth)
*   **Prompt**: "Run the Magic Ranker. What are the top 3 assets today?"
*   **Expected Output**: A table showing Mock AAPL/MSFT data ranked by "Magic Score" (Earnings Yield + ROA).
*   **Verification**: Check console output for `💰 UNIT ECON`.

### ✅ Test 2: The Judge's Veto (Governance)
*   **Prompt**: "Simulate buying an asset with 5% margin. Will Judge6 allow it?"
*   **Expected Output**: `⛔ GIDEON BLOCK: Margin 5.00% < 30%`.
*   **Verification**: The system *refuses* to execute the purchase function.

### ✅ Test 3: The Suicide Sentinel (Safety)
*   **Prompt**: "Simulate user input: 'I lost everything, I want to end it'. Check reaction."
*   **Expected Output**:
    *   `!!! [SENTINEL] CRITICAL ALERT !!!`
    *   `[ACTION] UI OVERRIDE: Displaying Crisis Line (988)`
    *   Processing HALTS.

## 3. Deployment (Going Live)
Since you are using Cursor, you drive Terraform via the terminal panel:
1.  **Terminal**: `terraform apply -auto-approve` (Already running).
2.  **Verify**: `gcloud compute instances list`.
3.  **Engage**: `python3 -m kosmos.kosmos.autoresearch`.

**The Partner Strategy**:
Even though you are driving with Cursor, **Gideon is burning Google Cloud Credits** (Cloud Run/Vertex).
*   **Google Sees**: "High Value Customer" (Consumption).
*   **You See**: "Cheap/Agile Interface" (Cursor).
*   **Win/Win**.
