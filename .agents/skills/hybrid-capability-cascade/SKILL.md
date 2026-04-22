---
name: hybrid-capability-cascade
description: >
  Governs the 3-Tier Capability Cascade routing doctrine for all agent operations.
  Tier 1 (Native JSON/MCP Tools) → Tier 2 (Workspace Skill Files) → Tier 3 (Dynamic Acquisition).
  This is the master routing skill. It DOES NOT replace any existing JSON schemas,
  MCP servers, or global skills. It layers a deterministic decision path on top.
  Activates on EVERY request to determine which execution layer handles it.
---

# Hybrid Capability Cascade — 3-Tier Routing Doctrine

## Core Principle
**Layer, never replace.** All existing JSON tool schemas (A2A, AG-UI, Firestore
Pipelines, Privilege Middleware, MCP servers) remain the primary execution layer.
This doctrine adds deterministic routing OVER them.

## The 3-Tier Cascade

### Tier 1: Native JSON Tools (The Muscle)
**Speed:** Fastest. **Security:** Highest. **Priority:** FIRST.

Use for ALL operations that have a matching MCP server or JSON tool schema:

| Domain | Tool |
|--------|------|
| Firebase Auth/Firestore/Hosting | `firebase-mcp-server` MCP |
| Google API documentation | `google-developer-knowledge` MCP |
| Browser automation/screenshots | `chrome-devtools-mcp` MCP |
| Design system generation | `StitchMCP` MCP |
| Architectural reasoning | `sequential-thinking` MCP |
| GitHub API operations | `github` MCP |
| Media generation | `media-generators` MCP |
| Cloud Run deployment | `gcloud` CLI (MCP-wrapped) |
| A2A agent routing | Firestore + ADK JSON schemas |
| AG-UI streaming | SSE transport JSON schemas |

**Rule:** If a Tier 1 tool CAN handle it, it MUST handle it. No fallback.

### Tier 2: Workspace Skill Files (The Brain)
**Speed:** Fast. **Security:** High (code-reviewed). **Priority:** SECOND.

For procedural workflows that SEQUENCE Tier 1 tools:

| Skill | Purpose |
|-------|---------|
| `.agents/skills/stitch-design-spec/` | Sequences StitchMCP + DESIGN.md lint |
| `.agents/skills/dynamic-tool-acquisition/` | SOP for Tier 3 fallback |
| `.agents/skills/mcp-fleet-vanguard/` | Pre-flight MCP integrity check |
| `.agents/skills/db-architect-guard/` | Database schema routing |
| `.agents/skills/notebooklm-oracle/` | Architectural context retrieval |
| `.agents/skills/skillify/` | Session capture as reusable skills |
| `~/.gemini/antigravity/skills/*/SKILL.md` | 211 global skills (style guides, security, etc.) |

**Rule:** Tier 2 skills tell the agent HOW to use Tier 1 tools. They never bypass them.

### Tier 3: Dynamic Acquisition (The Fallback)
**Speed:** Slower (download). **Security:** Medium (community). **Priority:** LAST.

When user requests a capability NOT covered by Tier 1 or Tier 2:

```
1. Search: CI=true npx -y skills --skill find-skills --query "<need>"
2. Observe: Parse exact skill name and arguments from output
3. Execute: CI=true npx -y skills --skill <discovered_skill> <args>
```

**Rule:** Never use Tier 3 without confirming Tier 1 and Tier 2 cannot handle it.

## JSON Tool Schemas (Injected)

### Tool A: Vercel Dynamic Skills CLI
```json
{
  "name": "vercel_dynamic_skills_cli",
  "description": "Tier 3 fallback. Discovers/executes atomic capabilities via npx skills CLI.",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {"type": "string", "enum": ["discover", "execute"]},
      "query_or_skill_name": {"type": "string"},
      "cli_arguments": {"type": "string"}
    },
    "required": ["action", "query_or_skill_name"]
  }
}
```

### Tool B: Stitch DESIGN.md Linter & Compiler
```json
{
  "name": "stitch_design_spec_manager",
  "description": "Lints DESIGN.md for WCAG compliance and scaffolds spec-compliant components.",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {"type": "string", "enum": ["lint", "scaffold"]},
      "target": {"type": "string"}
    },
    "required": ["action", "target"]
  }
}
```

## Routing Decision Tree

```
User Request
  │
  ├─ Has matching MCP server tool? ──→ Tier 1 (execute JSON tool)
  │
  ├─ Has matching .agents/skills/? ──→ Tier 2 (read SKILL.md, sequence Tier 1)
  │
  ├─ Has matching global skill? ────→ Tier 2 (read ~/.gemini/antigravity/skills/)
  │
  ├─ Unknown capability? ──────────→ Tier 3 (npx skills discover → execute)
  │
  └─ Still unknown? ───────────────→ Report to user with discovered options
```

## What This Doctrine Does NOT Change
- ❌ Does NOT delete any existing JSON tool schemas
- ❌ Does NOT remove any MCP server configurations
- ❌ Does NOT deprecate `antigravity-mcp-config.json`
- ❌ Does NOT override GEMINI.md capability resolution doctrine
- ❌ Does NOT change A2A, AG-UI, or Firestore pipeline schemas

## What This Doctrine ADDS
- ✅ Deterministic 3-tier routing for capability resolution
- ✅ Tool A (`vercel_dynamic_skills_cli`) for gap-filling
- ✅ Tool B (`stitch_design_spec_manager`) for DESIGN.md operations
- ✅ Project-scope skills that sequence existing MCP tools
- ✅ Infinite fallback (never say "I can't") via Tier 3 discovery

## Profitability Impact
- **Reduced token waste:** Tier 1 JSON tools fire in <100ms vs. Tier 3 download+execute
- **Reduced hallucination cost:** Structured routing prevents wasted retries
- **Client deliverable speed:** Auto-scaffold from DESIGN.md = faster UI delivery
- **Knowledge retention:** Skills persist across sessions (no re-prompting)
