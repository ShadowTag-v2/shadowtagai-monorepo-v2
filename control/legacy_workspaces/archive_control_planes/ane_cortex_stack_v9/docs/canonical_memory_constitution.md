# Canonical Memory Constitution v8

## Purpose

Make memory the single source of truth for Antigravity and editor launch.
Codebase is evidence and upgrade target, never the default authority for standards/settings/procedures.

## Truth hierarchy

1. authority-current.json
2. authority snapshots + atoms
3. active tasks / drift reports
4. memory bank generated views
5. summaries + journal
6. code graph / code chunks
7. raw codebase

## Buckets

- canonical: current truth that must win conflicts
- derived: generated views for humans/tools
- historical: journal/summaries/older threads
- speculative: brainstorms, valuations, future ideas
- deprecated: superseded configs/docs/roots

## Core rule

If codebase conflicts with authority memory, update the codebase and preserve memory authority.

## Startup contract

1. Load authority-current.json
2. Load top authority atoms
3. Load active tasks
4. Load current drift reports
5. Load recent summary
6. Only then inspect codebase

## Compatibility surface

Maintain .agent/memory/ for Antigravity compatibility, but treat it as derived from canonical authority.

## Write barrier

Any change to standards/settings/procedures/startup behavior is not real until it updates:

- authority-current.json
- authority_snapshots
- authority atoms
- optional journal entry
