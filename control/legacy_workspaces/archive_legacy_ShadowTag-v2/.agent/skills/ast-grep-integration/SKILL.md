# ast-grep (sg) Integration Skill

> **AUTHORITY:** The Board of Directors
> **SKILL:** Structural Code Search & Replacement

## Concept

`ast-grep` (aliased as `sg`) is fundamentally faster and more precise than standard regex searches (like `ripgrep`) because it understands the Abstract Syntax Tree (AST) of the code.

## Global Configuration

The master configuration file `sgconfig.yml` is located at the root of the monorepo: `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/sgconfig.yml`.
This points the agent to the `rules/` directory for any custom YAML rules.

## Core Directives for Antigravity Agent

1. **Always prefer `sg` over `grep`** when searching for specific code structures, function calls, or syntax patterns.
2. **Absolute Pathing:** Always provide absolute paths or paths directly relative to the project root when executing commands to avoid Docker volume mismatch resolution. Avoid `./` in yaml rules.

## Example Usage

- **One-off structural search:** `sg -p 'function_name($ARGS)' -l python /absolute/path/to/search/`
- **Scanning with pre-defined rules:** `sg scan --rule /absolute/path/to/rule.yml /absolute/path/to/search/`
