# Claude Code Hooks Configuration

This directory contains a comprehensive hooks setup for Claude Code workbench, demonstrating various hook types and patterns based on the [official hooks reference](https://code.claude.com/docs/en/hooks).

## Overview

Hooks allow you to intercept and respond to events in Claude Code sessions, enabling:
- Automated validation and safety checks
- Environment setup and context injection
- Code formatting and quality enforcement
- Logging and notifications
- Intelligent decision-making with LLM-based hooks

## Directory Structure

```
.claude/
├── settings.json          # Hook configuration
├── HOOKS.md              # This documentation
├── hooks/                # Hook scripts
│   ├── session-start.sh          # SessionStart: Environment setup
│   ├── validate-prompt.py        # UserPromptSubmit: Prompt validation
│   ├── validate-bash.py          # PreToolUse (Bash): Command validation
│   ├── check-file-safety.py      # PreToolUse (Write/Edit): File safety
│   ├── format-code.sh            # PostToolUse (Write/Edit): Code formatting
│   ├── log-command.sh            # PostToolUse (Bash): Command logging
│   └── notify-permission.sh      # Notification: Permission tracking
└── logs/                 # Generated logs (created on first use)
    ├── commands.log      # Bash command history
    └── permissions.log   # Permission request log
```

## Configured Hooks

### 1. SessionStart Hook

**File**: `hooks/session-start.sh`

**Purpose**: Initialize environment and provide project context

**What it does**:
- Sets up Node.js environment (nvm)
- Configures project-specific environment variables
- Adds `node_modules/.bin` to PATH
- Injects project context into the conversation

**Environment Variables Set**:
- `PROJECT_NAME`: Project identifier
- `NODE_ENV`: Development environment
- `PATH`: Extended with local bin directories

**Output**: Context information visible to Claude

---

### 2. UserPromptSubmit Hook

**File**: `hooks/validate-prompt.py`

**Purpose**: Validate user prompts and add contextual information

**What it does**:
- Scans for hardcoded credentials or private keys
- Blocks prompts containing sensitive data
- Adds timestamp to context
- Provides project-specific context based on prompt content

**Security Checks**:
- Detects `password`, `api_key`, `secret_key`, etc.
- Detects private key patterns
- Blocks and warns user if sensitive data found

**Context Injection**:
- Current timestamp
- FastAPI-specific guidance
- Claude Agent SDK version information

---

### 3. PreToolUse Hook - Bash Validation

**File**: `hooks/validate-bash.py`

**Purpose**: Validate bash commands for best practices and safety

**What it does**:
- Enforces use of modern tools (ripgrep vs grep)
- Prevents dangerous operations
- Blocks commands that should use dedicated tools

**Validation Rules** (blocks execution):
- ❌ `grep` → Use `rg` (ripgrep)
- ❌ `find -name` → Use `rg --files`
- ❌ `cat` for reading files → Use Read tool
- ❌ `rm -rf /` → Dangerous deletion
- ❌ `chmod 777` → Security risk
- ❌ `curl | bash` → Security risk

**Output**: Errors shown to Claude, warnings shown to user

---

### 4. PreToolUse Hook - File Safety

**File**: `hooks/check-file-safety.py`

**Purpose**: Check file operations for safety

**What it does**:
- Prevents modification of sensitive files
- Detects path traversal attempts
- Warns about potentially dangerous content

**Protected Files/Patterns**:
- `.env` files
- Credential files (`credentials.json`)
- Private keys (`.pem`, `.key`, `id_rsa`)
- SSH directory
- Git configuration

**Content Safety Checks** (warns but allows):
- Hardcoded credentials in content
- Private keys in content
- World-writable permissions in scripts

---

### 5. PostToolUse Hook - Code Formatting

**File**: `hooks/format-code.sh`

**Purpose**: Automatically format code after Write/Edit operations

**What it does**:
- Formats Python files with `black`
- Formats JS/TS files with `prettier`
- Formats JSON files with `jq`
- Makes shell scripts executable

**Supported Formats**:
- `.py` → `black`
- `.js`, `.ts`, `.jsx`, `.tsx` → `prettier`
- `.json` → `jq`
- `.sh` → `chmod +x`

**Note**: Formatters run silently; errors are ignored if tools not installed

---

### 6. PostToolUse Hook - Command Logging

**File**: `hooks/log-command.sh`

**Purpose**: Log all bash commands executed during session

**What it does**:
- Logs commands to `.claude/logs/commands.log`
- Includes timestamp and session ID
- Maintains last 1000 commands

**Log Format**:
```
[2025-11-15T10:30:45Z] [Session: abc12345] npm install
```

---

### 7. Notification Hook - Permission Tracking

**File**: `hooks/notify-permission.sh`

**Purpose**: Track permission requests

**What it does**:
- Logs permission requests to `.claude/logs/permissions.log`
- Can be extended for desktop notifications

---

### 8. Stop Hook - Intelligent Stop Decision (LLM-based)

**Type**: Prompt-based hook (no script file)

**Purpose**: Use LLM to decide if Claude should continue working

**What it does**:
- Analyzes conversation context
- Checks if tasks are complete
- Identifies pending errors or todos
- Blocks stopping if work remains

**Decision Criteria**:
1. All user-requested tasks complete?
2. Any errors need addressing?
3. Follow-up work needed?
4. Todos still pending?

**This is a prompt-based hook** - it sends context to Haiku model for intelligent decision-making.

---

## Hook Types Demonstrated

### Command-Based Hooks (`type: "command"`)
Execute shell scripts/commands:
- SessionStart
- UserPromptSubmit
- PreToolUse (Bash, Write/Edit)
- PostToolUse (Bash, Write/Edit)
- Notification

### Prompt-Based Hooks (`type: "prompt"`)
Use LLM for intelligent decisions:
- Stop (intelligent continuation decision)

## Hook Output Patterns

### Exit Code Pattern

Scripts use exit codes to control behavior:
- `0`: Success (stdout shown to user in transcript mode)
- `2`: Blocking error (stderr shown to Claude)
- Other: Non-blocking error (stderr shown to user)

### JSON Output Pattern

Scripts can return structured JSON for advanced control:

```json
{
  "decision": "block",  // or "approve" for PreToolUse
  "reason": "Explanation shown to Claude",
  "continue": false,  // Stop Claude execution
  "stopReason": "Message shown to user",
  "systemMessage": "Warning shown to user",
  "suppressOutput": true,  // Hide from transcript
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "Context for Claude"
  }
}
```

## Hook Input Format

All hooks receive JSON via stdin:

```json
{
  "session_id": "abc123...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.py",
    "content": "..."
  }
}
```

## Environment Variables

Available in all hooks:
- `$CLAUDE_PROJECT_DIR`: Absolute path to project root
- `$CLAUDE_CODE_REMOTE`: `"true"` if web environment, empty if CLI
- Standard system environment

Only in SessionStart hooks:
- `$CLAUDE_ENV_FILE`: Path to file for persisting environment variables

## Testing Hooks

### Check Configuration
```bash
# In Claude Code session
/hooks
```

### Enable Debug Mode
```bash
claude --debug
```

### Test Individual Scripts
```bash
# Test with sample input
echo '{"session_id":"test","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"grep test.txt"}}' | \
  .claude/hooks/validate-bash.py
```

### View Logs
```bash
# Command history
cat .claude/logs/commands.log

# Permission requests
cat .claude/logs/permissions.log
```

## Customization

### Adding New Hooks

1. **Create a script** in `.claude/hooks/`
2. **Make it executable**: `chmod +x .claude/hooks/your-script.sh`
3. **Add to settings.json**:
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "YourTool",
           "hooks": [
             {
               "type": "command",
               "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/your-script.sh",
               "timeout": 30
             }
           ]
         }
       ]
     }
   }
   ```

### Modifying Validation Rules

Edit the validation arrays in scripts:
- `validate-bash.py`: `VALIDATION_RULES`
- `check-file-safety.py`: `PROTECTED_PATTERNS`, `PROTECTED_DIRS`
- `validate-prompt.py`: `sensitive_patterns`

### Adjusting Timeouts

In `settings.json`, set `timeout` (in seconds):
```json
{
  "type": "command",
  "command": "...",
  "timeout": 60  // 60 seconds
}
```

## Best Practices

1. **Quote shell variables**: Always use `"$VAR"` not `$VAR`
2. **Validate inputs**: Never trust JSON input blindly
3. **Handle errors gracefully**: Use `set -e` and proper error handling
4. **Use absolute paths**: Reference scripts via `$CLAUDE_PROJECT_DIR`
5. **Test hooks separately**: Test scripts with sample input before using
6. **Keep timeouts reasonable**: Default 60s, adjust based on operation
7. **Log important events**: Use `.claude/logs/` for debugging

## Security Considerations

### Hooks Execute with Your Permissions
- Hooks can access any file you can access
- Hooks can modify/delete files
- Review all hook code before use

### This Configuration Protects:
- Credential files (`.env`, keys)
- Git configuration
- Private keys and secrets
- System files (via path traversal prevention)

### Always Review:
- Commands before execution
- File operations before approval
- Content for sensitive data

## Troubleshooting

### Hook Not Running?
1. Check `/hooks` command output
2. Verify script is executable: `ls -l .claude/hooks/`
3. Check JSON syntax: `python3 -m json.tool < .claude/settings.json`
4. Review debug output: `claude --debug`

### Hook Failing?
1. Test script manually with sample input
2. Check exit code: `echo $?`
3. Review error output
4. Check file permissions

### Need More Context?
1. Add logging to your scripts
2. Use `echo` to stderr for debugging
3. Check `.claude/logs/` files

## MCP Tools Support

Hooks work with MCP tools using the pattern `mcp__<server>__<tool>`:

```json
{
  "matcher": "mcp__memory__.*",
  "hooks": [...]
}
```

Example matchers:
- `mcp__memory__create_entities`
- `mcp__filesystem__read_file`
- `mcp__.*__write.*` (all write operations from MCP)

## References

- [Official Hooks Reference](https://code.claude.com/docs/en/hooks)
- [Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
- [Plugin Hooks](https://code.claude.com/docs/en/plugins-reference#hooks)
- [MCP Integration](https://code.claude.com/docs/en/mcp)

## Examples in This Setup

| Hook Event | Example Script | Pattern Demonstrated |
|------------|----------------|---------------------|
| SessionStart | `session-start.sh` | Environment setup, context injection |
| UserPromptSubmit | `validate-prompt.py` | Security validation, context addition |
| PreToolUse (Bash) | `validate-bash.py` | Command validation, blocking |
| PreToolUse (Write/Edit) | `check-file-safety.py` | File protection, warnings |
| PostToolUse (Write/Edit) | `format-code.sh` | Automatic formatting |
| PostToolUse (Bash) | `log-command.sh` | Logging, history tracking |
| Notification | `notify-permission.sh` | Permission tracking |
| Stop | (Inline prompt) | LLM-based decision making |

## License

This hooks configuration is provided as an example/reference implementation.
Use at your own risk. Review all code before use in production.

---

**Note**: Hooks execute automatically and can modify your system. Always review and test hooks thoroughly before deploying in production environments.
