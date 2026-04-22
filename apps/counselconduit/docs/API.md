# CounselConduit API Documentation

## Base URL
- **Production:** `https://counselconduit-api.run.app`
- **Staging:** `https://counselconduit-staging-api.run.app`
- **Local:** `http://localhost:8080`

## Authentication
All privileged endpoints require the `X-Kovel-Auth` header with a Firebase ID token.

```
X-Kovel-Auth: <firebase_id_token>
```

In development mode, prefix tokens with `dev_` to bypass Firebase verification.

---

## Endpoints

### POST `/enclave/v1/query`
Execute a synchronous Kovel-privileged query.

**Request:**
```json
{
  "attorney_id": "",
  "query": "What are the precedents for qualified immunity in CA?",
  "context_documents": ["Optional document text..."],
  "max_tokens": 4096,
  "temperature": 0.3
}
```

**Response:**
```json
{
  "attorney_id": "uid_123",
  "response": "Based on Harlow v. Fitzgerald (1982)...",
  "token_count": 1240,
  "model": "gemini-2.5-flash",
  "citations": []
}
```

### POST `/enclave/v1/query/stream`
Stream a privileged query response via Server-Sent Events.

**Response:** SSE stream
```
data: Based on
data: Harlow v. Fitzgerald
data: (1982)...
data: [DONE]
```

### GET `/enclave/v1/health`
Health check endpoint.

```json
{"status": "operational", "service": "CounselConduit Kovel Enclave", "version": "3.0.0"}
```

---

## Billing Endpoints

### POST `/billing/checkout`
Create a Stripe checkout session.

```json
{"tier": "professional", "annual": false}
```

**Response:**
```json
{"checkout_url": "https://checkout.stripe.com/...", "session_id": "cs_123"}
```

### POST `/billing/portal`
Redirect to Stripe billing portal.

### GET `/billing/usage`
Get current billing period usage.

---

## Webhook Endpoints

### POST `/webhooks/stripe`
Receives Stripe webhook events. Requires valid `Stripe-Signature` header.

**Subscribed Events:**
- `checkout.session.completed` — Provision attorney access
- `customer.subscription.updated` — Update tier
- `customer.subscription.deleted` — Revoke access
- `invoice.payment_succeeded` — Record billing event
- `invoice.payment_failed` — Alert + grace period

---

## Governance

All AI responses pass through the **Judge 6** governance pipeline before returning:

| Risk Level | Score | Action |
|-----------|-------|--------|
| 🟢 GREEN | 1-9 | Auto-approved |
| 🟡 AMBER | 10-15 | Approved with warning |
| 🔴 RED | 16-25 | Blocked — requires human review |

---

## Error Codes

| Status | Meaning |
|--------|---------|
| 400 | Bad request / invalid payload |
| 401 | Invalid or expired auth token |
| 403 | Missing Kovel authentication |
| 500 | Internal server error |

## Rate Limits
- **Trial:** 100 requests/day
- **Professional:** 1,000 requests/day
- **Enterprise:** Unlimited
