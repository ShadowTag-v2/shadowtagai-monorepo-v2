# First Beads epics/tasks for ANE workbench v3

## Epic: bd-ane1 — Establish ANE knowledge substrate
- bd-ane1.1 Initialize SQLite file index for ANE repo
- bd-ane1.2 Parse symbols for bridge/, training/, training_dynamic/
- bd-ane1.3 Create LanceDB ane_chunks table and upsert code/doc chunks
- bd-ane1.4 Sync doc registry into Postgres
- bd-ane1.5 Add /api/search and /api/context for antigravity

## Epic: bd-ane2 — M1 Pro 64GB baseline
- bd-ane2.1 Record host profile and macOS version
- bd-ane2.2 Compare README M4 claims against M1
- bd-ane2.3 Create first benchmark summary + memory events
- bd-ane2.4 Mirror experiment tasks into Postgres

## Epic: bd-ane3 — CortexLTM compatibility
- bd-ane3.1 Create thread/event/summary adapter
- bd-ane3.2 Add master memory writes for stable findings
- bd-ane3.3 Surface memory in /api/context
