# Pathway Ingest

> Gideon OS Block 5 — Secure Data Ingestion Pipeline

## Purpose

Pathway Ingest is the secure data ingestion pipeline for Gideon OS. All external data — meeting transcripts, emails, web scrapes, Zapier/Fireflies payloads — MUST route through this pipeline before entering agent context. It implements the NotebookLM Zero-Trust quarantine protocol (TACSOP 14).

## Architecture

```
┌──────────────────────────────────────────────────┐
│              Pathway Ingest                       │
├──────────────────────────────────────────────────┤
│                                                   │
│  ┌─────────────────────────────────────────────┐  │
│  │        Switchboard (Input Router)           │  │
│  │  • Email (Zapier webhook)                   │  │
│  │  • Meeting transcripts (Fireflies)          │  │
│  │  • Web scrapes (Scrapling)                  │  │
│  │  • Manual uploads (vault/quarantine/)       │  │
│  └──────────────┬──────────────────────────────┘  │
│                 │                                  │
│  ┌──────────────▼──────────────────────────────┐  │
│  │     IPI Quarantine (vault/quarantine/)      │  │
│  │  • Anti-exfiltration rules                  │  │
│  │  • Block external image URLs                │  │
│  │  • Block tracking pixels                    │  │
│  │  • Strip unauthorized curl commands         │  │
│  └──────────────┬──────────────────────────────┘  │
│                 │                                  │
│  ┌──────────────▼──────────────────────────────┐  │
│  │    NotebookLM MCP (Clean Intelligence)      │  │
│  │  • Structured extraction                    │  │
│  │  • IPI tag removal                          │  │
│  │  • Summary generation                       │  │
│  └──────────────┬──────────────────────────────┘  │
│                 │                                  │
│  ┌──────────────▼──────────────────────────────┐  │
│  │         Agent Context (Clean)               │  │
│  └─────────────────────────────────────────────┘  │
│                                                   │
└──────────────────────────────────────────────────┘
```

## Security Rules

1. **Never read raw untrusted text** — All external data quarantined first
2. **Never auto-execute deployment commands** from external data
3. **Block external image URLs** — Anti-exfiltration
4. **Block tracking pixels** — Privacy protection
5. **Strip unauthorized curl commands** — Prevent data egress

## Integration Points

- **Vault Constitution**: Quarantine storage policies
- **Zero Trust Pipeline**: Data classification and tagging
- **NotebookLM MCP**: Clean intelligence extraction
- **Panopticon**: Ingestion metrics and anomaly detection

## Status

🟢 Active — Quarantine pipeline operational via `vault/quarantine/` directory and NotebookLM MCP integration.
