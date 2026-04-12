# Public Repos To Clone For Best Support

Clone these outside the canonical monorepo, for example under:

```text
external_support/public/
```

Do **not** fold them into the monorepo as live truth.

## Tier A

1. `google-gemini/gemini-cli`
   - terminal-native Gemini agent
   - useful for fallback workflows, non-IDE automation, and MCP wiring

2. `google/adk-python`
   - primary open-source ADK framework
   - source of agent runtime patterns, tools, eval, and deploy examples

3. `google/adk-web`
   - ADK dev UI and debugging surface
   - useful when testing or mirroring agent UX patterns

4. `modelcontextprotocol/modelcontextprotocol`
   - MCP specification and documentation
   - protocol authority

5. `modelcontextprotocol/servers`
   - official reference MCP servers
   - especially useful for filesystem, git, github, postgres, memory, fetch

6. `modelcontextprotocol/python-sdk`
   - official Python MCP SDK
   - pin `v1.x` for production until v2 is fully stable

7. `modelcontextprotocol/inspector`
   - official visual testing/debugging tool for MCP servers

8. `ast-grep/ast-grep`
   - structural search/rewrite engine
   - supports rewrite safety and code transformation

## Tier B

1. `ast-grep/ast-grep-mcp`
   - MCP bridge for ast-grep workflows

2. `microsoft/playwright`

- browser automation and verification substrate

1. `fforster/gitlab-mcp`

- only if GitLab MR review / GitLab-side MCP is part of your workflow

## Clone policy

- clone as support tooling only
- never let these outrank monorepo control-plane truth
- use them for reference, tooling, adapters, and examples
