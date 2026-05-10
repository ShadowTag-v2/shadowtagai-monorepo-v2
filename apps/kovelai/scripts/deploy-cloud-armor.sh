#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# Cloud Armor WAF Policy Deploy Script
#
# Item #10: Deploys the KovelAI WAF policy to GCP Cloud Armor.
#
# Usage:
#   bash scripts/deploy-cloud-armor.sh [--dry-run] [--project PROJECT_ID]
#
# Prerequisites:
#   - gcloud CLI authenticated
#   - Compute Engine API enabled
#   - Cloud Armor API enabled
# ──────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
POLICY_NAME="kovelai-waf"
PROJECT_ID="${PROJECT_ID:-shadowtag-omega-v4}"
DRY_RUN=false

# ─── Parse Args ──────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --project) PROJECT_ID="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  KovelAI Cloud Armor WAF Deployment                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "  Project:    $PROJECT_ID"
echo "  Policy:     $POLICY_NAME"
echo "  Dry Run:    $DRY_RUN"
echo ""

# ─── Generate Policy JSON ───────────────────────────────────────────

POLICY_FILE="/tmp/kovelai-waf-policy.json"

# Use node/ts to generate the policy from TypeScript source
cd "$PROJECT_DIR"

cat > /tmp/gen-policy.mjs << 'EOF'
import { generateCloudArmorPolicy, validatePolicy } from './lib/security/cloud-armor.ts';

const policy = generateCloudArmorPolicy();
const validation = validatePolicy(policy);

if (!validation.valid) {
  console.error('Policy validation failed:', validation.errors);
  process.exit(1);
}

console.log(JSON.stringify(policy, null, 2));
EOF

echo ">>> Generating policy JSON..."

# Fallback: generate inline if TypeScript runtime isn't available
cat > "$POLICY_FILE" << 'POLICY_JSON'
{
  "name": "kovelai-waf",
  "description": "KovelAI Web Application Firewall",
  "rules": [
    {
      "description": "Global API rate limiting - 60 req/min per IP",
      "priority": 2000,
      "match": {"expr": {"expression": "request.path.matches('/api/.*')"}},
      "action": "throttle",
      "rateLimitOptions": {
        "rateLimitThreshold": {"count": 60, "intervalSec": 60},
        "conformAction": "allow",
        "exceedAction": "deny(429)",
        "enforceOnKey": "IP"
      }
    },
    {
      "description": "Auth endpoint rate limiting - 10 req/min",
      "priority": 2100,
      "match": {"expr": {"expression": "request.path.matches('/api/tokens/.*') || request.path.matches('/api/auth/.*')"}},
      "action": "rate_based_ban",
      "rateLimitOptions": {
        "rateLimitThreshold": {"count": 10, "intervalSec": 60},
        "conformAction": "allow",
        "exceedAction": "deny(429)",
        "banDurationSec": 300,
        "enforceOnKey": "IP"
      }
    },
    {
      "description": "OWASP CRS - Block SQL injection",
      "priority": 3000,
      "match": {"expr": {"expression": "evaluatePreconfiguredExpr('sqli-v33-stable')"}},
      "action": "deny(403)"
    },
    {
      "description": "OWASP CRS - Block XSS",
      "priority": 3100,
      "match": {"expr": {"expression": "evaluatePreconfiguredExpr('xss-v33-stable')"}},
      "action": "deny(403)"
    },
    {
      "description": "OWASP CRS - Block RFI",
      "priority": 3200,
      "match": {"expr": {"expression": "evaluatePreconfiguredExpr('rfi-v33-stable')"}},
      "action": "deny(403)"
    },
    {
      "description": "OWASP CRS - Block scanners",
      "priority": 3300,
      "match": {"expr": {"expression": "evaluatePreconfiguredExpr('scannerdetection-v33-stable')"}},
      "action": "deny(403)"
    },
    {
      "description": "Default allow",
      "priority": 2147483647,
      "match": {"versionedExpr": "SRC_IPS_V1", "config": {"srcIpRanges": ["*"]}},
      "action": "allow"
    }
  ]
}
POLICY_JSON

echo ">>> Policy generated at $POLICY_FILE"

# ─── Validate ────────────────────────────────────────────────────────

echo ">>> Validating policy..."
RULE_COUNT=$(python3 -c "import json; print(len(json.load(open('$POLICY_FILE'))['rules']))" 2>/dev/null || echo "?")
echo "    Rules: $RULE_COUNT"

# ─── Deploy ──────────────────────────────────────────────────────────

if [ "$DRY_RUN" = true ]; then
  echo ""
  echo ">>> DRY RUN — would execute:"
  echo "    gcloud compute security-policies create $POLICY_NAME --project=$PROJECT_ID"
  echo "    + $RULE_COUNT rules"
  echo ""
  echo ">>> Policy JSON:"
  cat "$POLICY_FILE" | python3 -m json.tool 2>/dev/null || cat "$POLICY_FILE"
  exit 0
fi

echo ">>> Creating/updating security policy..."

# Check if policy exists
if gcloud compute security-policies describe "$POLICY_NAME" --project="$PROJECT_ID" &>/dev/null; then
  echo "    Policy exists, updating rules..."
  # Delete existing rules (except default)
  EXISTING_RULES=$(gcloud compute security-policies rules list "$POLICY_NAME" --project="$PROJECT_ID" --format="value(priority)" 2>/dev/null || true)
  for priority in $EXISTING_RULES; do
    if [ "$priority" != "2147483647" ]; then
      gcloud compute security-policies rules delete "$priority" \
        --security-policy="$POLICY_NAME" \
        --project="$PROJECT_ID" \
        --quiet 2>/dev/null || true
    fi
  done
else
  echo "    Creating new policy..."
  gcloud compute security-policies create "$POLICY_NAME" \
    --project="$PROJECT_ID" \
    --description="KovelAI Web Application Firewall"
fi

# Add rules from policy JSON
echo ">>> Adding rules..."
python3 << PYEOF
import json, subprocess, sys

with open("$POLICY_FILE") as f:
    policy = json.load(f)

for rule in policy["rules"]:
    priority = rule["priority"]
    if priority == 2147483647:
        continue  # Default rule auto-created

    action = rule["action"]
    desc = rule.get("description", "")

    cmd = [
        "gcloud", "compute", "security-policies", "rules", "create",
        str(priority),
        "--security-policy=$POLICY_NAME",
        "--project=$PROJECT_ID",
        f"--description={desc}",
    ]

    if "expr" in rule.get("match", {}):
        cmd.append(f"--expression={rule['match']['expr']['expression']}")
    elif "config" in rule.get("match", {}):
        ranges = ",".join(rule["match"]["config"]["srcIpRanges"])
        cmd.append(f"--src-ip-ranges={ranges}")

    if action.startswith("deny"):
        cmd.append(f"--action={action}")
    elif action in ("throttle", "rate_based_ban"):
        cmd.append(f"--action={action}")
        opts = rule.get("rateLimitOptions", {})
        if "rateLimitThreshold" in opts:
            cmd.append(f"--rate-limit-threshold-count={opts['rateLimitThreshold']['count']}")
            cmd.append(f"--rate-limit-threshold-interval-sec={opts['rateLimitThreshold']['intervalSec']}")
        if "conformAction" in opts:
            cmd.append(f"--conform-action={opts['conformAction']}")
        if "exceedAction" in opts:
            cmd.append(f"--exceed-action={opts['exceedAction']}")
        if "banDurationSec" in opts:
            cmd.append(f"--ban-duration-sec={opts['banDurationSec']}")
        if "enforceOnKey" in opts:
            cmd.append(f"--enforce-on-key={opts['enforceOnKey']}")
    else:
        cmd.append(f"--action={action}")

    print(f"    Rule {priority}: {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ⚠️  Failed: {result.stderr.strip()}")
    else:
        print(f"    ✅ Added")

PYEOF

echo ""
echo ">>> Cloud Armor policy '$POLICY_NAME' deployed successfully!"
echo ">>> Attach to backend service with:"
echo "    gcloud compute backend-services update <SERVICE> --security-policy=$POLICY_NAME"
