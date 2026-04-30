# Judge 6 Repo Maintenance Policy

## GREEN — auto-apply allowed

- Ruff formatting
- Ruff import cleanup
- Biome formatting
- obvious dead whitespace
- generated report updates

## YELLOW — stage patch, human review

- ast-grep codemods
- package config changes
- nontrivial lint autofixes
- dependency config changes
- file moves

## ORANGE — explicit approval required

- auth code
- billing code
- deployment config
- infrastructure code
- database migrations
- security policy files
- CI/CD secrets or permissions

## RED — block

- secret exposure
- private key exposure
- destructive shell
- force-push automation
- automatic hard reset
- disabling permission checks
- bypassing security scanners
- deleting history
