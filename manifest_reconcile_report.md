# Manifest Reconcile Report

- Primary: `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/monorepo_manifest.yaml`
- Secondary: `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/manifests/monorepo_manifest.yaml`

## Summary

- only in primary: 59
- only in secondary: 46
- differing keys: 1
- critical drift items: 0

## Recommendation

Root manifest should remain canonical. Reconcile or retire the second manifest before any large migration or fold-in.

## Differing keys

### `workspace.name`
- section: `workspace`
- severity: `medium`
- primary: `Monorepo-Uphillsnowball`
- secondary: `pnkln`

