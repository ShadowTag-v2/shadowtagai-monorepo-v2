# Revenue Optimization for API Features

## Purpose
Maximize revenue from every API feature through strategic monetization, usage tracking, and conversion optimization. Every feature is an opportunity—never leave money on the table.

## When to Use This Skill
Activate when:
- Designing new API endpoints
- Reviewing existing features for revenue potential
- Implementing pricing tiers
- Adding usage tracking/billing
- Analyzing feature adoption
- Planning product strategy

## Core Revenue Doctrine

**Bootstrap Discipline:**
- ROI ≥3× within 18 months (required)
- LTV:CAC ≥4:1 within 12 months (required)
- Kill-switch on underperforming features
- Evidence-only decisions (data, not opinions)

**Revenue Awareness:**
Every feature session must answer:
1. What's the revenue model?
2. How do we track usage?
3. What's the upsell path?
4. How do we measure success?

## Monetization Strategy Matrix

### 1. Freemium Model
**Pattern**: Free tier with premium upgrades

```python
# app/models/pricing.py
from enum import Enum

class Tier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

# Feature gating configuration
TIER_LIMITS = {
    Tier.FREE: {
        "api_calls_per_month": 1000,
        "max_file_size_mb": 5,
        "features": ["basic_search", "export_json"],
        "rate_limit_per_minute": 10,
    },
    Tier.PRO: {
        "api_calls_per_month": 50000,
        "max_file_size_mb": 50,
        "features": ["basic_search", "advanced_search", "export_json", "export_csv", "webhooks"],
        "rate_limit_per_minute": 100,
        "priority_support": True,
    },
    Tier.ENTERPRISE: {
        "api_calls_per_month": -1,  # Unlimited
        "max_file_size_mb": 500,
        "features": ["*"],  # All features
        "rate_limit_per_minute": 1000,
        "priority_support": True,
        "custom_integrations": True,
        "sla": "99.9%",
    }
}


# app/core/feature_gates.py
from fastapi import HTTPException, status

async def check_feature_access(
    feature: str,
    current_user,
    upgrade_message: str = "Upgrade to access this feature"
):
    """Check if user tier has access to feature"""
    user_tier = current_user.subscription_tier
    allowed_features = TIER_LIMITS[user_tier]["features"]

    if "*" not in allowed_features and feature not in allowed_features:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": upgrade_message,
                "feature": feature,
                "current_tier": user_tier,
                "upgrade_url": f"/pricing?highlight={feature}",
                "required_tier": get_minimum_tier_for_feature(feature)
            }
        )


async def check_usage_quota(
    usage_type: str,
    amount: int,
    current_user
):
    """Check and enforce usage quotas"""
    user_tier = current_user.subscription_tier
    limit_key = f"{usage_type}_per_month"
    limit = TIER_LIMITS[user_tier].get(limit_key, 0)

    if limit == -1:  # Unlimited
        return

    current_usage = await get_current_usage(current_user.id, usage_type)

    if current_usage + amount > limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": f"Monthly {usage_type} quota exceeded",
                "current_usage": current_usage,
                "limit": limit,
                "upgrade_url": "/pricing",
                "percentage_used": (current_usage / limit) * 100
            }
        )

    # Track usage
    await increment_usage(current_user.id, usage_type, amount)


# Usage in endpoint
@router.post("/api/v1/advanced-search")
async def advanced_search(
    query: SearchQuery,
    current_user = Depends(get_current_active_user)
):
    """Advanced search (Pro+ feature)"""
    await check_feature_access("advanced_search", current_user)
    await check_usage_quota("api_calls", 1, current_user)

    results = await perform_advanced_search(query)
    return results
```

### 2. Usage-Based Pricing
**Pattern**: Pay per API call/resource

```python
# app/core/metering.py
from datetime import datetime
from decimal import Decimal

class UsageTracker:
    """Track billable API usage"""

    async def track_api_call(
        self,
        user_id: int,
        endpoint: str,
        cost_credits: Decimal = Decimal("1.0")
    ):
        """Record API call for billing"""
        usage_record = {
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "endpoint": endpoint,
            "credits": cost_credits,
            "billed": False
        }
        await save_usage_record(usage_record)

    async def track_resource_usage(
        self,
        user_id: int,
        resource_type: str,
        quantity: int,
        unit_cost: Decimal
    ):
        """Track resource consumption (storage, compute, etc.)"""
        total_cost = quantity * unit_cost
        usage_record = {
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "resource_type": resource_type,
            "quantity": quantity,
            "unit_cost": unit_cost,
            "total_cost": total_cost,
            "billed": False
        }
        await save_usage_record(usage_record)


# Pricing configuration
ENDPOINT_PRICING = {
    "/api/v1/basic-search": Decimal("0.001"),  # $0.001 per call
    "/api/v1/advanced-search": Decimal("0.01"),  # $0.01 per call
    "/api/v1/ai-analysis": Decimal("0.10"),  # $0.10 per call
    "/api/v1/bulk-export": Decimal("1.00"),  # $1.00 per export
}

RESOURCE_PRICING = {
    "storage_gb_month": Decimal("0.10"),  # $0.10 per GB/month
    "compute_hour": Decimal("0.50"),  # $0.50 per compute hour
    "api_call": Decimal("0.001"),  # $0.001 per API call
}


# Middleware to track all API usage
@app.middleware("http")
async def track_usage_middleware(request: Request, call_next):
    """Automatically track API usage for billing"""
    response = await call_next(request)

    # Only track authenticated requests
    if hasattr(request.state, "user"):
        user_id = request.state.user.id
        endpoint = request.url.path
        cost = ENDPOINT_PRICING.get(endpoint, Decimal("0.001"))

        tracker = UsageTracker()
        await tracker.track_api_call(user_id, endpoint, cost)

    return response
```

### 3. Tiered Feature Flags
**Pattern**: Gradual feature unlocks

```python
# app/core/feature_flags.py
from typing import Optional

class FeatureFlag:
    """Dynamic feature flags with tier-based access"""

    def __init__(self, name: str, minimum_tier: Tier):
        self.name = name
        self.minimum_tier = minimum_tier

    async def is_enabled_for_user(self, user) -> bool:
        """Check if feature is enabled for user"""
        tier_hierarchy = {
            Tier.FREE: 0,
            Tier.PRO: 1,
            Tier.ENTERPRISE: 2,
        }

        user_level = tier_hierarchy[user.subscription_tier]
        required_level = tier_hierarchy[self.minimum_tier]

        return user_level >= required_level


# Feature flag registry
FEATURES = {
    "webhooks": FeatureFlag("webhooks", Tier.PRO),
    "custom_branding": FeatureFlag("custom_branding", Tier.ENTERPRISE),
    "api_keys": FeatureFlag("api_keys", Tier.PRO),
    "sso": FeatureFlag("sso", Tier.ENTERPRISE),
    "audit_logs": FeatureFlag("audit_logs", Tier.ENTERPRISE),
}


async def require_feature(feature_name: str):
    """Dependency to check feature access"""
    async def check(current_user = Depends(get_current_active_user)):
        feature = FEATURES.get(feature_name)
        if not feature:
            raise ValueError(f"Unknown feature: {feature_name}")

        if not await feature.is_enabled_for_user(current_user):
            raise HTTPException(
                status_code=402,
                detail=f"Feature '{feature_name}' requires {feature.minimum_tier} tier"
            )

        return current_user
    return check


# Usage
@router.post("/api/v1/webhooks")
async def create_webhook(
    webhook: WebhookCreate,
    current_user = Depends(require_feature("webhooks"))
):
    """Create webhook (Pro+ feature)"""
    return await create_webhook_in_db(webhook, current_user.id)
```

### 4. Add-On Pricing
**Pattern**: Base service + optional expensive operations

```python
# app/core/addons.py
from decimal import Decimal

class AddOn:
    """Purchasable add-on features"""

    def __init__(
        self,
        name: str,
        price: Decimal,
        credits: int,
        description: str
    ):
        self.name = name
        self.price = price
        self.credits = credits
        self.description = description


# Add-on catalog
ADDONS = {
    "ai_analysis": AddOn(
        name="AI Analysis Pack",
        price=Decimal("49.99"),
        credits=100,
        description="100 AI-powered analysis credits"
    ),
    "export_credits": AddOn(
        name="Export Credits",
        price=Decimal("19.99"),
        credits=500,
        description="500 bulk export credits"
    ),
    "storage_boost": AddOn(
        name="Storage Boost",
        price=Decimal("9.99"),
        credits=100,  # 100GB
        description="Additional 100GB storage"
    ),
}


async def consume_credits(
    user_id: int,
    addon_type: str,
    amount: int = 1
):
    """Consume purchased add-on credits"""
    balance = await get_addon_balance(user_id, addon_type)

    if balance < amount:
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Insufficient credits",
                "addon": addon_type,
                "required": amount,
                "available": balance,
                "purchase_url": f"/addons/{addon_type}"
            }
        )

    await deduct_credits(user_id, addon_type, amount)


# Usage
@router.post("/api/v1/ai-analysis")
async def run_ai_analysis(
    data: AnalysisInput,
    current_user = Depends(get_current_active_user)
):
    """Run AI analysis (requires credits)"""
    await consume_credits(current_user.id, "ai_analysis", 1)

    result = await perform_ai_analysis(data)
    return result
```

## Conversion Funnel Optimization

### 1. Strategic Upgrade Prompts

```python
# app/core/conversion.py
from typing import Optional

async def create_upgrade_prompt(
    feature: str,
    user,
    context: Optional[dict] = None
) -> dict:
    """Generate contextual upgrade prompt"""
    current_tier = user.subscription_tier
    required_tier = get_minimum_tier_for_feature(feature)

    tier_pricing = {
        Tier.PRO: {"monthly": 29, "annual": 290},
        Tier.ENTERPRISE: {"monthly": 199, "annual": 1990},
    }

    prompt = {
        "message": f"Unlock {feature} with {required_tier}",
        "current_tier": current_tier,
        "required_tier": required_tier,
        "pricing": tier_pricing[required_tier],
        "features_unlocked": get_features_for_tier(required_tier),
        "cta": "Start Free Trial",
        "trial_days": 14,
        "urgency": None,
        "social_proof": await get_customer_count(required_tier),
    }

    # Add contextual urgency
    if context and context.get("usage_near_limit"):
        prompt["urgency"] = "You're at 90% of your free quota"

    # Add use case specific benefits
    if feature == "webhooks":
        prompt["benefit"] = "Automate workflows and integrate with your tools"

    return prompt


# Usage in endpoint error responses
@router.post("/api/v1/advanced-search")
async def advanced_search(query: SearchQuery, current_user = Depends(get_current_active_user)):
    try:
        await check_feature_access("advanced_search", current_user)
        # ... rest of logic
    except HTTPException as e:
        if e.status_code == 402:
            # Enhance error with conversion-optimized prompt
            upgrade_prompt = await create_upgrade_prompt(
                "advanced_search",
                current_user,
                context={"search_query": query.text}
            )
            e.detail.update({"upgrade_info": upgrade_prompt})
        raise e
```

### 2. Usage Analytics & Insights

```python
# app/analytics/revenue.py
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class RevenueMetrics:
    """Revenue performance metrics"""
    mrr: Decimal  # Monthly Recurring Revenue
    arr: Decimal  # Annual Recurring Revenue
    arpu: Decimal  # Average Revenue Per User
    ltv: Decimal  # Lifetime Value
    cac: Decimal  # Customer Acquisition Cost
    ltv_cac_ratio: Decimal
    churn_rate: Decimal


async def calculate_revenue_metrics(
    start_date: datetime,
    end_date: datetime
) -> RevenueMetrics:
    """Calculate key revenue metrics"""

    # MRR calculation
    active_subscriptions = await get_active_subscriptions(end_date)
    mrr = sum(sub.monthly_value for sub in active_subscriptions)

    # ARR
    arr = mrr * 12

    # ARPU
    total_users = await count_active_users(end_date)
    arpu = mrr / total_users if total_users > 0 else Decimal(0)

    # LTV (simplified: average monthly revenue * average customer lifetime)
    avg_lifetime_months = Decimal(24)  # Example: 2 years
    ltv = arpu * avg_lifetime_months

    # CAC (from marketing spend)
    new_customers = await count_new_customers(start_date, end_date)
    marketing_spend = await get_marketing_spend(start_date, end_date)
    cac = marketing_spend / new_customers if new_customers > 0 else Decimal(0)

    # LTV:CAC ratio
    ltv_cac_ratio = ltv / cac if cac > 0 else Decimal(0)

    # Churn rate
    churned = await count_churned_customers(start_date, end_date)
    beginning_customers = await count_active_users(start_date)
    churn_rate = churned / beginning_customers if beginning_customers > 0 else Decimal(0)

    return RevenueMetrics(
        mrr=mrr,
        arr=arr,
        arpu=arpu,
        ltv=ltv,
        cac=cac,
        ltv_cac_ratio=ltv_cac_ratio,
        churn_rate=churn_rate
    )


async def identify_expansion_opportunities(user_id: int) -> list[dict]:
    """Identify upsell/cross-sell opportunities"""
    user = await get_user(user_id)
    usage = await get_usage_stats(user_id, days=30)
    opportunities = []

    # Near quota limit
    if usage["api_calls"] > 0.8 * TIER_LIMITS[user.subscription_tier]["api_calls_per_month"]:
        opportunities.append({
            "type": "quota_upgrade",
            "message": "You're using 80% of your API quota",
            "action": "Upgrade to Pro for 50× more API calls",
            "urgency": "high"
        })

    # Using gated features
    blocked_feature_attempts = await get_blocked_features(user_id, days=30)
    if blocked_feature_attempts:
        opportunities.append({
            "type": "feature_unlock",
            "message": f"Unlock {len(blocked_feature_attempts)} features you've tried",
            "features": blocked_feature_attempts[:3],
            "action": "Start Pro trial",
            "urgency": "medium"
        })

    # High engagement, low tier
    if user.subscription_tier == Tier.FREE and usage["active_days"] >= 20:
        opportunities.append({
            "type": "power_user",
            "message": "You're a power user!",
            "action": "Upgrade to Pro and unlock your full potential",
            "urgency": "medium"
        })

    return opportunities
```

### 3. A/B Testing for Pricing

```python
# app/core/experiments.py
import hashlib

class PricingExperiment:
    """A/B test pricing variations"""

    def __init__(self, name: str, variants: dict):
        self.name = name
        self.variants = variants  # {"control": 29, "variant_a": 24, "variant_b": 34}

    def get_variant_for_user(self, user_id: int) -> str:
        """Consistent variant assignment based on user ID"""
        hash_input = f"{self.name}:{user_id}".encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        variant_index = hash_value % len(self.variants)
        return list(self.variants.keys())[variant_index]

    def get_price_for_user(self, user_id: int) -> Decimal:
        """Get price variant for user"""
        variant = self.get_variant_for_user(user_id)
        return Decimal(str(self.variants[variant]))


# Define experiments
PRICING_EXPERIMENTS = {
    "pro_tier_price": PricingExperiment(
        "pro_tier_price_q4_2025",
        {"control": 29, "low": 24, "high": 34}
    ),
    "annual_discount": PricingExperiment(
        "annual_discount_test",
        {"control": 0.17, "aggressive": 0.25, "conservative": 0.10}
    ),
}


@router.get("/api/v1/pricing")
async def get_pricing(current_user: Optional[User] = Depends(get_current_user_optional)):
    """Return pricing (with A/B test variants)"""
    if current_user:
        experiment = PRICING_EXPERIMENTS["pro_tier_price"]
        pro_price = experiment.get_price_for_user(current_user.id)

        # Track which variant shown
        await track_experiment_exposure(
            current_user.id,
            "pro_tier_price",
            experiment.get_variant_for_user(current_user.id)
        )
    else:
        pro_price = Decimal("29")  # Default for anonymous

    return {
        "tiers": {
            "free": {"price": 0, "features": TIER_LIMITS[Tier.FREE]},
            "pro": {"price": pro_price, "features": TIER_LIMITS[Tier.PRO]},
            "enterprise": {"price": "custom", "features": TIER_LIMITS[Tier.ENTERPRISE]},
        }
    }
```

## Billing Integration

```python
# app/integrations/stripe.py
import stripe
from decimal import Decimal

stripe.api_key = secrets.get_secret("stripe-api-key")


async def create_subscription(
    user_id: int,
    tier: Tier,
    payment_method_id: str,
    billing_cycle: str = "monthly"
) -> dict:
    """Create Stripe subscription"""

    user = await get_user(user_id)

    # Create or retrieve customer
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            metadata={"user_id": user_id}
        )
        await update_user_stripe_customer(user_id, customer.id)
    else:
        customer = stripe.Customer.retrieve(user.stripe_customer_id)

    # Attach payment method
    stripe.PaymentMethod.attach(
        payment_method_id,
        customer=customer.id
    )

    # Set as default
    stripe.Customer.modify(
        customer.id,
        invoice_settings={"default_payment_method": payment_method_id}
    )

    # Get price ID
    price_ids = {
        (Tier.PRO, "monthly"): "price_pro_monthly",
        (Tier.PRO, "annual"): "price_pro_annual",
        (Tier.ENTERPRISE, "monthly"): "price_enterprise_monthly",
        (Tier.ENTERPRISE, "annual"): "price_enterprise_annual",
    }
    price_id = price_ids[(tier, billing_cycle)]

    # Create subscription
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{"price": price_id}],
        metadata={"user_id": user_id, "tier": tier}
    )

    # Update user tier
    await update_user_subscription(
        user_id,
        tier=tier,
        stripe_subscription_id=subscription.id,
        billing_cycle=billing_cycle
    )

    return {
        "subscription_id": subscription.id,
        "status": subscription.status,
        "current_period_end": subscription.current_period_end,
    }


async def handle_usage_based_billing(user_id: int, period_start: datetime, period_end: datetime):
    """Calculate and report usage-based charges to Stripe"""

    usage_records = await get_usage_records(user_id, period_start, period_end, billed=False)

    total_amount = sum(record.total_cost for record in usage_records)

    if total_amount > 0:
        # Report usage to Stripe
        subscription = await get_user_subscription(user_id)

        stripe.InvoiceItem.create(
            customer=subscription.stripe_customer_id,
            amount=int(total_amount * 100),  # Convert to cents
            currency="usd",
            description=f"API usage for {period_start.date()} to {period_end.date()}"
        )

        # Mark records as billed
        await mark_usage_records_billed(usage_records)
```

## Revenue Review Checklist

**For every new feature:**

- [ ] Monetization strategy defined (freemium/usage/tier/addon)
- [ ] Usage tracking implemented
- [ ] Tier gates configured (if applicable)
- [ ] Quota limits set
- [ ] Upgrade prompts implemented
- [ ] Analytics events added
- [ ] A/B test planned (for pricing changes)
- [ ] ROI projection calculated (target ≥3×)
- [ ] LTV:CAC impact estimated
- [ ] Documentation updated (pricing page)

**For revenue analysis:**

- [ ] MRR/ARR tracked
- [ ] ARPU calculated
- [ ] LTV:CAC ratio measured (target ≥4:1)
- [ ] Churn rate monitored
- [ ] Expansion opportunities identified
- [ ] Kill-switch criteria defined

## Common Revenue Mistakes to Avoid

1. **Free Forever**: Not limiting free tier = burning money
2. **Invisible Value**: Not showing users what they're missing
3. **Soft Limits**: Warnings without enforcement = no urgency
4. **Missing Tracking**: Can't optimize what you don't measure
5. **Complex Pricing**: Confusion kills conversions
6. **No Upsell Path**: Every NO should include upgrade CTA
7. **Ignoring Churn**: Retention > Acquisition

## Success Metrics

**Bootstrap Compliance:**
- ROI ≥3× in 18 months ✅
- LTV:CAC ≥4:1 in 12 months ✅
- Usage tracking on 100% of endpoints ✅
- Conversion funnel measured at each stage ✅

**Revenue Velocity:**
- Feature → Monetization time: <1 week
- Pricing experiment cycle: <2 weeks
- Revenue decision based on data (not opinions)

---

**Remember**: Every feature is a revenue opportunity. Track everything. Test constantly. Kill ruthlessly what doesn't deliver ROI.
