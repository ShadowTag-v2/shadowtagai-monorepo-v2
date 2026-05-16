# Hunter-Killer Stack: Dockerfile Injection Snippet

Add the following exact lines to your Cloud Workstation or Container `Dockerfile` (e.g., `images/antigravity-crd/Dockerfile`) to permanently inject the Hunter-Killer stack.

```dockerfile
# ⏺ ///▙▖▙▖▞ THE HUNTER-KILLER MANDATE (Optimized)

# 1. Install Ripgrep (rg) - Upgraded to latest for PCRE2 optimization
RUN curl -LO https://github.com/BurntSushi/ripgrep/releases/download/14.1.0/ripgrep_14.1.0-1_amd64.deb \
    && dpkg -i ripgrep_14.1.0-1_amd64.deb \
    && rm ripgrep_14.1.0-1_amd64.deb

# 2. Install AST-Grep (sg) - Native Linux Binary (NO NPM TAX)
RUN curl -L https://github.com/ast-grep/ast-grep/releases/latest/download/x86_64-unknown-linux-gnu.tar.gz -o sg.tar.gz \
    && tar -xzf sg.tar.gz -C /usr/local/bin \
    && chmod +x /usr/local/bin/ast-grep \
    && ln -s /usr/local/bin/ast-grep /usr/local/bin/sg \
    && rm sg.tar.gz

# 3. Install ugrep & jq (Universal Backup + JSON Parser)
RUN apt-get update && apt-get install -y ugrep jq && rm -rf /var/lib/apt/lists/*

```

**Execution Note:**
Once deployed, The Board will invoke `subprocess.run(["rg", ...])` and `subprocess.run(["sg", ...])` directly at bare-metal speeds.
