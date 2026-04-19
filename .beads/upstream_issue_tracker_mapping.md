# Upstream Issue Tracker Mapping

> These are the public repositories where the third-party findings originate.
> No issues need to be filed — these are all intentional test fixtures in the upstream repos.

| Source Repo | Upstream URL | Findings | Top Rule | Action |
|---|---|---|---|---|
| terraform (click-to-deploy) | https://github.com/GoogleCloudPlatform/click-to-deploy | 435 | generic-api-key | None — test fixtures |
| opentofu | https://github.com/opentofu/opentofu | 104 | generic-api-key | None — doc examples |
| lighthouse | https://github.com/nicolo-ribaudo/lighthouse | 60 | gcp-api-key | None — PSI test keys |
| lighthouse-ci | https://github.com/nicolo-ribaudo/lighthouse-ci | 38 | generic-api-key | None — test fixtures |
| notebooklm-py | https://github.com/nicolo-ribaudo/notebooklm-py | 22 | generic-api-key | None — test fixtures |
| openclaw (cyberpunk_stack) | https://github.com/openclaw-io/openclaw | 7 | discord-client-secret | None — bundled dist |
| labs (internal) | Internal R&D | 9 | generic-api-key | None — test redaction |
| semaphore | https://github.com/nicolo-ribaudo/semaphore | 5 | generic-api-key | None — test fixtures |
| FFmpeg | https://github.com/FFmpeg/FFmpeg | 2 | generic-api-key | None — build config |
| claude-code-src | Internal extraction | 2 | generic-api-key | None — analysis artifact |
| flagger | https://github.com/fluxcd/flagger | 1 | generic-api-key | None — test fixture |
| obsidian-excalidraw-plugin | https://github.com/zsviczian/obsidian-excalidraw-plugin | 1 | generic-api-key | None — build artifact |
| 90DaysOfDevOps (via terraform) | https://github.com/MichaelCade/90DaysOfDevOps | 5 | private-key | None — tutorial k8s config |

## Conclusion

All findings are intentional test fixtures or documentation examples in upstream repositories.
No upstream issues need to be filed. The secrets are either:
1. Explicitly labeled as test keys in the source code
2. Example values in documentation
3. Build-time generated hashes/tokens
