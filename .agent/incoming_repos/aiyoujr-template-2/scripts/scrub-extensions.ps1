param(
  [string[]]$keep = @(
    "Continue.continue",
    "biomejs.biome",
    "esbenp.prettier-vscode",
    "ms-python.python",
    "eamodio.gitlens",
    "bradlc.vscode-tailwindcss",
    "Vue.volar",
    "github.copilot"
  )
)
$ErrorActionPreference = "Continue"
$cli = if (Get-Command cursor -ErrorAction SilentlyContinue) { "cursor" } elseif (Get-Command code -ErrorAction SilentlyContinue) { "code" } else { $null }
if (-not $cli) { Write-Warning "No Cursor/VS Code CLI found in PATH"; exit 0 }
$installed = (& $cli --list-extensions) | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
foreach ($ext in $installed) {
  if ($keep -notcontains $ext) {
    try { & $cli --uninstall-extension $ext --force | Out-Null } catch { Write-Warning "Failed to uninstall $ext" }
  }
}
Write-Host "Scrub complete."

