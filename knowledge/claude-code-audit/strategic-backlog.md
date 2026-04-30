# Strategic Implications & Actionable Backlog

This backlog distills the strategic implications from the audit into immediate engineering tasks.

## Epic 1: GrowthBook Overrides & Feature Gates
**Objective:** Transition hardcoded behaviors into remote or env-controlled feature gates to enable dynamic tuning.
- [ ] Task 1.1: Audit all \`process.env\` checks and refactor into a unified \`feature()\` function wrapper.
- [ ] Task 1.2: Implement caching strategy for remote flag fetching (analogous to \`getFeatureValue_CACHED_MAY_BE_STALE\`).
- [ ] Task 1.3: Document the 49 obfuscated codename flags into a permanent dictionary.
- [ ] Task 1.4: Build killswitches for experimental features (e.g., Tree-sitter shadow parsing).

## Epic 2: API Micro-Compaction
**Objective:** Optimize token budgets before payloads hit the API via targeted AST reduction and history trimming.
- [ ] Task 2.1: Write script to strip unmodified \`AST\` node chunks during diffs.
- [ ] Task 2.2: Limit maximum token lengths per tool execution output before they are appended to session logs.
- [ ] Task 2.3: Build an intelligent truncator that replaces raw stdout with summarized output for large blobs.

## Epic 3: VCR Mode Adoption
**Objective:** Enable deterministic local testing by recording and replaying LLM responses and shell command outputs.
- [ ] Task 3.1: Develop an interception layer at the \`queryWithModel\` level to serialize inputs/outputs to a \`.vcr_cassettes\` directory.
- [ ] Task 3.2: Implement a \`--replay\` CLI flag to bypass live LLM API calls and load responses directly from cassettes.
- [ ] Task 3.3: Write automated tests to verify replay mode correctly mirrors expected execution flow without API tokens.
