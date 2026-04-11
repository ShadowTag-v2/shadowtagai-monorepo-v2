# Rule 40: AST-Grep Structural Search Patterns
# Source: ast-grep/ast-grep-mcp cursor rules
# Created: 2026-04-11

## Purpose
Codifies AST-based structural code search patterns for precise refactoring and dead code detection.

## Core Principle
> Use structural (AST) matching over regex for code transformations.
> Regex matches text. AST-grep matches meaning.

## When to Use AST-Grep
- Finding specific function call patterns across a codebase
- Detecting deprecated API usage
- Enforcing coding standards structurally
- Dead code detection (complement to `vulture`)
- Refactoring patterns (rename, restructure)

## Pattern Syntax

### Basic Pattern Matching
```yaml
rule:
  pattern: console.log($$$ARGS)
  # Matches any console.log call with any arguments
```

### With Constraints
```yaml
rule:
  pattern: fetch($URL)
  constraints:
    URL:
      not:
        regex: "^['\"]https://"
  # Finds fetch calls NOT using HTTPS
```

### Metavariables
- `$VAR` — matches single AST node
- `$$$ARGS` — matches multiple nodes (variadic)
- Named captures for constraints

## CodeRabbit Security Rules (554 rules installed)

Location: `tools/ast-grep-rules/`

| Language | Rules | Focus |
|----------|-------|-------|
| Python | 48 | SQL injection, hardcoded secrets, debug mode, insecure DB passwords |
| TypeScript | 6 | Security anti-patterns |
| JavaScript | 7 | Security anti-patterns |
| Go | 11 | TLS, gRPC, JWT, hardcoded keys |
| Rust | 8 | Memory safety, crypto |

### Running Security Scan
```bash
# Full security scan using CodeRabbit rules
ast-grep scan --rule tools/ast-grep-rules/python/security/ apps/ tools/
ast-grep scan --rule tools/ast-grep-rules/typescript/security/ apps/
```

## Integration with Compiler Guillotine
AST-grep runs BEFORE the Compiler Guillotine (Skill: compiler-guillotine):
1. AST-grep security scan → CodeRabbit rules (Phase 0)
2. AST-grep sweep → identify structural issues
3. Vulture sweep → dead code detection  
4. Ruff fix → auto-format
5. Regression test → confirm no breakage

## Integration with Pre-Agent Protocol
The AST-grep security scan should run as part of Phase 3 (Execution) in the Pre-Agent Protocol to catch security issues that diagnostic thinking alone cannot identify.

## Cursor Rules File
Store project-specific AST patterns in `.cursor/rules/ast-grep.mdc` or equivalent.
These patterns are loaded by the MCP server at startup.

## Anti-Patterns
- ❌ Using regex to find function calls (misses multi-line, comments)
- ❌ Manual search-and-replace for refactoring
- ❌ Ignoring AST-grep warnings without understanding
