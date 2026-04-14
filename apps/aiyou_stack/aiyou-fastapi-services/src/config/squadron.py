from pydantic import BaseModel

# DOCTRINE: Cor.86 Ultrathink v2 (iCloud Note)
# COMPONENT: Squadron Structure
# SCALE: 650 Agents


class Troop(BaseModel):
    name: str
    strength: int
    model: str
    role: str
    tier: str


class SquadronConfig(BaseModel):
    total_agents: int = 650
    mission_status: str = "STANDING BY"
    troops: dict[str, Troop]


# The "Cor.86" Definition
AUTORESEARCH_TRIAD_SQUADRON = SquadronConfig(
    troops={
        "HHT": Troop(
            name="HHT",
            strength=90,
            model="gemini-2.0-pro-exp-02-05",  # Updated to latest verified
            role="Command, Strategy, Judge 6",
            tier="PRO",
            education=[
                "Business Judgment Rule",
                "Obviously Awesome (Positioning)",
                "Clausewitz On War",
            ],
        ),
        "AIR_CAV": Troop(
            name="AIR_CAV",
            strength=120,
            model="gemini-2.0-pro-exp-02-05",
            role="Rapid Response, Critical Fixes",
            tier="PRO",
            education=["The Site Reliability Workbook", "NVIDIA Deep Learning"],
        ),
        "ALPHA": Troop(
            name="ALPHA",
            strength=130,
            model="gemini-2.0-flash-001",
            role="Recon, Search, Intake",
            tier="FLASH",
            education=["Google Search Operators", "GDrive API"],
        ),
        "BRAVO": Troop(
            name="BRAVO",
            strength=130,
            model="gemini-2.0-flash-001",
            role="Engineering, Implementation",
            tier="FLASH",
            education=["Clean Code", "Refactoring"],
        ),
        "CHARLIE": Troop(
            name="CHARLIE",
            strength=130,
            model="gemini-2.0-flash-001",
            role="Testing, CI, Documentation",
            tier="FLASH",
            education=["Pytest Guide", "Playwright Docs"],
        ),
        "CODEPMCS": Troop(
            name="CODEPMCS",
            strength=50,
            model="gemini-2.0-pro-exp-02-05",
            role="Security, ArchLint, Compliance",
            tier="PRO",
            education=["NIST 800-53", "PCI DSS v4.0", "HIPAA Security Rule"],
        ),
    },
)

MONETIZATION_MATRIX = {
    "BASIC": {
        "price": 25000,
        "agents": "minion + Risk Radar",
        "cloud_run": True,
    },
    "AIT": {"price": 100000, "agents": "+ Oracle + JudgeJura", "cloud_run": True},
    "SOF": {"price": 400000, "agents": "+ CodePMCS + Hunter/Killer", "cloud_run": False},  # Partial
    "THE_CHILD": {"price": 1000000, "agents": "Full Sovereign AI", "cloud_run": False},
}
