# pnkln Integration Plan: ShadowTag v2 × UltraThink Framework

**Technical Architecture for Compound Revenue System**
**Date**: 2025-11-18
**Mode**: Bourne/160 STRICT

---

## Executive Summary

This document outlines the technical integration of:
1. **ShadowTag v2** - Dual-layer watermarking (this branch)
2. **UltraThink Framework** - AI orchestration (`claude/pnkln-ultrathink-framework-01SX9cmBe23YZ7WxueesKzw5`)
3. **Referenced initiatives** - Kernel chaining, Gemini migration, superpowers marketplace, etc.

**Goal**: Create unified AI Content Authenticity Platform with embedded revenue intelligence.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│            pnkln CONTENT AUTHENTICITY PLATFORM               │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
         ┌──────▼──────┐            ┌───────▼──────┐
         │ SHADOWTAG   │            │  ULTRATHINK  │
         │     v2      │◄───────────┤  FRAMEWORK   │
         └─────────────┘            └──────────────┘
                │                           │
    ┌───────────┼───────────┐      ┌────────┼────────┐
    │           │           │      │        │        │
┌───▼───┐  ┌───▼───┐  ┌────▼───┐ ┌▼────┐ ┌▼─────┐ ┌▼────┐
│Video  │  │Audio  │  │Receipt │ │Desig│ │Wealth│ │Monet│
│Stego  │  │Stego  │  │Chain   │ │ner  │ │Accel.│ │Arch.│
└───────┘  └───────┘  └────────┘ └─────┘ └──────┘ └─────┘
     │          │           │         │       │        │
     └──────────┴───────────┴─────────┴───────┴────────┘
                              │
                    ┌─────────▼──────────┐
                    │  UNIFIED FASTAPI   │
                    │    /api/v2/*       │
                    └────────────────────┘
```

---

## Directory Structure (Post-Integration)

```
pnkln-stack-fastapi-services/
├── shadowtag_v2/              # Content watermarking
│   ├── video_stego.py
│   ├── audio_stego.py
│   ├── receipt_chain.py
│   └── cli.py
│
├── ultrathink/                # AI orchestration (merged from branch)
│   ├── core/
│   │   ├── orchestrator.py
│   │   └── skills.py
│   ├── agents/
│   │   ├── designer.py       # UltraThink Designer
│   │   ├── wealth.py         # Wealth Accelerator
│   │   └── registry.yaml
│   └── cli.py
│
├── api/                       # Unified FastAPI service
│   ├── main.py               # Main app
│   ├── v1/                   # ShadowTag v2 endpoints
│   │   ├── watermark.py
│   │   └── verify.py
│   ├── v2/                   # Integrated platform endpoints
│   │   ├── content.py        # Full content authenticity flow
│   │   ├── agents.py         # UltraThink agent execution
│   │   └── marketplace.py    # Skills/data marketplace
│   ├── billing/
│   │   ├── stripe.py         # Stripe integration
│   │   ├── usage.py          # Usage tracking
│   │   └── tiers.py          # Pricing tiers
│   └── models.py
│
├── integration/               # Cross-system integration
│   ├── content_pipeline.py   # Creator workflow orchestration
│   ├── revenue_engine.py     # Monetization intelligence
│   └── data_flywheel.py      # Corpus management
│
├── marketplace/               # Skills/data marketplace
│   ├── skills_registry.py
│   ├── licensing.py
│   └── analytics.py
│
├── tests/
│   ├── test_shadowtag/
│   ├── test_ultrathink/
│   ├── test_integration/
│   └── test_marketplace/
│
├── docs/
│   ├── MONEY_CHANGES.md      # Revenue strategy (THIS)
│   ├── INTEGRATION_PLAN.md   # This document
│   └── OPERATIONS.md
│
└── notebooks/
    ├── shadowtag_v2_vertex_workbench.ipynb
    └── ultrathink_demos.ipynb
```

---

## Integration Phases

### Phase 1: Merge Codebases (Week 1)

#### 1.1 Fetch UltraThink Framework

```bash
# Checkout ultrathink branch
git fetch origin claude/pnkln-ultrathink-framework-01SX9cmBe23YZ7WxueesKzw5

# Create integration branch
git checkout -b claude/integration-shadowtag-ultrathink-011HjffkzypaspRcDZL1uXf1

# Merge ultrathink framework
git merge origin/claude/pnkln-ultrathink-framework-01SX9cmBe23YZ7WxueesKzw5 --allow-unrelated-histories
```

#### 1.2 Restructure Directories

```bash
# Move pnkln-framework → ultrathink
mv pnkln-framework ultrathink

# Update imports in ultrathink/
find ultrathink -type f -name "*.py" -exec sed -i 's/from core\./from ultrathink.core./g' {} +
find ultrathink -type f -name "*.py" -exec sed -i 's/from agents\./from ultrathink.agents./g' {} +
```

#### 1.3 Merge Requirements

```bash
# Combine requirements
cat ultrathink/requirements.txt >> requirements.txt
sort -u requirements.txt -o requirements.txt

# Update pyproject.toml
# Add ultrathink dependencies
```

#### 1.4 Update CI/CD

```yaml
# .github/workflows/ci.yml - add ultrathink tests
- name: Run UltraThink tests
  run: pytest tests/test_ultrathink/ -v

- name: Run Integration tests
  run: pytest tests/test_integration/ -v
```

---

### Phase 2: API Integration (Week 2)

#### 2.1 Create Unified Endpoints

**File**: `api/v2/content.py`

```python
"""
Unified content authenticity + monetization endpoint.
Combines ShadowTag v2 watermarking with UltraThink revenue intelligence.
"""

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from shadowtag_v2 import embed_video_watermark, VideoWatermarkConfig
from ultrathink.core import pnklnOrchestrator
from api.billing import track_usage, check_tier_limits

router = APIRouter(prefix="/v2/content", tags=["Content Platform"])


class ContentRequest(BaseModel):
    """Request for full content authenticity flow."""
    prompt: str
    optimize_for_virality: bool = False
    suggest_monetization: bool = False
    create_blockchain_receipt: bool = False


@router.post("/process")
async def process_content(
    file: UploadFile,
    request: ContentRequest,
    user_id: str,  # From auth middleware
):
    """
    Full content authenticity pipeline:
    1. Optionally optimize content for virality (UltraThink Designer)
    2. Optionally suggest monetization strategies (Wealth Accelerator)
    3. Embed watermark (ShadowTag v2)
    4. Optionally create blockchain receipt
    5. Return content + revenue intelligence
    """
    # Check user tier limits
    tier_limits = check_tier_limits(user_id)
    if not tier_limits.can_watermark:
        raise HTTPException(429, "Tier limit exceeded")

    # Save uploaded file
    input_path = save_upload(file)

    results = {}

    # Step 1: Content optimization (if requested)
    if request.optimize_for_virality:
        orchestrator = pnklnOrchestrator()
        optimization = orchestrator.execute(
            prompt=f"Optimize this content for maximum social media virality: {request.prompt}",
            agent_id="ultrathink_designer"
        )
        results["optimization"] = optimization.output

    # Step 2: Monetization strategy (if requested)
    if request.suggest_monetization:
        orchestrator = pnklnOrchestrator()
        monetization = orchestrator.execute(
            prompt=f"Design monetization strategy for: {request.prompt}",
            agent_id="wealth_accelerator"
        )
        results["monetization"] = monetization.output
        results["revenue_identified_usd"] = monetization.metrics.get("revenue_identified_usd", 0)

    # Step 3: Watermark embedding
    output_path = get_output_path(user_id, file.filename)
    watermark_result = embed_video_watermark(
        input_path, output_path, request.prompt, VideoWatermarkConfig()
    )
    results["watermark"] = watermark_result

    # Step 4: Blockchain receipt (if requested)
    if request.create_blockchain_receipt:
        receipt = create_blockchain_receipt(request.prompt, get_blockchain_config())
        results["blockchain_receipt"] = receipt

    # Track usage for billing
    track_usage(user_id, "watermark", watermark_result)

    return {
        "ok": True,
        "output_url": f"/api/v2/download/{output_path.name}",
        "results": results
    }
```

#### 2.2 Agent Execution Endpoint

**File**: `api/v2/agents.py`

```python
"""UltraThink agent execution API."""

from fastapi import APIRouter
from pydantic import BaseModel

from ultrathink.core import pnklnOrchestrator

router = APIRouter(prefix="/v2/agents", tags=["AI Orchestration"])


class AgentRequest(BaseModel):
    prompt: str
    agent_id: str = "ultrathink_designer"  # or "wealth_accelerator"


@router.post("/execute")
async def execute_agent(request: AgentRequest, user_id: str):
    """Execute UltraThink agent with prompt."""
    # Check tier limits
    tier_limits = check_tier_limits(user_id)
    if not tier_limits.can_execute_agents:
        raise HTTPException(429, "Tier limit exceeded")

    # Execute agent
    orchestrator = pnklnOrchestrator()
    result = orchestrator.execute(
        prompt=request.prompt,
        agent_id=request.agent_id
    )

    # Track usage
    track_usage(user_id, "agent_execution", result)

    return {
        "ok": True,
        "output": result.output,
        "activated_skills": result.activated_skills,
        "metrics": result.metrics,
        "audit_hash": result.audit_hash
    }
```

#### 2.3 Billing Integration

**File**: `api/billing/stripe.py`

```python
"""Stripe integration for tiered pricing."""

import stripe
from api.config import settings

stripe.api_key = settings.stripe_secret_key


TIERS = {
    "free": {
        "watermarks_per_month": 10,
        "agent_executions_per_month": 0,
        "features": ["video_watermark"],
        "price_usd": 0,
    },
    "creator": {
        "watermarks_per_month": 1000,
        "agent_executions_per_month": 100,
        "features": ["video_watermark", "audio_watermark", "blockchain_testnet"],
        "price_usd": 29,
        "stripe_price_id": "price_creator_monthly",
    },
    "pro": {
        "watermarks_per_month": 10000,
        "agent_executions_per_month": 1000,
        "features": ["all", "blockchain_mainnet", "custom_configs", "webhooks"],
        "price_usd": 99,
        "stripe_price_id": "price_pro_monthly",
    },
    "enterprise": {
        "watermarks_per_month": -1,  # Unlimited
        "agent_executions_per_month": -1,
        "features": ["all", "white_label", "sla", "dedicated_support"],
        "price_usd": 500,  # Starting price, custom quotes
        "stripe_price_id": "price_enterprise_monthly",
    },
}


async def create_checkout_session(user_id: str, tier: str):
    """Create Stripe checkout session for tier upgrade."""
    tier_config = TIERS.get(tier)
    if not tier_config or tier == "free":
        raise ValueError("Invalid tier")

    session = stripe.checkout.Session.create(
        customer_email=get_user_email(user_id),
        payment_method_types=["card"],
        line_items=[{
            "price": tier_config["stripe_price_id"],
            "quantity": 1,
        }],
        mode="subscription",
        success_url=f"{settings.frontend_url}/billing/success",
        cancel_url=f"{settings.frontend_url}/billing/cancel",
        metadata={"user_id": user_id, "tier": tier},
    )

    return session
```

**File**: `api/billing/usage.py`

```python
"""Usage tracking for billing."""

from datetime import datetime, timezone
from typing import Dict, Any

import redis

redis_client = redis.Redis.from_url(settings.redis_url)


def track_usage(user_id: str, action: str, metadata: Dict[str, Any]):
    """Track usage event for billing."""
    key = f"usage:{user_id}:{datetime.now(timezone.utc).strftime('%Y-%m')}"

    # Increment counters
    if action == "watermark":
        redis_client.hincrby(key, "watermarks", 1)
    elif action == "agent_execution":
        redis_client.hincrby(key, "agent_executions", 1)

    # Track revenue metrics
    if "revenue_identified_usd" in metadata:
        redis_client.hincrbyfloat(key, "revenue_identified_usd", metadata["revenue_identified_usd"])

    # Set expiry (keep 2 months of data)
    redis_client.expire(key, 60 * 60 * 24 * 60)


def check_tier_limits(user_id: str):
    """Check if user has exceeded tier limits."""
    tier = get_user_tier(user_id)
    tier_config = TIERS[tier]

    key = f"usage:{user_id}:{datetime.now(timezone.utc).strftime('%Y-%m')}"
    usage = redis_client.hgetall(key)

    watermarks_used = int(usage.get(b"watermarks", 0))
    executions_used = int(usage.get(b"agent_executions", 0))

    return TierLimits(
        can_watermark=watermarks_used < tier_config["watermarks_per_month"] or tier_config["watermarks_per_month"] == -1,
        can_execute_agents=executions_used < tier_config["agent_executions_per_month"] or tier_config["agent_executions_per_month"] == -1,
        tier=tier,
        watermarks_used=watermarks_used,
        watermarks_limit=tier_config["watermarks_per_month"],
    )
```

---

### Phase 3: Skills Marketplace (Week 3-4)

#### 3.1 Skills Registry API

**File**: `api/v2/marketplace.py`

```python
"""Skills and data marketplace."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/v2/marketplace", tags=["Marketplace"])


class Skill(BaseModel):
    id: str
    name: str
    description: str
    creator_id: str
    price_usd: float
    free: bool = False
    downloads: int = 0
    rating: float = 0.0


@router.get("/skills")
async def list_skills(category: str = None, free_only: bool = False):
    """List available skills in marketplace."""
    # Query from database
    skills = query_skills(category=category, free_only=free_only)
    return {"skills": skills}


@router.post("/skills/{skill_id}/purchase")
async def purchase_skill(skill_id: str, user_id: str):
    """Purchase skill from marketplace."""
    skill = get_skill(skill_id)

    if not skill.free:
        # Create Stripe payment
        payment = create_skill_payment(user_id, skill)
        if not payment.succeeded:
            raise HTTPException(402, "Payment required")

        # Revenue share: 70% creator, 30% platform
        distribute_revenue(skill.creator_id, skill.price_usd * 0.7)

    # Grant access
    grant_skill_access(user_id, skill_id)

    return {"ok": True, "skill": skill}
```

#### 3.2 Data Licensing API

```python
@router.get("/data/corpus")
async def get_corpus_info():
    """Get information about watermark verification corpus."""
    corpus_stats = get_corpus_stats()

    return {
        "total_watermarks": corpus_stats["count"],
        "total_verifications": corpus_stats["verifications"],
        "formats": ["video", "audio"],
        "anonymized": True,
        "licensing_available": True,
        "contact": "licensing@pnkln.ai"
    }


@router.post("/data/license-request")
async def request_data_license(
    organization: str,
    use_case: str,
    contact_email: str,
):
    """Request data licensing (academic or commercial)."""
    # Create license request ticket
    ticket = create_license_request(organization, use_case, contact_email)

    # Notify sales team
    notify_sales(ticket)

    return {
        "ok": True,
        "message": "License request submitted. Our team will contact you within 2 business days.",
        "ticket_id": ticket.id
    }
```

---

### Phase 4: Revenue Intelligence (Week 5-6)

#### 4.1 Wealth Accelerator Integration

**File**: `integration/revenue_engine.py`

```python
"""Revenue intelligence engine using Wealth Accelerator."""

from ultrathink.core import pnklnOrchestrator


def analyze_content_revenue_potential(prompt: str, content_metadata: dict):
    """Analyze revenue potential for content."""
    orchestrator = pnklnOrchestrator()

    analysis_prompt = f"""
    Analyze revenue potential for this content:

    Prompt: {prompt}
    Metadata: {content_metadata}

    Provide:
    1. Estimated revenue potential (conservative, optimistic)
    2. Monetization strategies (ranked by ROI)
    3. Immediate actions (executable in 24-48 hours)
    4. 90-day revenue roadmap
    """

    result = orchestrator.execute(
        prompt=analysis_prompt,
        agent_id="wealth_accelerator"
    )

    return {
        "revenue_analysis": result.output,
        "revenue_identified_usd": result.metrics.get("revenue_identified_usd", 0),
        "actionable_next_steps": extract_actions(result.output),
    }


def suggest_tier_upgrade(user_id: str):
    """Suggest tier upgrade based on usage patterns."""
    usage = get_user_usage(user_id)
    tier = get_user_tier(user_id)

    if tier == "free" and usage["watermarks"] >= 8:  # 80% of limit
        return {
            "suggested_tier": "creator",
            "reason": "You're approaching your free tier limit. Upgrade to Creator for 100× more watermarks.",
            "roi_analysis": "At $29/month, break-even at 1 paid verification. Your content is already generating interest.",
        }

    # More upgrade logic...
```

#### 4.2 Creator Dashboard

**Frontend Component** (example, not implemented):

```typescript
// Dashboard showing revenue intelligence

interface RevenueInsights {
  contentWatermarked: number;
  revenueIdentified: number;  // From Wealth Accelerator
  revenueGenerated: number;   // Actual sales
  suggestedActions: string[];
  tierUpgradeRecommendation: TierUpgrade | null;
}

function CreatorDashboard() {
  const insights = useRevenueInsights();

  return (
    <div>
      <h1>Content Revenue Dashboard</h1>
      <MetricCard
        title="Revenue Identified"
        value={`$${insights.revenueIdentified}`}
        subtitle="Potential from your content (AI-analyzed)"
      />
      <ActionsPanel actions={insights.suggestedActions} />
      {insights.tierUpgradeRecommendation && (
        <TierUpgradeCard recommendation={insights.tierUpgradeRecommendation} />
      )}
    </div>
  );
}
```

---

## Testing Strategy

### Integration Tests

**File**: `tests/test_integration/test_content_pipeline.py`

```python
"""Integration tests for full content pipeline."""

import pytest
from pathlib import Path

from api.v2.content import process_content
from integration.content_pipeline import ContentPipeline


@pytest.mark.integration
async def test_full_content_pipeline(sample_video, test_user):
    """Test complete content authenticity + monetization pipeline."""
    request = ContentRequest(
        prompt="AI-generated sunset timelapse",
        optimize_for_virality=True,
        suggest_monetization=True,
        create_blockchain_receipt=True,
    )

    result = await process_content(
        file=sample_video,
        request=request,
        user_id=test_user.id,
    )

    # Assert watermark embedded
    assert result["watermark"]["ok"] is True
    assert Path(result["output_url"]).exists()

    # Assert virality optimization ran
    assert "optimization" in result["results"]

    # Assert monetization strategy provided
    assert "monetization" in result["results"]
    assert result["results"]["revenue_identified_usd"] > 0

    # Assert blockchain receipt created
    assert "blockchain_receipt" in result["results"]
    assert result["results"]["blockchain_receipt"]["tx_hash"]


@pytest.mark.integration
def test_skills_marketplace_revenue_share():
    """Test revenue sharing in skills marketplace."""
    # Creator lists skill
    skill = create_skill(
        creator_id="creator_123",
        name="Test Skill",
        price_usd=10.0,
    )

    # User purchases skill
    purchase_skill(skill_id=skill.id, user_id="user_456")

    # Assert revenue distributed correctly
    creator_balance = get_creator_balance("creator_123")
    platform_revenue = get_platform_revenue()

    assert creator_balance == 7.0  # 70%
    assert platform_revenue >= 3.0  # 30%
```

---

## Deployment

### Infrastructure Requirements

```yaml
# kubernetes/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: pnkln-platform
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: gcr.io/pnkln/platform:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: REDIS_URL
          value: redis://redis:6379
        - name: STRIPE_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: stripe-credentials
              key: secret
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
            nvidia.com/gpu: "1"  # For video processing
          limits:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: "1"
```

### Monitoring

```python
# api/monitoring.py

from prometheus_client import Counter, Histogram

watermark_embeddings = Counter(
    "shadowtag_watermark_embeddings_total",
    "Total watermark embeddings",
    ["tier", "media_type"]
)

agent_executions = Counter(
    "ultrathink_agent_executions_total",
    "Total agent executions",
    ["agent_id", "tier"]
)

revenue_identified = Histogram(
    "pnkln_revenue_identified_usd",
    "Revenue identified by Wealth Accelerator",
    buckets=[0, 100, 500, 1000, 5000, 10000, 50000]
)
```

---

## Migration Path

### For Existing Users

1. **ShadowTag v2 users**: Automatically migrated to `/api/v1/*` endpoints (backward compatible)
2. **New platform users**: Use `/api/v2/*` endpoints for full feature set
3. **UltraThink beta users**: Agents accessible via `/api/v2/agents/*`

### Database Migrations

```sql
-- Add billing tables
CREATE TABLE user_tiers (
    user_id UUID PRIMARY KEY,
    tier VARCHAR(50) NOT NULL,
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE usage_events (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE skills_marketplace (
    skill_id UUID PRIMARY KEY,
    creator_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    price_usd DECIMAL(10, 2),
    downloads INT DEFAULT 0,
    revenue_total DECIMAL(12, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Success Metrics

### Technical KPIs

- API latency p95 < 2s for watermark embedding
- Agent execution latency p95 < 5s
- System uptime > 99.9%
- Test coverage ≥ 98%

### Business KPIs

- MRR: $0 → $50K in 90 days
- Paid conversions: 5% of free tier users
- Skills marketplace GMV: $10K/month by month 6
- Data licensing: 1 customer @ $100K/year by month 6

### Product KPIs

- Daily active creators: 500 by month 3
- Watermarks embedded: 10K/day by month 3
- Agent executions: 1K/day by month 3
- Skills published: 50 by month 6

---

## Risk Mitigation

### Technical Risks

1. **GPU availability**: Pre-provision capacity, use spot instances
2. **LLM API costs**: Implement token optimization (RoT, ICoT)
3. **Database scaling**: Use read replicas, caching layer
4. **Blockchain gas spikes**: Batch receipts, use Polygon for majority

### Business Risks

1. **Low conversion**: Aggressive free trial, viral referrals
2. **High CAC**: Product-led growth, organic content marketing
3. **Churn**: Monthly value delivery, usage analytics, proactive support
4. **Competition**: Patent protection, network effects, data moat

---

## Next Actions

### This Week
1. ✅ Merge ultrathink branch
2. ✅ Create `/api/v2/*` endpoints
3. ✅ Implement Stripe billing MVP
4. 🔄 Ship Creator tier ($29/month)

### Next Month
5. 🔄 Launch skills marketplace
6. 🔄 First data licensing conversation
7. 🔄 Close first enterprise contract
8. 🔄 Publish integration case studies

---

**Version**: 1.0.0
**Framework**: KERNEL + pnkln-JR + UltraThink
**Risk Gate**: RA-4 (High - strategic integration)

---

*"Integration is not about connecting systems. It's about multiplying value."* — pnkln Engineering
