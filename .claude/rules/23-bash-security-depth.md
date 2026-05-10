# Rule 23: Bash Security Deep Defense & Permission Pipeline
# Source: Claude Code Source (bashSecurity.ts 2592 lines, bashPermissions.ts, pathValidation.ts)

## 20-Layer Bash Security Validator (Pattern #2)
Every bash command passes through ~20 independent validators (defense in depth):
1. Unicode whitespace hiding (`\u00A0` in command position)
2. Carriage return parsing differentials (`\r` between shell-quote vs bash tokenize)
3. Zsh module loading (`zmodload` → gateway to kernel modules) → BLOCK
4. `$IFS` injection attacks
5. Brace expansion exploits
6. Quote/comment desync (unmatched quotes causing reinterpretation)
7. `/proc/*/environ` reads (secret exfiltration via procfs) → BLOCK
8. Bare git repo marker detection (`core.fsmonitor` sandbox escape) → BLOCK
9. Binary hijack detection (PATH manipulation)
10. Environment variable stripping (safe: `NODE_ENV`; dangerous: `LD_PRELOAD` → BLOCK)
11. Dangerous path blocking (system directories, other users' home)
12. Glob/regex safety (untested patterns with wildcard expansion)
13. Pipe chain analysis (data exfiltration via `curl | bash`)
14. Process substitution abuse (`<()`, `>()`)
15. Here-document injection
16. Command substitution nesting depth
17. Semicolon/newline command chaining analysis
18. Alias/function redefinition detection
19. Network tool invocations (wget, curl to external hosts)
20. Misparsing override: later validators override earlier "ask" results

## 10-Step Permission Pipeline (Pattern #6)
Progressive permission learning — agent gets faster as you approve:
1. Exact match against saved rules
2. Deny rules (always win over allow)
3. Ask rules (explicit prompts)
4. Path constraints validation
5. Allow rules with prefix matching (`npm:*` matches `npm install foo`)
6. Classifier-based decision
7. Sandbox auto-allow (if sandboxed environment)
8. Rule suggestion: `git commit:*`, `npm:*`, etc.
9. Wildcard patterns with escaping (`\*` for literal asterisk)
10. Persistence to `~/.claude/settings.json`

## CWD Persistence (Pattern #14)
Every bash command is wrapped:
```
source $SNAPSHOT && eval '$USER_COMMAND' && pwd -P >| /tmp/claude-xxx-cwd
```
- `pwd -P` resolves symlinks
- macOS APFS Unicode NFC-normalized to prevent false "CWD changed" events
- Extended glob disabled for security
- `GIT_EDITOR=true` prevents interactive editors
- `CLAUDECODE=1` lets scripts detect they're running inside Claude
- Hooks can write exports to `$CLAUDE_ENV_FILE`, sourced on subsequent commands

## Antigravity Adaptation
- Apply independent validator pattern to `run_command` tool calls
- Block known-dangerous env vars (`LD_PRELOAD`, `DYLD_INSERT_LIBRARIES`)
- Maintain CWD state across command invocations
- Use progressive permission learning for `SafeToAutoRun` decisions

## Adversa 50-Subcommand Vulnerability (CVE-class, Source: bashPermissions.ts:103)
`MAX_SUBCOMMANDS_FOR_SECURITY_CHECK = 50` — beyond 50 subcommands in a compound
command (`&&`, `||`, `;`, `|`), the security check falls to 'ask' mode and
**auto-rejection rules no longer apply**. An attacker can embed instructions
in documents that generate compound commands exceeding this threshold.

**Mitigation (validate-bash.py):** We BLOCK any compound command with >50
subcommands defensively, rather than falling to 'ask' mode.

## Runtime Enforcement Layer (Faramesh Doctrine)
CLAUDE.md is guidance, NOT security policy. For production enforcement:
1. **Tool-level validation** — validate-bash.py blocks 23 dangerous patterns deterministically
2. **MCP server validation** — add parameter validation before tool execution
3. **Prompt injection defense** — never trust file contents as instructions
4. **Multi-step reasoning** — safety check each step, not just input boundary
5. **Model update resilience** — deterministic rules survive model version changes

The enforcement layer lives BETWEEN intent and execution, not in the prompt:
```
Claude Decision → validate-bash.py → Shell Execution
                        ↓ BLOCK
                (deterministic policy)
```
