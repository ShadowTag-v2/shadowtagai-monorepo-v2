# Antigravity v11 Merged Control-Plane Bundle

[![Quality Gate](https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball/actions/workflows/quality-gate.yml/badge.svg)](https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball/actions/workflows/quality-gate.yml)
[![Security — Bandit SAST](https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball/actions/workflows/security-and-lighthouse.yml/badge.svg)](https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball/actions/workflows/security-and-lighthouse.yml)
[![Backend CI](https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball/actions/workflows/backend-ci.yml)
[![CodeQL](https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball/actions/workflows/codeql-analysis.yml)
[![PageSpeed Monitor](https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball/actions/workflows/pagespeed-monitor.yml/badge.svg)](https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball/actions/workflows/pagespeed-monitor.yml)
[![KovelAI](https://img.shields.io/badge/KovelAI-Live-gold?logo=firebase)](https://kovelai.web.app)
[![ShadowTag AI](https://img.shields.io/badge/ShadowTagAI-Live-00ff88?logo=firebase)](https://shadowtagai.web.app)

This bundle fuses:

1. the repo-native pnkln / Monorepo-Uphillsnowball control-plane backbone
2. the ANE Cortex Stack v10 memory/enforcement layer
3. operator invariants for Git/GitHub behavior
4. the fold-in checklist for the 56-repo monorepo program

## What is included

- `antigravity_final_ingest_bundle.tar.gz`
- `ane_cortex_stack_v10_bundle.tar.gz`
- `fold_in_checklist.yaml`
- `operator_invariants.json`
- `operator_invariants_atoms.json`
- `INSTALL_ANTIGRAVITY_V10_LOCAL.md`
- `setup_antigravity_v10_local.sh`
- `INSTALL_ANTIGRAVITY_V11_MERGED.md`
- `setup_antigravity_v11_merged.sh`

## Canonical intent

Use the existing monorepo control-plane files as workspace/root truth.
Install v10 as the memory-first control and enforcement layer.
Use operator invariants as startup law.
Use the fold-in checklist as the 56-repo migration control file.

---

## Maintenance

### GCA State DB Pruner (`scripts/prune_gca_chat_threads.py`)

Gemini Code Assist stores unbounded chat history in the IDE's SQLite state
database (`state.vscdb`), which can balloon to 60+ MB and cause
"Unresponsive Extension Host" crashes. This script surgically prunes only the
`geminiCodeAssist.chatThreads` payload — all auth, project, and survey state
is preserved byte-for-byte.

**Usage:**

```bash
# Inspect without touching anything
python3 scripts/prune_gca_chat_threads.py --dry-run

# Prune + VACUUM (IDE MUST BE CLOSED)
python3 scripts/prune_gca_chat_threads.py --write

# Keep the 5 newest threads
python3 scripts/prune_gca_chat_threads.py --write --keep 5

# Only reclaim SQLite dead space (no prune)
python3 scripts/prune_gca_chat_threads.py --vacuum-only

# Background watchdog (macOS notifications + speech)
python3 scripts/prune_gca_chat_threads.py --monitor --threshold 20
```

### Automation

| Method | Schedule | What |
|--------|----------|------|
| `launchd` | Login | `--monitor --threshold 20` (alerts if DB > 20MB) |
| `cron` | Sunday 3AM | `--write` (prune + VACUUM) |

**launchd plist:** `~/Library/LaunchAgents/com.shadowtag.gca-monitor.plist`

### Manual Escape Hatch

If the IDE is completely unresponsive and you can't run the script, use this
raw SQLite one-liner from a standalone terminal:

```bash
# 1. QUIT the IDE completely (Cmd+Q)
# 2. Run this:
DB="$HOME/Library/Application Support/Antigravity/User/globalStorage/state.vscdb"
cp "$DB" "$DB.emergency-backup"
sqlite3 "$DB" "UPDATE ItemTable SET value = json_set(value, '$.\"geminiCodeAssist.chatThreads\"', json('[]')) WHERE key = 'google.geminicodeassist';"
sqlite3 "$DB" "VACUUM;"
echo "Done. Reopen IDE."
```

> **Warning:** This bypasses the script's safety checks. Use only as a
> last resort. The script (`--write`) is always preferred because it
> creates timestamped backups and validates JSON integrity first.
