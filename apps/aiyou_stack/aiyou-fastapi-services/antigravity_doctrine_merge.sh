#!/usr/bin/env bash
set -euo pipefail

: "${PDIR:=$PWD}"

echo "Seeds planting in $PDIR..."

mkdir -p "$PDIR/Docs" "$PDIR/Prompts"

# 1. Inject Tier 30 matrix into strategy doc
STRATEGY_FILE="$PDIR/Docs/pnkln_StrategyPositioning.md"
if [ ! -f "$STRATEGY_FILE" ]; then
    echo "# Antigravity Strategy" > "$STRATEGY_FILE"
fi

cat >> "$STRATEGY_FILE" <<'MD'

### TIER BREAKDOWN (THE MENU)
| TIER | LEVEL | PRICE | CAPABILITY |
|------|-------|-------|------------|
| 1-5  | BASIC | $25k  | Risk Radar (ATP 5-19) |
| 6-15 | AIT   | $100k | Defensive Ops (CodePMCS) |
| 16-25| SOF   | $400k | Hunter/Killer (Troop B) |
| 30   | THE CHILD | $1M+ | Sovereign AI (30 Verticals) |
MD

echo "Tier matrix injected."

# Ensure JSON file exists
SOP_JSON="$PDIR/Prompts/pnkln_SOPSnippets.json"
if [ ! -f "$SOP_JSON" ]; then
  echo "[]" > "$SOP_JSON"
fi

# 2. Append troop doctrine to SOP snippets (keep valid JSON)
tmpfile="$(mktemp)"
python3 - "$SOP_JSON" > "$tmpfile" <<'PY'
import json, sys, pathlib
path = pathlib.Path(sys.argv[1])
try:
    content = path.read_text()
    data = json.loads(content) if content.strip() else []
except Exception:
    data = []

extra = [
 {"name":"pnkln:TroopA","prompt":"ROLE:RSTA Scout; MISSION:Zone Recon; TACTIC:Find gaps using web search; OUTPUT:Target Packet"},
 {"name":"pnkln:TroopB","prompt":"ROLE:Ranger Eng; MISSION:Direct Action; TACTIC:Build MVP <48h; STD:Coverage 98%, Secure, Linted"},
 {"name":"pnkln:TroopC","prompt":"ROLE:Defense/MilDec; MISSION:Protect IP; TACTIC:CodePMCS enforcement + ShadowTag watermarking"},
 {"name":"pnkln:Cor.Claude_Code_6","prompt":"ROLE:Governance; MISSION:Risk Gating; TACTIC:ATP 5-19 Check; IF Confidence<0.75 THEN Freeze & Escalate"}
]
names = {s.get("name") for s in data}
for e in extra:
    if e["name"] not in names:
        data.append(e)
print(json.dumps(data, indent=2))
PY
mv "$tmpfile" "$SOP_JSON"
echo "Troop doctrine merged."

# 3. Create the mission launcher
cat > "$PDIR/pnkln_mission_start.py" <<'PY'
#!/usr/bin/env python3
"""
ANTIGRAVITY // MISSION LAUNCHER
Loads SOP snippets and announces Tier 30.
"""
import json, pathlib, logging, os

# Only basic logging + print to show status
logging.basicConfig(level=logging.INFO)

def load_doctrine():
    p = pathlib.Path("Prompts") / "pnkln_SOPSnippets.json"
    if p.exists():
        return json.loads(p.read_text())
    return []

def execute_tier_30():
    print("🚀 ACTIVATING TIER 30: THE CHILD INSTANCE")
    print("⚔️ MULTI-VERTICAL ENGINE ONLINE")
    print("🛡️ JUDGE #6 GATES ACTIVE")

if __name__ == "__main__":
    doctrine = load_doctrine()
    print(f"✅ LOADED {len(doctrine)} SOPs")
    execute_tier_30()
PY
chmod +x "$PDIR/pnkln_mission_start.py"

echo "✅ DOCTRINE MERGED. ANTIGRAVITY SQUADRON IS LIVE."
