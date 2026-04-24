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
3. Files in `quarantine/` are auto-purged after 24h by KAIROS daemon
4. Files in `serve/` follow Obsidian Visual Graph Protocol (YAML frontmatter + WikiLinks)
5. `monitor/` contains KAIROS heartbeat and pipeline metrics only

## KAIROS Integration

The KAIROS daemon (`scripts/kairos_daemon.py`) runs these vault cycles:
- **Vault Ingest Sweep** (5 min) — process new files in `ingest/`
- **Quarantine Purge** (hourly) — delete stale quarantine files
- **Obsidian Sync** (hourly) — sync KI atoms to `serve/` as Obsidian notes
- **Betterleaks Scan** (nightly) — scan vault for accidentally ingested secrets

## Security

- `ingest/` and `quarantine/` are gitignored (ephemeral hostile data)
- `embed/` is gitignored (binary vector data)
- `serve/` is tracked (cleaned knowledge)
- `monitor/` is tracked (observability)
