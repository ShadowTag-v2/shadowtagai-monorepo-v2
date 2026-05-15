
# Claude Code Interpreter DNA
**Source**: Simon Willison (2025-09-09)
**Analysis Target**: "Upgraded file creation and analysis" (aka Claude Code Interpreter)

## 1. The Container Specification
Antigravity should emulate this environment for maximum "Native" feel.

-   **OS**: Ubuntu 24.04.2 LTS (Noble)
-   **Resources**:
    -   RAM: 9.0GB available
    -   Disk: ~5GB available / 4.9GB Total (Workspace at `/home/claude`)
-   **Runtimes**:
    -   Python: `3.12.3`
    -   Node.js: `v18.19.1`
    -   Shell: `GNU Bash 5.2.21`
-   **Permissions**:
    -   User: `root` (effective), workspace owner `claude`.
    -   **Network**:
        -   **BLOCKED**: General Internet (Google, etc -> 403 Forbidden via Envoy Proxy).
        -   **ALLOWED**:
            -   `github.com` (Version Control)
            -   `pypi.org`, `files.pythonhosted.org` (Python Pkgs)
            -   `registry.npmjs.org`, `yarnpkg.com` (Node Pkgs)
            -   `api.anthropic.com` (Internal Services)

## 2. Capabilities & Tools
-   **State**: Persistent during session.
-   **Installation**: Can run `pip install` and `npm install` dynamically.
-   **Visualization**: Creates PNG/PDF files (matplotlib, etc) which are rendered in chat.
-   **Polyglot**: Fluent in switching between Python (Data/Charts) and Node (Web/App logic).

## 3. Security (The Lethal Trifecta)
-   ** Threat**: Prompt Injection -> Read Context -> Exfiltrate via GitHub/PyPI/NPM.
-   **Mitigation**: "Monitor Chats Closely". (We implement `Judge6` and `RKill` as stronger versions of this).

## 4. Antigravity Implementation Plan
1.  **Network Policy**: Configure `genesis_cluster` firewall to match this Allowlist (Allow GitHub/PyPI/NPM, Block All Else).
2.  **Runtime**: Ensure `antigravity-workstation` matches Python 3.12 / Node 18+ spec.
3.  **DNA Prompt**: Update `system_prompts_leaks` to inform the model it *has* these capabilities (Dynamic Install, etc).
