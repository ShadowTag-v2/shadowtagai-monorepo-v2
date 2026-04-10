# Task List: Omega Loop Transfer

## 1. Infrastructure State (The Hardware)
- [ ] **Monitor Deployment**: Check `trinity-cluster` status.
    - Command: `gcloud workstations clusters list --region us-central1 --project shadowtag-omega-v4`
- [ ] **Verify Reachability**: Tunnel via `gcloud workstations start` (if active).

## 2. Codebase & Doctrine (The Software)
- [x] **Verify Kernel Model**: Ensure [src/trinity_kernel/core.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/src/trinity_kernel/core.py)            model="gemini-2.0-flash-exp",`. (Confirmed)
- [x] **Verify Auth Daemon**: Check [scripts/omega_auth_daemon.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/scripts/omega_auth_daemon.py) status/config. (Confirmed Logic)
- [x] **Verify Environment**: Check `STRIPE_SECRET_KEY` availability for [BennettWorker](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/src/trinity_kernel/core.py#235-273). (Verified: Missing SK, using Fallback)

## 3. Environment Setup (Interruption)
- [/] **Install OpenJDK**: Deploy OpenJDK 21 via Homebrew for Antigravity IDE support.
    - [x] `brew install openjdk@21` (Already installed)
    - [x] Symlink to `/Library/Java/JavaVirtualMachines`
    - [x] Verify `java -version`
- [x] **Configure Python Interpreter**: Set path to `/usr/local/bin/python3` in `.vscode/settings.json` (Completed)
- [x] **Configure Java Settings**: Apply comprehensive `vscode-java` configuration in `.vscode/settings.json` (Completed)
- [x] **Clone vscode-java**: `git clone https://github.com/redhat-developer/vscode-java.git external_sdks/vscode-java` (Completed)
    - [x] `npm install` (Completed)
    - [x] `npm run compile` (Failed: TypeScript errors in `@types/leaflet`, check logs)
- [x] **Fix Java LS Errors**: Core Java support fixed (JDK 21). Plugin bundle errors require extension reinstall. (Completed)
- [x] **Ingest Red Hat Tools**:
    - [x] `git clone https://github.com/redhat-developer/yaml-language-server.git external_sdks/yaml-language-server`
    - [x] `git clone https://github.com/redhat-developer/vscode-yaml.git external_sdks/vscode-yaml`
    - [x] `git clone https://github.com/redhat-developer/vscode-xml.git external_sdks/vscode-xml`
    - [x] `git clone https://github.com/redhat-developer/app-services-guides.git external_sdks/app-services-guides`
- [x] **Ingest Package Managers**:
    - [x] `git clone https://github.com/npm/npm.git external_sdks/npm`
    - [x] `git clone https://github.com/npm/cli.git external_sdks/npm-cli`
    - [x] `git clone https://github.com/Homebrew/homebrew-core.git external_sdks/homebrew-core`
    - [x] `git clone https://github.com/Homebrew/homebrew-cask.git external_sdks/homebrew-cask`
    - [x] `git clone https://github.com/Homebrew/install.git external_sdks/homebrew-install`

## 4. Execution (The Loop)
- [x] **Execute Kernel**: Run `python3 -m src.trinity_kernel.core` (Active: Harvester engaged).
- [x] **Verify Loop**: Confirm Harvester -> Thinking -> Action cycle (Harvester started, listening for events).

---
# Archived Tasks (Previous Session)
- [x] Configure Gemini 3 Preview
- [x] Research Chrome DevTools MCP Issues
- [x] Fix Antigravity Command Error
- [x] Fix Java Language Server Crash
- [x] Protocol: Formalize 'AI Mode' Protocol
- [x] **Deploy**: Execute Cloud Run Deployment (`judge6-governance` - **REVERSED/DELETED** per user command)
- [x] **Upgrade**: Implement Chrome DevTools MCP Multi-Session (`chrome-devtools-mcp` - **COMPLETE**)
