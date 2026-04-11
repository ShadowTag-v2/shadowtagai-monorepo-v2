# Rule 50: Obsidian Vault Protocol

## Purpose
Defines how the agent operates within an Obsidian vault context — file conventions, linking strategies, and knowledge graph maintenance.

## Vault Awareness

When `OBSIDIAN_VAULT_ROOT` is set or the user references their vault:
1. **All markdown outputs** that persist knowledge → save to vault
2. **Use wikilinks** — `[[Note]]` not `[Note](Note.md)`
3. **Include frontmatter** — every note MUST have YAML frontmatter with `title`, `date`, `tags`
4. **Respect folder structure** — `00-Inbox/`, `10-Daily/`, `20-Research/`, etc.
5. **Never touch `.obsidian/`** — plugin configs are user-managed

## Linking Rules

- Create `[[target]]` links freely — Obsidian handles broken links gracefully
- Use `[[Note|alias]]` when the note title is technical or long
- Use `#tags` from the approved taxonomy (see obsidian-vault-operator skill)
- Cross-reference research outputs: `[[20-Research/topic]]`

## Daily Note Integration

- Daily notes: `10-Daily/YYYY-MM-DD.md`
- Append session summaries to the current daily note
- Link to artifacts, decisions, and research notes

## Knowledge Graph Hygiene

- Prefer links over tags for concept relationships
- One note per concept (atomic notes)
- Use MOC (Map of Content) notes for topic aggregation
- Archive stale notes to `70-Archive/`
