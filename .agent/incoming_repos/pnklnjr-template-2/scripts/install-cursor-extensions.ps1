$ErrorActionPreference = "Continue"
$exts = @(
  "Continue.continue",
  "biomejs.biome",
  "esbenp.prettier-vscode",
  "ms-python.python",
  "eamodio.gitlens",
  "bradlc.vscode-tailwindcss",
  "Vue.volar",
  "github.copilot",
  "rust-lang.rust-analyzer"
)

$cli = if (Get-Command cursor -ErrorAction SilentlyContinue) { "cursor" } elseif (Get-Command code -ErrorAction SilentlyContinue) { "code" } else { $null }
if (-not $cli) { Write-Warning "No Cursor/VS Code CLI found in PATH"; exit 0 }

foreach ($e in $exts) {
  try { & $cli --install-extension $e --force | Out-Null } catch { Write-Warning "Failed to install $e" }
}

Write-Host "Installed $($exts.Count) extensions. Restart Cursor for best results."
