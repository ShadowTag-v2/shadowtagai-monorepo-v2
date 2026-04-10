# VS Code / Antigravity launch hydration

## Goal

On every extension/session launch, hydrate from memory before looking at repo context.

## Required startup calls

1. GET /api/hydrate-pack
2. Cache authority + atoms + active tasks + drift reports locally for the session
3. Use /api/context only after hydrate-pack has been loaded
4. If drift_reports are non-empty, prioritize upgrade tasks before exploratory repo work

## Launch policy

- authority snapshot is canonical
- atoms are the primary retrieval surface
- codebase is evidence and upgrade target
- old repo docs/config cannot silently redefine standards/settings

## Minimum session state to cache

- authority.startup_contract
- authority.standards
- authority.settings
- top atoms
- active tasks
- current drift reports
