from service.app.config import load_settings
from service.app.adapters.authority_promotions import propose_promotion

s = load_settings()
pid = propose_promotion(
    s.postgres_dsn,
    s.repo_id,
    "setting",
    "settings",
    {"default_inference_backend": "ane", "fallback_backend": "metal"},
    "assistant"
)
print({"promotion_id": pid})
