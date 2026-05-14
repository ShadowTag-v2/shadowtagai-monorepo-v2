# Implementation Plan: Stage 3 Canonicalization and Repo-Drift Audit

## User Review Required
We are proceeding to Stage 3 as requested. Please review the specific audit targets and correction strategies below. If approved, we will begin the scans.

## Proposed Changes

### 1. Stale Model Audit
- **Target**: Scan all `.json`, `.yaml`, `.py`, and `.md` files for legacy model names.
- **Correction**: Replace legacy strings with the doctrinal `gemini-3.1-family` or the exact vendor-specific concrete model IDs as required by the tool.

### 2. Dual MCP Elimination
- **Target**: Identify any MCP configuration files other than `antigravity-mcp-config.json` (e.g. `workspace-mcp-config.json`, `mcp.json`).
- **Correction**: Remove them or demote them to `.archive` to ensure there is only *one* structural source of truth for MCP.

### 3. Naming and Identifier Scrub
- **Target**: Find instances of `flyingmonkey` and legacy project descriptors.
- **Correction**: Replace `flyingmonkey` with `https://github.com/karpathy/autoresearch` and ensure `shadowtag-omega-v4` is the unified project ID.

### 4. Code Root Canonicalization
- **Target**: Ensure that active code resides only in `apps/counselconduit`, `labs/uphillsnowball`, or `operations/`.
- **Correction**: Move anomalous code into the `reference/archive/` or `reference/upstreams/` buckets per the monorepo bounds.

## Verification Plan
### Automated Tests
1. **Find by Name / Grep Scans**: Run extensive `grep` and `fd` passes to verify zero hits on the forbidden terms.
2. **Git Status**: Verify working tree clean against the main branch post-audit.

### Manual Verification
1. Review generated diffs in `notify_user` to ensure no false positives were replaced.
