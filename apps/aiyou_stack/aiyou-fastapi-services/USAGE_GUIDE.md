# Growth Engineer - Usage Guide

This guide provides detailed examples of how to use the Growth Engineer agent for various growth engineering tasks.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Analyzing User Hooks](#analyzing-user-hooks)
3. [Designing Viral Loops](#designing-viral-loops)
4. [Creating A/B Tests](#creating-ab-tests)
5. [Analyzing Growth Metrics](#analyzing-growth-metrics)
6. [Designing Engagement Features](#designing-engagement-features)
7. [Implementing Analytics](#implementing-analytics)
8. [Optimizing Referral Systems](#optimizing-referral-systems)
9. [General Queries](#general-queries)

## Getting Started

### Prerequisites

1. Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

1. Verify the server is running:

```bash
curl http://localhost:8000/health
```

### Authentication

Currently, the API doesn't require authentication, but you'll need to configure your `ANTHROPIC_API_KEY` in the `.env` file for the agent to work.

## Analyzing User Hooks

User hooks are the moments where users get engaged and find value in your product.

### Example: E-commerce App

```bash
curl -X POST "http://localhost:8000/api/v1/growth/analyze/user-hooks" \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "ShopEasy",
    "user_flows": [
      {"step": "landing", "conversion_rate": 0.85, "drop_off": 0.15},
      {"step": "browse_products", "conversion_rate": 0.70, "drop_off": 0.15},
      {"step": "add_to_cart", "conversion_rate": 0.40, "drop_off": 0.30},
      {"step": "checkout", "conversion_rate": 0.60, "drop_off": 0.40},
      {"step": "purchase", "conversion_rate": 0.95, "drop_off": 0.05}
    ],
    "current_features": [
      "product_recommendations",
      "wishlist",
      "one_click_checkout",
      "price_alerts"
    ],
    "metrics": {
      "dau": 5000,
      "mau": 25000,
      "retention_d7": 0.25,
      "retention_d30": 0.15,
      "avg_order_value": 75.50
    },
    "goals": [
      "improve_cart_conversion",
      "increase_repeat_purchases",
      "reduce_checkout_abandonment"
    ]
  }'
```

### Example: SaaS Product

```python
import httpx
import asyncio

async def analyze_saas_hooks():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/growth/analyze/user-hooks",
            json={
                "app_name": "ProjectManager Pro",
                "user_flows": [
                    {"step": "signup", "conversion_rate": 0.75},
                    {"step": "team_setup", "conversion_rate": 0.50},
                    {"step": "first_project", "conversion_rate": 0.60},
                    {"step": "invite_teammate", "conversion_rate": 0.30},
                    {"step": "active_usage", "conversion_rate": 0.70}
                ],
                "current_features": [
                    "kanban_boards",
                    "time_tracking",
                    "team_chat",
                    "file_sharing"
                ],
                "metrics": {
                    "trial_users": 1000,
                    "activated_users": 400,
                    "paid_conversions": 120,
                    "retention_d30": 0.55
                },
                "goals": [
                    "increase_activation",
                    "improve_trial_conversion",
                    "boost_team_invites"
                ]
            }
        )
        return response.json()

result = asyncio.run(analyze_saas_hooks())
print(result)
```

## Designing Viral Loops

Viral loops create self-sustaining growth where users bring in more users.

### Example: Social Network

```bash
curl -X POST "http://localhost:8000/api/v1/growth/design/viral-loop" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "ConnectHub",
    "value_proposition": "Professional networking that actually works",
    "target_audience": "Young professionals and entrepreneurs",
    "current_users": 10000,
    "sharing_incentive": "Premium features for successful referrals",
    "constraints": [
      "mobile_first",
      "privacy_focused",
      "no_spam"
    ]
  }'
```

### Example: Content Platform

```python
from app.agents import GrowthEngineerAgent
import asyncio

async def design_content_loop():
    agent = GrowthEngineerAgent()

    result = await agent.design_viral_loop({
        "product_name": "CreatorSpace",
        "value_proposition": "Monetize your content, grow your audience",
        "target_audience": "Content creators and influencers",
        "current_users": 5000,
        "sharing_incentive": "Revenue sharing for referred creators",
        "constraints": [
            "creator_friendly",
            "fair_monetization",
            "quality_content_only"
        ]
    })

    return result

result = asyncio.run(design_content_loop())
```

## Creating A/B Tests

Design statistically valid experiments to test growth hypotheses.

### Example: Onboarding Optimization

```bash
curl -X POST "http://localhost:8000/api/v1/growth/experiment/ab-test" \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_name": "Simplified_Onboarding_V3",
    "hypothesis": "Reducing onboarding steps from 5 to 3 increases activation by 20%",
    "variants": [
      {
        "name": "control",
        "description": "Current 5-step onboarding with profile setup, preferences, tutorial, team invite, and first action"
      },
      {
        "name": "treatment_a",
        "description": "3-step onboarding: quick signup, essential preferences, first action"
      },
      {
        "name": "treatment_b",
        "description": "2-step onboarding: signup and immediate value delivery"
      }
    ],
    "primary_metric": "activation_rate",
    "secondary_metrics": [
      "time_to_first_value",
      "completion_rate",
      "d7_retention"
    ],
    "expected_effect_size": 0.20,
    "traffic_allocation": {
      "control": 0.40,
      "treatment_a": 0.30,
      "treatment_b": 0.30
    }
  }'
```

### Example: Pricing Page Test

```python
async def test_pricing_page():
    agent = GrowthEngineerAgent()

    result = await agent.create_ab_test({
        "experiment_name": "Pricing_Annual_Highlight",
        "hypothesis": "Highlighting annual savings increases annual plan selection by 25%",
        "variants": [
            {
                "name": "control",
                "description": "Standard pricing table with monthly/annual toggle"
            },
            {
                "name": "treatment",
                "description": "Annual option highlighted with savings badge and 'Most Popular' label"
            }
        ],
        "primary_metric": "annual_plan_selection_rate",
        "secondary_metrics": [
            "total_conversions",
            "average_contract_value",
            "time_on_pricing_page"
        ],
        "expected_effect_size": 0.25,
        "traffic_allocation": {
            "control": 0.5,
            "treatment": 0.5
        }
    })

    return result
```

## Analyzing Growth Metrics

Get insights and recommendations from your growth data.

### Example: Comprehensive Metrics Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/growth/analyze/metrics" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": {
      "signups": 2500,
      "activated_users": 1200,
      "dau": 800,
      "mau": 4000,
      "retention_d1": 0.65,
      "retention_d7": 0.35,
      "retention_d30": 0.20,
      "viral_coefficient": 0.45,
      "referral_rate": 0.15,
      "conversion_rate": 0.48,
      "churn_rate": 0.08
    },
    "time_period": "last_30_days",
    "goals": [
      "reach_10000_mau",
      "achieve_40_percent_d7_retention",
      "increase_viral_coefficient_above_1"
    ],
    "benchmarks": {
      "retention_d7": 0.40,
      "retention_d30": 0.25,
      "viral_coefficient": 0.60,
      "activation_rate": 0.50
    }
  }'
```

## Designing Engagement Features

Create features that boost engagement and retention.

### Example: Gamification Feature

```bash
curl -X POST "http://localhost:8000/api/v1/growth/design/engagement-feature" \
  -H "Content-Type: application/json" \
  -d '{
    "feature_type": "gamification",
    "objective": "Increase daily active usage by 35% through achievement system",
    "target_users": "All users, with focus on users with 3-14 day tenure",
    "constraints": [
      "mobile_friendly",
      "not_annoying",
      "meaningful_rewards"
    ],
    "existing_features": [
      "user_profiles",
      "activity_feed",
      "leaderboard",
      "badges"
    ]
  }'
```

### Example: Notification System

```python
async def design_notification_system():
    agent = GrowthEngineerAgent()

    result = await agent.design_engagement_feature({
        "feature_type": "smart_notifications",
        "objective": "Re-engage dormant users and reduce churn by 20%",
        "target_users": "Users inactive for 7+ days",
        "constraints": [
            "respect_user_preferences",
            "multi_channel",
            "personalized",
            "not_spammy"
        ],
        "existing_features": [
            "email_system",
            "push_notifications",
            "in_app_messages"
        ]
    })

    return result
```

## Implementing Analytics

Set up comprehensive tracking for growth metrics.

### Example: Event Tracking Setup

```bash
curl -X POST "http://localhost:8000/api/v1/growth/implement/analytics" \
  -H "Content-Type: application/json" \
  -d '{
    "events_to_track": [
      {
        "name": "user_signup",
        "properties": ["source", "device", "referrer", "signup_method"]
      },
      {
        "name": "user_activated",
        "properties": ["time_to_activation", "activation_action", "device"]
      },
      {
        "name": "feature_used",
        "properties": ["feature_name", "usage_duration", "success"]
      },
      {
        "name": "referral_sent",
        "properties": ["channel", "incentive_type", "recipient_count"]
      },
      {
        "name": "purchase_completed",
        "properties": ["plan_type", "amount", "payment_method"]
      }
    ],
    "metrics_needed": [
      "daily_active_users",
      "monthly_active_users",
      "activation_rate",
      "retention_cohorts",
      "funnel_conversion",
      "viral_coefficient",
      "revenue_metrics"
    ],
    "platform": "web_and_mobile",
    "tools": ["mixpanel", "segment"],
    "compliance_requirements": ["gdpr", "ccpa", "privacy_shield"]
  }'
```

## Optimizing Referral Systems

Improve existing referral programs.

### Example: Referral Optimization

```bash
curl -X POST "http://localhost:8000/api/v1/growth/optimize/referral" \
  -H "Content-Type: application/json" \
  -d '{
    "referral_metrics": {
      "invites_sent": 5000,
      "invites_clicked": 1500,
      "signups_from_referrals": 500,
      "activated_referrals": 250,
      "referrer_conversion": 0.20,
      "average_referrals_per_user": 2.5
    },
    "referral_flow": [
      "referral_button_click",
      "share_modal_open",
      "channel_selection",
      "message_customization",
      "share_action",
      "friend_click",
      "friend_signup",
      "friend_activation",
      "reward_delivery"
    ],
    "incentives": {
      "referrer_reward": "1 month free premium",
      "referee_reward": "20% off first month",
      "milestone_bonus": "3 referrals = 3 months free"
    },
    "issues": [
      "low_click_through_rate",
      "high_dropoff_at_signup",
      "delayed_reward_delivery",
      "unclear_value_proposition"
    ]
  }'
```

## General Queries

Ask any growth engineering question.

### Example: General Growth Question

```bash
curl -X POST "http://localhost:8000/api/v1/growth/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How can I improve my product'\''s viral coefficient from 0.4 to above 1.0?",
    "context": {
      "product_type": "collaboration_tool",
      "current_k_factor": 0.4,
      "current_users": 10000,
      "stage": "growth",
      "constraints": ["limited_budget", "small_team"]
    }
  }'
```

### Example: Complex Growth Strategy

```python
async def ask_growth_strategy():
    agent = GrowthEngineerAgent()

    result = await agent.general_growth_query(
        user_query="""
        I need a comprehensive growth strategy for my B2B SaaS product.
        Current metrics:
        - 1000 trial signups/month
        - 15% trial-to-paid conversion
        - 60% annual retention
        - $200 MRR per customer
        - 2.0 viral coefficient on paid users

        Goals:
        - Double MRR in 6 months
        - Improve trial conversion to 25%
        - Reduce CAC by 30%

        What should I focus on?
        """,
        context={
            "industry": "project_management",
            "team_size": 5,
            "budget": "50k_monthly",
            "tech_stack": ["python", "react", "postgresql"]
        }
    )

    return result
```

## Best Practices

### 1. Start with Analysis

Always analyze your current state before implementing changes:

- Understand your user hooks
- Know your current metrics
- Identify bottlenecks

### 2. Test Everything

Use A/B testing for all significant changes:

- Design proper experiments
- Calculate required sample sizes
- Wait for statistical significance

### 3. Focus on Value

Ensure growth tactics enhance user value:

- No dark patterns
- Authentic engagement
- Sustainable growth

### 4. Measure Impact

Track the right metrics:

- Primary metrics (activation, retention)
- Secondary metrics (engagement, virality)
- Business metrics (revenue, LTV/CAC)

### 5. Iterate Quickly

Run rapid experiments:

- Small, focused tests
- Quick iterations
- Learn and adapt

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure `ANTHROPIC_API_KEY` is set in `.env`
   - Verify the key is valid

2. **Timeout Errors**
   - Complex queries may take longer
   - Consider increasing timeout settings

3. **Invalid Request**
   - Check request schema matches examples
   - Validate JSON syntax

## Next Steps

1. Start with user hook analysis
2. Design your first viral loop
3. Set up A/B testing framework
4. Implement analytics tracking
5. Monitor and optimize continuously

For more examples and advanced usage, check the API documentation at `/docs`.
