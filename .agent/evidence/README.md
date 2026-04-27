# Evidence Ledger — Flight Recorder

Evidence reports capture the outcome of gated operations. Every push attempt,
deployment, secret scan, and lint sweep produces evidence.

## Structure

```text
.agent/evidence/
  ├── push/              # Push gate evidence
  │   └── *.yaml         # Per-push attempt records
  ├── deploy/            # Deployment evidence
  │   └── *.yaml         # Per-deployment records
  ├── scans/             # Security scan evidence
  │   └── *.yaml         # Per-scan records
  └── README.md          # This file
```

## Evidence Schema

```yaml
# Minimal evidence record
evidence_id: "evt-<uuid7>"
timestamp: "2026-04-27T00:00:00Z"
agent: "antigravity"
operation: "github.push|firebase.deploy|secret_scan|lint_sweep"
contract_id: "tool_contracts/<contract>.yaml"
result: "pass|fail|blocked"
preconditions:
  - name: "auth_verified"
    status: "pass"
  - name: "betterleaks_clean"
    status: "pass"
details:
  commit_sha: "abc123"
  branch: "main"
  files_changed: 12
artifacts:
  - path: ".reports/secrets/betterleaks-staged.json"
    type: "scan_report"
```

## Rules

1. Evidence is **immutable**. Once written, never modified.
2. Evidence is **referenced** from `.beads/issues.jsonl` entries.
3. Evidence files are git-tracked (they are small YAML records).
4. Raw scan reports go to `.reports/` (some git-tracked, some not).
5. Evidence proves that a gate was checked, not that it will always pass.
