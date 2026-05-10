# Output Styles

> Adapt Claude Code for uses beyond software engineering

Output styles allow you to use Claude Code as any type of agent while keeping its core capabilities, such as running local scripts, reading/writing files, and tracking TODOs.

## What are Output Styles?

Output styles directly modify Claude Code's system prompt to customize:

- How Claude responds and communicates
- The level of explanation and educational content
- Whether Claude asks you to contribute code yourself
- The overall tone and approach to tasks

## Built-in Output Styles

This project includes three built-in output styles:

### 1. Default

**Standard software engineering assistance with efficient, concise output**

The Default style is optimized for efficient software engineering:

- Concise, focused responses
- Proactive testing and verification
- Security-aware implementation
- Minimal explanation, maximum efficiency

Use when: You want to get things done quickly and efficiently.

### 2. Explanatory

**Educational mode with insights about implementation choices and codebase patterns**

The Explanatory style helps you learn while coding:

- Provides educational "💡 Insight" sections
- Explains design decisions and trade-offs
- Highlights patterns and best practices
- Teaches the "why" behind implementation choices

Use when: You want to understand the codebase and learn best practices.

### 3. Learning

**Collaborative learn-by-doing mode where you implement strategic pieces of code yourself**

The Learning style makes coding interactive:

- Asks you to implement key pieces with `TODO(human)` markers
- Provides scaffolding and clear instructions
- Explains concepts before asking you to code
- Offers progressive hints when you need help

Use when: You want hands-on practice and active learning.

## Using Output Styles

### Via Slash Command

Access the output style menu:

```bash
/output-style
```

Switch to a specific style:

```bash
/output-style explanatory
/output-style learning
/output-style default
```

Create a new custom style:

```bash
/output-style:new I want an output style that responds like a pirate
```

### Via Utility Script

List available styles:

```bash
node output-style-loader.js list
```

Set the active style:

```bash
node output-style-loader.js set explanatory
```

Get the content of a specific style:

```bash
node output-style-loader.js get learning
```

Load the active style content:

```bash
node output-style-loader.js active
```

### Programmatically (Node.js)

```javascript
const { loadOutputStyle, setActiveOutputStyle } = require("./output-style-loader");

// Load a specific output style
const systemPrompt = await loadOutputStyle("explanatory");

// Set the active style for this project
await setActiveOutputStyle("learning");

// Load whatever style is currently active
const activePrompt = await loadActiveOutputStyle();
```

## Creating Custom Output Styles

### File Structure

Output styles are markdown files with YAML frontmatter:

```markdown
---
name: My Custom Style
description: A brief description for users
---

# Custom Style Instructions

You are an interactive CLI tool that helps users with software engineering tasks.

[Your custom instructions here...]

## Tone and Style

[Define communication style...]

## Task Approach

[Define how to approach tasks...]
```

### Storage Locations

**Project-level** (applies only to this project):

```
.claude/output-styles/my-style.md
```

**User-level** (available across all projects):

```
~/.claude/output-styles/my-style.md
```

Project-level styles override user-level styles with the same name.

### Creating a New Style

1. **Via command** (recommended):

   ```bash
   /output-style:new [your description of desired behavior]
   ```

2. **Manually**:
   - Create a `.md` file in `.claude/output-styles/` or `~/.claude/output-styles/`
   - Follow the format shown above
   - Activate it with `/output-style [name]`

## How Output Styles Work

### System Prompt Modification

Output styles work by completely replacing the software engineering-specific parts of Claude Code's default system prompt with custom instructions.

**What gets replaced:**

- Task approach and methodology
- Communication style and tone
- Code generation preferences
- Testing and verification steps

**What stays the same:**

- Available tools (Read, Write, Edit, Bash, etc.)
- Core capabilities (file operations, git, etc.)
- Safety and security guidelines
- Tool usage policies

### Settings Storage

When you activate an output style, the selection is saved to:

```
.claude/settings.local.json
```

Example:

```json
{
  "outputStyle": "explanatory"
}
```

This setting applies to all new conversations in this project.

### Conversation Scope

**Important:** Output styles apply to NEW conversations only.

- The current conversation continues with its existing style
- Start a fresh session to see the new style in action
- Each session loads the output style once at startup

## Comparisons to Related Features

### Output Styles vs. CLAUDE.md

| Feature                | Output Styles          | CLAUDE.md                   |
| ---------------------- | ---------------------- | --------------------------- |
| Modifies system prompt | ✅ Yes, replaces parts | ❌ No                       |
| When loaded            | At session start       | With every message          |
| Content location       | Separate files         | Single file in project root |
| Best for               | Changing behavior/tone | Adding project context      |

### Output Styles vs. `--append-system-prompt`

| Feature                  | Output Styles       | --append-system-prompt |
| ------------------------ | ------------------- | ---------------------- |
| Replaces prompt sections | ✅ Yes              | ❌ No, only appends    |
| File-based               | ✅ Yes              | ❌ No, CLI flag        |
| Reusable                 | ✅ Yes              | ❌ Per-invocation      |
| Switchable               | ✅ Yes, via command | ❌ Must restart        |

### Output Styles vs. Agents

| Feature           | Output Styles           | Agents                     |
| ----------------- | ----------------------- | -------------------------- |
| Affects main loop | ✅ Yes                  | ❌ No, separate subprocess |
| Tool access       | 🔄 Same as default      | 🎯 Can be restricted       |
| Model selection   | 🔄 Same as default      | 🎯 Can be customized       |
| Use case          | Change overall behavior | Task-specific execution    |

### Output Styles vs. Custom Slash Commands

| Feature     | Output Styles             | Slash Commands           |
| ----------- | ------------------------- | ------------------------ |
| Think of as | "Stored system prompts"   | "Stored prompts"         |
| Applies to  | Entire session            | Single interaction       |
| Persistence | ✅ Saved in settings      | ❌ One-time execution    |
| Scope       | Changes Claude's behavior | Executes a specific task |

## Examples

### Example 1: Educational Coding

```bash
# Switch to explanatory mode
/output-style explanatory

# Now ask questions - you'll get detailed explanations
"How does the authentication system work?"
"Why did you choose this pattern?"
```

### Example 2: Learn By Doing

```bash
# Switch to learning mode
/output-style learning

# Request a feature - Claude will leave strategic parts for you
"Add input validation to the user registration form"

# Claude creates the structure and adds TODO(human) markers:
# TODO(human): Implement email validation logic
# Hint: Check for @ symbol and valid domain format
```

### Example 3: Efficient Coding

```bash
# Switch to default mode for speed
/output-style default

# Request a feature - Claude implements it quickly
"Add error logging to all API endpoints"
```

### Example 4: Custom Style

```bash
# Create a style that speaks like a mentor
/output-style:new I want an output style that acts as a senior engineering mentor, asking thoughtful questions and providing wisdom

# Then refine the generated file
# Edit .claude/output-styles/[name].md
```

## Best Practices

### Choosing a Style

- **Default**: Use for production work, bug fixes, and routine tasks
- **Explanatory**: Use when learning a new codebase or concept
- **Learning**: Use when you want to practice coding skills
- **Custom**: Use for specialized workflows or team preferences

### Creating Custom Styles

1. **Start simple**: Begin with small modifications to existing styles
2. **Be specific**: Clearly define the desired behavior and tone
3. **Test thoroughly**: Try the style with various tasks
4. **Iterate**: Refine based on actual usage
5. **Document**: Add clear descriptions so others understand the purpose

### Team Usage

For teams, consider:

- Creating project-level styles for consistent team behavior
- Documenting available styles in your project README
- Using style names that clearly indicate their purpose
- Sharing custom styles via `.claude/output-styles/` in git

## Troubleshooting

### Style not taking effect?

Output styles only apply to NEW sessions. Start a fresh conversation to see changes.

### Style not found?

Check:

1. File exists in `.claude/output-styles/` or `~/.claude/output-styles/`
2. File has `.md` extension
3. File has valid YAML frontmatter
4. Name matches (case-insensitive)

### Want to reset to default?

```bash
/output-style default
```

Or delete the `outputStyle` field from `.claude/settings.local.json`.

## Advanced Usage

### Programmatic Integration

Use output styles in your own applications built with Claude Agent SDK:

```javascript
const { ClaudeAgent } = require("@anthropic-ai/claude-agent-sdk");
const { loadActiveOutputStyle } = require("./output-style-loader");

// Load the active output style
const customSystemPrompt = await loadActiveOutputStyle();

// Use it with the agent
const agent = new ClaudeAgent({
  systemPrompt: customSystemPrompt,
  // ... other options
});

const response = await agent.query("Help me refactor this code");
```

### Dynamic Style Switching

```javascript
// Let users pick their style
const { setActiveOutputStyle, listOutputStyles } = require("./output-style-loader");

const styles = await listOutputStyles();
console.log(
  "Available styles:",
  styles.map((s) => s.name),
);

// User selects "learning"
await setActiveOutputStyle("learning");

// Start new session with selected style
// (requires restarting the agent)
```

## Related Features

- [Slash Commands](/.claude/commands/) - Custom commands for specific tasks
- [Agents](/docs/agents.md) - Specialized subagents for specific purposes
- [Hooks](/docs/hooks.md) - Automatic actions on events
- [CLAUDE.md](/.claude/CLAUDE.md) - Project-specific context (if exists)

## Further Reading

- [Claude Agent SDK Documentation](https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk)
- [System Prompt Best Practices](https://docs.anthropic.com/claude/docs/system-prompts)
- [Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
