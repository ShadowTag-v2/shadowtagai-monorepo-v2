# Monorepo Weekly Scorecard

## Week of
`YYYY-MM-DD`

## Overall score
- Current week score: `__/100`
- Last week score: `__/100`
- Delta: `+/-__`

---

## Category scores

| Category | Weight | Score | Weighted score | Notes |
|---|---:|---:|---:|---|
| Canonical repo resolution | 20 |  |  |  |
| Live tree cleanliness | 20 |  |  |  |
| GitHub governance | 15 |  |  |  |
| Bazel / CI reliability | 15 |  |  |  |
| `third_party` discipline | 10 |  |  |  |
| Shared contracts | 10 |  |  |  |
| Workspace / tooling stability | 10 |  |  |  |

---

## 1) Canonical repo resolution

### Audit questions
- Are all shared repos marked canonical or archived?
- Does `monorepo_manifest.yaml` contain any `status: unresolved` entries?
- Does each canonical repo have exactly one live root?

### Evidence
- Manifest path:
- Commit / PR:
- Example current entries:

```yaml
# paste exact manifest examples here
```

### Scoring guide

* `20/20`: zero unresolved repos
* `10/20`: one or two unresolved repos remain
* `0/20`: multiple unresolved repos and unclear canonical roots

### Current examples

* Good example:
* Bad example:
* Fix next week:

---

## 2) Live tree cleanliness

### Audit questions

* Are backup, recovered, raw-ingest, and legacy trees still inside live app roots?
* Were any moved to `archive/` this week?
* Are there still nested repo copies in live paths?

### Evidence

* Example path removed:
* Example path still blocking:
* Archive move commit / PR:

### Specific examples

* `_PRE_OMEGA_BACKUP_*` status:
* `ShadowTag-Omega` status:
* `arsenal_recovered` status:
* `raw_ingest` status:

### Scoring guide

* `20/20`: no non-canonical trees in live paths
* `10/20`: some remain but clear progress made
* `0/20`: no meaningful cleanup

---

## 3) GitHub governance

### Audit questions

* Is `main` protected?
* Are PRs required?
* Are code owner reviews required?
* Are `bazel-build` and `bazel-test` required and passing?

### Evidence

* Ruleset summary:
* Last PR merged with checks:
* CODEOWNERS path:
* Required checks visible:

### Specific examples

* Last green `bazel-build`:
* Last green `bazel-test`:
* Example PR with owner review:
* Example violation or gap:

### Scoring guide

* `15/15`: fully enforced on `main`
* `8/15`: workflow exists but enforcement partial
* `0/15`: direct-to-main and no required checks

---

## 4) Bazel / CI reliability

### Audit questions

* Does `bazel build //...` pass?
* Does `bazel test //...` pass?
* Are archive/legacy trees excluded from active CI scope?

### Evidence

* Latest CI run link:
* Build result:
* Test result:
* Failure source if red:

### Specific examples

* Good:
* Bad:
* Fix next week:

### Scoring guide

* `15/15`: stable green CI on live code
* `8/15`: intermittent failures, but real progress
* `0/15`: CI untrusted or constantly failing from structural noise

---

## 5) `third_party` discipline

### Audit questions

* Is there a centralized `third_party/` policy?
* Are vendored dependencies centralized or still scattered?
* Are app-local vendor mirrors still acting as source of truth?

### Evidence

* Policy file / path:
* Example dependency moved:
* Example app-local vendor path still unresolved:

### Scoring guide

* `10/10`: centralized and enforced
* `5/10`: partial centralization
* `0/10`: scattered vendor worlds remain

---

## 6) Shared contracts

### Audit questions

* Is there one chosen shared contract root?
* Are services using shared schemas/contracts?
* Are duplicated local API definitions being removed?

### Evidence

* Contract root:
* Example shared contract:
* Example migrated service:
* Example remaining duplicate definition:

### Scoring guide

* `10/10`: contract root exists and is in use
* `5/10`: contract root exists but adoption partial
* `0/10`: no centralized contract layer

---

## 7) Workspace / tooling stability

### Audit questions

* Is workspace root stable?
* Is Python interpreter binding stable?
* Is basedpyright narrowed to canonical live roots?
* Are symlink-jungle warnings gone?
* Is local RAG indexing canonical-only?

### Evidence

* Active interpreter:
* Basedpyright source file count:
* Pyright warnings:
* RAG/index note:
* Workspace root verification output:

### Specific examples

* Good:
* Bad:
* Fix next week:

### Scoring guide

* `10/10`: stable and boring
* `5/10`: mostly stable, some drift/noise remains
* `0/10`: recurring workspace/env/index failures

---

## Weekly highlights

* Best improvement this week:
* Most important blocker removed:
* Biggest regression:
* Highest-risk unresolved item:

---

## Next-week commitments

1.
2.
3.

---

## Executive summary

Write 3–5 sentences:

* where the monorepo stands now
* what changed this week
* what still blocks 10/10
* what must happen next week to stay on plan