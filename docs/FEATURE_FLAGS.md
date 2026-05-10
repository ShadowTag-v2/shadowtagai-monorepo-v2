# Feature Flags Registry

> **Last audited:** 2026-04-30
> **Scope:** All boolean environment variable flags across the ShadowTag-v2 monorepo

## CounselConduit (`apps/counselconduit/`)

| Flag | Default | File | Description |
|------|---------|------|-------------|
| `APP_ENV` | `development` | `auth.py`, `dispatch_router.py`, `app_error.py`, `middleware/__init__.py`, `fastapi_kovel_enclave.py`, `cloud_tasks_gdpr_handler.py` | Controls environment behavior. Set to `production` to enforce strict auth, opaque errors, OIDC token validation. `development` enables dev token bypass, permissive admin auth. |
| `ENABLE_ANT_GATE` | `false` | `middleware_ant.py` | Enables Ant Gate middleware for internal engineering tooling. When `true`, requests with `X-ShadowTag-Ant-Gate: true` header get `user_type=ant` injected into `request.state`. |
| `SKIP_SMOKE` | `0` | `tests/test_smoke.py` | Skips smoke tests when set to `1`. Used in CI when smoke tests are run separately. |
| `ADMIN_API_KEY` | (unset) | `dispatch_router.py` | Admin endpoint auth key for Cloud Scheduler service-to-service calls. |
| `ENABLE_ANT_FORENSIC_LOGGING` | `false` | `dispatch_router.py` | When enabled AND user is `ant`, emits enhanced structured logs with full request/response metadata for debugging. |
| `GOOGLE_APPLICATION_CREDENTIALS` | (unset) | `auth.py` | Path to service account JSON for Firebase Admin SDK initialization. Falls back to ADC. |
| `GOOGLE_CLOUD_PROJECT` | `shadowtag-omega-v4` | `auth.py` | Firebase project ID for token verification. |
| `CLOUD_RUN_URL` | (unset) | `dispatch_router.py` | Cloud Run service URL used as OIDC token audience for admin endpoint verification. |

## AiYou Stack (`apps/aiyou_stack/`)

| Flag | Default | File | Description |
|------|---------|------|-------------|
| `MOCK_CLOUD_RUN_ANE` | `true` | `edge_router.py`, `central_hive_mind.py` | Mocks Cloud Run Apple Neural Engine calls. Set to `false` for production. |
| `MOCK_MODE` | `false` | `pnkln_file_search/config/mock_mode.py` | Enables mock mode for file search operations. |
| `ENABLE_LAYER_1_GEMINI` | `true` | `vertex_ai_orchestrator.py` | Enables Gemini layer in multi-model orchestrator. |
| `ENABLE_LAYER_2_PYTORCH` | `true` | `vertex_ai_orchestrator.py` | Enables PyTorch layer in multi-model orchestrator. |
| `ENABLE_LAYER_3_RULES` | `true` | `vertex_ai_orchestrator.py` | Enables rules-based layer in multi-model orchestrator. |
| `MITMPROXY_ENABLE_METRICS` | `true` | `scripts/mitmproxy_ultra.py` | Enables metrics collection in mitmproxy. |
| `MITMPROXY_MODEL_FALLBACK` | `true` | `scripts/mitmproxy_ultra.py` | Enables model fallback in mitmproxy routing. |
| `ALLOW_ORIGINS` | (unset) | `slides_agent_demo/app/fast_api_app.py` | Comma-separated CORS origins. |

## Packages

| Flag | Default | Package | File | Description |
|------|---------|---------|------|-------------|
| `AGNT_VCR_MODE` | `off` | `packages/vcr` | `recorder.py` | VCR operational mode: `off`, `record`, `replay`, `diff`. |
| `AGNT_VCR_DIR` | `./vcr_cassettes` | `packages/vcr` | `recorder.py` | Override directory for VCR cassette storage. |
| `AGNT_VCR_RECORD` | `0` | `packages/agnt_vcr` | `vcr.py` | Legacy VCR record flag (`1` to enable). |
| `AGNT_VCR_REPLAY` | `0` | `packages/agnt_vcr` | `vcr.py` | Legacy VCR replay flag (`1` to enable). |
| `AG_CACHED_MICROCOMPACT` | `true` | `scripts` | `ag_context_compactor.py` | Enables cached microcompact in context compaction. Auto-enabled for `ant` users. |

## Agent / CI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `CI` | (unset) | Set to `true` to suppress interactive TUI prompts (Inquirer.js, bubbletea, etc.). Mandatory for headless CLI operations. |
| `DISABLE_TELEMETRY` | `1` | Disables telemetry reporting from all tooling. Hardcoded in operator invariants. |
| `DISABLE_ERROR_REPORTING` | `1` | Disables error reporting. Hardcoded in operator invariants. |

## Naming Conventions

All boolean flags follow this pattern:

```python
# Truthy values: "true", "1", "t", "y", "yes" (case-insensitive)
os.getenv("FLAG_NAME", "false").lower() in ("true", "1", "t", "y", "yes")

# Simple equality check
os.getenv("FLAG_NAME") == "value"
```

## Adding New Flags

1. Add the flag to this document in the appropriate section.
2. Use the truthy pattern above for boolean flags.
3. Default to **disabled** (`false`) for safety.
4. Document the flag in the module docstring where it's consumed.
5. For CounselConduit production flags, coordinate with `gcloud run services update` to set env vars.
