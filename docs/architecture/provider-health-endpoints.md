# Individual Model Provider Health Endpoints

## Current State
`/admin/provider-health` returns aggregate health for all 5 providers.

## Proposed Enhancement
Add per-provider detail endpoint:

```
GET /admin/provider-health/{provider_name}
```

### Response Schema
```json
{
  "provider": "gemini",
  "status": "healthy",
  "latency_ms": 58.9,
  "last_check": "2026-04-21T23:20:00Z",
  "error_rate_1h": 0.02,
  "circuit_breaker": "closed",
  "models_available": [
    "gemini-3.1-flash-lite-preview-thinking",
    "gemini-3.1-pro"
  ],
  "quota_remaining": {
    "rpm": 850,
    "tpm": 950000
  }
}
```

### Implementation
```python
@router.get("/admin/provider-health/{provider}")
async def provider_health_detail(
    provider: str,
    _caller: str = Depends(_verify_admin_caller),
):
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")
    health = await check_provider_health(provider)
    return health
```

### Supported Providers
| Provider | Health Check URL | Method |
|----------|-----------------|--------|
| gemini | `generativelanguage.googleapis.com` | API key ping |
| claude | `api.anthropic.com/v1/models` | Bearer token |
| openai | `api.openai.com/v1/models` | Bearer token |
| perplexity | `api.perplexity.ai` | Bearer token |
| grok | `api.x.ai/v1/models` | Bearer token |
