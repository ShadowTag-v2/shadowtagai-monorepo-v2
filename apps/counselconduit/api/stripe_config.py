# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# apps/counselconduit/api/stripe_config.py
"""Stripe Product & Price Configuration — LIVE IDs.

Created 2026-04-17. All IDs are production (live mode).
Stripe Account: acct_1Syh9JEHnWpykeMi (US)
"""

# ── Products ──
PRODUCT_TRIAL = "prod_UM2XwCF1byjegL"
PRODUCT_PROFESSIONAL = "prod_UM2X10cpyay52e"
PRODUCT_ENTERPRISE = "prod_UM2XMVp9Er7A0i"

# ── Prices ──
PRICE_PRO_MONTHLY = "price_1TNKSREHnWpykeMiRMDlVgLl"  # $149/mo
PRICE_PRO_ANNUAL = "price_1TNKSjEHnWpykeMi0S9GCVjy"  # $1,428/yr ($119/mo)
PRICE_ENT_MONTHLY = "price_1TNKSREHnWpykeMi8mrDf4rI"  # $20,000/mo

# ── Coupons ──
COUPON_BETA_50 = "3wseBY7Z"  # 50% off, 3 months, max 100 redemptions

# ── Customer Portal ──
PORTAL_CONFIG_ID = "bpc_1TNKSjEHnWpykeMi0qQPoaHm"

# ── Webhook Endpoint ──
WEBHOOK_ENDPOINT_ID = "we_1TNKSjEHnWpykeMiQZqmpy3X"
WEBHOOK_URL = "https://counselconduit-api.run.app/webhooks/stripe"

# ── Tier → Price Mapping ──
TIER_PRICES = {
    "professional_monthly": PRICE_PRO_MONTHLY,
    "professional_annual": PRICE_PRO_ANNUAL,
    "enterprise_monthly": PRICE_ENT_MONTHLY,
}

# ── Tier → Token Limits ──
TIER_TOKEN_LIMITS = {
    "trial": 10_000,
    "professional": 100_000,
    "enterprise": 1_000_000,
}
