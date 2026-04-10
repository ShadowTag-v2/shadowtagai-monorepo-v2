---
description: Manage and switch between output styles to customize Claude's behavior
argument-hint: [style-name or 'list']
---

# Output Style Management

You are helping the user manage output styles. Output styles customize how Claude responds and behaves.

## Arguments Provided

Arguments: `$ARGUMENTS`

## Available Actions

### 1. List Available Styles (if no arguments or "list")

If the user didn't provide arguments or provided "list", show all available output styles:

1. Read all `.md` files from:
   - `.claude/output-styles/` (project-level)
   - `~/.claude/output-styles/` (user-level, if exists)

2. Parse the frontmatter from each file to get:
   - `name`: The display name
   - `description`: What the style does

3. Display a formatted list:

```
Available Output Styles:

Project Styles (.claude/output-styles/):
  • Default - Standard software engineering assistance with efficient, concise output
  • Explanatory - Educational mode with insights about implementation choices and codebase patterns
  • Learning - Collaborative learn-by-doing mode where you implement strategic pieces of code yourself

User Styles (~/.claude/output-styles/):
  • [Any user-defined styles found]

Usage:
  /output-style [name]     Switch to a specific style
  /output-style list       Show this list
  /output-style:new        Create a new custom output style
```

### 2. Switch to a Style (if style name provided)

If the user provided a style name:

1. Locate the style file (case-insensitive match):
   - First check `.claude/output-styles/[name].md`
   - Then check `~/.claude/output-styles/[name].md`

2. If found:
   - Read the complete markdown file content
   - Extract the instructions from the file (everything after frontmatter)
   - Store the selection in `.claude/settings.local.json`:
     ```json
     {
       "outputStyle": "style-name"
     }
     ```
   - Confirm the switch:
     ```
     ✓ Switched to "[Style Name]" output style

     [Description from frontmatter]

     This style will be applied to future conversations in this project.
     Note: The current conversation will continue with the previous style.
     Start a new session to use the new style.
     ```

3. If not found:
   - Show available styles and suggest correct spelling

### 3. Create New Style

If the command is `/output-style:new [description]`:

1. Ask the user for:
   - Name for the new style
   - Where to save it (user-level or project-level)

2. Create a template file with the provided description:

```markdown
---
name: [User's Style Name]
description: [User's description]
---

# [Style Name] Instructions

You are an interactive CLI tool that helps users with software engineering tasks.

## Custom Behaviors

[Instructions based on user's description]

## Tone and Style

[Customized tone guidance]

## Task Approach

[Customized approach]
```

3. Inform the user they can edit the file directly to refine it

## Error Handling

- If the output styles directory doesn't exist, create it
- If settings.local.json doesn't exist, create it with just the outputStyle field
- Handle file permission errors gracefully
- Validate markdown frontmatter format

## Important Notes

- Output styles modify Claude's system prompt
- Changes apply to NEW conversations only
- The current conversation continues with its existing style
- Project-level styles override user-level styles with the same name
- Styles are stored as markdown files with YAML frontmatter
