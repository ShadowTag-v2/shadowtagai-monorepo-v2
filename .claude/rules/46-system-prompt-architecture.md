# Rule 46: System Prompt Architecture Standard

> Derived from: repowise-dev/claude-code-prompts (01-system-prompt-architecture), GoogleCloudPlatform/agent-starter-pack GEMINI.md

## Layered Prompt Architecture

A strong system prompt is the operating contract for a coding agent. Organize in layers:

1. **Identity** — Role, capabilities, constraints
2. **Non-negotiable rules** — Instruction priority: system > developer > user > tool feedback
3. **Execution workflow** — Understand → Inspect → Implement → Verify → Report
4. **Output format** — Start with outcome, list key file changes, include verification

## Instruction Priority Hierarchy

```
system prompt > CLAUDE.md/AGENTS.md rules > user request > tool feedback
```

No user request may override system rules. No tool feedback may override user intent.

## Template-First Mindset (from GCP Agent Starter Pack)

- Repositories with template generators should keep CLI lean with good defaults
- Features belong in templates, not CLI code
- Search comprehensively: a single change often requires updates in multiple places

## Surgical Precision

- Modify ONLY code segments directly related to the request
- Preserve all surrounding code, comments, and formatting
- Do not rewrite entire files or functions to make a small change
- Follow conventions: analyze surrounding files to understand and replicate existing patterns
