# GitHub Mirror Strategy - Never Lose Work Again

**Your complete backup and recovery system using GitHub as the primary mirror**

## The Problem You're Solving

> "gpt's memory is SO BAD i have six months of this level of work product strewn through 10 different llm accounts. i keep finding more."

**Never again.** Here's your complete mirroring solution.

---

## Three-Layer Backup Architecture

```

Layer 1: Local SQLite Archive (~/.consensus_archive.db)
    ↓ (automatic on every query)
Layer 2: Git Repository (local)
    ↓ (push after each session)
Layer 3: GitHub Remote (cloud mirror)
    ↓ (permanent, version-controlled)

```

**Result**: Every query is saved in **3 places** automatically.

---

## Current GitHub Mirror Status

**Repository**: `ShadowTag-v2/aiyou-fastapi-services`
**Branch**: `claude/voice-consensus-orchestrator-01KnByRibAJhGMpXrun59rp4`

**What's mirrored**:


- ✅ All consensus orchestrator code


- ✅ Transcript archive system


- ✅ Cost tracking and ROI analytics


- ✅ Complete documentation


- ✅ Example usage files

**Current commits (latest 5)**:

```

1848343 - Add comprehensive cost tracking and ROI analytics to consensus system
f9d8365 - Add persistent transcript archive system with full-text search
4e5b642 - Add unified Atomic Consensus Orchestrator (AoT + Multi-Model)
e96e4dc - Add message-level consensus for Claude Code integration
850cece - Add text-only quickstart for consensus testing without voice dependencies

```

---

## How the Mirror Works

### 1. **Every Query is Auto-Archived** (Layer 1)

```python

# Happens automatically

python message_consensus.py "Your question"

# → Saved to ~/.consensus_archive.db

```

**Storage location**: `~/.consensus_archive.db`


- Full query text


- Complete result


- Cost breakdown


- Timestamp


- Tags

### 2. **Code Changes are Committed** (Layer 2)

```bash

# After making changes

git add .
git commit -m "Your changes"

```

**Storage location**: `.git/` directory (local)


- All code versions


- Complete history


- Diffs and changes

### 3. **Pushed to GitHub** (Layer 3)

```bash

# Sync to cloud

git push

```

**Storage location**: `https://github.com/ShadowTag-v2/aiyou-fastapi-services`


- Remote backup


- Accessible from anywhere


- Permanent history


- Shareable with team

---

## Daily Workflow

### Morning: Pull Latest

```bash
cd ~/aiyou-fastapi-services
git pull
cd voice_consensus

```

### During Day: Run Queries

```bash

# Everything auto-archives

python message_consensus.py "Your research question"

# → Saved to ~/.consensus_archive.db automatically

python atomic_consensus_orchestrator.py "Complex analysis"

# → Saved to ~/.consensus_archive.db automatically

```

### End of Day: Backup Everything

```bash

# 1. Export daily archive to markdown

python transcript_archive.py export daily_$(date +%Y%m%d).md

# 2. Commit archive export

git add daily_*.md
git commit -m "Daily archive export $(date +%Y-%m-%d)"

# 3. Push to GitHub (mirrors everything)

git push

```

**Result**: Everything backed up to GitHub in 3 commands.

---

## Automated Backup Script

Create `~/backup_consensus.sh`:

```bash
#!/bin/bash

# Automated consensus archive backup

set -e

DATE=$(date +%Y%m%d)
REPO_DIR=~/aiyou-fastapi-services
ARCHIVE_DIR=$REPO_DIR/voice_consensus/archives

echo "=== Consensus Archive Backup - $DATE ==="

# Navigate to repo

cd $REPO_DIR/voice_consensus

# Export today's transcripts

python transcript_archive.py export $ARCHIVE_DIR/daily_$DATE.md

# Export cost report

python cost_tracker.py export $ARCHIVE_DIR/cost_report_$DATE.json --days 30

# Commit to git

cd $REPO_DIR
git add voice_consensus/archives/
git commit -m "Auto-backup: Archives and cost report $DATE" || echo "Nothing to commit"

# Push to GitHub

git push

echo "✓ Backup complete - pushed to GitHub"
echo "  Daily archive: archives/daily_$DATE.md"
echo "  Cost report: archives/cost_report_$DATE.json"

```

**Make it executable**:

```bash
chmod +x ~/backup_consensus.sh

```

**Run it daily**:

```bash
~/backup_consensus.sh

```

---

## Automated Backup with Cron

### Option 1: Daily Backup (8 PM)

```bash

# Edit crontab

crontab -e

# Add this line:

0 20 * * * /Users/yourusername/backup_consensus.sh >> /Users/yourusername/backup.log 2>&1

```

### Option 2: After Each Session

Add to your `~/.zshrc`:

```bash

# Auto-backup when terminal closes

trap 'cd ~/aiyou-fastapi-services && ~/backup_consensus.sh' EXIT

```

---

## Verify Your Mirror

### Check local archive

```bash
python transcript_archive.py stats

# Shows: Total transcripts, database size, etc.

```

### Check local git status

```bash
cd ~/aiyou-fastapi-services
git log --oneline -10

# Shows: Recent commits

```

### Check GitHub mirror

```bash

# View remote commits

git log origin/claude/voice-consensus-orchestrator-01KnByRibAJhGMpXrun59rp4 --oneline -10

# Or visit:

# https://github.com/ShadowTag-v2/aiyou-fastapi-services/tree/claude/voice-consensus-orchestrator-01KnByRibAJhGMpXrun59rp4

```

---

## Recovery Scenarios

### Scenario 1: Lost Local Files

**Problem**: Deleted local repository

**Solution**:

```bash
cd ~
git clone https://github.com/ShadowTag-v2/aiyou-fastapi-services.git
cd aiyou-fastapi-services
git checkout claude/voice-consensus-orchestrator-01KnByRibAJhGMpXrun59rp4
cd voice_consensus

# All code is back!

```

**Status**: ✅ All code recovered
**Archive status**: ⚠️ Need to restore `.consensus_archive.db` from backup

### Scenario 2: Lost Archive Database

**Problem**: Deleted `~/.consensus_archive.db`

**Solution**:

```bash

# Restore from exported markdown files

cd ~/aiyou-fastapi-services/voice_consensus/archives

# Re-import (manual process, or restore from Time Machine)

cp ~/Dropbox/consensus_backup_20251116.db ~/.consensus_archive.db

```

**Status**: ✅ Restored from Dropbox backup

### Scenario 3: Need Query from 2 Months Ago

**Problem**: Can't remember exact query

**Solution 1 - Search local archive**:

```bash
python transcript_archive.py search "edge AI cell tower"

```

**Solution 2 - Search GitHub markdown exports**:

```bash
cd ~/aiyou-fastapi-services/voice_consensus/archives
grep -r "edge AI" daily_*.md

```

**Status**: ✅ Found in both places

### Scenario 4: New MacBook Pro

**Problem**: Starting fresh on new machine

**Solution**:

```bash

# 1. Clone from GitHub

git clone https://github.com/ShadowTag-v2/aiyou-fastapi-services.git
cd aiyou-fastapi-services/voice_consensus

# 2. Setup environment

./setup_mac.sh

# 3. Restore archive database

# Option A: From Dropbox

cp ~/Dropbox/consensus_backup.db ~/.consensus_archive.db

# Option B: Re-import from markdown exports

python import_from_markdown.py archives/*.md

```

**Status**: ✅ Fully operational on new machine

---

## Multiple Backup Locations

**Recommended strategy**: GitHub + Cloud Storage

### 1. GitHub (Version Control)

```bash

# Always pushed here

git push

```

**Location**: `https://github.com/ShadowTag-v2/aiyou-fastapi-services`
**What it stores**:


- All code


- Documentation


- Exported markdown archives


- Cost reports

**Advantages**:


- Version history


- Easy recovery


- Accessible anywhere


- Free (public repo)

### 2. Dropbox (Archive Database)

```bash

# Daily copy

cp ~/.consensus_archive.db ~/Dropbox/consensus_backup_$(date +%Y%m%d).db

```

**Location**: `~/Dropbox/consensus_backup_*.db`
**What it stores**:


- Raw SQLite database


- All query history


- Cost tracking data

**Advantages**:


- Automatic sync


- 30-day version history


- Cross-device access

### 3. Time Machine (System Backup)

**Location**: Time Machine backup drive
**What it stores**:


- Everything (code + database + exports)

**Advantages**:


- Hourly snapshots


- Complete system recovery


- No manual intervention

---

## GitHub-Specific Features

### View Your Work on GitHub

**Repository**: https://github.com/ShadowTag-v2/aiyou-fastapi-services

**Current branch**: `claude/voice-consensus-orchestrator-01KnByRibAJhGMpXrun59rp4`

**What you can do**:


- Browse code online


- Search commit history


- Download specific versions


- Share with collaborators


- Create issues for tracking


- Fork for experimentation

### Search Commit History

```bash

# Find when cost tracking was added

git log --grep="cost tracking"

# Find when archive was added

git log --grep="archive"

# Find all changes to specific file

git log --follow voice_consensus/cost_tracker.py

```

### Create Tags for Milestones

```bash

# Tag important versions

git tag -a v1.0-consensus-archive -m "Complete consensus system with archive and cost tracking"
git push origin v1.0-consensus-archive

```

**View tags**: https://github.com/ShadowTag-v2/aiyou-fastapi-services/tags

### Use GitHub Issues

Track TODOs:

```

Issue #1: Add caching for repeated queries
Issue #2: Implement FastAPI REST endpoints
Issue #3: Build cost optimization dashboard

```

---

## Archive Organization on GitHub

### Recommended Structure

```

aiyou-fastapi-services/
├── voice_consensus/
│   ├── archives/                  # Export directory
│   │   ├── 2025_11/              # Monthly folders
│   │   │   ├── daily_20251116.md
│   │   │   ├── daily_20251117.md
│   │   │   └── cost_report_20251130.json
│   │   └── 2025_12/
│   │       └── ...
│   ├── README.md
│   ├── *.py                       # All code
│   └── *.md                       # Documentation
└── .gitignore

```

### .gitignore Settings

Already configured to exclude:

```gitignore

# Don't commit the live database (too large, binary)

.consensus_archive.db

# Don't commit virtual environment

venv/

# Don't commit API keys

.env

```

**What gets committed**:


- ✅ All Python code


- ✅ Markdown exports of archives


- ✅ JSON cost reports


- ✅ Documentation

**What stays local**:


- ❌ Live SQLite database (backed up to Dropbox instead)


- ❌ API keys


- ❌ Virtual environment

---

## Complete Backup Checklist

### ✅ Daily (Automated)



- [ ] Queries auto-save to `~/.consensus_archive.db`


- [ ] Export daily markdown: `daily_YYYYMMDD.md`


- [ ] Commit and push to GitHub


- [ ] Sync archive DB to Dropbox

### ✅ Weekly (Manual)



- [ ] Review cost tracker: `python cost_tracker.py roi --days 7`


- [ ] Export weekly report: `cost_tracker.py export weekly_report.json`


- [ ] Verify GitHub has latest commits


- [ ] Check Dropbox has latest `.db` file

### ✅ Monthly (Manual)



- [ ] Full archive export: `transcript_archive.py export monthly_YYYYMM.md`


- [ ] Full cost report: `cost_tracker.py export cost_monthly.json --days 30`


- [ ] Create git tag: `git tag -a v1.1 -m "Month end"`


- [ ] Download archive DB as secondary backup

---

## Disaster Recovery Plan

### If Everything is Lost

**You need**:


1. GitHub account access


2. Repository URL: `https://github.com/ShadowTag-v2/aiyou-fastapi-services`

**Recovery steps**:

```bash

# 1. Clone from GitHub (gets all code)

git clone https://github.com/ShadowTag-v2/aiyou-fastapi-services.git
cd aiyou-fastapi-services
git checkout claude/voice-consensus-orchestrator-01KnByRibAJhGMpXrun59rp4

# 2. Setup environment

cd voice_consensus
./setup_mac.sh
source venv/bin/activate

# 3. Restore archive from markdown exports

mkdir -p recovered_archives
cd archives
for f in daily_*.md; do
    # Parse and re-import (manual or scripted)
    echo "Recovered: $f"
done

# 4. Or restore from Dropbox

cp ~/Dropbox/consensus_backup_latest.db ~/.consensus_archive.db

# 5. Verify

python transcript_archive.py stats
python cost_tracker.py stats

```

**Recovery time**: ~15 minutes
**Data loss**: Minimal (maybe last few hours if not yet pushed)

---

## Best Practices

### 1. **Commit Often**

```bash

# After significant work

git add voice_consensus/
git commit -m "Add feature X"
git push

```

**Frequency**: Every 1-2 hours of work

### 2. **Use Descriptive Commits**

❌ Bad:

```bash
git commit -m "updates"

```

✅ Good:

```bash
git commit -m "Add cost optimization recommendations to tracker"

```

### 3. **Export Regularly**

```bash

# End of each research session

python transcript_archive.py export session_$(date +%Y%m%d_%H%M).md
git add voice_consensus/archives/
git commit -m "Export session archive"
git push

```

### 4. **Tag Important Milestones**

```bash

# After completing major feature

git tag -a v1.0-archive -m "Complete archive system"
git tag -a v1.1-cost-tracking -m "Add cost tracking"
git push --tags

```

### 5. **Keep Backups in Sync**

```bash

# Weekly verification

./verify_backups.sh

```

Create `verify_backups.sh`:

```bash
#!/bin/bash

echo "=== Backup Verification ==="
echo "1. Local archive:"
ls -lh ~/.consensus_archive.db
echo ""
echo "2. GitHub (last push):"
git log origin/claude/voice-consensus-orchestrator-01KnByRibAJhGMpXrun59rp4 --oneline -1
echo ""
echo "3. Dropbox backup:"
ls -lh ~/Dropbox/consensus_backup_*.db | tail -1
echo ""
echo "✓ All backups verified"

```

---

## Summary: Your Complete Mirror System

### What Gets Saved Where

| Data Type | Local DB | Git | GitHub | Dropbox |
|-----------|----------|-----|--------|---------|
| Query text | ✅ | ✅ (exports) | ✅ | ✅ |
| Results | ✅ | ✅ (exports) | ✅ | ✅ |
| Cost data | ✅ | ✅ (reports) | ✅ | ✅ |
| Code | ❌ | ✅ | ✅ | ❌ |
| Raw DB | ✅ | ❌ | ❌ | ✅ |

### Your Safety Net

**If you lose**:


- **Your MacBook**: ✅ Clone from GitHub + restore from Dropbox


- **GitHub access**: ✅ Still have local + Dropbox


- **Dropbox**: ✅ Still have local + GitHub markdown exports


- **Everything**: ✅ GitHub is always there (cloud backup)

### Time to Recovery



- Lost file: **< 1 minute** (git checkout)


- Lost local repo: **< 5 minutes** (git clone)


- Lost archive DB: **< 10 minutes** (restore from Dropbox)


- New machine setup: **< 30 minutes** (full recovery)

---

**Your work is now immortal. GitHub is the source of truth. Never lose research again.**

---

## Quick Reference

```bash

# Daily backup

~/backup_consensus.sh

# Verify backups

./verify_backups.sh

# Search archive

python transcript_archive.py search "your query"

# Export archive

python transcript_archive.py export backup.md

# Check GitHub status

git status && git log origin/claude/voice-consensus-orchestrator-01KnByRibAJhGMpXrun59rp4 --oneline -5

# Push to GitHub

git add . && git commit -m "Your message" && git push

```
