# Claude Code Plugins Guide

This document provides detailed information about the Claude Code plugin system integrated into this repository.

## What Are Claude Code Plugins?

Plugins extend Claude Code with custom functionality that can be shared across projects and teams. They can include:

- **Commands**: Custom slash commands (like `/new-endpoint`)
- **Agents**: Specialized AI agents for specific tasks
- **Skills**: Capabilities that Claude can invoke autonomously
- **Hooks**: Event handlers that run automatically
- **MCP Servers**: Integrations with external tools

## Plugin Architecture

### Directory Structure

```
claude-plugins/                      # Local marketplace
├── .claude-plugin/
│   └── marketplace.json            # Marketplace configuration
├── fastapi-dev/                    # Plugin directory
│   ├── .claude-plugin/
│   │   └── plugin.json            # Plugin metadata
│   ├── commands/                   # Slash commands (*.md)
│   ├── agents/                     # Agent definitions (*.md)
│   ├── skills/                     # Agent skills
│   │   └── skill-name/
│   │       └── SKILL.md
│   └── hooks/                      # Event hooks
│       └── hooks.json
└── another-plugin/                 # Additional plugins...
```

### Component Types

#### 1. Commands (Slash Commands)

Commands are markdown files that define custom slash commands. They include:
- Frontmatter with metadata (description)
- Instructions for Claude on how to handle the command
- Context and examples

**Example: `commands/my-command.md`**
```markdown
---
description: Short description shown in /help
---

# Command Title

Detailed instructions for Claude on what to do when this command is invoked.

Ask the user for:
- Required information

Then:
- Steps to execute
- What to create or modify
```

**Usage:** `/my-command`

#### 2. Agents

Agents are specialized AI assistants with specific roles and capabilities. They are markdown files in the `agents/` directory.

**Example: `agents/my-agent.md`**
```markdown
---
description: What this agent does
---

# Agent Name

You are an expert in [domain]. Your role is to [purpose].

## Capabilities
- What you can do
- Your expertise areas

## Guidelines
- How you should approach tasks
- Best practices to follow
```

**Usage:**
```bash
/agents
# Then select "my-agent" from the list
```

#### 3. Skills

Skills are capabilities that Claude can invoke autonomously based on the task context. Unlike commands (user-invoked) or agents (user-selected), skills are model-invoked.

**Example: `skills/my-skill/SKILL.md`**
```markdown
---
description: What this skill helps with
---

# Skill Name

This skill assists with [capability].

## When to Use

Claude will automatically use this skill when:
- Condition 1
- Condition 2

## How to Use

[Instructions for Claude on how to use this skill]
```

**Usage:** Automatic - Claude decides when to use it

#### 4. Hooks

Hooks are event handlers that execute commands in response to events. They are defined in `hooks/hooks.json`.

**Example: `hooks/hooks.json`**
```json
{
  "pre_commit": {
    "description": "Run before git commits",
    "enabled": true,
    "command": "pytest tests/ -q"
  },
  "post_edit": {
    "description": "Run after file edits",
    "enabled": true,
    "command": "npm test",
    "file_pattern": "*.js"
  },
  "user_prompt_submit": {
    "description": "Run before processing user input",
    "enabled": false,
    "command": "echo 'Processing...'"
  }
}
```

Available hook types:
- `pre_commit` - Before creating git commits
- `post_edit` - After editing files
- `user_prompt_submit` - Before processing user prompts

## Plugin Lifecycle

### Installation

Plugins are installed when:
1. User manually installs via `/plugin install`
2. Repository is trusted and plugin is in `autoInstall` list
3. Marketplace has `autoInstall: true` in settings.json

### Activation

Once installed:
- **Commands**: Immediately available via `/command-name`
- **Agents**: Listed in `/agents` menu
- **Skills**: Available for Claude to invoke
- **Hooks**: Active if enabled in hooks.json

### Updates

To update a plugin after changes:
```bash
/plugin uninstall plugin-name@marketplace-name
/plugin install plugin-name@marketplace-name
```

## Creating Custom Plugins

### Step 1: Create Plugin Directory

```bash
mkdir -p claude-plugins/my-plugin/.claude-plugin
mkdir -p claude-plugins/my-plugin/commands
```

### Step 2: Create Plugin Manifest

`claude-plugins/my-plugin/.claude-plugin/plugin.json`:
```json
{
  "name": "my-plugin",
  "description": "What this plugin does",
  "version": "1.0.0",
  "author": {
    "name": "Your Name",
    "url": "https://github.com/yourname"
  },
  "keywords": ["fastapi", "custom"],
  "homepage": "https://github.com/yourname/repo"
}
```

### Step 3: Add Components

Create commands, agents, skills, or hooks as needed (see Component Types above).

### Step 4: Register in Marketplace

Edit `claude-plugins/.claude-plugin/marketplace.json`:
```json
{
  "plugins": [
    {
      "name": "my-plugin",
      "source": "./my-plugin",
      "description": "Brief description"
    }
  ]
}
```

### Step 5: Install and Test

```bash
/plugin install my-plugin@aiyou-fastapi-plugins
```

## Best Practices

### Command Design

1. **Clear Description**: Write concise descriptions for `/help` listing
2. **Ask, Don't Assume**: Prompt user for required information
3. **Provide Context**: Give Claude enough context to complete the task
4. **Include Examples**: Show expected formats and structures
5. **Handle Errors**: Consider edge cases and error scenarios

### Agent Design

1. **Specific Role**: Define a clear, focused purpose
2. **Expertise Domain**: Specify what the agent is expert in
3. **Guidelines**: Provide decision-making frameworks
4. **Constraints**: Set boundaries and limitations

### Skill Design

1. **Autonomous**: Skills should work without user intervention
2. **Contextual**: Clear conditions for when to invoke
3. **Complete**: Include all necessary instructions
4. **Efficient**: Don't duplicate existing capabilities

### Hook Design

1. **Fast**: Hooks should execute quickly
2. **Reliable**: Handle failures gracefully
3. **Informative**: Provide useful feedback
4. **Optional**: Allow users to disable if needed

## Debugging Plugins

### Check Plugin Status

```bash
/plugin
# View installed plugins and their status
```

### Validate Plugin Structure

Ensure:
- `plugin.json` is valid JSON
- `marketplace.json` includes your plugin
- Command files have proper frontmatter
- Skill directories contain `SKILL.md`
- Hook JSON is valid

### Test Incrementally

1. Create minimal plugin first
2. Test each component separately
3. Add complexity gradually
4. Reinstall after each change

### Common Issues

**Command not showing in /help:**
- Check frontmatter has `description:`
- Ensure file is in `commands/` directory
- Verify plugin is installed
- Check file name (should be `*.md`)

**Agent not in /agents list:**
- Verify file is in `agents/` directory
- Check frontmatter syntax
- Ensure plugin is installed

**Skill not being invoked:**
- Skills are autonomous - Claude decides when to use
- Check skill description clarity
- Verify `SKILL.md` is in correct location
- Ensure skill directory name is meaningful

**Hook not running:**
- Check `"enabled": true` in hooks.json
- Verify command is valid and executable
- Check file_pattern if using post_edit

## Advanced Topics

### Multi-Plugin Workflows

Combine plugins for complex workflows:
1. Use command from plugin A
2. Invoke agent from plugin B
3. Let skill from plugin C assist automatically

### Plugin Dependencies

While not formally supported, document dependencies:
- Required Python packages
- Required system tools
- Other plugin requirements

### Team Plugin Distribution

For team use:
1. Commit plugins to repository
2. Configure in `.claude/settings.json`
3. Team members trust repository
4. Plugins auto-install for everyone

### Version Management

Use semantic versioning in `plugin.json`:
- Major: Breaking changes
- Minor: New features, backward compatible
- Patch: Bug fixes

## Security Considerations

### Hook Safety

Hooks execute shell commands - be cautious:
- Validate commands before enabling
- Avoid running untrusted code
- Review hooks from external sources
- Keep hooks disabled by default for destructive operations

### Plugin Sources

Only install plugins from trusted sources:
- Official marketplaces
- Verified team repositories
- Personal plugins you created

### Command Injection

When creating commands that execute shell commands:
- Sanitize user input
- Use safe command construction
- Avoid dynamic command generation
- Quote paths and arguments properly

## Resources

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [Plugin Reference](https://docs.claude.com/en/plugins-reference)
- [Plugin Marketplaces](https://docs.claude.com/en/plugin-marketplaces)
- [Slash Commands](https://docs.claude.com/en/slash-commands)
- [Subagents](https://docs.claude.com/en/sub-agents)
- [Agent Skills](https://docs.claude.com/en/skills)
- [Hooks](https://docs.claude.com/en/hooks)

## Examples from This Repository

### FastAPI Dev Plugin

**Purpose:** Accelerate FastAPI development

**Components:**
- Commands: `/new-endpoint`, `/crud-endpoints`, `/new-model`, `/run-dev`, `/add-middleware`
- Agent: architecture-advisor

**Use Case:** Creating a new API resource
```bash
/crud-endpoints
# Follow prompts to create models and endpoints
```

### FastAPI Testing Plugin

**Purpose:** Comprehensive testing support

**Components:**
- Commands: `/run-tests`, `/gen-tests`, `/validate-api`
- Skill: pytest-helper
- Hooks: pre_commit, post_edit (disabled by default)

**Use Case:** Testing workflow
```bash
/gen-tests       # Generate tests for new endpoint
/run-tests       # Run test suite
/validate-api    # Validate against OpenAPI schema
```

## Contributing to Plugins

To contribute improvements:

1. **Fork and Branch**
   ```bash
   git checkout -b feature/improve-plugin
   ```

2. **Make Changes**
   - Edit plugin files
   - Test thoroughly
   - Document new features

3. **Test Installation**
   ```bash
   /plugin uninstall plugin-name@aiyou-fastapi-plugins
   /plugin install plugin-name@aiyou-fastapi-plugins
   ```

4. **Submit PR**
   - Clear description of changes
   - Usage examples
   - Breaking changes noted

## FAQ

**Q: Can I use plugins from multiple marketplaces?**
A: Yes! Add multiple marketplace sources in `.claude/settings.json`.

**Q: How do I share plugins with my team?**
A: Commit the `claude-plugins/` directory and `.claude/settings.json` to your repository.

**Q: Can plugins access the filesystem?**
A: Plugins provide instructions to Claude, who has filesystem access. Hooks can execute commands directly.

**Q: Are plugins language-specific?**
A: No, plugins work with any project. These FastAPI plugins are Python-focused but the system is universal.

**Q: Can I have private plugins?**
A: Yes! Keep them in a private repository and reference it in your marketplace configuration.

**Q: What's the difference between commands and agents?**
A: Commands are single-purpose tasks (user-invoked). Agents are conversational assistants with ongoing context (user-selected).

**Q: When should I use a skill vs a command?**
A: Skills are autonomous (Claude decides when to use). Commands are explicit (user invokes). Use skills for capabilities Claude should apply automatically.

**Q: Can plugins call other plugins?**
A: Not directly, but Claude can use multiple plugin components together in a workflow.

---

For more information, see the [official Claude Code plugins documentation](https://docs.claude.com/en/docs/plugins).
