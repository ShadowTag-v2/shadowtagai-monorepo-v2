# Antigravity Manifest-Aware Fold-In Guide

This bundle is for one thing: stop blind repo copying.

Use it before any fold-in, subtree import, or monorepo migration.

## What is inside

- `fold_in_repo_checklist.py`
  - scans an incoming repo for stale model strings, stale MCP/control-plane references, stale naming, nested `.git` directories, and obvious secret-like material
  - checks the requested destination against the monorepo's canonical repo roots
  - flags split-brain manifest conditions if more than one manifest surface exists and they disagree

- `manifest_reconcile_report.py`
  - compares two manifest files key-by-key
  - classifies drift by section
  - emits a markdown or JSON report you can hand to Antigravity before a large migration

## Recommended order

1. Reconcile manifest truth first.
2. Only then run fold-in checks for each incoming repo.
3. Block any move into a destination already declared canonical unless you are performing a true merge.

## Example: manifest reconcile

```bash
python3 manifest_reconcile_report.py \
  /path/to/Monorepo-Uphillsnowball/monorepo_manifest.yaml \
  /path/to/Monorepo-Uphillsnowball/manifests/monorepo_manifest.yaml \
  --markdown-out manifest_reconcile_report.md \
  --json-out manifest_reconcile_report.json
```

## Example: fold-in preflight

```bash
python3 fold_in_repo_checklist.py \
  RepoName \
  /path/to/incoming/repo \
  apps/target-path \
  --monorepo-root /path/to/Monorepo-Uphillsnowball \
  --out RepoName_foldin_report.json
```

## Blocking rules

Treat the run as blocked if any of these appear:

- `manifest_split_brain`
- `destination_conflict`
- `secret_like`
- `nested_git`
- unresolved high-severity stale model or stale control-plane drift in code that will become live

## What to do with results

- `manifest_split_brain`
  - keep the root manifest canonical
  - reconcile or retire the second manifest

- `destination_conflict`
  - do not copy over the destination blindly
  - perform a merge-aware import instead

- `stale_model`
  - migrate old model strings to the current family contract

- `stale_mcp`
  - collapse references onto the canonical MCP surface

- `stale_naming`
  - normalize naming before fold-in so the incoming repo does not reintroduce thread drift

## Packaging principle

One zip. No duplicate tools. No second control plane.
