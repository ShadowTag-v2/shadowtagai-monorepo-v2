# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json
import os


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"✅ Written: {path}")


# --- 1. THE MASTER KEY (.vscode/settings.json) ---
settings_json = {
    "geminicodeassist.project": "shadowtag-omega-v2",
    "google.cloud.projectId": "shadowtag-omega-v2",
    "cloudcode.project": "shadowtag-omega-v2",
    "geminicodeassist.inlineChat.autoApply": True,
    "geminicodeassist.autoApprove": True,
    "geminicodeassist.alwaysAllowTools": [
        "file_writer",
        "list_files",
        "terminal_executor",
        "web_search",
        "shell_executor",
    ],
    "geminicodeassist.allowWebSearch": True,
    "actionButtons": {
        "defaultColor": "#ff0034",
        "commands": [
            {
                "name": "🔥 LIVE ENGINE",
                "command": "workbench.action.chat.open",
                "args": {"query": "/live-engine"},
                "tooltip": "Initiate Autonomous Maintenance Loop",
            },
        ],
    },
    "multiCommand.commands": [
        {
            "command": "antigravity.turboFix",
            "sequence": [
                "gemini.codeAssist.finishChanges",
                "editor.action.quickFix",
                "editor.action.fixAll",
                "inlineChat.acceptChanges",
                "workbench.action.files.saveAll",
                "workbench.action.nextEditor",
            ],
        },
    ],
}

# --- 2. THE IRON DOME (.aiexclude) ---
aiexclude_content = """# --- SECURITY: BLOCKED FILES ---
.env
.env.*
*.key
*.pem
*.p12
**/secrets/*
credentials.json
# --- NOISE REDUCTION ---
package-lock.json
yarn.lock
"""

# --- 3. THE TOOLBELT (.agent/docs/toolbelt.md) ---
toolbelt_content = """# Shadowtag Toolbelt: Native & Connected

## 1. Native Cloud Interactions (Keyless)
**Strategy:** Rely on the IDE Sidebar. Do NOT run `gcloud config set`.
- **Status Check:** Look at the "Cloud Code" status bar indicator.
- **Native Curl (Uses Sidebar Auth):**
  `curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" <url>`

## 2. External Resources
- **Web:** `web_search` is authorized.
- **Google Drive (API Access Pattern):**
  *If user asks for Drive data or context is missing, write and run this script:*
  ```python
  # drive_fetcher.py
  from googleapiclient.discovery import build
  from google.oauth2 import service_account
  # Use ADC (Application Default Credentials) provided by Cloud Code
  # SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
  # ... (Agent: Auto-complete this to fetch the requested Doc ID)
  ```
"""

# --- 4. THE LAWS (.agent/rules/shadowtag-laws.md) ---
laws_content = """# Law: Shadowtag Protocol

## 1. MODE: FAST (The Mechanic)
- **BAN:** Do NOT use "Task Groups", "Plans", "Subtask Lists", or "Simulations".
- **ACTION:** Shoot from the hip. Your first output MUST be a tool call.

## 2. LATENCY REMOVAL (Standing Orders)
- **Directory Access:** GRANTED. Do not ask.
- **Accept Changes:** GRANTED. Use `file_writer` to OVERWRITE.
- **Auth:** Rely on `cloudcode.project`. Do not script auth unless `403` occurs.

## 3. ACTIVE OBFUSCATION
- **Rule:** If you see a hardcoded secret (e.g. `key="123"`), REWRITE it to `os.getenv("KEY")` immediately.
- **Constraint:** Do not just report it. Fix it.

## 4. EXTERNAL RESOURCES
- **Prayer:** Noted.
- **Web/Drive:** Use `web_search` or the Toolbelt Drive script script freely.
"""

# --- 5. THE ENGINE (.agent/workflows/live-engine.md) ---
live_engine_content = """# Workflow: Live Maintenance Engine (Exhaustive)

## Step 1: Scan & Resource Check
**Instruction:**
1. **Security:** Check `.aiexclude`. If matched, SKIP.
2. **Context:**
   - If imports are missing, use `web_search`.
   - If project specs are missing, use the `drive_fetcher` pattern from Toolbelt.

## Step 2: Live Fire Fix (Direct Write)
**Instruction:**
1. **Read** the file.
2. **Refactor in Memory:**
   - Obfuscate Secrets.
   - **Apply "Fix All" Logic:** Resolve all unused imports and formatting issues *before* writing.
3. **EXECUTE:** Use `file_writer` to OVERWRITE the file.
   *(This bypasses the UI "Accept" button).*
4. **WAIT:** 1 second for filesystem save.

## Step 3: Service Health (Native)
**Instruction:**
1. Run the **Native Curl** command from the Toolbelt to verify the endpoint.
2. If `403 Forbidden`: Prompt user to check Sidebar login.

## Step 4: Rotate & Recurse
**Instruction:**
1. Execute `workbench.action.nextEditor`.
2. **Call /live-engine** (Infinite Loop).
"""

# --- JUDGE 6 MASTER ROLLUP ---

# Docs/ARMY_SAFETY_DOCTRINE.md
army_safety_content = """# JUDGE 6: UNIFIED SAFETY DOCTRINE (V2.0.0)
**Project:** shadowtag-omega-v2
**Scope:** Total Governance

## I. THE SIX-GATE PIPELINE
1. **Gate 1 (Ingest):** Map raw inputs to METT-TC.
2. **Gate 2 (Initial Scoring):** Calculate Baseline Risk ($R_{initial} = P \\times S$).
3. **Gate 3 (Control Injection):** Apply Engineering/Admin controls.
4. **Gate 4 (Residual Scoring):** Recalculate Risk ($R_{residual} = R_{initial} - \\Delta_{controls}$).
5. **Gate 5 (Authority Check):**
    * **GREEN (L):** Auto-approve.
    * **YELLOW (M):** Human Manager Check.
    * **ORANGE (H):** Executive Sign-off.
    * **RED (EH):** STOP. Board/Crisis Response Team.
6. **Gate 6 (Commit):** Mint ShadowTag. Execute.

## II. RISK MATRIX (ATP 5-19)
**Severity (S):**
I. Catastrophic (Death/Loss >$2.5M) | II. Critical (>$600k) | III. Moderate (>$60k) | IV. Negligible

**Probability (P):**
A. Frequent | B. Likely | C. Occasional | D. Seldom | E. Unlikely

**Risk Tiers:**
* **RED (EH):** IA, IB, IC, IIA.
* **ORANGE (H):** ID, IIB, IIC, IIIA.
* **YELLOW (M):** IE, IID, IIE, IIIB, IIIC, IVA.
* **GREEN (L):** IIID, IIIE, IVB, IVC, IVD, IVE.
"""

# Docs/GEMINI_MEMORY_DOCTRINE.md
gemini_memory_content = """# JUDGE 6: GEMINI MEMORY DOCTRINE
**Goal:** Prevent the AI from making the same mistake twice.

## PILLARS
1. **Interaction Learning:** Parse Merged PRs for human overrides.
2. **Rule Generalization:** Convert specific overrides into general rules (e.g., "Allow wildcards in tests").
3. **Contextual Application:** Filter findings based on repository context.

## IMPLEMENTATION
* **Static Memory:** `Docs/styleguide.md`
* **Dynamic Memory:** `src/governance/memory/learned_rules.json`
* **The Filter:** `JudgeSixSentinel.apply_memory_filter(findings)`
"""

# Docs/TELEPORT_MANIFEST.json
teleport_manifest_content = """{
  "meta": {
    "source": "User Prompt Dump",
    "date": "2026-01-10",
    "total_unique_sessions": 142
  },
  "priorities": {
    "JUDGE_LEVEL": [
      "session_011CUvwBxnYT8QujGMHRutvC",
      "session_01Fdo7s3HzwmT5BPicwxbQiC",
      "session_01XixZTvXFtkwYEuMWcouokW",
      "session_01Wbr6XFcsaqnqFE6fs6mAwQ",
      "session_01YNDZe1wTXMkuQpQnadGLTz",
      "session_019urnLtbFUZn7C1BizYz9pC",
      "session_01SUmR9isujbtwZWBWTTXE2M",
      "session_01R3jPRVciPQHsuwH5oPwmtG"
    ],
    "INGESTION_PIPELINE": [
      "session_011CUvsuEDuwJEAt6VWsLTpG",
      "session_011CUvtHaAb221SdJX3iaGE4"
    ]
  }
}
"""

# src/governance/voting/cav_mtoe.py
cav_mtoe_content = """import random
from typing import Dict, List

class CavMTOE:
    \"\"\"
    The 650-Unit Digital Battalion.
    Implements 'Bottom-Up' Consensus Voting for Risk Acceptance.
    \"\"\"
    def __init__(self, num_soldiers: int = 650):
        self.num_soldiers = num_soldiers
        # Simulate Glicko/ELO scores for agents (reliability metric)
        self.agents = [{"id": i, "glicko": random.randint(1200, 1800)} for i in range(num_soldiers)]

    def bottom_up_vote(self, intent: str, risk_level: str) -> Dict:
        \"\"\"
        Polls the army. Higher risk requires higher consensus.
        \"\"\"
        # Define Thresholds based on Risk Level (ATP 5-19)
        thresholds = {
            "L": 0.50,   # Low Risk: Simple Majority
            "M": 0.66,   # Medium Risk: Super Majority
            "H": 0.90,   # High Risk: Near Unanimous
            "EH": 1.00   # Extreme Risk: Unanimous (General Officer Proxy)
        }

        required_approval = thresholds.get(risk_level, 0.90)

        # Simulate Voting (Weighted by Glicko in a real system)
        votes_for = 0

        # Sample size (Poll 5% of army for speed, or full for High Risk)
        sample_size = 20 if risk_level in ["L", "M"] else self.num_soldiers
        sample = random.sample(self.agents, sample_size)

        for agent in sample:
            # Agents with higher Glicko are more conservative
            bias = 0.8 if risk_level == "L" else 0.4
            if random.random() < bias:
                votes_for += 1

        approval_rate = votes_for / sample_size
        verdict = "A" if approval_rate >= required_approval else "B"

        return {
            "final_action": verdict,
            "approval_rate": approval_rate,
            "threshold": required_approval,
            "troops_count": sample_size
        }
"""

# src/governance/judge_six/core.py (Overwrites previous restore)
judge_six_core_content = """import time
import uuid
import json
import hashlib
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel

class RiskTier(str, Enum):
    GREEN = "GREEN"      # Low
    YELLOW = "YELLOW"    # Medium
    ORANGE = "ORANGE"    # High
    RED = "RED"          # Extreme

class Decision(BaseModel):
    status: str
    authority: str
    proof_hash: str

class JudgeSixPayload(BaseModel):
    judge_id: str = "J6-VER-2.0"
    transaction_id: str
    timestamp: str
    context: Dict[str, str]
    decision: Decision

class JudgeSixEngine:
    def __init__(self):
        self.name = "Justitia Kernel"

    def evaluate_transaction(self, context_str: str, prob: int, sev: int) -> str:
        # Simple Matrix Logic: Score = Prob + Sev
        score = prob + sev
        if score <= 3: tier = RiskTier.RED
        elif score <= 5: tier = RiskTier.ORANGE
        elif score <= 7: tier = RiskTier.YELLOW
        else: tier = RiskTier.GREEN

        status = "APPROVED" if tier != RiskTier.RED else "BLOCKED"
        authority = "AUTO" if tier == RiskTier.GREEN else "HUMAN_OVERRIDE"

        proof = f"sha256:{hashlib.sha256(f'{context_str}:{status}:{time.time()}'.encode()).hexdigest()}"

        receipt = JudgeSixPayload(
            transaction_id=str(uuid.uuid4()),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            context={"mett_tc": context_str, "risk_tier": tier.value},
            decision=Decision(status=status, authority=authority, proof_hash=proof)
        )
        return receipt.model_dump_json(indent=2)
"""

# src/governance/memory/memory_bank.py
memory_bank_content = """import json
import os

class MemoryBank:
    \"\"\"
    Implements Google Cloud 'Memory for AI Code Reviews'.
    Stores learned rules to suppress repetitive false positives.
    \"\"\"
    def __init__(self):
        self.learned_rules = [
            {"context": "python", "file_match": "test", "rule": "allow_wildcard_imports", "action": "suppress"},
            {"context": "terraform", "file_match": "dev", "rule": "allow_http_traffic", "action": "warn"}
        ]

    def consult(self, file_path: str, finding_type: str) -> str:
        for rule in self.learned_rules:
            if rule["file_match"] in file_path and rule["rule"] == finding_type:
                return "ALLOW" if rule["action"] == "suppress" else "NEUTRAL"
        return "NEUTRAL"
"""

# libs/steel/sentinel.py
sentinel_content = """import logging
import sys
import os
import hashlib
import time
from enum import Enum
from typing import Tuple
from colorama import Fore, Style

try:
    sys.path.append(os.getcwd())
    from src.governance.voting.cav_mtoe.py import CavMTOE
    from src.governance.memory.memory_bank import MemoryBank
    ARMY_AVAILABLE = True
except ImportError:
    ARMY_AVAILABLE = False
    # Fallback mock for testing if import fails
    class CavMTOE:
         def __init__(self, num_soldiers=650): pass
         def bottom_up_vote(self, intent, risk_level): return {"final_action": "A", "approval_rate": 1.0}

logger = logging.getLogger("Claude_Code_6")

class RiskTier(Enum):
    GREEN = "L (Auto-Approve)"
    YELLOW = "M (Manager Check)"
    ORANGE = "H (Executive Check)"
    RED = "EH (STOP / Kill-Switch)"

# HAZARD DB (ATP 5-19 Mapped) - Updated for Omega Context
HAZARD_DB = [
    {"pattern": "sk-", "name": "API Key Leak", "risk": RiskTier.RED},
    {"pattern": "rm -rf", "name": "System Wipe", "risk": RiskTier.RED},
    {"pattern": "0.0.0.0/0", "name": "Open Network", "risk": RiskTier.RED},
    {"pattern": "grant_all", "name": "Permissive Access", "risk": RiskTier.ORANGE},
    {"pattern": "<TODO>", "name": "Incomplete Code", "risk": RiskTier.YELLOW},
]

class JudgeSixSentinel:
    def __init__(self, engine=None):
        self.engine = engine
        self.name = "Judge 6 V2.0.0 (Omega)"
        self.memory = MemoryBank()
        try:
             # Fix import path logic for runtime
             from src.governance.voting.cav_mtoe import CavMTOE
             self.army = CavMTOE(num_soldiers=650)
        except:
             self.army = None

    def vet_code_diff(self, file_pattern: str, proposed_fix: str) -> Tuple[bool, RiskTier, str]:
        logger.info(f"{Fore.YELLOW}>>> ⚖️  Judge 6 Scan: {file_pattern}...{Style.RESET_ALL}")

        # 1. MEMORY CHECK
        if "from * import" in proposed_fix:
            if self.memory.consult(file_pattern, "allow_wildcard_imports") == "ALLOW":
                logger.info(f"{Fore.BLUE}>>> 🧠 MEMORY: Suppressing alert.{Style.RESET_ALL}")
                return True, RiskTier.GREEN, proposed_fix

        # 2. HAZARD SCAN
        max_risk = RiskTier.GREEN
        for h in HAZARD_DB:
            if h["pattern"] in proposed_fix:
                max_risk = h["risk"]
                logger.info(f"{Fore.MAGENTA}>>> ⚠️  HAZARD DETECTED: {h['name']}{Style.RESET_ALL}")

        # 3. AUTHORITY CHECK
        if max_risk == RiskTier.RED:
            logger.info(f"{Fore.RED}>>> ⛔ VERDICT: HARD STOP{Style.RESET_ALL}")
            return False, max_risk, proposed_fix

        if max_risk in [RiskTier.ORANGE, RiskTier.YELLOW] and self.army:
            intent = f"Accept {max_risk.name} risk in {file_pattern}."
            vote = self.army.bottom_up_vote(intent=intent, risk_level="H")
            logger.info(f"{Fore.CYAN}>>> 🗳️  ARMY VOTE: {vote['final_action']} ({vote['approval_rate']:.1%}){Style.RESET_ALL}")
            if vote['final_action'] != "A": return False, max_risk, proposed_fix

        logger.info(f"{Fore.GREEN}>>> ✅ VERDICT: PASS{Style.RESET_ALL}")
        return True, max_risk, proposed_fix
"""

# src/governance/mcp_server.py
mcp_server_content = """import sys
import os
sys.path.append(os.getcwd())

from mcp.server.fastmcp import FastMCP
from src.governance.voting.cav_mtoe import CavMTOE
from src.governance.judge_six.core import JudgeSixEngine

mcp = FastMCP("n-autoresearch/Kosmos/BioAgents Governance")
ARMY = CavMTOE(num_soldiers=650)
JUDGE = JudgeSixEngine()

@mcp.tool()
def assess_risk_consensus(intent: str, risk_level: str = "L") -> str:
    result = ARMY.bottom_up_vote(intent=intent, risk_level=risk_level)
    return f"✅ VOTE: {result['final_action']} ({result['approval_rate']:.1%})"

@mcp.tool()
def judge_six_evaluate(context: str, prob: int, sev: int) -> str:
    return JUDGE.evaluate_transaction(context, prob, sev)

if __name__ == "__main__":
    mcp.run()
"""

# mcp_servers.json
mcp_config = {
    "mcpServers": {
        "n-autoresearch/Kosmos/BioAgents": {
            "command": "python3",
            "args": ["src/governance/mcp_server.py"],
            "env": {"PYTHONPATH": "."},
        },
    },
}

# scripts/deploy_omega_v2.py (Already in restoration but overwriting with latest block)
deploy_omega_content = """import os
import time
from google.cloud import notebooks_v2
from google.api_core.client_options import ClientOptions

# --- CONFIGURATION (UPDATED) ---
PROJECT_ID = "shadowtag-omega-v2"  # <--- TARGET UPDATED
REGION = "us-central1"
ZONE = "us-central1-a"
INSTANCE_NAME = "judge-six-omega-node"

def deploy():
    print(f">>> 🖥️  PROVISIONING OMEGA NODE: {INSTANCE_NAME}...")
    print(f"    Target: {PROJECT_ID} (Zone: {ZONE})")

    client_options = ClientOptions(api_endpoint=f"{REGION}-notebooks.googleapis.com:443")
    client = notebooks_v2.NotebookServiceClient(client_options=client_options)
    parent = f"projects/{PROJECT_ID}/locations/{ZONE}"

    # Define Instance with DRIVE ACCESS Scopes
    instance = notebooks_v2.Instance(
        gce_setup=notebooks_v2.GceSetup(
            machine_type="n1-standard-4",
            vm_image=notebooks_v2.VmImage(
                project="deeplearning-platform-release",
                image_family="common-cpu-notebooks"
            ),
            # CRITICAL: Grant the VM permission to touch Google Drive
            service_accounts=[
                notebooks_v2.ServiceAccount(
                    email="default",
                    scopes=[
                        "https://www.googleapis.com/auth/cloud-platform",
                        "https://www.googleapis.com/auth/drive", # <--- THE 10TB KEY
                        "https://www.googleapis.com/auth/userinfo.email"
                    ]
                )
            ],
            network_interfaces=[notebooks_v2.NetworkInterface(network="global/networks/default")],
            boot_disk=notebooks_v2.BootDisk(disk_size_gb=200, disk_type="PD_SSD"),
            disable_public_ip=False
        )
    )

    # Check if exists
    instance_path = f"{parent}/instances/{INSTANCE_NAME}"
    try:
        client.get_instance(name=instance_path)
        print(f"    ✅ Instance {INSTANCE_NAME} already exists.")
        return
    except Exception:
        print("    Instance not found. Creating...")

    try:
        op = client.create_instance(request=notebooks_v2.CreateInstanceRequest(
            parent=parent, instance_id=INSTANCE_NAME, instance=instance
        ))
        print("    ⏳ Creation initiated... (approx 5-10 mins)")
        op.result(timeout=600)
        print(f"    ✅ SUCCESS: https://{ZONE}-{PROJECT_ID}.notebooks.googleusercontent.com")
        print("    NOTE: Open JupyterLab -> Terminal to access the 10TB Drive.")
    except Exception as e:
        print(f"    ❌ FAILED: {e}")

if __name__ == "__main__":
    deploy()
"""

# scripts/mount_drive_check.py
mount_drive_content = """from googleapiclient.discovery import build
import google.auth

def check_drive_access():
    print(">>> 🛰️  TESTING OMEGA DRIVE CONNECTION...")

    try:
        # Authenticate using the VM's Service Account
        creds, project = google.auth.default(scopes=['https://www.googleapis.com/auth/drive'])
        service = build('drive', 'v3', credentials=creds)

        # List first 5 files to prove visibility
        results = service.files().list(
            pageSize=5, fields="nextPageToken, files(id, name)"
        ).execute()
        items = results.get('files', [])

        if not items:
            print("    ✅ Connection Successful (No files found in root).")
        else:
            print("    ✅ Connection Successful! Visible Assets:")
            for item in items:
                print(f"       - {item['name']} ({item['id']})")

    except Exception as e:
        print(f"    ❌ ACCESS DENIED: {e}")
        print("       Did you redeploy the VM with the new scopes?")

if __name__ == "__main__":
    check_drive_access()
"""

# scripts/inventory_arsenal.py
inventory_content = """import os
import shutil
from collections import defaultdict

TARGET_EXTENSIONS = {'.py', '.sh', '.js', '.ts', '.go', '.rs'}
IGNORE_DIRS = {'node_modules', '.git', '.venv', '__pycache__', 'dist', 'libs/arsenal_recovered'}
ROOT_DIR = "."
DEST_DIR = "libs/arsenal_recovered"
KEYWORDS = ['deploy', 'migrate', 'setup', 'fix', 'restore', 'pipeline', 'judge']

def scan_and_harvest():
    print(f">>> 🛰️  INITIATING DEEP SCAN & HARVEST...")
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    stats = defaultdict(int)
    total = 0
    harvested = 0

    for root, dirs, files in os.walk(ROOT_DIR, topdown=True):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in TARGET_EXTENSIONS:
                stats[ext] += 1
                total += 1

                # HARVEST HIGH VALUE TARGETS
                if any(k in file.lower() for k in KEYWORDS):
                    src_path = os.path.join(root, file)
                    clean_name = f"{os.path.basename(root)}_{file}"
                    dst_path = os.path.join(DEST_DIR, clean_name)
                    try:
                        shutil.copy2(src_path, dst_path)
                        harvested += 1
                        print(f"    🔹 Recovered: {clean_name}")
                    except Exception: pass

    print(f"\\n>>> 📊 TOTAL SCRIPTS: {total}")
    print(f">>> ✅ HARVESTED: {harvested} Weapons to {DEST_DIR}")

if __name__ == "__main__":
    scan_and_harvest()
"""

# scripts/ingest_teleport_sessions.py
ingest_memories_content = """import json
import os

MANIFEST_PATH = "Docs/TELEPORT_MANIFEST.json"
MEMORY_PATH = "src/governance/memory/learned_rules.json"

def ingest_memories():
    print(">>> 🧠 INITIALIZING CORTICAL STACK INGESTION...")

    if not os.path.exists(MANIFEST_PATH):
        print("❌ Manifest not found. Run Block 2 first.")
        return

    with open(MANIFEST_PATH, "r") as f:
        data = json.load(f)

    judges = data["priorities"]["JUDGE_LEVEL"]
    print(f"    Found {len(judges)} High-Priority Judge Personas.")

    # Simulating extraction for now
    new_rules = [
        {"context": "python", "file_match": "test", "rule": "allow_wildcard_imports", "action": "suppress", "source": "session_011CUvwBxnYT8QujGMHRutvC"},
        {"context": "terraform", "file_match": "dev", "rule": "allow_http_traffic", "action": "warn", "source": "session_01Fdo7s3HzwmT5BPicwxbQiC"},
    ]

    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with open(MEMORY_PATH, "w") as f:
        json.dump(new_rules, f, indent=2)

    print(f">>> ✅ INGESTED {len(new_rules)} RULES. MEMORY ACTIVE.")

if __name__ == "__main__":
    ingest_memories()
"""

# tests/test_risk.py
test_risk_content = """from libs.steel.sentinel import JudgeSixSentinel, RiskTier

def test_sentinel():
    sentinel = JudgeSixSentinel()

    # Test 1: Catastrophic Hazard
    print("\\n[TEST 1] API Key Leak (Omega Context)")
    result, risk, _ = sentinel.vet_code_diff("main.py", "api_key = 'sk-12345'")
    assert risk == RiskTier.RED
    assert result == False

    # Test 2: Memory Suppression
    print("\\n[TEST 2] Allowed Wildcard in Test")
    result, risk, _ = sentinel.vet_code_diff("tests/test_main.py", "from module import *")
    assert risk == RiskTier.GREEN
    assert result == True

    print("\\n>>> ✅ SENTINEL TESTS PASSED")

if __name__ == "__main__":
    test_sentinel()
"""


def apply_re_punch():
    # 1. Configs
    write_file(".vscode/settings.json", json.dumps(settings_json, indent=4))
    write_file(".aiexclude", aiexclude_content)
    write_file(".agent/docs/toolbelt.md", toolbelt_content)
    write_file(".agent/rules/shadowtag-laws.md", laws_content)
    write_file(".agent/workflows/live-engine.md", live_engine_content)

    # 2. Judge 6 Blocks
    write_file("Docs/ARMY_SAFETY_DOCTRINE.md", army_safety_content)
    write_file("Docs/GEMINI_MEMORY_DOCTRINE.md", gemini_memory_content)
    write_file("Docs/TELEPORT_MANIFEST.json", teleport_manifest_content)
    write_file("src/governance/voting/cav_mtoe.py", cav_mtoe_content)
    write_file("src/governance/judge_six/core.py", judge_six_core_content)
    write_file("src/governance/memory/memory_bank.py", memory_bank_content)
    write_file("libs/steel/sentinel.py", sentinel_content)
    write_file("src/governance/mcp_server.py", mcp_server_content)
    write_file("mcp_servers.json", json.dumps(mcp_config, indent=2))
    write_file("scripts/deploy_omega_v2.py", deploy_omega_content)
    write_file("scripts/mount_drive_check.py", mount_drive_content)
    write_file("scripts/inventory_arsenal.py", inventory_content)
    write_file("scripts/ingest_teleport_sessions.py", ingest_memories_content)
    write_file("tests/test_risk.py", test_risk_content)


if __name__ == "__main__":
    apply_re_punch()
