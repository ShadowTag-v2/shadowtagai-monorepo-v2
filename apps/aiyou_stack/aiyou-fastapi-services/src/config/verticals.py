"""Vertical-Specific Configurations for 30 Regulated Industries

Each vertical has custom settings for:
- k: Number of chunks to retrieve
- chunk_size: Words per chunk
- temperature: Model temperature
- force_lc_threshold: Confidence threshold for forcing LC
- enable_reranking: Whether to use reranking
- citation_required: Whether to enforce chunk citations
"""

from dataclasses import dataclass
from enum import Enum


@dataclass
class VerticalConfig:
    """Configuration for a specific industry vertical"""

    name: str
    description: str
    k: int = 5
    chunk_size: int = 300
    overlap: int = 50
    temperature: float = 0.1
    force_lc_threshold: float = 0.95
    enable_reranking: bool = False
    citation_required: bool = False
    model: str = "gemini-1.5-flash-001"  # Default to Flash for cost
    max_output_tokens: int = 512


class VerticalType(Enum):
    """Industry vertical categories"""

    # High-stakes regulated industries (Gemini Pro required)
    HEALTHCARE_COMPLIANCE = "healthcare_compliance"
    DEFENSE_CONTRACTS = "defense_contracts"
    FINANCIAL_REGULATIONS = "financial_regulations"
    AEROSPACE_ENGINEERING = "aerospace_engineering"
    NUCLEAR_SAFETY = "nuclear_safety"

    # Medium-stakes regulated industries (Gemini Pro recommended)
    PHARMACEUTICAL_RESEARCH = "pharmaceutical_research"
    MEDICAL_DEVICES = "medical_devices"
    CYBERSECURITY = "cybersecurity"
    ENVIRONMENTAL_COMPLIANCE = "environmental_compliance"
    ENERGY_REGULATIONS = "energy_regulations"

    # Standard regulated industries (Gemini Flash acceptable)
    CONSTRUCTION_CODES = "construction_codes"
    AUTOMOTIVE_STANDARDS = "automotive_standards"
    FOOD_SAFETY = "food_safety"
    TELECOMMUNICATIONS = "telecommunications"
    INSURANCE_REGULATIONS = "insurance_regulations"
    REAL_ESTATE_COMPLIANCE = "real_estate_compliance"
    TRANSPORTATION_SAFETY = "transportation_safety"
    MARITIME_REGULATIONS = "maritime_regulations"
    AVIATION_STANDARDS = "aviation_standards"
    CHEMICAL_SAFETY = "chemical_safety"

    # Commercial industries (Gemini Flash optimized)
    MANUFACTURING_QUALITY = "manufacturing_quality"
    SUPPLY_CHAIN = "supply_chain"
    RETAIL_COMPLIANCE = "retail_compliance"
    HOSPITALITY_STANDARDS = "hospitality_standards"
    EDUCATION_ACCREDITATION = "education_accreditation"
    LABOR_EMPLOYMENT = "labor_employment"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    DATA_PRIVACY = "data_privacy"
    CORPORATE_GOVERNANCE = "corporate_governance"
    TAX_REGULATIONS = "tax_regulations"


# ============================================================================
# VERTICAL CONFIGURATIONS (30 Regulated Industries)
# ============================================================================

VERTICAL_CONFIGS: dict[VerticalType, VerticalConfig] = {
    # ------------------------------------------------------------------------
    # HIGH-STAKES REGULATED INDUSTRIES
    # ------------------------------------------------------------------------
    VerticalType.HEALTHCARE_COMPLIANCE: VerticalConfig(
        name="Healthcare Compliance",
        description="HIPAA, FDA, CMS regulations and healthcare compliance",
        k=10,  # Higher k for regulatory complexity
        chunk_size=300,
        overlap=50,
        temperature=0.05,  # Very low for accuracy
        force_lc_threshold=0.95,  # High-stakes queries
        enable_reranking=False,
        citation_required=True,
        model="gemini-1.5-pro-001",  # Pro required
        max_output_tokens=1024,
    ),
    VerticalType.DEFENSE_CONTRACTS: VerticalConfig(
        name="Defense Contracts",
        description="FAR, DFARS, ITAR and defense contracting regulations",
        k=8,
        chunk_size=400,  # Longer chunks for technical specs
        overlap=75,
        temperature=0.05,
        force_lc_threshold=0.98,  # Extreme accuracy required
        enable_reranking=True,
        citation_required=True,
        model="gemini-1.5-pro-001",
        max_output_tokens=1024,
    ),
    VerticalType.FINANCIAL_REGULATIONS: VerticalConfig(
        name="Financial Regulations",
        description="SEC, FINRA, Basel, Dodd-Frank financial compliance",
        k=8,
        chunk_size=300,
        overlap=50,
        temperature=0.05,
        force_lc_threshold=0.95,
        enable_reranking=True,
        citation_required=True,
        model="gemini-1.5-pro-001",
        max_output_tokens=1024,
    ),
    VerticalType.AEROSPACE_ENGINEERING: VerticalConfig(
        name="Aerospace Engineering",
        description="FAA, NASA, aerospace engineering standards",
        k=8,
        chunk_size=350,
        overlap=60,
        temperature=0.05,
        force_lc_threshold=0.95,
        enable_reranking=True,
        citation_required=True,
        model="gemini-1.5-pro-001",
        max_output_tokens=1024,
    ),
    VerticalType.NUCLEAR_SAFETY: VerticalConfig(
        name="Nuclear Safety",
        description="NRC, nuclear safety regulations and standards",
        k=10,
        chunk_size=300,
        overlap=60,
        temperature=0.03,  # Extremely low
        force_lc_threshold=0.98,
        enable_reranking=True,
        citation_required=True,
        model="gemini-1.5-pro-001",
        max_output_tokens=1024,
    ),
    # ------------------------------------------------------------------------
    # MEDIUM-STAKES REGULATED INDUSTRIES
    # ------------------------------------------------------------------------
    VerticalType.PHARMACEUTICAL_RESEARCH: VerticalConfig(
        name="Pharmaceutical Research",
        description="FDA drug approval, clinical trials, pharmaceutical compliance",
        k=8,
        chunk_size=300,
        overlap=50,
        temperature=0.1,
        force_lc_threshold=0.90,
        enable_reranking=True,
        citation_required=True,
        model="gemini-1.5-pro-001",
        max_output_tokens=768,
    ),
    VerticalType.MEDICAL_DEVICES: VerticalConfig(
        name="Medical Devices",
        description="FDA medical device regulations and quality standards",
        k=7,
        chunk_size=300,
        overlap=50,
        temperature=0.1,
        force_lc_threshold=0.90,
        enable_reranking=False,
        citation_required=True,
        model="gemini-1.5-pro-001",
        max_output_tokens=768,
    ),
    VerticalType.CYBERSECURITY: VerticalConfig(
        name="Cybersecurity",
        description="NIST, ISO 27001, cybersecurity frameworks and compliance",
        k=7,
        chunk_size=300,
        overlap=50,
        temperature=0.1,
        force_lc_threshold=0.85,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-pro-001",
        max_output_tokens=768,
    ),
    VerticalType.ENVIRONMENTAL_COMPLIANCE: VerticalConfig(
        name="Environmental Compliance",
        description="EPA, environmental regulations and compliance",
        k=6,
        chunk_size=300,
        overlap=50,
        temperature=0.1,
        force_lc_threshold=0.85,
        enable_reranking=False,
        citation_required=True,
        model="gemini-1.5-pro-001",
        max_output_tokens=768,
    ),
    VerticalType.ENERGY_REGULATIONS: VerticalConfig(
        name="Energy Regulations",
        description="FERC, energy sector regulations and standards",
        k=6,
        chunk_size=300,
        overlap=50,
        temperature=0.1,
        force_lc_threshold=0.85,
        enable_reranking=False,
        citation_required=True,
        model="gemini-1.5-pro-001",
        max_output_tokens=768,
    ),
    # ------------------------------------------------------------------------
    # STANDARD REGULATED INDUSTRIES
    # ------------------------------------------------------------------------
    VerticalType.CONSTRUCTION_CODES: VerticalConfig(
        name="Construction Codes",
        description="Building codes, construction standards and compliance",
        k=5,
        chunk_size=300,
        overlap=50,
        temperature=0.15,
        force_lc_threshold=0.80,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.AUTOMOTIVE_STANDARDS: VerticalConfig(
        name="Automotive Standards",
        description="NHTSA, automotive safety and manufacturing standards",
        k=5,
        chunk_size=300,
        overlap=50,
        temperature=0.15,
        force_lc_threshold=0.80,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.FOOD_SAFETY: VerticalConfig(
        name="Food Safety",
        description="FDA food safety, HACCP, food industry compliance",
        k=6,
        chunk_size=300,
        overlap=50,
        temperature=0.1,
        force_lc_threshold=0.85,
        enable_reranking=False,
        citation_required=True,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.TELECOMMUNICATIONS: VerticalConfig(
        name="Telecommunications",
        description="FCC, telecommunications regulations and standards",
        k=5,
        chunk_size=300,
        overlap=50,
        temperature=0.15,
        force_lc_threshold=0.80,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.INSURANCE_REGULATIONS: VerticalConfig(
        name="Insurance Regulations",
        description="State insurance regulations and compliance",
        k=6,
        chunk_size=300,
        overlap=50,
        temperature=0.1,
        force_lc_threshold=0.85,
        enable_reranking=False,
        citation_required=True,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.REAL_ESTATE_COMPLIANCE: VerticalConfig(
        name="Real Estate Compliance",
        description="Real estate regulations, zoning, and compliance",
        k=5,
        chunk_size=300,
        overlap=50,
        temperature=0.15,
        force_lc_threshold=0.80,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.TRANSPORTATION_SAFETY: VerticalConfig(
        name="Transportation Safety",
        description="DOT, transportation safety regulations",
        k=5,
        chunk_size=300,
        overlap=50,
        temperature=0.15,
        force_lc_threshold=0.80,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.MARITIME_REGULATIONS: VerticalConfig(
        name="Maritime Regulations",
        description="Coast Guard, maritime safety and compliance",
        k=5,
        chunk_size=300,
        overlap=50,
        temperature=0.15,
        force_lc_threshold=0.80,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.AVIATION_STANDARDS: VerticalConfig(
        name="Aviation Standards",
        description="FAA aviation standards and regulations",
        k=6,
        chunk_size=300,
        overlap=50,
        temperature=0.1,
        force_lc_threshold=0.85,
        enable_reranking=False,
        citation_required=True,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.CHEMICAL_SAFETY: VerticalConfig(
        name="Chemical Safety",
        description="OSHA, chemical safety regulations and standards",
        k=6,
        chunk_size=300,
        overlap=50,
        temperature=0.1,
        force_lc_threshold=0.85,
        enable_reranking=False,
        citation_required=True,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    # ------------------------------------------------------------------------
    # COMMERCIAL INDUSTRIES (Cost-Optimized)
    # ------------------------------------------------------------------------
    VerticalType.MANUFACTURING_QUALITY: VerticalConfig(
        name="Manufacturing Quality",
        description="ISO 9001, manufacturing quality standards",
        k=5,
        chunk_size=300,
        overlap=50,
        temperature=0.2,
        force_lc_threshold=0.75,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.SUPPLY_CHAIN: VerticalConfig(
        name="Supply Chain",
        description="Supply chain standards and best practices",
        k=5,
        chunk_size=300,
        overlap=50,
        temperature=0.2,
        force_lc_threshold=0.75,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.RETAIL_COMPLIANCE: VerticalConfig(
        name="Retail Compliance",
        description="Retail industry compliance and standards",
        k=5,
        chunk_size=300,
        overlap=50,
        temperature=0.2,
        force_lc_threshold=0.75,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.HOSPITALITY_STANDARDS: VerticalConfig(
        name="Hospitality Standards",
        description="Hospitality industry standards and regulations",
        k=5,
        chunk_size=300,
        overlap=50,
        temperature=0.2,
        force_lc_threshold=0.75,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.EDUCATION_ACCREDITATION: VerticalConfig(
        name="Education Accreditation",
        description="Educational accreditation standards and compliance",
        k=5,
        chunk_size=300,
        overlap=50,
        temperature=0.2,
        force_lc_threshold=0.75,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.LABOR_EMPLOYMENT: VerticalConfig(
        name="Labor & Employment",
        description="Labor laws, employment regulations and compliance",
        k=6,
        chunk_size=300,
        overlap=50,
        temperature=0.15,
        force_lc_threshold=0.80,
        enable_reranking=False,
        citation_required=True,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.INTELLECTUAL_PROPERTY: VerticalConfig(
        name="Intellectual Property",
        description="Patent, trademark, copyright regulations",
        k=6,
        chunk_size=300,
        overlap=50,
        temperature=0.15,
        force_lc_threshold=0.80,
        enable_reranking=False,
        citation_required=True,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.DATA_PRIVACY: VerticalConfig(
        name="Data Privacy",
        description="GDPR, CCPA, data privacy regulations",
        k=6,
        chunk_size=300,
        overlap=50,
        temperature=0.15,
        force_lc_threshold=0.80,
        enable_reranking=False,
        citation_required=True,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.CORPORATE_GOVERNANCE: VerticalConfig(
        name="Corporate Governance",
        description="Corporate governance standards and compliance",
        k=5,
        chunk_size=300,
        overlap=50,
        temperature=0.2,
        force_lc_threshold=0.75,
        enable_reranking=False,
        citation_required=False,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
    VerticalType.TAX_REGULATIONS: VerticalConfig(
        name="Tax Regulations",
        description="IRS, tax code and regulations",
        k=6,
        chunk_size=300,
        overlap=50,
        temperature=0.1,
        force_lc_threshold=0.85,
        enable_reranking=False,
        citation_required=True,
        model="gemini-1.5-flash-001",
        max_output_tokens=512,
    ),
}


def get_vertical_config(vertical: VerticalType) -> VerticalConfig:
    """Get configuration for a specific vertical"""
    return VERTICAL_CONFIGS[vertical]


def get_vertical_by_name(name: str) -> VerticalType:
    """Get vertical type by name (case-insensitive)"""
    name_lower = name.lower().replace(" ", "_").replace("-", "_")

    for vertical_type in VerticalType:
        if vertical_type.value == name_lower:
            return vertical_type

    raise ValueError(f"Unknown vertical: {name}")


def list_verticals() -> dict[str, str]:
    """List all available verticals with descriptions"""
    return {vertical.value: VERTICAL_CONFIGS[vertical].description for vertical in VerticalType}


def get_cost_tier_summary() -> dict[str, list]:
    """Get summary of verticals by cost tier (model used)"""
    pro_verticals = []
    flash_verticals = []

    for vertical_type, config in VERTICAL_CONFIGS.items():
        if "pro" in config.model:
            pro_verticals.append(vertical_type.value)
        else:
            flash_verticals.append(vertical_type.value)

    return {
        "high_cost_pro": pro_verticals,
        "standard_cost_flash": flash_verticals,
        "total_verticals": len(VERTICAL_CONFIGS),
    }
