# PR Review Checklist

## Scope
- Is the change single-purpose and reviewable?
- Is the diff smaller than it needed to be?

## Security
- Are authn/authz boundaries correct?
- Are inputs validated?
- Are uploads handled safely?
- Are logs free of secrets and PII?

## Architecture
- Are boundaries clean?
- Is business logic separated from UI?
- Did this avoid unnecessary abstractions?

## Performance
- Did this avoid async waterfalls?
- Did this avoid unnecessary client bundle growth?

## Operations
- Do tests pass?
- Do lint, type checks, and secret scans pass?
- Is there a rollback path?
