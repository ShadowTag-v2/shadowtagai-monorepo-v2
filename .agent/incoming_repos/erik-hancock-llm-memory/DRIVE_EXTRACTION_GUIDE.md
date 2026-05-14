# Google Drive Knowledge Extraction Guide

Complete guide for extracting and indexing content from **Google Drive** including documents, ebooks (PDF/EPUB/MOBI), zip archives, and code files.

## Quick Start

### 1. Install Dependencies

```bash
cd erik-hancock-llm-memory
pip install -r requirements-drive.txt
```

### 2. Setup Google Drive API

```bash
# Enable API
1. Go to: https://console.cloud.google.com/apis/library/drive.googleapis.com
2. Click "Enable"

# Create OAuth Credentials
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Desktop app"
4. Name: "LLM Memory Drive Extractor"
5. Click "Create"
6. Download JSON
7. Save as: scripts/credentials.json
```

### 3. Run Extraction

```bash
# Set API key for embeddings (optional)
export GOOGLE_API_KEY="your-gemini-api-key"

# Run extraction
python scripts/extract_google_drive.py

# Browser will open for authentication
# Grant access to your Google Drive
# Extraction will begin automatically
```

### 4. Merge with Memory System

```bash
# Merge Drive knowledge with conversations
python scripts/merge_drive_knowledge.py

# Deploy to Claude Code
python scripts/claude_code_memory_local.py
```

## Supported File Types

### ✅ Documents
- **PDF**: Text extraction via PyPDF2
- **DOCX**: Microsoft Word documents
- **TXT**: Plain text files
- **MD**: Markdown files

### ✅ Ebooks
- **PDF**: Books, papers, manuals
- **EPUB**: Digital books (full text extraction)
- **MOBI**: Kindle books

### ✅ Archives
- **ZIP**: Extracts all files inside
  - Processes PDFs, EPUB, TXT, MD, code files within ZIP
  - Max 50 files per archive (configurable)
- **TAR.GZ**: Compressed archives

### ✅ Google Workspace
- **Google Docs**: Exported as plain text
- **Google Sheets**: Exported as CSV
- **Google Slides**: Exported as plain text

### ✅ Code Files
- **Python**: .py files
- **JavaScript**: .js files
- **TypeScript**: .ts files
- **JSON**: .json files
- **YAML**: .yaml, .yml files

## How It Works

### Extraction Process

```
┌─────────────────────────────────────────┐
│  1. AUTHENTICATE WITH GOOGLE DRIVE      │
│     OAuth 2.0 flow (one-time setup)     │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  2. LIST ALL FILES                      │
│     Scans entire Drive (max 1000 files) │
│     Filters to supported types          │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  3. DOWNLOAD FILES                      │
│     Binary content for each file        │
│     Google Workspace files exported     │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  4. EXTRACT TEXT                        │
│     PDF: PyPDF2 page-by-page           │
│     EPUB: Extract HTML + parse         │
│     DOCX: Extract paragraphs           │
│     ZIP: Recursive extraction          │
│     Code: UTF-8 decode                 │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  5. GENERATE EMBEDDINGS (optional)      │
│     Gemini embedding-001                │
│     For semantic search                 │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  6. SAVE TO drive_knowledge/            │
│     documents/   - Extracted text       │
│     metadata/    - File info JSON       │
│     embeddings/  - Gemini vectors       │
│     index.json   - Master index         │
└─────────────────────────────────────────┘
```

### Merge Process

```
┌─────────────────────────────────────────┐
│  1. LOAD DRIVE KNOWLEDGE                │
│     drive_knowledge/index.json          │
│     All extracted documents             │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  2. CONVERT TO KNOWLEDGE ENTRIES        │
│     Normalize to memory schema          │
│     Extract tags from content           │
│     Add metadata (owners, links, etc)   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  3. LOAD EXISTING MEMORY                │
│     memory/current.json                 │
│     Conversations + existing knowledge  │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  4. MERGE & DEDUPLICATE                 │
│     Combine by unique ID                │
│     Preserve existing entries           │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  5. SAVE UPDATED MEMORY                 │
│     memory/current.json                 │
│     memory/snapshots/ (versioned)       │
└─────────────────────────────────────────┘
```

## Output Structure

### drive_knowledge/

```
drive_knowledge/
├── documents/
│   ├── a1b2c3d4e5f6.txt          # Extracted text (hashed filename)
│   ├── f6e5d4c3b2a1.txt
│   └── ...
├── metadata/
│   ├── a1b2c3d4e5f6.json         # File metadata
│   │   {
│   │     "id": "drive-file-id",
│   │     "name": "My Book.pdf",
│   │     "mime_type": "application/pdf",
│   │     "size": 1024000,
│   │     "created": "2024-01-01T00:00:00Z",
│   │     "modified": "2024-06-01T00:00:00Z",
│   │     "owners": [{"displayName": "ShadowTagAi Team"}],
│   │     "web_link": "https://drive.google.com/...",
│   │     "hash": "a1b2c3d4e5f6",
│   │     "text_length": 50000,
│   │     "word_count": 8500
│   │   }
│   └── ...
├── embeddings/
│   ├── a1b2c3d4e5f6.json         # Gemini embeddings
│   │   {
│   │     "embedding": [0.123, -0.456, ...]  # 768-dim vector
│   │   }
│   └── ...
└── index.json
    {
      "extracted_at": "2025-01-16T12:00:00Z",
      "total_files": 250,
      "processed": 200,
      "skipped": 50,
      "files": [
        {
          "hash": "a1b2c3d4e5f6",
          "name": "My Book.pdf",
          "type": "pdf",
          "size": 1024000,
          "word_count": 8500,
          "has_embedding": true
        },
        ...
      ]
    }
```

### memory/current.json (after merge)

```json
{
  "version": "1.0.0",
  "last_updated": "2025-01-16T12:00:00Z",
  "conversations": [ ... ],
  "knowledge": [
    {
      "id": "drive_a1b2c3d4e5f6",
      "source": "google-drive",
      "type": "pdf",
      "title": "My Book.pdf",
      "content": "Full extracted text...",
      "created_at": "2024-01-01T00:00:00Z",
      "modified_at": "2024-06-01T00:00:00Z",
      "metadata": {
        "drive_id": "1abc...",
        "mime_type": "application/pdf",
        "size": 1024000,
        "owners": [{"displayName": "ShadowTagAi Team"}],
        "web_link": "https://drive.google.com/...",
        "word_count": 8500,
        "text_length": 50000
      },
      "embedding": [0.123, -0.456, ...],
      "tags": ["pdf", "ebook", "research"],
      "indexed_at": "2025-01-16T12:00:00Z"
    }
  ],
  "shadowtagai_architecture": { ... },
  "llm_allocation": { ... },
  "jr_framework": { ... }
}
```

## Special Features

### ZIP Archive Extraction

When a ZIP file is encountered, the script:

1. Opens the archive
2. Scans all files inside (max 50)
3. Processes supported types:
   - `*.pdf` → PDF text extraction
   - `*.epub` → EPUB text extraction
   - `*.txt, *.md, *.py, *.js` → UTF-8 decode
4. Combines all extracted text with file separators

**Example ZIP output:**

```
FILE: docs/chapter1.md

# Chapter 1: Introduction
...

---FILE SEPARATOR---

FILE: code/example.py

def hello():
    print("Hello world")
...

---FILE SEPARATOR---

FILE: book.pdf

Page 1 text...
Page 2 text...
```

### Ebook Processing

**EPUB Extraction:**
- Parses EPUB structure
- Extracts all chapters/sections
- Strips HTML tags
- Preserves reading order
- Handles embedded images (skipped)

**PDF Extraction:**
- Page-by-page text extraction
- Preserves paragraph breaks
- Handles multi-column layouts
- Skips images/graphics

**MOBI Extraction:**
- Converts to text format
- Extracts all content
- Handles Kindle-specific formatting

### Embedding Generation

If `GOOGLE_API_KEY` is set, generates 768-dimensional Gemini embeddings for:

- **Semantic search**: Find similar documents
- **Context-aware retrieval**: Relevant knowledge for queries
- **Clustering**: Group related content

**Cost**: ~$0.00015 per document (first 20k chars)

## Cost Analysis

### Extraction Costs

```
Google Drive API:          $0 (free tier: unlimited)
Document processing:       $0 (runs locally)
```

### Embedding Costs

```
Gemini embedding-001:      $0.00001 per 1000 chars
Average document:          10,000 chars = $0.0001
1,000 documents:           $0.10
```

### Total Cost Example

```
Extract 500 Drive files:   $0 (API calls free)
Generate embeddings:       $50 (500 × $0.0001)
────────────────────────────────────────
TOTAL:                     $50 (one-time)

Maintenance:               $0 (no recurring cost)
ROI:                       Unlimited (knowledge always available)
```

## Advanced Usage

### Filter by Folder

```python
# Modify list_all_files() to filter by folder
results = service.files().list(
    q="'FOLDER_ID' in parents",  # Only files in this folder
    pageSize=100,
    fields="nextPageToken, files(...)"
).execute()
```

### Custom File Types

```python
# Add support for more types in SUPPORTED_TYPES dict
SUPPORTED_TYPES = {
    'application/x-latex': 'tex',
    'text/xml': 'xml',
    'application/json': 'json',
    # ... add more
}

# Add extraction function
def extract_text_from_latex(content: bytes) -> str:
    # Your LaTeX extraction logic
    return text
```

### Incremental Updates

```bash
#!/bin/bash
# scripts/weekly_drive_sync.sh

# Weekly Google Drive sync
echo "🔄 Weekly Drive Sync"

# Extract new/modified files only
python scripts/extract_google_drive_incremental.py

# Merge
python scripts/merge_drive_knowledge.py

# Commit
git add memory/ drive_knowledge/
git commit -m "Weekly Drive sync: $(date +%Y-%m-%d)"
git push
```

### Search with Embeddings

```python
# Search Drive knowledge by semantic similarity
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load memory
with open('memory/current.json') as f:
    memory = json.load(f)

# Your query embedding (generate with Gemini)
query_embedding = [0.123, -0.456, ...]  # 768-dim vector

# Find similar documents
similarities = []
for entry in memory['knowledge']:
    if entry.get('embedding'):
        sim = cosine_similarity(
            [query_embedding],
            [entry['embedding']]
        )[0][0]
        similarities.append((entry, sim))

# Sort by similarity
results = sorted(similarities, key=lambda x: x[1], reverse=True)

# Top 10 results
for entry, score in results[:10]:
    print(f"{score:.3f} - {entry['title']}")
```

## Troubleshooting

### Authentication Failed

**Problem**: Browser auth fails or credentials.json not found

**Solution**:
1. Verify credentials.json is in `scripts/` directory
2. Check OAuth consent screen is configured
3. Try deleting `scripts/token.json` and re-authenticating
4. Ensure Desktop app type (not Web application)

### Download Quota Exceeded

**Problem**: "User rate limit exceeded" error

**Solution**:
1. Google Drive API has quotas (10,000 requests/100 seconds)
2. Script includes rate limiting, but large extractions may hit limit
3. Wait 60 seconds and resume
4. Process fewer files per run

### PDF Extraction Returns Empty

**Problem**: PDF file downloaded but no text extracted

**Solution**:
1. PDF might be image-based (scanned document)
2. Use OCR: `pip install pytesseract` + modify extraction
3. Or skip: Some PDFs are intentionally text-free (images only)

### ZIP Files Not Processing

**Problem**: ZIP downloaded but contents not extracted

**Solution**:
1. Check ZIP isn't password-protected
2. Verify file types inside ZIP are supported
3. Check max_files limit (default 50 per ZIP)
4. Look for errors in console output

### Out of Memory

**Problem**: Script crashes with MemoryError

**Solution**:
1. Process fewer files per run
2. Skip large files: Add size filter
```python
if file.get('size', 0) > 50_000_000:  # Skip files > 50MB
    continue
```
3. Disable embeddings (uses less memory)

## Security & Privacy

### What Gets Accessed

- ✅ Files you own in Google Drive
- ✅ Files shared with you (read access)
- ❌ **NOT accessed**: Other users' private files

### Data Storage

- **Local only**: All extracted content stays on your machine
- **No cloud upload**: Nothing sent to external servers (except Gemini for embeddings)
- **OAuth token**: Stored locally in `scripts/token.json`

### Best Practices

1. **Review before extraction**:
   ```bash
   # List files first without downloading
   python scripts/list_drive_files.py  # Create this if needed
   ```

2. **Filter sensitive files**:
   ```python
   # Skip folders with sensitive data
   SKIP_FOLDERS = ['Private', 'Confidential', 'Secrets']

   if any(skip in file['name'] for skip in SKIP_FOLDERS):
       continue
   ```

3. **Encrypt extracted data**:
   ```bash
   # Use git-crypt for drive_knowledge/
   cd erik-hancock-llm-memory
   git-crypt init
   git-crypt add-gpg-user your-key-id
   echo "drive_knowledge/* filter=git-crypt diff=git-crypt" >> .gitattributes
   ```

## Complete Workflow Example

```bash
# ========================================
# STEP 1: Setup (one-time)
# ========================================

cd erik-hancock-llm-memory

# Install dependencies
pip install -r requirements-drive.txt

# Setup Google Drive API credentials
# (Follow "Setup Google Drive API" section above)

# Set Gemini API key for embeddings
export GOOGLE_API_KEY="your-api-key"

# ========================================
# STEP 2: Extract from Google Drive
# ========================================

python scripts/extract_google_drive.py

# Output:
# 🔐 Authenticating with Google Drive...
#    ✓ Authenticated successfully
#
# 📂 Scanning Google Drive (max 1000 files)...
#    ✓ Found 342 total files
#
# 📊 File type breakdown:
#    pdf: 85
#    docx: 45
#    epub: 20
#    txt: 30
#    zip: 15
#    py: 50
#    ...
#    Total supported: 250 / 342
#
# ⚡ Process 250 files? (y/n): y
#
# 📝 Processing 250 files...
#    [1/250] My Book.pdf
#       Type: application/pdf
#       ⬇ Downloading...
#       📄 Extracting text...
#       🧠 Generating embedding...
#       ✓ Processed (45000 chars, 7500 words)
#    ...
#
# ✅ Processing Complete!
#    Processed: 245
#    Skipped: 5
#    Total words: 850,000
#
# 📂 Output: /path/to/drive_knowledge
#    documents/   - 245 text files
#    metadata/    - 245 JSON files
#    embeddings/  - 245 JSON files
#    index.json   - Master index

# ========================================
# STEP 3: Merge with memory system
# ========================================

python scripts/merge_drive_knowledge.py

# Output:
# 📋 Loading Google Drive index...
#    Files extracted: 245
#    Total words: 850,000
#
# 📖 Loading extracted documents...
#    Loaded 245 documents
#
# 🔄 Converting to knowledge entries...
#    Created 245 knowledge entries
#
# 📖 Loading existing memory...
#    Current conversations: 2121
#    Current knowledge: 0
#
# 🔀 Merging knowledge entries...
#    Existing: 0
#    New: 245
#    Added: 245
#    Total: 245
#
# 💾 Saving updated memory...
#    ✓ Saved to memory/current.json
#    ✓ Created snapshot: memory_drive_merge_20250116_120000.json
#
# 📊 Knowledge Base Statistics
#    Total knowledge entries: 245
#
#    By source:
#       google-drive: 245
#
#    By type:
#       pdf: 85
#       docx: 45
#       epub: 20
#       txt: 30
#       ...
#
#    Total words: 850,000
#    With embeddings: 245 (100.0%)
#
# ✅ Merge Complete!

# ========================================
# STEP 4: Deploy to Claude Code
# ========================================

python scripts/claude_code_memory_local.py

# Restart Claude Code
# All Drive knowledge now available as context!

# ========================================
# STEP 5: Verify
# ========================================

# Check memory
cat memory/current.json | jq '.knowledge | length'
# Output: 245

# Check by type
cat memory/current.json | jq '.knowledge | group_by(.type) | map({type: .[0].type, count: length})'
# Output:
# [
#   {"type": "pdf", "count": 85},
#   {"type": "docx", "count": 45},
#   {"type": "epub", "count": 20},
#   ...
# ]

# Total knowledge
cat memory/current.json | jq '.knowledge | map(.metadata.word_count) | add'
# Output: 850000
```

## Integration with Memory System

After merging, Drive knowledge is available in Claude Code:

**Example queries that use Drive knowledge:**

1. **"What did I write about SHADOWTAGAI in my docs?"**
   - Searches Drive documents for SHADOWTAGAI references
   - Returns relevant excerpts with file links

2. **"Summarize the ebook I uploaded about AI"**
   - Finds EPUB/PDF ebooks with "AI" tag
   - Provides summary from extracted content

3. **"Show me Python code examples from my Drive"**
   - Searches .py files and code in ZIPs
   - Returns code snippets with context

4. **"What research papers do I have on embeddings?"**
   - Semantic search using Gemini embeddings
   - Finds similar content even without exact keyword match

## FAQ

**Q: How often should I run Drive extraction?**
A: Monthly is sufficient. Run when you add significant new content.

**Q: Can I extract from Team Drives?**
A: Yes! The script scans all drives you have access to.

**Q: What about Google Photos?**
A: Photos are not extracted (images have no text). Use Google Photos API separately if needed.

**Q: Are file permissions preserved?**
A: Metadata includes owner info, but local extraction removes access control.

**Q: Can I search by file owner or date?**
A: Yes! Metadata includes owners, created/modified dates - add search logic as needed.

**Q: What if I delete a file from Drive?**
A: Re-run extraction. The merge script will keep existing entries (won't auto-delete).

## Support

Issues or questions:
1. Check console output for specific errors
2. Review `drive_knowledge/index.json` for extraction results
3. Check Google Drive API quotas/limits
4. File issue at: https://github.com/ehanc69/pnkln-fastapi-services/issues

## License

Proprietary - ShadowTagAi Corp.
