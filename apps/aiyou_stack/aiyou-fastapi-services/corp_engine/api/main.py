"""ShadowTagAI Corp Engine - Main API
===================================
Cloud-native, login-and-run enterprise SaaS platform.
"""

import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from ..core.self_config import (
    CompanySize,
    IndustryVertical,
    self_config_engine,
)
from ..models.tenant import (
    LICENSE_TIERS,
    LicenseTier,
    TenantCreate,
    TenantStatus,
)

app = FastAPI(
    title="ShadowTagAI Corp Engine",
    description="Elastic, self-configuring enterprise SaaS platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

# In-memory store (replace with Cloud SQL in production)
tenants_db: dict[str, dict] = {}
users_db: dict[str, dict] = {}


# ============================================================================
# Health & Info
# ============================================================================


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "corp-engine",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/license-tiers")
async def get_license_tiers():
    """Get available license tiers and feature matrix"""
    return {
        "tiers": [tier.model_dump() for tier in LICENSE_TIERS.values()],
        "currency": "USD",
        "billing_cycle": "annual",
    }


# ============================================================================
# Auth Endpoints
# ============================================================================


@app.post("/auth/provision")
async def provision_tenant(tenant: TenantCreate):
    """Provision a new tenant - the only setup needed.
    Customer gets login, platform runs immediately.
    """
    tenant_id = str(uuid.uuid4())

    # Auto-configure based on profile
    industry = IndustryVertical(tenant.industry) if tenant.industry else IndustryVertical.TECHNOLOGY
    size = CompanySize(tenant.company_size) if tenant.company_size else CompanySize.SMB

    ai_config = self_config_engine.generate_config(
        tenant_id=tenant_id,
        industry=industry,
        company_size=size,
        tech_stack=tenant.tech_stack or [],
        regulatory_requirements=tenant.regulatory_requirements or [],
    )

    # Store tenant
    tenants_db[tenant_id] = {
        "id": tenant_id,
        "name": tenant.name,
        "slug": tenant.slug,
        "license_tier": LicenseTier.STARTER,
        "status": TenantStatus.TRIAL,
        "industry": tenant.industry,
        "company_size": tenant.company_size,
        "tech_stack": tenant.tech_stack,
        "regulatory_requirements": tenant.regulatory_requirements,
        "ai_config": ai_config.model_dump(),
        "created_at": datetime.utcnow(),
    }

    return {
        "success": True,
        "tenant_id": tenant_id,
        "slug": tenant.slug,
        "login_url": f"https://app.shadowtagai.com/{tenant.slug}",
        "status": "ready",
        "ai_config_hash": ai_config.config_hash,
        "message": "Platform is live. Share login URL with your team.",
    }


@app.post("/auth/sso/callback")
async def sso_callback(request: Request):
    """Handle OAuth/SAML SSO callback"""
    # In production, validate SSO token and create session
    return {
        "success": True,
        "session_token": str(uuid.uuid4()),
        "expires_in": 86400,
    }


# ============================================================================
# Tenant Configuration
# ============================================================================


@app.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Get tenant details and configuration"""
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@app.put("/tenants/{tenant_id}/config")
async def update_tenant_config(
    tenant_id: str,
    industry: str | None = None,
    company_size: str | None = None,
    tech_stack: list[str] | None = None,
    regulatory_requirements: list[str] | None = None,
):
    """Update tenant profile - triggers AI reconfiguration"""
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Update profile
    if industry:
        tenant["industry"] = industry
    if company_size:
        tenant["company_size"] = company_size
    if tech_stack:
        tenant["tech_stack"] = tech_stack
    if regulatory_requirements:
        tenant["regulatory_requirements"] = regulatory_requirements

    # Regenerate AI config
    ai_config = self_config_engine.generate_config(
        tenant_id=tenant_id,
        industry=IndustryVertical(tenant["industry"] or "technology"),
        company_size=CompanySize(tenant["company_size"] or "smb"),
        tech_stack=tenant.get("tech_stack", []),
        regulatory_requirements=tenant.get("regulatory_requirements", []),
    )

    tenant["ai_config"] = ai_config.model_dump()

    return {
        "success": True,
        "message": "Configuration updated",
        "new_config_hash": ai_config.config_hash,
    }


@app.post("/tenants/{tenant_id}/upgrade")
async def upgrade_license(tenant_id: str, target_tier: LicenseTier):
    """Upgrade tenant license tier"""
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    old_tier = tenant["license_tier"]
    tenant["license_tier"] = target_tier
    tenant["status"] = TenantStatus.ACTIVE

    tier_info = LICENSE_TIERS[target_tier]

    return {
        "success": True,
        "previous_tier": old_tier,
        "new_tier": target_tier,
        "annual_fee_usd": tier_info.annual_fee_usd,
        "features": tier_info.model_dump(),
    }


# ============================================================================
# Intel Feed Endpoints
# ============================================================================


@app.get("/tenants/{tenant_id}/intel")
async def get_intel_feed(
    tenant_id: str,
    category: str | None = None,
    min_relevance: int = 50,
    limit: int = 20,
):
    """Get personalized intel feed for tenant"""
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # In production, fetch from Nightly Intel Pipeline
    # filtered by tenant's AI config
    ai_config = tenant.get("ai_config", {})
    categories = ai_config.get("intel_categories", [])

    return {
        "tenant_id": tenant_id,
        "intel_categories": categories,
        "items": [
            {
                "id": str(uuid.uuid4()),
                "type": "tech_update",
                "title": "Gemini 2.5 Pro Released - Performance Improvements",
                "summary": "Google released Gemini 2.5 Pro with 40% faster inference",
                "relevance_score": 95,
                "recommendations": [
                    "Consider upgrading primary model to gemini-3.1-flash-lite-preview",
                    "Test new capabilities in staging environment",
                ],
                "shadowtag_signature": "c2pa:ed25519:abc123...",
                "created_at": datetime.utcnow().isoformat(),
            },
            {
                "id": str(uuid.uuid4()),
                "type": "framework_release",
                "title": "LangChain v0.3 - Agent Architecture Overhaul",
                "summary": "Major update to agent orchestration patterns",
                "relevance_score": 85,
                "recommendations": [
                    "Review new agent patterns for integration opportunities",
                ],
                "shadowtag_signature": "c2pa:ed25519:def456...",
                "created_at": datetime.utcnow().isoformat(),
            },
        ],
        "next_refresh_at": datetime.utcnow().isoformat(),
    }


@app.post("/tenants/{tenant_id}/intel/{intel_id}/action")
async def action_intel(tenant_id: str, intel_id: str, action: str):
    """Mark intel as actioned"""
    return {
        "success": True,
        "intel_id": intel_id,
        "action": action,
        "actioned_at": datetime.utcnow().isoformat(),
    }


# ============================================================================
# Export Endpoints
# ============================================================================


@app.get("/tenants/{tenant_id}/export/config")
async def export_config(tenant_id: str, format: str = "json"):
    """Export tenant configuration"""
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {
        "format": format,
        "exported_at": datetime.utcnow().isoformat(),
        "config": tenant.get("ai_config", {}),
        "shadowtag_signature": "c2pa:ed25519:export123...",
    }


@app.get("/tenants/{tenant_id}/export/intel-report")
async def export_intel_report(
    tenant_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
):
    """Export intel report for period"""
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {
        "tenant_id": tenant_id,
        "period": {"start": start_date, "end": end_date},
        "total_intel_items": 156,
        "actioned_items": 42,
        "top_categories": ["tech_update", "security_alert", "framework_release"],
        "generated_at": datetime.utcnow().isoformat(),
        "shadowtag_signature": "c2pa:ed25519:report123...",
    }


# ============================================================================
# Self-Porting / Auto-Update Endpoints
# ============================================================================


@app.get("/tenants/{tenant_id}/updates")
async def check_updates(tenant_id: str):
    """Check for available framework/model updates"""
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    updates = await self_config_engine.check_for_updates(tenant_id)
    return updates


@app.post("/tenants/{tenant_id}/auto-port")
async def auto_port(tenant_id: str, target_framework: str):
    """Auto-port tenant to new framework"""
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    result = await self_config_engine.auto_port(tenant_id, target_framework)

    if result["success"]:
        # Update stored config
        tenant["ai_config"]["primary_model"] = target_framework

    return result


# ============================================================================
# Workspace Endpoints
# ============================================================================


@app.post("/tenants/{tenant_id}/workspaces")
async def create_workspace(tenant_id: str, name: str, description: str | None = None):
    """Create a new workspace within tenant"""
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Check license limits
    tier = LICENSE_TIERS[tenant["license_tier"]]
    # In production, count existing workspaces

    workspace_id = str(uuid.uuid4())

    return {
        "success": True,
        "workspace_id": workspace_id,
        "name": name,
        "tenant_id": tenant_id,
        "created_at": datetime.utcnow().isoformat(),
    }


@app.get("/tenants/{tenant_id}/workspaces")
async def list_workspaces(tenant_id: str):
    """List all workspaces for tenant"""
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {
        "tenant_id": tenant_id,
        "workspaces": [],  # In production, fetch from DB
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8700)
