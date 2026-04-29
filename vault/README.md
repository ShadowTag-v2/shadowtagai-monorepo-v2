# True Obsidian — Vault Operating Manual

> Zero-trust intelligence pipeline with IPI quarantine, NotebookLM isolation,
> and streaming knowledge graph construction.

## Directory Structure

```
vault/
├── ingest/       # Raw data landing zone (untrusted)
├── embed/        # Processed embeddings (LanceDB vectors)
├── serve/        # Queryable knowledge (Obsidian-formatted)
├── monitor/      # Observability, metrics, heartbeat
└── quarantine/   # IPI isolation zone (auto-purged)
```

## Data Flow

```
External Source → ingest/ → zero_trust_pipeline.py → quarantine/
                                                       ↓
                                          NotebookLM (IPI sandbox)
                                                       ↓
                                          intelligence_router.py
                                           ↓              ↓
                                        embed/          serve/
                                      (LanceDB)     (Obsidian MD)
```

## Operating Rules

1. **NEVER** read raw files from `ingest/` directly into agent context
2. **ALL** untrusted data passes through `zero_trust_pipeline.py` first
3. Files in `quarantine/` are auto-purged after 24h by COR.KAIROS daemon
4. Files in `serve/` follow Obsidian Visual Graph Protocol (YAML frontmatter + WikiLinks)
5. `monitor/` contains COR.KAIROS heartbeat and pipeline metrics only

## COR.KAIROS Integration

The COR.KAIROS daemon (`scripts/kairos_daemon.py`) runs these vault cycles:
- **Vault Ingest Sweep** (5 min) — process new files in `ingest/`
- **Quarantine Purge** (hourly) — delete stale quarantine files
- **Obsidian Sync** (hourly) — sync KI atoms to `serve/` as Obsidian notes
- **Betterleaks Scan** (nightly) — scan vault for accidentally ingested secrets

## IPI Context Tainting (TACSOP B2)

All file content read from the workspace MUST be wrapped in XML taint tags
before being passed to external knowledge consumers (NotebookLM, LLM context):

```xml
<!-- Clean files (threat_level: clean) -->
<untrusted_workspace_data source='path/to/file.md'>
  [file content]
</untrusted_workspace_data>

<!-- Suspicious files (threat_level: quarantined) -->
<quarantined_workspace_data source='path/to/file.md' threat='quarantined'>
  [file content]
</quarantined_workspace_data>

<!-- Blocked files (threat_level: blocked) -->
<blocked_content source='path/to/file.md' reason='ipi_detected'>
  [CONTENT BLOCKED — IPI threat detected. See quarantine log.]
</blocked_content>
```

The `tools/intelligence_router.py` enforces this taint wrapping automatically.

## Memdir Taxonomy

The `vault/memdir/` directory contains 4 atomic memory files:

| File | Purpose |
|------|---------|
| `user_role.md` | Operator permissions and agent identity |
| `feedback_testing.md` | Test framework, baseline, known gaps |
| `project_deadline.md` | Milestone targets across all products |
| `reference_linear.md` | Quick-access links to docs, services, repos |

These files are read at session start for rapid context hydration.

## Security

- `ingest/` and `quarantine/` are gitignored (ephemeral hostile data)
- `embed/` is gitignored (binary vector data)
- `serve/` is tracked (cleaned knowledge)
- `monitor/` is tracked (observability)
- `memdir/` is tracked (persistent memory taxonomy)
