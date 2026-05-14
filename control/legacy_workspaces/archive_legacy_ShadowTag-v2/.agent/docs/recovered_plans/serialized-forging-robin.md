# Plan: Share Claude Memory with Antigravity (3 Methods)

## Task
Export current Claude Code session memory to Antigravity/Ultrathink via:
1. GCS Bucket (for GKE pods)
2. CLAUDE.md (for new sessions)
3. Firestore (real-time sync)

---

## Existing Infrastructure (Already Built)

| Component | Location | Status |
|-----------|----------|--------|
| Memory Schema | `erik-hancock-llm-memory/memory/current.json` | ✅ 214 docs |
| Firestore Backend | `kosmos/persistence/firestore_backend.py` | ✅ Ready |
| GCS Pattern | `{project}-workbench-memory/memory/` | ✅ Bucket exists |
| CLAUDE.md | Root `/CLAUDE.md` | ✅ Exists |
| Ultrathink Prompt | `prompts/antigravity_ultrathink.py` | ✅ 650 agents |

---

## Implementation Plan: Memory Merge (All 3 Targets)

### Approach
Merge this Claude Code session into `memory/current.json` schema, then sync to all 3 targets.

### Data to Merge (per existing schema)

**Into `conversations` array:**
```json
{
  "id": "claude-code-2025-11-28",
  "source": "claude_code",
  "date": "2025-11-28",
  "summary": "GKE quota fix, Terraform deploy, memory sharing setup",
  "key_decisions": [
    "Deleted autopilot-cluster-1 to free quota",
    "Created shadowtagai-production cluster",
    "Migrated Anthropic → Gemini in terraform"
  ],
  "artifacts": [
    "terraform/main.tf",
    "terraform/secrets.tf",
    "scripts/deploy-all.sh"
  ]
}
```

**Into `knowledge` array:**
```json
{
  "topic": "gke_quota_management",
  "learned": "autopilot clusters consume 40 CPUs (5 nodes × 8)",
  "source": "claude-code-2025-11-28"
},
{
  "topic": "terraform_state_buckets",
  "learned": "Backend bucket: acquired-jet-478701-b3-terraform-state",
  "source": "claude-code-2025-11-28"
}
```

### File: `scripts/sync_claude_memory.py`

```python
#!/usr/bin/env python3
"""Sync Claude Code session to memory bank (GCS + Firestore + CLAUDE.md)"""

import json
from datetime import datetime
from pathlib import Path
from google.cloud import storage, firestore

PROJECT_ID = "acquired-jet-478701-b3"
MEMORY_PATH = Path("erik-hancock-llm-memory/memory/current.json")
GCS_BUCKET = f"{PROJECT_ID}-workbench-memory"

def load_memory():
    return json.loads(MEMORY_PATH.read_text())

def save_memory(memory):
    MEMORY_PATH.write_text(json.dumps(memory, indent=2))

def merge_session(memory, session_data):
    """Merge session into conversations/knowledge arrays"""
    memory["conversations"].append(session_data["conversation"])
    memory["knowledge"].extend(session_data["knowledge"])
    memory["last_updated"] = datetime.now().isoformat()
    return memory

def sync_gcs(memory):
    """Upload to GCS bucket"""
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob("memory/current.json")
    blob.upload_from_string(json.dumps(memory, indent=2))
    print(f"✓ Synced to gs://{GCS_BUCKET}/memory/current.json")

def sync_firestore(memory):
    """Real-time sync to Firestore"""
    db = firestore.Client(project=PROJECT_ID)
    doc_ref = db.collection("claude_memory").document("current")
    doc_ref.set(memory)
    print("✓ Synced to Firestore claude_memory/current")

def update_claude_md(session_summary):
    """Append session context to CLAUDE.md"""
    claude_md = Path("CLAUDE.md")
    content = claude_md.read_text()

    section = f"""
## Last Session: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{session_summary}
"""
    # Replace existing or append
    if "## Last Session:" in content:
        import re
        content = re.sub(r"## Last Session:.*?(?=\n## |\Z)", section, content, flags=re.DOTALL)
    else:
        content += section

    claude_md.write_text(content)
    print("✓ Updated CLAUDE.md")

def main():
    session_data = {
        "conversation": {
            "id": f"claude-code-{datetime.now().strftime('%Y-%m-%d')}",
            "source": "claude_code",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "summary": "GKE quota fix, Terraform deploy shadowtagai-production",
            "key_decisions": [
                "Deleted autopilot-cluster-1 (freed 40 CPUs + 500GB SSD)",
                "Created shadowtagai-production GKE cluster",
                "Migrated Anthropic → Gemini in terraform configs"
            ],
            "artifacts": ["terraform/main.tf", "terraform/secrets.tf"]
        },
        "knowledge": [
            {"topic": "gke_quota", "learned": "Autopilot = 5 nodes × 8 CPUs = 40 CPUs"},
            {"topic": "terraform_bucket", "learned": "gs://acquired-jet-478701-b3-terraform-state"}
        ]
    }

    memory = load_memory()
    memory = merge_session(memory, session_data)
    save_memory(memory)
    sync_gcs(memory)
    sync_firestore(memory)
    update_claude_md(session_data["conversation"]["summary"])
    print("\n✅ Memory synced to all 3 targets")

if __name__ == "__main__":
    main()
```

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `scripts/sync_claude_memory.py` | CREATE | Unified sync script |
| `erik-hancock-llm-memory/memory/current.json` | MODIFY | Merge into conversations/knowledge |
| `/CLAUDE.md` | MODIFY | Append "Last Session" section |

---

## Execution
```bash
cd aiyou-fastapi-services
python3 scripts/sync_claude_memory.py
```

## Prerequisites
- `google-cloud-storage` and `google-cloud-firestore` installed
- ADC credentials configured (already done this session)
- GCS bucket `acquired-jet-478701-b3-workbench-memory` exists (create if not)

---

# Progress Report: All Verticals - November 28, 2025

## Status Summary

| Vertical | Status | Notes |
|----------|--------|-------|
| FlyingMonkeys Squadron | ✅ OPERATIONAL | 650 agents, 100% ready, :8600 |
| CodePMCS | ✅ MERGED | PR #295, +1,723 lines |
| ShadowTag Contracts | ✅ COMMITTED | 3ffd692d - tests passing |
| Ultrathink Prompt | ✅ COMPLETE | prompts/antigravity_ultrathink.py |
| 16-Repo Ecosystem | ✅ ALL MERGED | 16 PRs across repos |
| GKE Infrastructure | ⏳ DEPLOYING | Terraform in background |
| Drive Knowledge | ✅ EXTRACTED | 214 docs in drive_knowledge/ |

## Background Processes Still Running
- `ca8117` - FlyingMonkeys server :8600
- `a8b078` - FlyingMonkeys server :8600
- `b1334d` - FlyingMonkeys server :8600
- `576f55` - Terraform apply (shadowtagai-production)

## Completed This Session
1. ✅ GCloud ADC authentication
2. ✅ Created terraform state bucket
3. ✅ Fixed Anthropic → Gemini migration in terraform
4. ✅ Deleted autopilot-cluster-1 (freed 40 CPUs + 500GB SSD)
5. ✅ Started shadowtagai-production cluster creation

## Recent Commits
- `3ffd692d` fix: ShadowTag DNA Royalty contracts + tests passing
- `a96d50d5` feat: Unify squadron to 650 agents + add Ultrathink prompt
- `3ee2e0e0` feat: Add CodePMCS - AI-Powered Code Quality Platform (#295)

---

# Plan: Fix ShadowTagAI_DNARoyalty Solidity Contract

## Issues Identified

### 1. Compiler Warnings
```
Warning: Unused function parameter → contracts/ShadowTagAI_DNARoyalty.sol:139
         bytes calldata validationProof

Warning: Unused local variable → contracts/ShadowTagAI_DNARoyalty.sol:154
         uint256 totalPaid
```

### 2. Test Failure (Root Cause)
```
AssertionError: expected '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266' (overlord)
                to equal '0x3d7d0aa0DF762a686E491F2b863E1Aa5F4fE0e1D' (childTBA)
```

**Root Cause**: `RoyaltyMath.distributeRecursive()` breaks the loop BEFORE distributing royalties when parent == overlord. Also, `RoyaltyPaid` event is never emitted in `distributeViaUserOp`.

## Fixes

### Fix 1: `contracts/ShadowTagAI_DNARoyalty.sol` line 137-139
Prefix unused parameter with underscore:
```solidity
function distributeViaUserOp(
    UserOperation calldata userOp,
    uint256 usdCents,
    bytes calldata /* validationProof */  // Or _validationProof
) external whenNotPaused {
```

### Fix 2: `contracts/ShadowTagAI_DNARoyalty.sol` line 152-159
Remove unused variable assignment and add RoyaltyPaid events:
```solidity
// 3. Multi-level royalty logic using Library
(uint256 totalPaid, address[] memory recipients, uint256[] memory amounts, uint8[] memory generations) =
    RoyaltyMath.distributeRecursive(
        fromTBA,
        usdCents,
        parentOf,
        baseRoyaltyBps,
        claimedCents,
        OVERLORD
    );

// Emit events for each payout
for (uint256 i = 0; i < recipients.length; i++) {
    emit RoyaltyPaid(recipients[i], amounts[i], generations[i]);
}
```

### Fix 3: `contracts/libraries/RoyaltyMath.sol` - Restructure logic
The loop breaks BEFORE distributing when parent == overlord. Fix:
```solidity
function distributeRecursive(...) internal returns (
    uint256 totalPaid,
    address[] memory recipients,
    uint256[] memory amounts,
    uint8[] memory generations
) {
    address current = from;
    uint256 remaining = usdCents;
    totalPaid = 0;

    // Pre-allocate arrays (max 10 levels)
    recipients = new address[](10);
    amounts = new uint256[](10);
    generations = new uint8[](10);
    uint256 count = 0;

    for (uint256 i = 0; i < 10; i++) {
        address parent = parentOf[current];
        if (parent == address(0)) break;

        uint16 bps = baseRoyaltyBps[current];
        if (bps > 0) {
            uint256 cut = (remaining * bps) / 10000;
            claimedCents[parent] += cut;
            recipients[count] = parent;
            amounts[count] = cut;
            generations[count] = uint8(i);
            count++;
            totalPaid += cut;
            remaining -= cut;
        }

        if (parent == overlord) break; // Check AFTER distributing
        current = parent;
    }

    // Resize arrays to actual count
    assembly {
        mstore(recipients, count)
        mstore(amounts, count)
        mstore(generations, count)
    }
}
```

### Fix 4: Test expectation alignment
The test expects childTBA to "retain" 18%, but the library credits PARENT. Either:
- **Option A**: Change library so child retains bps% and parent gets (100-bps)%
- **Option B**: Update test to match current library behavior (parent gets bps%)

## Files to Modify
| File | Change |
|------|--------|
| `contracts/ShadowTagAI_DNARoyalty.sol` | Fix unused param, add event emissions |
| `contracts/libraries/RoyaltyMath.sol` | Fix break order, return event data |
| `test/FullIntegration.test.js` | Verify expectations match implementation |

