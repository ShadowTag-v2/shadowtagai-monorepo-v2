# GKE/Cloud Run Traffic Routing: Architectural ROC Drill (v4)

**TARGET IDENTIFIER:** `apps/src/main.py`
**OBJECTIVE:** Ensure 0-Day structural rigidity across the newly deployed Stripe and CopilotKit Edge Nodes prior to Sovereign GKE/Cloud Run transition.

## 🔴 **[CRITICAL VULNERABILITY DETECTED]: THE COPILOT PROXY WEALTH LEAK**

### Fault Mechanics

1. The `MonetizationMiddleware` enforces strict API Key validation (`X-ShadowTag-v2-API-KEY`) and token-burning tracking *only* if the incoming request path begins with the static `settings.api_prefix` (e.g. `/api/v1`).
2. `copilot_proxy.py` has statically bound its endpoint routing to `@router.post("/api/copilot/proxy")` entirely bypassing the structural API prefix mounting sequence (`app.include_router(copilot_router)` without `prefix=settings.api_prefix`).
3. **The Result:** The `/api/copilot/proxy` gateway is currently functioning as an unprotected Edge node. Any external network actor can hit this ingress unauthenticated, spinning up the `gemini-3.1-flash-lite-preview` LLM. The system will process payloads *without incrementing monetization tracking metrics*, resulting in direct financial attrition via unrestricted LLM API consumption (Wealth Leak).

## 🟢 **[COMPLIANCE CERTIFIED]: THE STRIPE WEBHOOK ISOLATION**

### Matrix Validation

1. `stripe_webhook.py` also bypasses the core `MonetizationMiddleware` (`settings.api_prefix`).
2. **However, this is architecturally deliberate and secure.** Stripe webhooks inherently must hit public, unauthenticated ingress ports because they originate from Stripe servers which cannot attach custom `X-ShadowTag-v2-API-KEY` parameters dynamically.
3. The cryptographic defense layer is fully contained within the route via `stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)`.
4. **Latency Verification:** Structural processing happens post-signature validation synchronously. This ensures zero payload spoofing and perfectly protects the unencrypted data state transitioning over TLS into the persistent Sovereign DB arrays.

## **IMMEDIATE COUNTER-ACTION REQUIRED**

- The `apps/src/api/copilot_proxy.py` endpoint must immediately be migrated under the `settings.api_prefix` umbrella or manually injected with `MonetizationMiddleware` level dependencies.

---
*End of Protocol. The Board demands immediate architectural enforcement before GKE spin-up.*
