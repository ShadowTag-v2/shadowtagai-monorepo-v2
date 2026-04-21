# GitHub Integration Protocol

## Always-On GitHub Awareness

Every agent session MUST maintain continuous GitHub state awareness:

1. **Session Start**: Fetch remote, check CI status, list open PRs
2. **Pre-Edit**: Verify no conflicting PRs touch the same files
3. **Pre-Commit**: Run pre-commit hooks, verify CI green on base
4. **Post-Commit**: Push to remote, create PR if feature work

## Commands Reference

```bash
# Branch state
git fetch origin --prune
git status
git log --oneline -5

# GitHub state (requires gh CLI)
gh pr list --state open --limit 10
gh issue list --state open --limit 10
gh run list --limit 5
gh pr checks <number>

# Create PR
gh pr create --title "feat: ..." --body "..." --base main
```

## Monorepo Guardrails

- Never push directly to `main`
- All changes via PR with at least one review (human or Claude)
- CI must pass before merge
- Conventional commits required
