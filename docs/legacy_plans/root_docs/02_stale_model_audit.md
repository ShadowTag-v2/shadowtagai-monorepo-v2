# 02_stale_model_audit.md

## Target state

The thread’s corrected direction is:

- use `gemini-3.1-family`
- do not leave `gemini-2.5-*`, `gemini-3.1-family-*`, or `gemini-3-pro-interactions-exp` in live code/docs unless explicitly archived or intentionally experimental

## Confirmed stale model findings

### A. `GEMINI.md`

Observed stale values:

- `gemini-2.5-pro`
- `gemini-3-pro-interactions-exp`

This file also points to the older `ShadowTag-Omega` root and older repo identity.

### B. `apps/nascent-apollo/src/antigravity/autoresearch.py`

Observed stale values:

- comment: “pure Gemini 1.5 Pro”
- `MODEL_NAME = "gemini-3.1-family"`
- constructor default `model: str = "gemini-3.1-family"`

This is live code drift, not just doc drift.

### C. `antigravity_block_3.sh`

Observed stale values:

- `gemini-3-pro-interactions-exp`
- `gemini-2.5-pro`

This means bootstrapping scripts are also capable of reintroducing stale models into generated code.

## Severity

### High

- any live Python code defaulting to old model names
- any code-generation shell scripts that rewrite old model names into repo files

### Medium

- docs that still instruct operators to use stale model names

### Low

- archived or backup trees, but only if they are fully quarantined from active workflows

## Patch rule

For each hit, classify as:

- **live** → patch now
- **adapter/reference** → annotate
- **archive/backup** → quarantine harder, exclude from workspace/search, do not revive

## Minimal patch objective

Normalize live code and control-plane docs to one declared family:

- `gemini-3.1-family`

Then explicitly tag legacy mentions as:

- archived
- historical
- not authoritative
