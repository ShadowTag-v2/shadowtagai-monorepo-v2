# /obsidian-sync — Sync Research to Obsidian Vault

Use this workflow to sync research outputs, session summaries, and artifacts to your Obsidian vault with proper frontmatter and [[wikilinks]].

## Prerequisites
- `OBSIDIAN_VAULT_ROOT` environment variable set, or vault path known
- Vault folder structure initialized (see obsidian-vault-operator skill)

## Workflow

### Step 1: Verify Vault Access
```bash
VAULT_ROOT=${OBSIDIAN_VAULT_ROOT:-~/Documents/Obsidian/ShadowTag-Vault}
ls "$VAULT_ROOT" > /dev/null 2>&1 && echo "✅ Vault accessible at $VAULT_ROOT" || echo "❌ Vault not found"
```

### Step 2: Initialize Folder Structure (if needed)
```bash
VAULT_ROOT=${OBSIDIAN_VAULT_ROOT:-~/Documents/Obsidian/ShadowTag-Vault}
mkdir -p "$VAULT_ROOT"/{00-Inbox,10-Daily,20-Research,30-Projects,40-References,50-Templates,60-Canvas,70-Archive}
```

### Step 3: Sync Research Output
For each research artifact generated (reports, summaries, etc.):

```bash
VAULT_ROOT=${OBSIDIAN_VAULT_ROOT:-~/Documents/Obsidian/ShadowTag-Vault}
TOPIC="[topic-slug]"
DATE=$(date +%Y-%m-%d)

cat > "$VAULT_ROOT/20-Research/$TOPIC.md" << 'NOTE'
---
title: "[Topic Title]"
date: YYYY-MM-DD
tags: [research, source/notebooklm]
notebook_id: "[id]"
status: active
---

# [Topic Title]

## Summary
[Research findings]

## Key Insights
[Extracted insights]

## Sources
[List of sources with citations]

## Related Notes
- [[]]
NOTE
```

### Step 4: Update Daily Note
```bash
VAULT_ROOT=${OBSIDIAN_VAULT_ROOT:-~/Documents/Obsidian/ShadowTag-Vault}
DAILY="$VAULT_ROOT/10-Daily/$(date +%Y-%m-%d).md"

# Create daily note if it doesn't exist
if [ ! -f "$DAILY" ]; then
cat > "$DAILY" << 'DAILY_NOTE'
---
title: "$(date +%Y-%m-%d)"
type: daily
---

# $(date +"%A, %B %d %Y")

## Notes
DAILY_NOTE
fi

echo "" >> "$DAILY"
echo "- Synced: [[20-Research/$TOPIC]]" >> "$DAILY"
```

### Step 5: Verify Links
```bash
# Check for broken wikilinks in recently created notes
grep -r '\[\[' "$VAULT_ROOT/20-Research/" | head -10
echo "✅ Sync complete"
```
