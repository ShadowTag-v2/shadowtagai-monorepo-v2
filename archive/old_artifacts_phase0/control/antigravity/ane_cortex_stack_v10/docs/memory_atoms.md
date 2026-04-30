# Memory atoms

## What they are
Atoms are the smallest stable retrievable memory units.

Examples:
- subject=`settings`, predicate=`default_inference_backend`, object=`ane`
- subject=`settings`, predicate=`fallback_backend`, object=`metal`
- subject=`standards`, predicate=`formatter`, object=`prettier-vscode`
- subject=`startup_contract`, predicate=`hydrate_before_reasoning`, object=`True`

## Why they help
- higher precision retrieval
- less prompt bloat
- easier conflict detection
- easier deprecation/versioning
- better authority enforcement

## Best practice
Use atoms for:
- rules
- settings
- standards
- procedures
- warnings
- decisions

Use summaries for:
- human-readable rollups
- dashboards
- session handoff

## Best overall shape
- authority-current.json = canonical snapshot
- memory_atoms = canonical retrieval units
- memories.jsonl = journal/history
- summaries = human-readable context
