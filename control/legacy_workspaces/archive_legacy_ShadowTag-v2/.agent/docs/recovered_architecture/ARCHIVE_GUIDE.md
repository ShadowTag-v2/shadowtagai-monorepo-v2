# Transcript Archive System

**Never lose your work again.** Persistent, searchable archive for all consensus queries and results.

## Why This Matters

You said it yourself:
> "gpt's memory is SO BAD i have six months of this level of work product strewn through 10 different llm accounts. i keep finding more."

This solves that problem permanently.

## What It Does



- ✅ **Auto-archives** every query and result


- ✅ **Full-text search** across all history


- ✅ **Tag system** for organization


- ✅ **Export** to JSON/Markdown


- ✅ **Local SQLite** (no cloud, fully portable)


- ✅ **Conversation threading** to link related queries


- ✅ **Never loses data** - it's your database, on your machine

## Automatic Archiving

Both orchestrators **automatically save** every query/result:

```bash

# This automatically saves to archive

python message_consensus.py "Your question"

# This also automatically saves

python atomic_consensus_orchestrator.py "Your complex question"

```

**Archive location:** `~/.consensus_archive.db`

Every query is saved with:


- Full query text


- Complete result


- Timestamp


- Models used


- Peer reviews conducted


- Execution time


- Success rate


- Tags (if you add them)


- Notes (if you add them)

## Searching Your Archive

### Search by keywords

```bash
python transcript_archive.py search "edge AI"

```

### Recent transcripts

```bash
python transcript_archive.py recent --limit 20

```

### Filter by tags

```bash
python transcript_archive.py search "architecture" --tags microservices api-design

```

### Filter by system type

```bash
python transcript_archive.py search "deployment" --type atomic

```

## Adding Tags and Notes

### Tag a transcript

```bash

# After running a query, it prints: [Archive] Saved as transcript #42

python transcript_archive.py tag 42 architecture production critical

```

### Add notes

```python
from transcript_archive import TranscriptArchive

archive = TranscriptArchive()
archive.add_note(42, "This design was approved by team. Use for production.")
archive.close()

```

## Viewing Full Transcripts

```bash

# Show complete transcript with all details

python transcript_archive.py show 42

```

Output:

```

================================================================================
Transcript #42 - 2025-11-16T10:30:15.123456
================================================================================

System: atomic
Tags: architecture,production,critical

Query:
Design a scalable edge AI architecture...

Final Output:
[Complete synthesized answer]

Metadata:
  Threads: 5
  Models: 15
  Reviews: 30
  Time: 45.32s

```

## Exporting Your Work

### Export to Markdown

```bash

# Export all transcripts

python transcript_archive.py export all_transcripts.md

# Export specific ones

python transcript_archive.py export selected.md --ids 10 15 20 42

```

### Export to JSON

```bash

# Full data export (for backup or analysis)

python transcript_archive.py export backup.json

# Specific transcripts

python transcript_archive.py export critical_decisions.json --ids 42 43 44

```

## Archive Statistics

```bash
python transcript_archive.py stats

```

Output:

```

================================================================================
Archive Statistics
================================================================================

Total Transcripts: 127
By System Type: {'atomic': 45, 'simple': 82}
Avg Models/Query: 4.2
Avg Reviews/Query: 8.7
Total Execution Time: 2.34 hours
Database Size: 12.45 MB
Database Path: /Users/you/.consensus_archive.db

```

## Conversation Threading

Link related queries together:

```python
from transcript_archive import TranscriptArchive

archive = TranscriptArchive()

# First query in thread

thread_id = "edge-ai-project-2025"

result1 = orchestrator.process_message(
    "Design edge AI architecture",
    auto_archive=True
)

# Manually archive with thread ID

archive.archive(
    user_query="Design edge AI architecture",
    result=result1,
    system_type="atomic",
    conversation_thread_id=thread_id
)

# Later, related query

result2 = orchestrator.process_message(
    "Cost analysis for edge AI deployment"
)

archive.archive(
    user_query="Cost analysis for edge AI deployment",
    result=result2,
    system_type="atomic",
    conversation_thread_id=thread_id  # Same thread
)

# Retrieve entire conversation

conversation = archive.get_by_thread(thread_id)
print(f"Found {len(conversation)} related queries")

archive.close()

```

## Full-Text Search Syntax

SQLite FTS5 supports advanced queries:

```bash

# AND search

python transcript_archive.py search "edge AND deployment"

# OR search

python transcript_archive.py search "kubernetes OR docker"

# NOT search

python transcript_archive.py search "architecture NOT monolithic"

# Phrase search

python transcript_archive.py search "\"real-time inference\""

# Prefix search

python transcript_archive.py search "micro*"  # finds microservices, microarchitecture, etc.

```

## Backup Your Archive

The archive is a single SQLite file: `~/.consensus_archive.db`

### Simple backup

```bash
cp ~/.consensus_archive.db ~/Dropbox/consensus_backup_$(date +%Y%m%d).db

```

### Automated daily backup

Add to your `~/.zshrc` or `~/.bashrc`:

```bash

# Backup consensus archive daily

alias backup-consensus='cp ~/.consensus_archive.db ~/Dropbox/consensus_backup_$(date +%Y%m%d).db'

```

### Export everything periodically

```bash

# Monthly export to Markdown

python transcript_archive.py export ~/Documents/consensus_archive_$(date +%Y_%m).md

```

## Programmatic Usage

```python
from transcript_archive import TranscriptArchive

# Initialize

archive = TranscriptArchive()

# Search

results = archive.search(
    query="microservices",
    limit=10,
    tags=["architecture"],
    system_type="atomic",
    date_from="2025-11-01",
    date_to="2025-11-30"
)

for r in results:
    print(f"[{r['id']}] {r['timestamp']}")
    print(f"Q: {r['user_query'][:100]}...")
    print(f"Tags: {r['tags']}\n")

# Get full transcript

transcript = archive.get_by_id(42)
print(transcript['final_output'])

# Add tags

archive.add_tags(42, ["production", "approved"])

# Add note

archive.add_note(42, "Implemented this design in Q4 2025")

# Export

archive.export_to_markdown("my_research.md")

# Stats

stats = archive.get_stats()
print(f"Total queries archived: {stats['total_transcripts']}")

# Close

archive.close()

```

## Integration with Your Workflow

### 1. Run Query → Auto-Archive → Tag Later

```bash

# Run your query (auto-archives)

python atomic_consensus_orchestrator.py "Complex question"

# Output: [Archive] Saved as transcript #127

# Tag it

python transcript_archive.py tag 127 important architecture

```

### 2. End-of-Day Review

```bash

# See today's work

python transcript_archive.py recent --limit 20

# Tag and annotate important ones

python transcript_archive.py tag 125 production-ready
python transcript_archive.py tag 127 needs-review

```

### 3. Weekly Export

```bash

# Export week's work to Markdown

python transcript_archive.py export week_$(date +%Y_W%U).md

```

### 4. Project-Based Organization

Use tags to organize by project:

```bash

# Tag transcripts for specific project

python transcript_archive.py tag 120 project:edge-ai
python transcript_archive.py tag 121 project:edge-ai
python transcript_archive.py tag 122 project:edge-ai

# Later, search by project

python transcript_archive.py search "" --tags project:edge-ai

```

## Disable Auto-Archive (if needed)

```python

# Atomic consensus without archiving

result = await orchestrator.process_message(
    "Your query",
    auto_archive=False  # Don't save this one
)

# Simple consensus without archiving

result = await orchestrator.process_message(
    "Your query",
    auto_archive=False
)

```

## Archive File Location

Default: `~/.consensus_archive.db`

### Change location

```python
from transcript_archive import TranscriptArchive

# Use custom location

archive = TranscriptArchive(db_path="~/Dropbox/my_consensus.db")

```

Or set environment variable:

```bash
export CONSENSUS_ARCHIVE_DB="~/Dropbox/my_consensus.db"

```

Then modify code to check:

```python
import os
db_path = os.environ.get("CONSENSUS_ARCHIVE_DB", "~/.consensus_archive.db")
archive = TranscriptArchive(db_path=db_path)

```

## Migrating from GPT/Other LLMs

### Manual Import



1. Copy your old transcripts into a file


2. For each transcript, run through consensus


3. It auto-archives

Or write a simple import script:

```python
from transcript_archive import TranscriptArchive
import json

archive = TranscriptArchive()

# Load your old GPT transcripts

with open("old_gpt_conversations.json") as f:
    old_convos = json.load(f)

for convo in old_convos:
    archive.archive(
        user_query=convo["query"],
        result={"final_output": convo["response"]},
        system_type="imported",
        tags=["gpt-import", "legacy"]
    )

archive.close()

```

## Benefits Over GPT Memory

| GPT | Consensus Archive |
|-----|-------------------|
| Scattered across accounts | Single local database |
| No search | Full-text search |
| Lost when session ends | Permanent |
| Can't export | Export to JSON/MD |
| No tags/organization | Tag system |
| Cloud-dependent | Local file |
| No threading | Conversation threads |
| Limited history | Unlimited |

## Troubleshooting

### "Database is locked"

Close other connections:

```python
archive.close()

```

### "No module named 'transcript_archive'"

Make sure you're in the `voice_consensus` directory.

### Archive not saving

Check if `ARCHIVE_AVAILABLE`:

```python
from message_consensus import ARCHIVE_AVAILABLE
print(ARCHIVE_AVAILABLE)  # Should be True

```

## CLI Quick Reference

```bash

# Search

python transcript_archive.py search "your query"
python transcript_archive.py search "query" --tags tag1 tag2
python transcript_archive.py search "query" --type atomic

# Recent

python transcript_archive.py recent --limit 20

# Show full transcript

python transcript_archive.py show 42

# Tag

python transcript_archive.py tag 42 important production

# Export

python transcript_archive.py export output.md
python transcript_archive.py export output.json --ids 10 20 30

# Stats

python transcript_archive.py stats

```

---

**Your research is now permanent, searchable, and portable. Never lose work again.**
