# Gitleaks Active Tree Audit Report

The targeted scan of the active development tree completed. We bypassed the 110GB archived histories to find only the credentials that reside in the current working footprint of `src/`, `apps/`, `tools/`, and `scripts/`.

### Exposed Credentials Found

> [!WARNING]
> The following legitimate credentials must be purged from the active tree prior to the Omnibus push:

| Rule | File Path | Secret Prefix |
|---|---|---|
| generic-api-key | `scripts/gdrive_token.json` | `GOCSP...ZSKh` |
| generic-api-key | `tools/antigravity/extensions/ms-python.python-2026.0.0-universal/out/client/plainExec.worker.js` | `c4a29...b11e` |
| gcp-api-key | `scripts/ingest_military_docs.py` | `AIzaS...H7UI` |
| gcp-api-key | `scripts/debug/verify_google_knowledge_mcp.py` | `AIzaS...H7UI` |
| gcp-api-key | `scripts/hook_knowledge_api.py` | `AIzaS...H7UI` |
| generic-api-key | `tools/antigravity/extensions/ms-python.python-2026.0.0-universal/out/client/extension.js` | `c4a29...b11e` |
| generic-api-key | `tools/antigravity/extensions/ms-python.debugpy-2025.18.0-darwin-arm64/bundled/libs/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/advapi32.py` | `windl...KeyW` |
| generic-api-key | `tools/antigravity/extensions/ms-python.python-2026.0.0-universal/out/client/plainExec.worker.js` | `7dc56...8d0f` |
| generic-api-key | `tools/antigravity/extensions/ms-python.python-2026.0.0-universal/out/client/extension.js` | `7dc56...8d0f` |
| generic-api-key | `tools/antigravity/extensions/ms-python.debugpy-2025.18.0-darwin-arm64/bundled/libs/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/advapi32.py` | `windl...eKey` |
| generic-api-key | `scripts/consolidated_sweeps/examples_mlperf_scripts/stable_diffusion_downloads.sh` | `a5362...2936` |
| generic-api-key | `scripts/consolidated_sweeps/airweave_backend_scripts/manual_stripe_pro_flow.py` | `44OLJ...rgU=` |
| generic-api-key | `tools/antigravity/extensions/ms-python.python-2026.0.0-universal/out/client/shellExec.worker.js` | `c4a29...b11e` |
| generic-api-key | `tools/antigravity/extensions/ms-python.debugpy-2025.18.0-darwin-arm64/bundled/libs/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/advapi32.py` | `windl...hKey` |
| generic-api-key | `tools/antigravity/extensions/ms-python.python-2026.0.0-universal/out/client/shellExec.worker.js` | `7dc56...8d0f` |
| generic-api-key | `scripts/token.json` | `GOCSP...ZSKh` |
| generic-api-key | `tools/antigravity/extensions/ms-python.debugpy-2025.18.0-darwin-arm64/bundled/libs/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/advapi32.py` | `windl...KeyA` |
| gcp-api-key | `scripts/harvest_knowledge.py` | `AIzaS...H7UI` |
| generic-api-key | `tools/antigravity/extensions/ms-python.python-2026.0.0-universal/out/client/plainExec.worker.js` | `0c6ae...7255` |
| generic-api-key | `scripts/consolidated_sweeps/pikeymickey_antigravity2api-nodejs_scripts/oauth-server.js` | `GOCSP...qDAf` |
| generic-api-key | `tools/antigravity/extensions/ms-python.python-2026.0.0-universal/out/client/extension.js` | `0c6ae...7255` |
| github-pat | `scripts/delete_forks.py` | `ghp_O...p1wO` |
| generic-api-key | `tools/external-proxy/docs/ARCHITECTURE.md` | `AIzaS...6...` |
| generic-api-key | `scripts/consolidated_sweeps/gcsfuse_perfmetrics_scripts/ls_metrics/directory_pb2.py` | `seria...pb=b` |
| generic-api-key | `scripts/consolidated_sweeps/pikeymickey_antigravity2api-nodejs_scripts/refresh-tokens.js` | `GOCSP...qDAf` |
| generic-api-key | `tools/antigravity/extensions/ms-python.python-2026.0.0-universal/out/client/shellExec.worker.js` | `0c6ae...7255` |

### Remediation Plan

To permanently erase these secrets from the active tree and its history before pushing, we must run `git-filter-repo`.
```bash
cat << 'EOF' > replacements.txt
AIzaSyBAJuLUQwDtMVSM5YPHpEaRVLXwuRuH7UI==>***REDACTED***
7dc56bab-3c0c-4e9f-9ebb-d1acadee8d0f==>***REDACTED***
a53625c4d45e3ca8ac0df8a353ea3a41ffc3292aa25259addd8b7dc5a6ce2936==>***REDACTED***
windll.advapi32.RegCloseKey==>***REDACTED***
44OLJ/s4OjYSyzVk9FtOk6033GrFS4Q4KWBdEstPrgU===>***REDACTED***
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==>***REDACTED***
windll.advapi32.RegEnumKeyW==>***REDACTED***
[PAT_SCRUBBED]==>***REDACTED***
AIzaSyDEF456...==>***REDACTED***
serialized_pb=b==>***REDACTED***
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==>***REDACTED***
windll.advapi32.RegFlushKey==>***REDACTED***
0c6ae279ed8443289764825290e4f9e2-1a736e7c-1324-4338-be46-fc2a58ae4d14-7255==>***REDACTED***
windll.advapi32.RegEnumKeyA==>***REDACTED***
c4a29126-a7cb-47e5-b348-11414998b11e==>***REDACTED***
EOF
git filter-repo --replace-text replacements.txt --force
```
