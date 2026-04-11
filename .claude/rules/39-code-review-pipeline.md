# Rule 39: Code Review Pipeline
# Source: coderabbitai/skills + obra/superpowers/receiving-code-review
# Created: 2026-04-11

## Purpose
Codifies the automated review → fix → verify cycle for all code changes.

## The Review Pipeline

### Phase 1: Automated Review
Before any PR or merge:
1. Run static analysis (linter, type checker)
2. Run test suite
3. Generate diff summary
4. Flag security-sensitive changes (secrets, auth, permissions)

### Phase 2: Review Triage
Group findings by severity:
- **Critical**: Security vulnerabilities, data loss risks, crash bugs
- **Warning**: Performance issues, API misuse, missing error handling
- **Info**: Style issues, naming conventions, documentation gaps

### Phase 3: Fix Implementation
For each finding:
1. Understand the root cause (don't just suppress the warning)
2. Implement the fix
3. Verify the fix independently
4. Confirm no regression

### Phase 4: Verification Gate
- All critical findings must be resolved
- Warnings must be triaged (fix or document exception)
- Run full test suite post-fix
- NO COMPLETION CLAIMS WITHOUT VERIFICATION

## Receiving Review Feedback

When receiving code review (from human or AI):
1. **Read ALL comments before responding** — understand the full picture
2. **Don't blindly implement suggestions** — verify they're technically correct
3. **Push back when suggestions are wrong** — with evidence, not opinion
4. **Ask clarifying questions** — if feedback is ambiguous
5. **Never performatively agree** — disagreement with evidence > agreement without

## Anti-Patterns
- ❌ "LGTM" without reading the diff
- ❌ Implementing review suggestions without testing
- ❌ Ignoring review comments because "it works"
- ❌ Batch-fixing without verifying each change
- ❌ Trusting AI review output as ground truth
