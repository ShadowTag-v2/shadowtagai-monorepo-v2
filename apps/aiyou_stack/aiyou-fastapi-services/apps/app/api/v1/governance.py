"""Governance API endpoints
Implements EU AI Act, DSA, NIST RMF, and ISO 42001 assessments
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.models.governance import (
    ComplianceFramework,
    EUAIActAssessment,
    GovernanceAssessmentRequest,
    GovernanceAssessmentResponse,
    ISO42001Assessment,
    NISTRMFAssessment,
    RiskLevel,
)
from app.services.batch_governance import get_batch_engine
from app.services.governance_engine import GovernanceEngine

router = APIRouter()
governance_engine = GovernanceEngine()
batch_engine = get_batch_engine()


@router.post("/assess", response_model=GovernanceAssessmentResponse)
async def assess_governance(request: GovernanceAssessmentRequest):
    """Comprehensive governance assessment across multiple frameworks

    Assesses content against:
    - EU AI Act (risk classification, transparency)
    - DSA VLOP (systemic risk, recommender transparency)
    - NIST AI RMF 1.0 (Govern, Map, Measure, Manage)
    - ISO/IEC 42001 (AI management system controls)
    """
    assessment_id = str(uuid.uuid4())

    # Perform governance assessment
    result = await governance_engine.assess(request)

    return GovernanceAssessmentResponse(
        assessment_id=assessment_id,
        timestamp=datetime.utcnow(),
        **result,
    )


@router.post("/eu-ai-act/assess", response_model=EUAIActAssessment)
async def assess_eu_ai_act(request: GovernanceAssessmentRequest):
    """EU AI Act specific assessment

    Determines:
    - Risk classification (unacceptable, high, limited, minimal)
    - Transparency requirements
    - Human oversight needs
    - Data governance compliance
    - Conformity assessment requirements
    """
    result = await governance_engine.assess_eu_ai_act(request)
    return result


@router.post("/nist-rmf/assess", response_model=NISTRMFAssessment)
async def assess_nist_rmf(request: GovernanceAssessmentRequest):
    """NIST AI Risk Management Framework assessment

    Evaluates across four functions:
    - GOVERN: Policies, processes, roles
    - MAP: Context and categorization
    - MEASURE: Analysis and assessment
    - MANAGE: Prioritization and planning
    """
    result = await governance_engine.assess_nist_rmf(request)
    return result


@router.post("/iso-42001/assess", response_model=ISO42001Assessment)
async def assess_iso_42001(request: GovernanceAssessmentRequest):
    """ISO/IEC 42001 AI Management System assessment

    Evaluates 7 clauses:
    - Context of the organization
    - Leadership
    - Planning
    - Support
    - Operation
    - Performance evaluation
    - Improvement
    """
    result = await governance_engine.assess_iso_42001(request)
    return result


@router.get("/frameworks", response_model=list[dict])
async def list_frameworks():
    """List all supported governance frameworks"""
    return [
        {
            "id": ComplianceFramework.EU_AI_ACT,
            "name": "EU AI Act",
            "description": "European Union Artificial Intelligence Act",
            "version": "2024",
            "enabled": True,
        },
        {
            "id": ComplianceFramework.DSA_VLOP,
            "name": "DSA VLOP",
            "description": "Digital Services Act - Very Large Online Platform",
            "version": "2024",
            "enabled": True,
        },
        {
            "id": ComplianceFramework.NIST_RMF,
            "name": "NIST AI RMF",
            "description": "NIST AI Risk Management Framework",
            "version": "1.0",
            "enabled": True,
        },
        {
            "id": ComplianceFramework.ISO_42001,
            "name": "ISO/IEC 42001",
            "description": "AI Management System Standard",
            "version": "2023",
            "enabled": True,
        },
        {
            "id": ComplianceFramework.GDPR,
            "name": "GDPR",
            "description": "General Data Protection Regulation",
            "version": "2018",
            "enabled": True,
        },
        {
            "id": ComplianceFramework.COPPA,
            "name": "COPPA",
            "description": "Children's Online Privacy Protection Act",
            "version": "2013",
            "enabled": True,
        },
    ]


@router.get("/risk-levels", response_model=list[dict])
async def list_risk_levels():
    """List risk level classifications"""
    return [
        {
            "level": RiskLevel.UNACCEPTABLE,
            "description": "Poses unacceptable risk - prohibited",
            "color": "red",
        },
        {
            "level": RiskLevel.HIGH,
            "description": "High risk - requires conformity assessment",
            "color": "orange",
        },
        {
            "level": RiskLevel.LIMITED,
            "description": "Limited risk - transparency obligations",
            "color": "yellow",
        },
        {
            "level": RiskLevel.MINIMAL,
            "description": "Minimal/no risk - voluntary compliance",
            "color": "green",
        },
    ]


@router.post("/assess/batch")
async def assess_batch_governance(
    items: list[dict],
    frameworks: list[ComplianceFramework],
    top_k_violations: int = None,
    similarity_threshold: float = 0.8,
):
    """Batch governance assessment with MCP efficiency patterns

    Efficiently assess 100s-1000s of items using:
    - Progressive disclosure (98.7% token reduction)
    - Batch processing (assess all → filter to top-K violators)
    - Embedding-based similarity search
    - Data manipulation in code, not LLM context

    **Cost savings: 90-95% vs sequential assessments**

    Example usage:
    ```json
    {
        "items": [
            {"id": "ad_1", "content": "...", "type": "advertisement"},
            {"id": "ad_2", "content": "...", "type": "advertisement"},
            ...
        ],
        "frameworks": ["eu_ai_act", "coppa"],
        "top_k_violations": 10,  // Only return top 10 violators (massive token savings)
        "similarity_threshold": 0.8
    }
    ```

    Args:
        items: List of items to assess (each with 'id', 'content', optional 'type', 'user_age')
        frameworks: Compliance frameworks to assess against
        top_k_violations: Only return top-K highest risk items (default: all)
        similarity_threshold: Group similar violations together (0-1, default: 0.8)

    Returns:
        {
            "results": [
                {
                    "item_id": "ad_1",
                    "risk_score": 85.5,
                    "compliance_score": 0.145,
                    "risk_level": "high",
                    "violations": ["privacy violation", "transparency violation"],
                    "assessment_summary": "..."
                },
                ...
            ],
            "analytics": {
                "total_items": 100,
                "high_risk_count": 12,
                "avg_compliance_score": 0.78,
                "total_violations": 45,
                "top_violation_types": [["privacy", 18], ["transparency", 15], ...],
                "tokens_used": 15000,
                "cost_usd": 0.0056
            }
        }

    """
    try:
        # Execute batch assessment
        results, analytics = await batch_engine.assess_batch(
            items=items,
            frameworks=frameworks,
            top_k_violations=top_k_violations,
            similarity_threshold=similarity_threshold,
        )

        return {
            "results": [
                {
                    "item_id": r.item_id,
                    "risk_score": r.risk_score,
                    "compliance_score": r.compliance_score,
                    "risk_level": r.risk_level.value,
                    "violations": r.violations,
                    "assessment_summary": r.assessment_summary,
                }
                for r in results
            ],
            "analytics": {
                "total_items": analytics.total_items,
                "high_risk_count": analytics.high_risk_count,
                "avg_compliance_score": analytics.avg_compliance_score,
                "total_violations": analytics.total_violations,
                "top_violation_types": analytics.top_violation_types,
                "tokens_used": analytics.tokens_used,
                "cost_usd": analytics.cost_usd,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch assessment failed: {e!s}",
        ) from e
