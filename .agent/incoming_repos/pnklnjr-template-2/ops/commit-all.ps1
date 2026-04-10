param([string]$Message = "chore: bootstrap (elevated auto-commit)")
$ErrorActionPreference = "Continue"
function Has-Cli($n){ if (Get-Command $n -ErrorAction SilentlyContinue) { $true } else { $false } }
if (-not (Has-Cli "git")) { Write-Error "git not found in PATH"; exit 1 }

try { git rev-parse --is-inside-work-tree 1>$null 2>$null } catch { }
if ($LASTEXITCODE -ne 0) { git init | Out-Null }

# Ensure identity (set if missing)
$name = git config user.name 2>$null
$email = git config user.email 2>$null
if (-not $name)  { git config user.name  "ops-bot" }
if (-not $email) { git config user.email "ops-bot@local" }

git add -A
git diff --cached --quiet 1>$null 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host "No changes to commit."; exit 0 }

git commit -m "$Message"

# Try to push if upstream exists; otherwise attempt to set upstream to origin HEAD
git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 1>$null 2>$null
if ($LASTEXITCODE -eq 0) {
  git push
} else {
  git remote -v 1>$null 2>$null
  if ($LASTEXITCODE -eq 0) {
    git push -u origin HEAD 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Host "Committed locally. Push skipped (no auth or remote)." }
  } else {
    Write-Host "Committed locally. No remote configured."
  }
}
Write-Host "Done."

