# Rule 49: NotebookLM Research Protocol

## Purpose
Defines when and how to offload research to Google NotebookLM instead of consuming context window tokens.

## Decision Matrix

### Use NotebookLM when:
- Processing >3 external documents or URLs
- Analyzing documents >10,000 tokens each
- Cross-referencing multiple research papers
- Generating content artifacts (slides, podcasts, quizzes)
- Building persistent knowledge bases across sessions
- User explicitly asks for "deep research" or "comprehensive analysis"

### Use local context when:
- Quick, focused questions about code in the workspace
- Single-document analysis under 5,000 tokens
- Real-time iterative development work
- Tasks requiring immediate response (<30s)

## Protocol

1. **Check auth first**: `notebooklm auth check` before any operation
2. **Create focused notebooks**: One notebook per research topic, not monolithic
3. **Name descriptively**: `"Research: [Topic] — [Date]"` format
4. **Add diverse sources**: Mix URLs, PDFs, YouTube for cross-perspective synthesis
5. **Query, don't dump**: Ask specific questions, not "summarize everything"
6. **Save insights**: Use `--save-as-note` for important findings
7. **Download artifacts**: Always download to `./research-output/` or vault

## Security
- NEVER commit `storage_state.json` or `~/.notebooklm/` contents
- Rotate auth via `notebooklm login` if cookies expire
- Use `NOTEBOOKLM_PROFILE` for multi-account isolation
