# Thread Transfer Manifest: Omega Singularity V2

## Architectural State
- **Compute**: Pure serverless (Google Cloud Run Gen 2).
- **VFS**: Virtual File System (`libs/steel/vfs.py`) with shadow-write staging at `/workspace`.
- **Relay**: Redis-backed state synchronization for ephemeral containers.
- **Defense**: 17-Layer DOW CRSMC compliant Sentinel Shield (`src/shield/judge.py`).

## Core Components
| Component | Responsibility | File Path |
| :--- | :--- | :--- |
| **Sentinel** | OODA Loop & Policy Enforcement | `scripts/sentinel_loop.py` |
| **Web UI** | Dark Luxury "Autonomous Sentinel" Interface | `apps/shadowtag-web/` |
| **Ingestion** | Gemini 2.5 + Drive V6 Intelligence | `scripts/ingest_drive_docs.py` |
| **Lake** | BQ Zero-ETL Embedding Engine | `libs/steel/bq_autonomous_lake.py` |
| **Pickle** | Structural DOM Hijacking | `scripts/pickle_protocol.py` |

## Branding & Contact
- **Entity**: ShadowTagAi Inc.
- **Address**: 495 N Main St., #119, Lakeport, CA 95453
- **Tel**: (369) 235-5643
- **Fax**: (707) 263-8659
- **Email**: founder@shadowtagai.com
- **Web**: www.shadowtagai.com
- **Primary**: Autonomous Sentinel (Enterprise-Grade).
- **Aesthetic**: #000000 Base, #b58900 Gold, #dc322f Crimson.
- **Protocol**: A2UI Declarative JSON for secure rendering.

## Exit Status
- **Tag**: `singularity-v1`
- **Hash**: [LATEST_COMMIT_HASH]
- **Stability**: PROVEN via `pyflakes` and Visual Audit.
