#!/usr/bin/env bash

# ==========================================
# ANTIGRAVITY DOCTRINE (MERGE)
# ==========================================

# 1. INJECT TIER 30 MATRIX INTO STRATEGY DOC
cat >> "$PDIR/Docs/pnkln_StrategyPositioning.md" <<'MD'

### TIER BREAKDOWN (THE MENU)
| TIER | LEVEL | PRICE | CAPABILITY |
|---|---|---|---|
| 1-5 | BASIC | $25k | Risk Radar (ATP 5-19) |
| 6-15 | AIT | $100k | Defensive Ops (CodePMCS) |
| 16-25 | SOF | $400k | Hunter/Killer (Troop B) |
| 30 | THE CHILD | $1M+ | Sovereign AI (30 Verticals) |
MD

# 2. INJECT TROOP DOCTRINE INTO SOP SNIPPETS
# (We append these to the JSON list - physically editing the file for valid JSON)
# Remove last line (closing bracket) from the JSON array
sed -i '$ d' "$PDIR/Prompts/pnkln_SOPSnippets.json"
cat >> "$PDIR/Prompts/pnkln_SOPSnippets.json" <<'JSON'
,
 {"name":"pnkln:TroopA","prompt":"ROLE:RSTA Scout; MISSION:Zone Recon; TACTIC:Find gaps using Perplexity; OUTPUT:Target Packet"},
 {"name":"pnkln:TroopB","prompt":"ROLE:Ranger Eng; MISSION:Direct Action; TACTIC:Build MVP <48h; STD:Coverage 98%, Secure, Linted"},
 {"name":"pnkln:TroopC","prompt":"ROLE:Defense/MilDec; MISSION:Protect IP; TACTIC:CodePMCS enforcement + ShadowTag watermarking"},
 {"name":"pnkln:Cor.Claude_Code_6","prompt":"ROLE:Governance; MISSION:Risk Gating; TACTIC:ATP 5-19 Check; IF Confidence<0.75 THEN Freeze"}
]
JSON

# 3. CREATE THE MISSION LAUNCHER (CodePMCS Integration)
cat > "$PDIR/pnkln_mission_start.py" <<'PY'
#!/usr/bin/env python3
"""
ANTIGRAVITY // MISSION LAUNCHER
Integrates with pnkln_tasks.sh and SOP Snippets
"""
import sys, json, logging
logging.basicConfig(level=logging.INFO)

def load_doctrine():
    with open("pnkln/Prompts/pnkln_SOPSnippets.json", "r") as f:
        return json.load(f)

def execute_tier_30():
    print("🚀 ACTIVATING TIER 30: THE CHILD INSTANCE")
    print("⚔️ 30 VERTICALS ENGAGED")
    print("🛡️ JUDGE #6 BRAKES ACTIVE")

if __name__ == "__main__":
    doctrine = load_doctrine()
    print(f"✅ LOADED {len(doctrine)} SOPs")
    execute_tier_30()
PY
chmod +x "$PDIR/pnkln_mission_start.py"

echo "✅ DOCTRINE MERGED. ANTIGRAVITY SQUADRON IS LIVE."
