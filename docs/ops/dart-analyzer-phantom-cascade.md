# Dart Analyzer Phantom Cascade — Mitigation Guide

> **Status:** ACTIVE | **Version:** 1.0 | **Updated:** 2026-05-04

## Problem

The Monorepo-Uphillsnowball repo contains 30+ Dart packages across `tools/dio/`,
`tools/google-cloud-dart/`, and `external_repos/`. When the Dart Analysis Server
starts, it eagerly discovers every `pubspec.yaml` in the workspace tree and
attempts to:

1. Run `pub get` for each package
2. Build resolution graphs across all packages
3. Analyze all `.dart` files recursively

This creates a **phantom cascade**: thousands of file reads, network requests
to pub.dev, and CPU-bound analysis for packages that are not being actively
edited. On macOS, this also contributes to FSEvents queue overflow.

## Mitigation

### 1. Exclude Reference Repos from Dart Analysis

The following paths are excluded via `.vscode/settings.json`:

```json
{
  "dart.analysisExcludedFolders": [
    "external_repos",
    "tools/dio",
    "tools/google-cloud-dart"
  ]
}
```

### 2. Do Not Recursively `pub get`

**Rule:** Run `dart pub get` only in the specific package directory you are
actively editing. Never run it at the repo root or via a recursive script.

```bash
# ✅ CORRECT — targeted pub get
cd tools/my-dart-package && dart pub get

# ❌ WRONG — recursive pub get across entire repo
find . -name pubspec.yaml -execdir dart pub get \;
```

### 3. Restart Analysis Server After Exclusion Changes

After modifying `dart.analysisExcludedFolders`, the Dart Analysis Server must
be restarted to pick up the changes:

1. Open VS Code Command Palette (`Cmd+Shift+P`)
2. Run: `Dart: Restart Analysis Server`

Or via terminal:
```bash
# Kill existing analysis servers
pkill -f dart_analysis_server || true
```

### 4. Watcher Relief Script

The `scripts/local-watcher-relief.sh` script safely removes local-only heavy
directories that contribute to watcher pressure:

```bash
# Dry run first
scripts/local-watcher-relief.sh --dry-run

# Execute
scripts/local-watcher-relief.sh
```

Targets (local-only, not committed):
- `external_repos/upstream/` (clone cache)
- `.gitnexus/` (index cache)
- `.index/` (search index)
- `.lancedb/` / `.lancedb_data/` (vector DB cache)
- `browser_artifacts/` (Chrome DevTools MCP artifacts)

### 5. Files/Watcher Excludes

These paths are excluded from the VS Code file watcher to prevent FSEvents
saturation:

```json
{
  "files.watcherExclude": {
    "**/external_repos/**": true,
    "**/.gitnexus/**": true,
    "**/.index/**": true,
    "**/.lancedb/**": true,
    "**/.lancedb_data/**": true,
    "**/browser_artifacts/**": true,
    "**/node_modules/**": true,
    "**/.next/**": true,
    "**/.turbo/**": true,
    "**/.dart_tool/**": true,
    "**/.pub-cache/**": true
  }
}
```

## Monitoring

Check for runaway Dart processes:
```bash
# Count active dart analysis servers
pgrep -c dart_analysis_server || echo "0 servers running"

# Check CPU usage
ps aux | grep dart_analysis_server | grep -v grep
```

## References

- `.vscode/settings.json` — IDE configuration
- `scripts/local-watcher-relief.sh` — Watcher relief script
- `docs/ops/ide-extension-policy.md` — Extension prohibition policy
