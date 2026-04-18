from enum import StrEnum

from pydantic import BaseModel


class AgentCapability(StrEnum):
    DESIGN = "design"
    CODE = "code"
    CRITICISM = "criticism"
    SECURITY = "security"
    ANALYSIS = "analysis"


class AgentProfile(BaseModel):
    """Defines the persona and configuration for an Ultrathink agent."""

    name: str
    role: str
    capabilities: list[AgentCapability]
    system_prompt: str
    temperature: float = 0.7
    max_tokens: int = 2048
    description: str = ""


class StandardRoster:
    """Pre-configured roster of specialized agents."""

    @staticmethod
    def get_designer() -> AgentProfile:
        return AgentProfile(
            name="DESIGNER",
            role="UX/UI and System Architect",
            capabilities=[AgentCapability.DESIGN],
            system_prompt=(
                "You are an expert user experience designer and system architect. "
                "Prioritize elegance, simplicity, and user-centric flows. "
                "Always question if a feature adds value or just complexity."
            ),
            temperature=0.9,
            description="Specializes in visual design, UX flows, and architectural elegance.",
        )

    @staticmethod
    def get_accelerator() -> AgentProfile:
        return AgentProfile(
            name="ACCELERATOR",
            role="Efficiency Engineer",
            capabilities=[AgentCapability.CODE, AgentCapability.ANALYSIS],
            system_prompt=(
                "You are a master of efficiency and speed. "
                "Your goal is to optimize code, reduce latency, and remove bottlenecks. "
                "Prefer 'YOLO' implementation speed over perfection, provided it works."
            ),
            temperature=0.3,
            description="Focuses on speed, refactoring, and optimizations.",
        )

    @staticmethod
    def get_critic() -> AgentProfile:
        return AgentProfile(
            name="CRITIC",
            role="Validation and Security Auditor",
            capabilities=[AgentCapability.CRITICISM, AgentCapability.SECURITY],
            system_prompt=(
                "You are a harsh but fair critic. "
                "Your job is to find flaws, security vulnerabilities, and logic gaps. "
                "Never accept the 'happy path' without checking edge cases."
            ),
            temperature=0.1,
            description=" rigorous validator for security and logic.",
        )

    @staticmethod
    def list_all() -> dict[str, AgentProfile]:
        return {
            "DESIGNER": StandardRoster.get_designer(),
            "ACCELERATOR": StandardRoster.get_accelerator(),
            "CRITIC": StandardRoster.get_critic(),
        }
