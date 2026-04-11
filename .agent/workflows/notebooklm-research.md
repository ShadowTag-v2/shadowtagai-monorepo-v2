# /notebooklm-research — Zero-Token Deep Research

// turbo-all

Use this workflow to offload document analysis to NotebookLM, consuming zero context window tokens for the heavy lifting.

## Prerequisites
- `notebooklm-py` installed (`pip install "notebooklm-py[browser]"`)
- Authenticated (`notebooklm login`)
- PATH includes `/Users/pikeymickey/Library/Python/3.13/bin`

## Workflow

### Step 1: Verify Authentication
```bash
export PATH="/Users/pikeymickey/Library/Python/3.13/bin:$PATH"
notebooklm status
```

### Step 2: Create Research Notebook
```bash
notebooklm create "Research: [TOPIC] — $(date +%Y-%m-%d)"
```

### Step 3: Add Sources
Add URLs, files, or YouTube videos:
```bash
# URLs
notebooklm source add "https://example.com/paper.pdf"

# Local files
notebooklm source add ./document.pdf

# YouTube
notebooklm source add "https://youtube.com/watch?v=..."

# Google Drive
notebooklm source add-drive "https://drive.google.com/file/d/..."

# Web research (auto-discovers related sources)
notebooklm source add-research "[search query]"
```

### Step 4: Wait for Research Sources (Optional)
If you used `add-research`, wait for discovery:
```bash
notebooklm research status
notebooklm research wait
```

### Step 5: Query for Insights
Ask focused questions — Gemini synthesizes across ALL sources:
```bash
notebooklm ask "What are the key findings across all sources?"
notebooklm ask "What practical implications exist for [use case]?"
notebooklm ask "What contradictions or gaps exist in the research?"
notebooklm ask "Summarize the technical architecture described"
```

### Step 6: Generate Artifacts
```bash
# Audio deep-dive (podcast)
notebooklm generate audio "deep dive focusing on key insights"

# Slide deck
notebooklm generate slide-deck

# Quiz for knowledge verification
notebooklm generate quiz "10 questions covering main concepts"

# Report
notebooklm generate report

# Mind map
notebooklm generate mind-map

# Flashcards
notebooklm generate flashcards
```

### Step 7: Wait for & Download Results
```bash
# Wait for artifact generation
notebooklm artifact wait

# Download artifacts
mkdir -p ./research-output
notebooklm download report -o ./research-output/
notebooklm download audio -o ./research-output/
notebooklm download slide-deck -o ./research-output/
notebooklm download quiz -o ./research-output/
```

### Step 8: Integrate Results
Read the downloaded artifacts and incorporate findings into the current task.

## Notes
- Each query costs zero additional context tokens — Gemini handles synthesis
- Notebooks persist — reusable across sessions
- Sources are pre-indexed — subsequent queries are instant
- Use `notebooklm source guide [SOURCE_ID]` for per-source summaries
- Use `notebooklm summary` for full notebook AI summary
