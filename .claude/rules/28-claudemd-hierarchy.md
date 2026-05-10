# Rule 28: CLAUDE.md 4-Location Hierarchy & Layered Instructions
# Source: claudemd.ts:1-26 (exact loading order confirmed via actual source code)

## Instruction Loading Hierarchy (Source-Verified)
Claude Code loads instructions from **FOUR locations**, in this exact order:

```
1. /etc/claude-code/CLAUDE.md  → "Managed" (global, enterprise-managed)
2. ~/.claude/CLAUDE.md         → "User"    (user-level, private)
3. ./CLAUDE.md + .claude/CLAUDE.md + .claude/rules/*.md
                               → "Project" (project-level, checked in)
4. CLAUDE.local.md             → "Local"   (private, gitignored)
```

### Priority Rules (claudemd.ts:9)
- Files are loaded in **reverse order of priority** — latest files = highest priority
- The model pays MORE attention to later-loaded files
- `.claude/rules/*.md` files support `paths:` frontmatter for conditional loading
- `@include` directives (@path, @./relative, @~/home) allow cross-file inclusion
- Max include depth: 5 levels (prevents circular references)
- Non-text file extensions are silently skipped in @include

### Layering Strategy
| Level | What to put here | Scope |
|-------|-----------------|-------|
| Managed (`/etc/`) | Org-wide coding standards, compliance rules | All users, all projects |
| User (`~/.claude/`) | Personal shortcuts, style preferences, editor config | All YOUR projects |
| Project (`./` + `.claude/`) | Architecture context, repo conventions, rules | Everyone on this project |
| Local (`CLAUDE.local.md`) | Personal overrides, experiments, draft rules | Only you, gitignored |

### CLAUDE.md Exclusions (claudemd.ts:547-573)
Settings can exclude specific CLAUDE.md paths via `claudeMdExcludes` patterns.
- Supports glob patterns with picomatch
- Resolves symlinks (handles macOS /tmp → /private/tmp)
- Only applies to User, Project, and Local types
- Managed types are NEVER excluded

### Anti-Pattern: Single-Layer Usage
Most developers only use project-level CLAUDE.md. Layering instruction files
across all 4 locations gives you:
- Org-wide policy that can't be overridden per-project
- Personal preferences that travel across repos
- Project context shared with the team
- Private experiments that don't pollute the repo

## Antigravity Implementation
- Global layer: `~/.claude/CLAUDE.md` (already exists, 80 lines)
- Project layer: `.claude/CLAUDE.md` + `.claude/rules/*.md` (27 modular rules)
- Local layer: Create `CLAUDE.local.md` (gitignored) for personal overrides
- `InstructionsLoaded` hook validates brevity and syncs CLAUDE.md → AGENTS.md

## Antigravity Adaptation for Gemini
Antigravity uses a parallel layering system:
- User rules: `<user_rules>` block in system prompt (equivalent to `~/.claude/CLAUDE.md`)
- Skill instructions: `SKILL.md` files (equivalent to `.claude/rules/*.md`)
- Knowledge items: KI artifacts (equivalent to project memories)
- Session context: Conversation logs and checkpoints (equivalent to Local memory)
