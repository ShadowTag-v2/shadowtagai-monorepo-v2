# /wrap-up — Session Memory Persistence

// turbo-all

End-of-session ritual that persists learnings to Master Brain (NotebookLM) and Obsidian vault.

## Prerequisites
- `notebooklm-py` installed and authenticated
- Master Brain ID exists at `~/.notebooklm/master-brain-id`
- OBSIDIAN_VAULT_ROOT set (optional, for Obsidian sync)

## Workflow

### Step 1: Generate Session Summary
Create a structured summary of this session's work:
```
Summarize the session in this format:
- What was accomplished (bullet points)
- Key decisions made
- Technical learnings
- Blockers/issues encountered
- Next steps
Save to: /tmp/session-summary-$(date +%Y%m%d).md
```

### Step 2: Upload to Master Brain
```bash
export PATH="/Users/pikeymickey/Library/Python/3.13/bin:$PATH"
BRAIN_ID=$(cat ~/.notebooklm/master-brain-id 2>/dev/null)
if [ -n "$BRAIN_ID" ]; then
  notebooklm use "$BRAIN_ID"
  notebooklm note create "Session $(date +%Y-%m-%d %H:%M)" --content "$(cat /tmp/session-summary-$(date +%Y%m%d).md)"
  echo "✅ Session note uploaded to Master Brain"
else
  echo "⚠️  No Master Brain ID found. Skipping upload."
fi
```

### Step 3: Update Obsidian Daily Note
```bash
VAULT="${OBSIDIAN_VAULT_ROOT:-$HOME/Documents/Obsidian/ShadowTag-Vault}"
TODAY=$(date +%Y-%m-%d)
DAILY="$VAULT/Daily Notes/$TODAY.md"

if [ -d "$VAULT" ]; then
  if [ ! -f "$DAILY" ]; then
    cat > "$DAILY" << EOF
---
date: "$TODAY"
type: daily-note
tags: [daily]
---
# $TODAY
EOF
  fi

  echo "" >> "$DAILY"
  echo "## Session Wrap-Up ($(date +%H:%M))" >> "$DAILY"
  cat /tmp/session-summary-$(date +%Y%m%d).md >> "$DAILY"
  echo "✅ Daily note updated: $DAILY"
else
  echo "⚠️  Obsidian vault not found at $VAULT"
fi
```

### Step 4: Verify
```bash
notebooklm note list 2>/dev/null | tail -5
echo "---"
cat "$VAULT/Daily Notes/$(date +%Y-%m-%d).md" 2>/dev/null | tail -10
```

## Notes
- Run this at the END of every session to build persistent cross-session memory
- The Master Brain notebook accumulates knowledge over time
- Use `notebooklm ask "What did I learn about [topic]?"` in future sessions to recall
- Obsidian vault can be browsed visually in the Obsidian app
