#!/usr/bin/env bash
set -euo pipefail
keep=(
  Continue.continue
  biomejs.biome
  esbenp.prettier-vscode
  ms-python.python
  eamodio.gitlens
  bradlc.vscode-tailwindcss
  Vue.volar
  github.copilot
)
cli=$(command -v cursor || true)
if [ -z "$cli" ]; then cli=$(command -v code || true); fi
if [ -z "$cli" ]; then echo "No Cursor/VS Code CLI found"; exit 0; fi
mapfile -t installed < <("$cli" --list-extensions)
for ext in "${installed[@]}"; do
  skip=false
  for k in "${keep[@]}"; do [[ "$ext" == "$k" ]] && skip=true && break; done
  if [ "$skip" = false ]; then "$cli" --uninstall-extension "$ext" --force || true; fi
done
echo "Scrub complete."

