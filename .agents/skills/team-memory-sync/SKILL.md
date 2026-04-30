# Team Memory Sync

## Overview
Harvested from `teamMemorySync/` and `remoteManagedSettings/`.

## Protocol
1. Team memory (shared context, architecture decisions) MUST be synchronized via standard Git ops on `GEMINI.md` or `knowledge/` directory.
2. **Secret Guarding:** Before committing any shared memory, the agent MUST run the `gitleaks_guardian.py` or equivalent secret scanner to ensure no API keys or local `.env` variables leak into the shared repository context.
