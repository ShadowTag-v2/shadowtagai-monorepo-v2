---
name: TACSOP 6 — XML Security Classification Pipeline
description: Codifies the 2-stage XML security classifier for automated execution and artifact parsing based on the Claude Code forensic synthesis.
---

# TACSOP 6 — XML Security Classification Pipeline (Draft)

**Status:** DRAFT (Pending Omni-Linter Validation)
**Trigger:** Any incoming tool call or shell command containing complex XML or AST execution blocks.
**Source Provenance:** `claude_code_services/src/services/yolo/` and `tools/`

## 1. The Core Vulnerability

Standard prompt-injected XML parsing is susceptible to Prompt Unchaining (escaping the XML wrapper) and Direct Tool Injection. To maintain the `YOLO` execution envelope safely, all inbound XML structures from agent generation or external memory must pass through a strict, 2-stage classification pipeline before execution.

## 2. The 2-Stage Classifier

### Stage 1: Lexical Sanitization (Fast Pass)
- **Goal:** Drop malformed or explicitly malicious payloads before AST parsing.
- **Rule:** XML tags MUST exactly match the predefined schema (e.g., `<tool_call>`, `<execute>`).
- **Rule:** Unmatched closing tags (`</tool_call>`) outside of a valid block instantly trigger a pipeline halt.
- **Implementation:** Regex-based boundary checking.

### Stage 2: Structural Verification (Deep Pass)
- **Goal:** Verify that the inner content of the XML block adheres to execution constraints.
- **Rule:** Subcommand capping — Shell commands parsed from XML cannot contain unbounded subshells (`$(...)`) unless explicitly whitelisted.
- **Rule:** Parameter type validation — All JSON or command arguments inside the XML must map 1:1 to the registered MCP or native tool schema.
- **Implementation:** AST-based parsing and schema resolution.

## 3. Implementation Directives

- All custom XML parsing logic MUST bypass standard regex and use the unified `XMLSecurityClassifier` module.
- Any failure in Stage 1 or 2 results in an immediate **Execution Abort** with an RFC 9457 error payload returned to the agent context.
- **Zero-Trust Memory:** Artifacts loaded from `SessionMemory` or `teamMemorySync` must be re-classified upon read, as persisted memory is treated as untrusted.

## 4. Banned Patterns

- `.*` regex matching inside XML extractors.
- Blindly trusting the `type` attribute of a tool call without verifying the signature against `antigravity-mcp-config.json`.
- Allowing `USER_TYPE === 'ant'` debugging flags to bypass the classifier in production.

---
*Draft generated via Kairos Intelligence Synthesis*
