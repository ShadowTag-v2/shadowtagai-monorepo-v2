# v10 Control Loop

## New pieces

- repo-root conflict detection
- code-graph validation
- promote-to-authority workflow

## Rule

1. Hydrate from authority + monorepo truth
2. Validate code references against code graph
3. Detect repo-root and config drift
4. Propose upgrades
5. Apply approved promotions to authority memory
6. Regenerate derived memory-bank views
7. Patch codebase toward authority
