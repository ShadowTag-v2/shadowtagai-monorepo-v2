# API Guide - Revenue Optimizer

Complete guide to using the Revenue Optimizer API.

## Authentication

Currently, the API does not require authentication. In production, implement JWT authentication or API keys.

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## Content Type

All requests should use `Content-Type: application/json`

## Pricing Tiers API

### List All Pricing Tiers

Get all available pricing tiers.

**Request:**

```http
GET /api/v1/pricing/tiers
```

**Query Parameters:**

- `active_only` (boolean, optional): Filter to only active tiers (default: true)

**Response:**

```json
[
  {
    "id": "tier_123",
    "name": "Professional",
    "slug": "professional",
    "description": "For growing businesses",
    "price": 49.99,
    "currency": "USD",
    "billing_interval": "monthly",
    "stripe_price_id": "price_abc",
    "api_requests_limit": 100000,
    "storage_limit_gb": 100,
    "user_seats": 10,
    "trial_period_days": 14,
    "is_trial_enabled": true,
    "is_active": true,
    "is_popular": false,
    "is_recommended": true,
    "features": ["Feature 1", "Feature 2"],
    "pricing_features": [
      {
        "id": "feat_1",
        "name": "Unlimited API calls",
        "is_included": true
      }
    ],
    "created_at": "2025-01-15T10:00:00Z"
  }
]
```

### Create Pricing Tier

Create a new pricing tier.

**Request:**

```http
POST /api/v1/pricing/tiers
```

**Body:**

```json
{
  "name": "Enterprise",
  "slug": "enterprise",
  "description": "For large organizations",
  "price": 199.99,
  "currency": "USD",
  "billing_interval": "monthly",
  "api_requests_limit": 1000000,
  "storage_limit_gb": 1000,
  "user_seats": 50,
  "trial_period_days": 14,
  "is_recommended": false,
  "features": ["Priority Support", "Custom Integration"]
}
```

**Response:**

```json
{
  "id": "tier_456",
  "name": "Enterprise",
  ...
}
```

## Subscriptions API

### Create Subscription

Create a new subscription for a user.

**Request:**

```http
POST /api/v1/subscriptions
```

**Body:**

```json
{
  "user_id": "user_123",
  "pricing_tier_id": "tier_abc",
  "start_trial": true,
  "stripe_customer_id": "cus_xyz"
}
```

**Response:**

```json
{
  "id": "sub_789",
  "user_id": "user_123",
  "pricing_tier_id": "tier_abc",
  "status": "trial",
  "is_active": true,
  "trial_start": "2025-01-15T10:00:00Z",
  "trial_end": "2025-01-29T10:00:00Z",
  "api_requests_used": "0",
  "storage_used_gb": "0",
  "created_at": "2025-01-15T10:00:00Z"
}
```

### Get User Subscription

Get the current subscription for a user.

**Request:**

```http
GET /api/v1/subscriptions/user/{user_id}
```

**Response:**

```json
{
  "id": "sub_789",
  "user_id": "user_123",
  "status": "active",
  ...
}
```

### Upgrade Subscription

Change subscription to a different pricing tier.

**Request:**

```http
PATCH /api/v1/subscriptions/{subscription_id}/upgrade
```

**Body:**

```json
{
  "pricing_tier_id": "tier_premium"
}
```

### Cancel Subscription

Cancel a subscription.

**Request:**

```http
POST /api/v1/subscriptions/{subscription_id}/cancel
```

**Body:**

```json
{
  "reason": "User requested cancellation",
  "immediate": false
}
```

- `immediate`: If true, cancel immediately. If false, cancel at period end.

## Payments API

### Create Checkout Session

Create a Stripe Checkout session for subscription signup.

**Request:**

```http
POST /api/v1/payments/checkout/session
```

**Body:**

```json
{
  "user_id": "user_123",
  "pricing_tier_id": "tier_abc",
  "success_url": "https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
  "cancel_url": "https://example.com/cancel",
  "customer_email": "customer@example.com",
  "trial_enabled": true
}
```

**Response:**

```json
{
  "session_id": "cs_test_abc123",
  "url": "https://checkout.stripe.com/c/pay/cs_test_abc123",
  "expires_at": "2025-01-15T11:00:00Z"
}
```

**Usage:**
Redirect the user to the `url` to complete checkout.

### Create Payment Intent

Create a one-time payment intent.

**Request:**

```http
POST /api/v1/payments/intent
```

**Body:**

```json
{
  "amount": 99.99,
  "currency": "USD",
  "user_id": "user_123",
  "description": "One-time payment for service",
  "metadata": {
    "order_id": "order_456"
  }
}
```

**Response:**

```json
{
  "payment_intent_id": "pi_abc123",
  "client_secret": "pi_abc123_secret_xyz",
  "status": "requires_payment_method"
}
```

### Create Refund

Refund a payment.

**Request:**

```http
POST /api/v1/payments/refund
```

**Body:**

```json
{
  "payment_id": "pay_123",
  "amount": 49.99,
  "reason": "Customer requested refund"
}
```

- `amount`: Optional. If not provided, full refund is issued.

## Revenue API

### Get Revenue Summary

Get comprehensive revenue summary for a period.

**Request:**

```http
GET /api/v1/revenue/summary?start_date=2025-01-01T00:00:00Z&end_date=2025-01-31T23:59:59Z
```

**Response:**

```json
{
  "period": {
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-01-31T23:59:59Z"
  },
  "revenue": {
    "gross_revenue": 15000.0,
    "net_revenue": 14250.0,
    "refunds": 500.0,
    "fees": 250.0
  },
  "recurring_revenue": {
    "mrr": 12000.0,
    "arr": 144000.0
  },
  "subscriptions": {
    "active_count": 250,
    "churn_rate": 2.5
  }
}
```

### Get MRR (Monthly Recurring Revenue)

**Request:**

```http
GET /api/v1/revenue/mrr
```

**Response:**

```json
{
  "mrr": 12000.0,
  "currency": "USD",
  "date": "2025-01-15T10:00:00Z"
}
```

### Get ARR (Annual Recurring Revenue)

**Request:**

```http
GET /api/v1/revenue/arr
```

**Response:**

```json
{
  "arr": 144000.0,
  "currency": "USD",
  "date": "2025-01-15T10:00:00Z"
}
```

### Get Churn Rate

**Request:**

```http
GET /api/v1/revenue/churn-rate?start_date=2025-01-01T00:00:00Z&end_date=2025-01-31T23:59:59Z
```

**Response:**

```json
{
  "churn_rate": 2.5,
  "period": {
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-01-31T23:59:59Z"
  }
}
```

### Get Customer Lifetime Value

**Request:**

```http
GET /api/v1/revenue/ltv/user_123
```

**Response:**

```json
{
  "user_id": "user_123",
  "lifetime_value": 599.88,
  "currency": "USD"
}
```

### Get Revenue Dashboard

**Request:**

```http
GET /api/v1/revenue/dashboard?days=30
```

**Response:**

```json
{
  "summary": {
    "period": {...},
    "revenue": {...},
    "recurring_revenue": {...},
    "subscriptions": {...}
  },
  "key_metrics": {
    "mrr": 12000.00,
    "arr": 144000.00,
    "churn_rate": 2.5
  },
  "period_days": 30
}
```

## Webhooks

### Stripe Webhook

Endpoint for receiving Stripe webhook events.

**Request:**

```http
POST /api/v1/webhooks/stripe
```

**Headers:**

- `Stripe-Signature`: Webhook signature for verification

**Supported Events:**

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`
- `customer.subscription.trial_will_end`

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content returned
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

Currently no rate limiting. Implement in production.

## Pagination

For endpoints returning lists, pagination can be added:

```http
GET /api/v1/pricing/tiers?page=1&per_page=20
```

(To be implemented)

## Filtering and Sorting

Many endpoints support filtering and sorting:

```http
GET /api/v1/subscriptions?status=active&sort=created_at&order=desc
```

(To be implemented)

## Best Practices

1. **Idempotency**: Use unique idempotency keys for payment operations
2. **Webhooks**: Always verify webhook signatures
3. **Error Handling**: Handle all error responses gracefully
4. **Retries**: Implement exponential backoff for retries
5. **Testing**: Use Stripe test mode for development
