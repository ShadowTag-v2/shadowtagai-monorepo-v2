#!/usr/bin/env bash
set -euo pipefail
exts=(
  Continue.continue
  biomejs.biome
  esbenp.prettier-vscode
  ms-python.python
  eamodio.gitlens
  bradlc.vscode-tailwindcss
  Vue.volar
  github.copilot
)
cli="$(command -v cursor || true)"
if [ -z "$cli" ]; then cli="$(command -v code || true)"; fi
if [ -z "$cli" ]; then echo "No Cursor/VS Code CLI found in PATH"; exit 0; fi
for e in "${exts[@]}"; do "$cli" --install-extension "$e" --force || true; done
echo "Extension install attempt complete."
#!/usr/bin/env bash
set -euo pipefail

exts=(
  "Continue.continue"
  "biomejs.biome"
  "esbenp.prettier-vscode"
  "ms-python.python"
  "eamodio.gitlens"
  "bradlc.vscode-tailwindcss"
  "Vue.volar"
  "github.copilot"
  "rust-lang.rust-analyzer"
)

if ! command -v code >/dev/null 2>&1; then
  echo "VS Code/Cursor CLI 'code' not found. Install Cursor and enable 'Shell Command: Install code command'." >&2
  exit 1
fi

for e in "${exts[@]}"; do
  code --install-extension "$e" || true
done

echo "Installed ${#exts[@]} extensions. Restart Cursor for best results."

