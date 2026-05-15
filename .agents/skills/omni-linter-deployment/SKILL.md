---
name: omni-linter-deployment
description: Packages and deploys self-optimized linter engines back into the Antigravity IDE.
---
# THE DARWINIAN HOT-SWAP PROTOCOL
1. **Build the Engine:** Compile the mutated engine binary (e.g., `cargo build --release` inside `ruff`).
2. **Inject the Transmission:** Copy the compiled binary into the `ruff-vscode` repository.
3. **Compile the VSIX:** Navigate to `ruff-vscode` and execute `npm install && npm run package` to generate the `.vsix` file.
4. **Ingest the Brain:** Execute `antigravity --install-extension *.vsix` to install the self-optimized linter directly into your active IDE environment.
