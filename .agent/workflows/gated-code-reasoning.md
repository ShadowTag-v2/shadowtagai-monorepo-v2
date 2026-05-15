# Gated Code Reasoning

Structured reasoning workflow for complex code changes requiring multi-step analysis.

## Contract
- Tool contract: `tool_contracts/code_reasoning.certificate.yaml`
- Package: `packages/code_reasoning/`
- Enforcement: advisory (mandatory for STATE B changes)

## When to Use
- Architecture shifts affecting >3 packages
- Auth or payment logic changes
- Database schema migrations
- Complex refactors where the blast radius is unclear

## Steps

1. **Scope the Problem** — Use `sequential-thinking` MCP to break down the change:
   - What is the current state?
   - What is the desired state?
   - What are the risks?

// turbo
2. **Impact Analysis** — Run `scripts/repo-oracle "<affected-area>"` to identify all affected files.

3. **Approach Selection** — Consider 2+ approaches:
   - Document tradeoffs for each
   - Select based on: simplicity > familiarity (Rich Hickey doctrine)
   - Log the decision in the implementation plan

4. **Edge Case Audit** — Think through edge cases before writing code:
   - Null/empty inputs
   - Concurrent access
   - Failure modes and recovery
   - Backwards compatibility

5. **Certificate Generation** — Before executing, produce a reasoning certificate:
   ```markdown
   ## Code Reasoning Certificate
   - **Change**: <description>
   - **Approach**: <selected approach>
   - **Rejected alternatives**: <list>
   - **Risk level**: LOW | MEDIUM | HIGH
   - **Blast radius**: <N files, M packages>
   - **Edge cases considered**: <list>
   - **Rollback plan**: <steps>
   ```

6. **Execute** — Implement the change following the certificate.

// turbo
7. **Verify** — Run full test suite: `/opt/homebrew/bin/python3.14 -m pytest --tb=short -q`

8. **Evidence** — Log certificate to `.agent/evidence/index.ndjson`.

## Completion Criteria
- Reasoning certificate produced and logged
- Implementation matches certificate scope (no scope creep)
- All tests pass
- No unaddressed edge cases
