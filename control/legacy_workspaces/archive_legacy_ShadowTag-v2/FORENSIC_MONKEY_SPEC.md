# Cor.58.7: The Forensic Evidence Specification

> **Role**: Scientist Monkey (Hypothesis-in / Evidence-out)
> **Constraint**: No Text Blobs. Only Proof.

## 1. The Drop-In Replacement Spec

**Service**: `kosmos-monkeys-v2`
**Logic**: Does not return "chat". Returns a `99_verdict.json` pointing to a Chain of Custody in GCS.

### Artifact Folder Layout (`gs://artifacts/{request_id}/{iter}/`)

- `00_plan.json`: The Hypothesis.
- `01_evidence/`: RAW PROOF.
  - `screenshot.png`: Visual Grounding.
  - `network.har`: Exfiltration Check.
  - `terminal.log`: Null Hypothesis Check.
- `99_verdict.json`: The Conclusion.

## 2. The Forensic Judge

The Judge no longer reads rhetoric. It verifies file system reality.

- **Ghost Check**: Do the files exist?
- **Blind Check**: Does the screenshot contain "404"?
- **Null Hypothesis**: Did code exit with 0 if vote is GO?
- **Exfiltration**: Did HAR contain unauthorized IPs?

## 3. Operations

- **Mode**: Tight Loop (Judge Every Iteration).
- **Cost**: $0.13 per verified success (vs $1.00 loose).
- **Value**: Selling "Audit-Grade Certainty".
