---
description: Run the security pass for rhtpa/osv-github and other CVEs
---

# Security Pass

When executing a security pass, perform the following:
1. Clone the required external repository or access the component.
2. Strip nested `.git` directories to prevent submodule drift.
3. Upgrade critical dependencies according to Trustify/CVE audits.
4. Run standard build/lint steps to ensure the upgrade did not break compilation.
5. Commit to the monorepo root.
