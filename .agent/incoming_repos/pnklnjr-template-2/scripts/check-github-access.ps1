$ErrorActionPreference = "Continue"
function Has-Cli($name) { if (Get-Command $name -ErrorAction SilentlyContinue) { return $true } else { return $false } }

if (Has-Cli "gh") {
  try { gh auth status } catch { Write-Warning "gh not authenticated" }
}
if (Has-Cli "git") {
  try { git remote -v } catch { Write-Warning "git unavailable" }
}
Write-Host "GitHub visibility depends on local auth; this environment cannot provide tokens."

