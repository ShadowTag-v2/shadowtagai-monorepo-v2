"""Vertical-specific configuration for regulatory compliance
Defines the 30 verticals with their regulatory requirements
"""

from dataclasses import dataclass


@dataclass
class VerticalConfig:
    """Configuration for a specific vertical"""

    name: str
    display_name: str
    regulations: list[str]
    description: str


# All 30 Pnkln verticals with regulatory requirements
VERTICALS = [
    VerticalConfig(
        name="defense",
        display_name="Defense & Aerospace",
        regulations=["ITAR", "CMMC", "DFARS"],
        description="International Traffic in Arms Regulations and Cybersecurity Maturity Model",
    ),
    VerticalConfig(
        name="healthcare",
        display_name="Healthcare",
        regulations=["HIPAA", "FDA", "HITECH"],
        description="Health Insurance Portability and Accountability Act",
    ),
    VerticalConfig(
        name="finance",
        display_name="Financial Services",
        regulations=["FINRA", "SOX", "GDPR", "PCI-DSS"],
        description="Financial Industry Regulatory Authority and compliance",
    ),
    VerticalConfig(
        name="insurance",
        display_name="Insurance",
        regulations=["STATE_REGS", "NAIC", "GDPR"],
        description="State insurance regulations and NAIC standards",
    ),
    VerticalConfig(
        name="pharma",
        display_name="Pharmaceutical",
        regulations=["FDA", "GxP", "21CFR11"],
        description="Good practice guidelines and FDA regulations",
    ),
    VerticalConfig(
        name="energy",
        display_name="Energy & Utilities",
        regulations=["NERC_CIP", "FERC", "EPA"],
        description="Critical Infrastructure Protection standards",
    ),
    VerticalConfig(
        name="manufacturing",
        display_name="Manufacturing",
        regulations=["ISO9001", "OSHA", "EPA"],
        description="Quality management and safety standards",
    ),
    VerticalConfig(
        name="retail",
        display_name="Retail",
        regulations=["PCI-DSS", "GDPR", "CCPA"],
        description="Payment card and consumer data protection",
    ),
    VerticalConfig(
        name="telecom",
        display_name="Telecommunications",
        regulations=["FCC", "CALEA", "CPNI"],
        description="FCC regulations and privacy requirements",
    ),
    VerticalConfig(
        name="government",
        display_name="Government",
        regulations=["FISMA", "FedRAMP", "NIST"],
        description="Federal security standards and compliance",
    ),
    VerticalConfig(
        name="education",
        display_name="Education",
        regulations=["FERPA", "COPPA", "GDPR"],
        description="Student privacy and data protection",
    ),
    VerticalConfig(
        name="legal",
        display_name="Legal Services",
        regulations=["ABA", "GDPR", "STATE_BAR"],
        description="Attorney ethics and client confidentiality",
    ),
    VerticalConfig(
        name="media",
        display_name="Media & Entertainment",
        regulations=["COPPA", "GDPR", "DMCA"],
        description="Content protection and privacy compliance",
    ),
    VerticalConfig(
        name="transportation",
        display_name="Transportation",
        regulations=["DOT", "FAA", "TSA"],
        description="Transportation security and safety standards",
    ),
    VerticalConfig(
        name="hospitality",
        display_name="Hospitality",
        regulations=["PCI-DSS", "ADA", "OSHA"],
        description="Payment security and accessibility standards",
    ),
    VerticalConfig(
        name="real_estate",
        display_name="Real Estate",
        regulations=["RESPA", "TILA", "FCRA"],
        description="Real estate transaction and consumer protection",
    ),
    VerticalConfig(
        name="agriculture",
        display_name="Agriculture",
        regulations=["USDA", "EPA", "OSHA"],
        description="Agricultural standards and environmental compliance",
    ),
    VerticalConfig(
        name="mining",
        display_name="Mining",
        regulations=["MSHA", "EPA", "OSHA"],
        description="Mine safety and environmental protection",
    ),
    VerticalConfig(
        name="construction",
        display_name="Construction",
        regulations=["OSHA", "EPA", "LOCAL_BUILDING"],
        description="Construction safety and building codes",
    ),
    VerticalConfig(
        name="biotech",
        display_name="Biotechnology",
        regulations=["FDA", "NIH", "CDC"],
        description="Biological research and safety standards",
    ),
    VerticalConfig(
        name="chemical",
        display_name="Chemical Industry",
        regulations=["EPA", "OSHA", "REACH"],
        description="Chemical safety and environmental protection",
    ),
    VerticalConfig(
        name="automotive",
        display_name="Automotive",
        regulations=["NHTSA", "EPA", "DOT"],
        description="Vehicle safety and emissions standards",
    ),
    VerticalConfig(
        name="aerospace",
        display_name="Aerospace",
        regulations=["FAA", "ITAR", "NASA"],
        description="Aviation safety and export controls",
    ),
    VerticalConfig(
        name="maritime",
        display_name="Maritime",
        regulations=["USCG", "IMO", "SOLAS"],
        description="Maritime safety and security standards",
    ),
    VerticalConfig(
        name="gaming",
        display_name="Gaming & Casino",
        regulations=["STATE_GAMING", "AML", "KYC"],
        description="Gaming regulations and anti-money laundering",
    ),
    VerticalConfig(
        name="nonprofit",
        display_name="Non-Profit",
        regulations=["IRS_501C3", "STATE_CHARITY", "FUNDRAISING"],
        description="Tax-exempt status and charitable regulations",
    ),
    VerticalConfig(
        name="sports",
        display_name="Sports & Recreation",
        regulations=["NCAA", "WADA", "ADA"],
        description="Athletic compliance and accessibility",
    ),
    VerticalConfig(
        name="environmental",
        display_name="Environmental Services",
        regulations=["EPA", "NEPA", "ESA"],
        description="Environmental protection and conservation",
    ),
    VerticalConfig(
        name="logistics",
        display_name="Logistics & Supply Chain",
        regulations=["DOT", "TSA", "CTPAT"],
        description="Transportation security and trade compliance",
    ),
    VerticalConfig(
        name="research",
        display_name="Research & Development",
        regulations=["NIH", "NSF", "IRB"],
        description="Research ethics and grant compliance",
    ),
]


def get_vertical_config(vertical_name: str) -> VerticalConfig:
    """Get configuration for a specific vertical"""
    for vertical in VERTICALS:
        if vertical.name == vertical_name:
            return vertical
    raise ValueError(f"Unknown vertical: {vertical_name}")


def list_verticals() -> list[str]:
    """List all available vertical names"""
    return [v.name for v in VERTICALS]
