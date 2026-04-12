# Claude Code Configuration

This directory contains Claude Code hooks and configuration for the workbench.

## Quick Start

1. **Review the configuration**:
   ```bash
   cat settings.json
   ```

2. **Read the hooks documentation**:
   ```bash
   cat HOOKS.md
   ```

3. **In a Claude Code session, check hooks are loaded**:
   ```
   /hooks
   ```

## What's Included

### Configuration Files
- `settings.json` - Hooks configuration with 8 different hook types

### Hook Scripts (in `hooks/` directory)
- `session-start.sh` - Environment setup and context
- `validate-prompt.py` - Prompt validation and security
- `validate-bash.py` - Bash command validation
- `check-file-safety.py` - File operation safety
- `format-code.sh` - Automatic code formatting
- `log-command.sh` - Command logging
- `notify-permission.sh` - Permission tracking

### Documentation
- `HOOKS.md` - Comprehensive hooks reference and guide
- `README.md` - This file

## Features

✅ **Security**: Blocks sensitive data in prompts and file operations
✅ **Best Practices**: Enforces modern tooling (ripgrep, Read tool, etc.)
✅ **Auto-formatting**: Python (black), JS/TS (prettier), JSON (jq)
✅ **Logging**: Command history and permission tracking
✅ **Context Injection**: Automatic project context in sessions
✅ **LLM-based Decisions**: Intelligent stop behavior

## Logs

Logs are created in `.claude/logs/` (gitignored):
- `commands.log` - All bash commands executed
- `permissions.log` - Permission requests

## Learn More

See `HOOKS.md` for complete documentation, including:
- How each hook works
- Customization options
- Testing and debugging
- Security considerations
- Best practices

## References

- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks)
- [Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
