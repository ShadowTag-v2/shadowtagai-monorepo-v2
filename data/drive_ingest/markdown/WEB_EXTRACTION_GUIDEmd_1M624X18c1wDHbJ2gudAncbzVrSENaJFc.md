# Web Extraction Guide: Claude.ai + Claude Code

Complete guide for extracting conversations from **Claude.ai** (regular chat) and **Claude Code for web** to merge with local 0xSero extractions.

## Quick Start

### 1. Extract from Claude.ai (Regular Chat)

```bash
# Navigate to https://claude.ai
# Open DevTools (F12)
# Go to Console tab
# Paste the extraction script:
```

Copy and paste the entire contents of `scripts/extract_claude_web.js` into the browser console, then press Enter.

**Output**: Downloads `claude_web_extraction_claude-ai-web_<timestamp>.json`

### 2. Extract from Claude Code Web

```bash
# Navigate to https://code.claude.com
# Open DevTools (F12)
# Go to Console tab
# Paste the extraction script:
```

Copy and paste the entire contents of `scripts/extract_claude_web.js` into the browser console, then press Enter.

**Output**: Downloads `claude_web_extraction_claude-code-web_<timestamp>.json`

### 3. Merge Extractions

```bash
# Move downloaded files to extractions/ directory
mv ~/Downloads/claude_web_extraction_*.json erik-hancock-llm-memory/extractions/

# Run merge script
cd erik-hancock-llm-memory
python scripts/merge_web_extractions.py
```

### 4. Generate Metadata (Optional)

```bash
# Generate Gemini metadata for new conversations
python scripts/extract_and_commit.py
```

### 5. Deploy to Claude Code

```bash
# Install updated memory to Claude Code
python scripts/claude_code_memory_local.py
```

## Complete Extraction Coverage

### ✅ Local Platforms (0xSero)
- **Cursor**: `state.vscdb` SQLite database
- **Claude Desktop**: Local storage
- **Codex**: Local database
- **Windsurf**: Local storage
- **Trae**: Local database

### ✅ Web Platforms (Browser Script)
- **Claude.ai**: Regular chat interface
- **Claude Code for web**: Web-based coding assistant

### 📱 Mobile (Manual Export)
- **Claude Mobile**: Export via app settings (if available)

## Extraction Script Technical Details

### What It Extracts

The browser script (`extract_claude_web.js`) scans:

1. **localStorage**
   - All keys containing: conversation, chat, message, claude, thread
   - Parsed as JSON when possible

2. **IndexedDB**
   - All databases
   - Specifically: conversation, chat, message stores
   - Complete object store records

3. **sessionStorage**
   - Temporary conversation data
   - Active session information

4. **DOM Elements**
   - Visible conversation UI elements
   - Message content and metadata
   - Conversation attributes

5. **API Endpoints** (if accessible)
   - `/api/conversations`
   - `/api/v1/conversations`
   - `/backend-api/conversations`

### Output Format

```json
{
  "metadata": {
    "platform": "claude-ai-web | claude-code-web",
    "extracted_at": "2025-01-16T12:00:00Z",
    "url": "https://claude.ai",
    "user_agent": "...",
    "extractor_version": "1.0.0"
  },
  "sources": {
    "localStorage": {
      "keys_found": 15,
      "data": { ... }
    },
    "indexedDB": {
      "databases_scanned": 3,
      "data": { ... }
    },
    "dom": {
      "conversations_found": 50,
      "data": [ ... ]
    },
    "sessionStorage": {
      "keys_found": 5,
      "data": { ... }
    },
    "api": {
      "endpoint": "/api/conversations",
      "conversations": [ ... ]
    }
  },
  "statistics": {
    "total_sources": 5,
    "localStorage_keys": 15,
    "indexedDB_records": 120,
    "dom_elements": 50,
    "sessionStorage_keys": 5,
    "api_conversations": 200
  }
}
```

## Merge Process

The `merge_web_extractions.py` script:

1. **Loads** all `claude_web_extraction_*.json` files from `extractions/`
2. **Parses** data from multiple sources (API → IndexedDB → localStorage → DOM priority)
3. **Normalizes** to standard conversation schema
4. **Deduplicates** by conversation_id
5. **Merges** with existing `memory/current.json`
6. **Creates snapshot** in `memory/snapshots/`

### Conversation Schema

```python
{
    'conversation_id': 'unique-id',
    'messages': [
        {
            'role': 'user | assistant',
            'content': 'message text',
            'timestamp': 1705414222000,
            'code_context': ['file1.py', 'file2.js']
        }
    ],
    'source': 'claude-ai-web | claude-code-web',
    'created_at': 1705414222000,
    'metadata': {
        'title': 'Conversation title',
        'tags': ['shadowtagai', 'judge-6'],
        'difficulty': 'beginner | intermediate | advanced',
        'quality_score': 0.85,
        'project': 'ShadowTag-v2-fastapi-services',
        'technologies': ['python', 'fastapi', 'gemini']
    }
}
```

## Troubleshooting

### No Data Extracted

**Problem**: Extraction script returns empty results

**Solutions**:
1. Ensure you're logged in to Claude.ai/code.claude.com
2. Navigate to a page with conversation history
3. Try scrolling to load more conversations
4. Check browser console for errors
5. Try running script multiple times (data loads async)

### API Endpoints Not Accessible

**Problem**: Script can't fetch from API

**Solution**: This is expected - the script falls back to localStorage/IndexedDB extraction

### Merge Script Finds No Conversations

**Problem**: `merge_web_extractions.py` reports 0 conversations

**Solutions**:
1. Check extraction JSON files manually
2. Verify JSON structure matches expected format
3. Look for data in different sources (API, IndexedDB, localStorage)
4. Check console output for parsing errors

### Duplicates After Merge

**Problem**: Same conversations appear multiple times

**Solution**: Merge script deduplicates by `conversation_id`. If duplicates persist:
```python
# Manually deduplicate memory/current.json
import json

with open('memory/current.json') as f:
    data = json.load(f)

# Remove duplicates
seen = set()
unique = []
for conv in data['conversations']:
    if conv['conversation_id'] not in seen:
        seen.add(conv['conversation_id'])
        unique.append(conv)

data['conversations'] = unique

with open('memory/current.json', 'w') as f:
    json.dump(data, f, indent=2)
```

## Security & Privacy

### What Gets Extracted

- ✅ Conversation messages
- ✅ Metadata (timestamps, tags)
- ✅ Code context (file references)
- ❌ **NOT extracted**: API keys, passwords, credentials

### Where Data Goes

- Local files only (`extractions/` directory)
- Never uploaded to cloud
- Controlled by you (on your machine)

### Recommended Practices

1. **Review extractions** before merging:
   ```bash
   cat extractions/claude_web_extraction_*.json | jq .
   ```

2. **Filter sensitive data** before merge:
   ```bash
   # Edit extraction JSON to remove sensitive conversations
   ```

3. **Encrypt memory files** (optional):
   ```bash
   # Use git-crypt or similar for memory/ directory
   ```

## Complete Workflow Example

```bash
# ========================================
# STEP 1: Extract from ALL platforms
# ========================================

# Local platforms (0xSero)
cd erik-hancock-llm-memory
python scripts/extract_and_commit.py

# Web platforms (browser console)
# Navigate to https://claude.ai
# Run: scripts/extract_claude_web.js
# Download: claude_web_extraction_claude-ai-web_<timestamp>.json

# Navigate to https://code.claude.com
# Run: scripts/extract_claude_web.js
# Download: claude_web_extraction_claude-code-web_<timestamp>.json

# ========================================
# STEP 2: Organize extractions
# ========================================

mv ~/Downloads/claude_web_extraction_*.json extractions/

# ========================================
# STEP 3: Merge all sources
# ========================================

python scripts/merge_web_extractions.py

# Output:
# 🔍 Scanning for web extraction files...
#    Found 2 extraction files
#    ✓ Loaded claude_web_extraction_claude-ai-web_1705414222000.json
#    ✓ Loaded claude_web_extraction_claude-code-web_1705414230000.json
#
# 📋 Parsing web conversations...
#    Processing claude_web_extraction_claude-ai-web_1705414222000.json (claude-ai-web)...
#       ✓ API: 150 conversations
#       ✓ IndexedDB: 50 conversations
#       ✓ localStorage: 20 conversations
#    Processing claude_web_extraction_claude-code-web_1705414230000.json (claude-code-web)...
#       ✓ API: 200 conversations
#       ✓ IndexedDB: 75 conversations
#
#    Total unique conversations: 495
#
# 🔀 Merging conversations...
#    Existing: 2121 (from 0xSero)
#    New: 495 (from web)
#    Added: 495
#    Total: 2616
#
# 💾 Saving updated memory...
#    ✓ Saved to memory/current.json
#    ✓ Created snapshot: memory_web_merge_20250116_120000.json
#
# ✅ Merge Complete!
#    Total conversations: 2616
#    New from web: 495

# ========================================
# STEP 4: Generate metadata (optional)
# ========================================

python scripts/extract_and_commit.py
# Generates Gemini metadata for 495 new conversations
# Cost: ~$0.15 (495 conversations × $0.0003)

# ========================================
# STEP 5: Deploy to Claude Code
# ========================================

python scripts/claude_code_memory_local.py
# Installs to ~/.claude-code/memory.md
# Restart Claude Code to load new memory

# ========================================
# STEP 6: Verify
# ========================================

# Check memory file
cat memory/current.json | jq '.conversations | length'
# Output: 2616

# Check sources
cat memory/current.json | jq '.conversations | group_by(.source) | map({source: .[0].source, count: length})'
# Output:
# [
#   {"source": "cursor-composer", "count": 1200},
#   {"source": "claude-code", "count": 800},
#   {"source": "codex", "count": 121},
#   {"source": "claude-ai-web", "count": 200},
#   {"source": "claude-code-web", "count": 295}
# ]
```

## Advanced Usage

### Incremental Updates

Run web extraction periodically to capture new conversations:

```bash
# Weekly cron job
0 0 * * 0 cd ~/erik-hancock-llm-memory && ./scripts/weekly_web_sync.sh
```

```bash
#!/bin/bash
# scripts/weekly_web_sync.sh

echo "🔄 Weekly Web Extraction Sync"
echo "=============================="

# Remind user to run browser script
echo "⚠️  Manual step required:"
echo "   1. Navigate to https://claude.ai"
echo "   2. Run extraction script in browser console"
echo "   3. Navigate to https://code.claude.com"
echo "   4. Run extraction script in browser console"
echo ""
echo "Press Enter when downloads complete..."
read

# Move extractions
mv ~/Downloads/claude_web_extraction_*.json extractions/

# Merge
python scripts/merge_web_extractions.py

# Commit
git add memory/
git commit -m "Weekly web extraction sync: $(date +%Y-%m-%d)"
git push

echo "✅ Sync complete!"
```

### Filtering Conversations

```python
# Filter by date range
import json
from datetime import datetime, timedelta

with open('memory/current.json') as f:
    data = json.load(f)

# Only keep conversations from last 30 days
cutoff = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)

filtered = [
    conv for conv in data['conversations']
    if conv['created_at'] >= cutoff
]

data['conversations'] = filtered

with open('memory/current_recent.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### Custom Extraction Logic

Modify `extract_claude_web.js` for platform-specific needs:

```javascript
// Add custom selectors for new UI elements
const customSelectors = [
    '[data-your-custom-attribute]',
    '.your-custom-class'
];

// Add custom API endpoints
const customEndpoints = [
    '/your-api/endpoint'
];

// Add custom data processing
function processCustomData(data) {
    // Your logic here
    return processed;
}
```

## Cost Analysis

### Extraction Costs

- **Browser script**: $0 (runs locally)
- **Merge script**: $0 (runs locally)

### Metadata Generation Costs

- **Gemini Flash 2.0**: $0.075 per 1M input tokens
- **Average cost per conversation**: ~$0.0003
- **1,000 new web conversations**: ~$0.30

### Total Cost Example

```
0xSero local extraction:     $0.45 (2,121 conversations)
Web extraction (claude.ai):  $0.15 (500 conversations)
Web extraction (code):       $0.15 (500 conversations)
────────────────────────────────────────────────────
TOTAL:                       $0.75 (3,121 conversations)

ROI: 2,526× ($7,200 annual value / $2.85 annual cost)
```

## FAQ

**Q: Do I need to run this every time I use Claude?**
A: No. Run periodically (weekly/monthly) to capture new conversations.

**Q: Can I automate the browser extraction?**
A: Partially. The browser script can run automatically, but you need to trigger it manually (can't auto-inject into Claude pages).

**Q: What if Anthropic changes their data structure?**
A: The extraction script tries multiple sources/formats. Update selectors/parsers as needed.

**Q: Is this against Claude's Terms of Service?**
A: You're extracting YOUR OWN data from YOUR browser. This is generally allowed, but review terms if concerned.

**Q: Can I extract other users' conversations?**
A: No. The script only accesses data visible in YOUR logged-in session.

## Support

Issues or questions:
1. Check console output for errors
2. Review extraction JSON files manually
3. Check `erik-hancock-llm-memory/README.md`
4. File issue at: https://github.com/ehanc69/ShadowTag-v2-fastapi-services/issues

## License

Proprietary - ShadowTagAi Corp.
