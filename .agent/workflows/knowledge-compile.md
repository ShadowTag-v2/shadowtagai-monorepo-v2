# Knowledge Compile

Compile session insights into durable Knowledge Items (KIs) for cross-session persistence.

## Contract
- Tool contract: `tool_contracts/knowledge.compile.yaml`
- Enforcement: advisory

## When to Use
- End of a productive session with new architectural decisions
- After resolving a non-trivial bug with reusable patterns
- When documenting integration patterns or API behaviors
- After research that produced actionable intelligence

## Steps

1. **Identify Candidates** — Review session actions for:
   - Architectural decisions (ADR-worthy)
   - Bug fix patterns (root cause + fix)
   - API behaviors discovered empirically
   - Integration patterns validated in production
   - Risk mitigations applied

2. **Check Existing KIs** — Search `~/.gemini/antigravity/knowledge/` for existing KIs on the same topic. Update rather than duplicate.

3. **Create KI Structure** — For each new KI:
   ```
   ~/.gemini/antigravity/knowledge/<ki-name>/
   ├── metadata.json
   └── artifacts/
       └── <content>.md
   ```

4. **Write metadata.json**:
   ```json
   {
     "title": "<descriptive title>",
     "summary": "<2-3 sentence summary>",
     "created": "<ISO timestamp>",
     "updated": "<ISO timestamp>",
     "references": ["<file paths or URLs>"],
     "tags": ["<relevant tags>"]
   }
   ```

5. **Write Artifact** — Distill the insight into a focused markdown document. Include:
   - Context and problem statement
   - Solution or pattern
   - Code examples if applicable
   - Cross-references to repo files

6. **Validate** — Ensure the KI is:
   - Actionable (not just notes)
   - Non-redundant with existing KIs
   - Referenced to actual repo state (not stale)

## Completion Criteria
- KI metadata.json has valid structure
- Artifact content is focused and actionable
- No duplicate KIs created
- Summary is concise (2-3 sentences max)
