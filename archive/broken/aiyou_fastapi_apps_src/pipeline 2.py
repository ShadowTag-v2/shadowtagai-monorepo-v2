"""
Antigravity Pipeline - Full Wire

Flow:
1. INTAKE: Gemini 3 Pro (2M context) atomizes input
2. RESEARCH: Perplexity → SuperGrok enriches atoms
3. EXECUTE: 10× Claude Code generates code
4. VOTE: n-autoresearch/Kosmos/BioAgents 650-agent consensus
5. VALIDATE: CodePMCS scans and auto-fixes
6. DEPLOY: GitHub → Cloud Build → Cloud Run
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .deploy import DeployManager
from .execute import ClaudeCodePool
from .intake import GeminiIntake
from .research import ResearchChain
from .validate import CodePMCSClient
from .vote import n-autoresearch/Kosmos/BioAgentsClient


class RiskLevel(Enum):
    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class JuraTier(Enum):
    FREE = "FREE"  # 30% traffic, 1 agent
    FLASH = "FLASH"  # 60% traffic, 3 agents
    PRO = "PRO"  # 10% traffic, 8+ agents


@dataclass
class Atom:
    """Atomic unit of work from intake"""

    id: str
    content: str
    risk_level: RiskLevel
    jura_tier: JuraTier
    tests: list[str] = field(default_factory=list)
    reasoning_chain: list[str] = field(default_factory=list)


@dataclass
class AntigravityMessage:
    """Standard message format for all Antigravity communications"""

    from_: str = "antigravity"
    to: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    atom_id: str = ""

    reasoning_chain: dict[str, Any] = field(default_factory=dict)
    task: dict[str, Any] = field(default_factory=dict)
    n-autoresearch/Kosmos/BioAgents: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "from": self.from_,
            "to": self.to,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "atom_id": self.atom_id,
            "reasoning_chain": self.reasoning_chain,
            "task": self.task,
            "n-autoresearch/Kosmos/BioAgents": self.n-autoresearch/Kosmos/BioAgents,
        }


@dataclass
class PipelineResult:
    """Result from full pipeline execution"""

    session_id: str
    success: bool
    atoms_processed: int
    code_generated: list[dict[str, Any]]
    consensus_results: list[dict[str, Any]]
    validation_results: list[dict[str, Any]]
    deployment: dict[str, Any] | None
    errors: list[str] = field(default_factory=list)


class AntigravityPipeline:
    """
    The Central Brain - Orchestrates all LLMs

    8,450 total agents:
    - Gemini 3 Pro: 650 agents (intake)
    - Perplexity: 650 agents (research)
    - SuperGrok: 650 agents (X/Grokipedia)
    - Claude Code ×10: 6,500 agents (execution)
    """

    CONSENSUS_THRESHOLDS = {
        RiskLevel.LOW: 0.50,
        RiskLevel.MED: 0.60,
        RiskLevel.HIGH: 0.75,
        RiskLevel.EXTREME: 0.90,
    }

    def __init__(
        self,
        gemini_api_key: str,
        perplexity_api_key: str,
        grok_api_key: str,
        anthropic_api_key: str,
        github_token: str,
        n-autoresearch/Kosmos/BioAgents_url: str = "https://n-autoresearch/Kosmos/BioAgents-server-215390634092.us-central1.run.app",
        codepmcs_url: str | None = None,
    ):
        self.intake = GeminiIntake(gemini_api_key)
        self.research = ResearchChain(perplexity_api_key, grok_api_key)
        self.executor = ClaudeCodePool(anthropic_api_key, pool_size=10)
        self.voter = n-autoresearch/Kosmos/BioAgentsClient(n-autoresearch/Kosmos/BioAgents_url)
        self.validator = CodePMCSClient(codepmcs_url) if codepmcs_url else None
        self.deployer = DeployManager(github_token)

        self.session_id = str(uuid.uuid4())

    async def run(self, task: str, auto_deploy: bool = False) -> PipelineResult:
        """
        Run the full pipeline:
        Input → Gemini → Perplexity → Grok → Claude → n-autoresearch/Kosmos/BioAgents → CodePMCS → Deploy
        """
        errors = []
        code_generated = []
        consensus_results = []
        validation_results = []
        deployment = None

        # Step 1: INTAKE - Gemini 3 Pro atomizes (2M context)
        print("[ANTIGRAVITY] Step 1: INTAKE - Gemini 3 Pro (2M context)")
        atoms = await self.intake.atomize(task)
        print(f"[ANTIGRAVITY] Created {len(atoms)} atoms")

        # Step 2: RESEARCH - Perplexity + SuperGrok enrich
        print("[ANTIGRAVITY] Step 2: RESEARCH - Perplexity → SuperGrok")
        enriched_atoms = await self.research.enrich(atoms)
        print(f"[ANTIGRAVITY] Enriched {len(enriched_atoms)} atoms with research")

        # Step 3: EXECUTE - 10× Claude Code generates
        print("[ANTIGRAVITY] Step 3: EXECUTE - 10× Claude Code")
        for atom in enriched_atoms:
            try:
                code = await self.executor.generate(atom)
                code_generated.append(
                    {
                        "atom_id": atom.id,
                        "code": code,
                        "reasoning": atom.reasoning_chain,
                    }
                )
            except Exception as e:
                errors.append(f"Execute error for atom {atom.id}: {str(e)}")
        print(f"[ANTIGRAVITY] Generated code for {len(code_generated)} atoms")

        # Step 4: VOTE - n-autoresearch/Kosmos/BioAgents 650-agent consensus
        print("[ANTIGRAVITY] Step 4: VOTE - n-autoresearch/Kosmos/BioAgents (650 agents)")
        for code_item in code_generated:
            atom = next((a for a in enriched_atoms if a.id == code_item["atom_id"]), None)
            threshold = self.CONSENSUS_THRESHOLDS.get(atom.risk_level, 0.75) if atom else 0.75

            try:
                result = await self.voter.vote(
                    code=code_item["code"], task=task, threshold=threshold
                )
                consensus_results.append(
                    {
                        "atom_id": code_item["atom_id"],
                        "approved": result.get("approved", False),
                        "confidence": result.get("confidence", 0),
                        "votes": result.get("votes", {}),
                    }
                )
            except Exception as e:
                errors.append(f"Vote error for atom {code_item['atom_id']}: {str(e)}")

        approved_code = [
            c for c, r in zip(code_generated, consensus_results) if r.get("approved", False)
        ]
        print(f"[ANTIGRAVITY] {len(approved_code)}/{len(code_generated)} approved by consensus")

        # Step 5: VALIDATE - CodePMCS scans
        if self.validator and approved_code:
            print("[ANTIGRAVITY] Step 5: VALIDATE - CodePMCS")
            for code_item in approved_code:
                try:
                    scan_result = await self.validator.scan(code_item["code"])
                    validation_results.append(
                        {
                            "atom_id": code_item["atom_id"],
                            "passed": scan_result.get("passed", False),
                            "issues": scan_result.get("issues", []),
                            "fixes": scan_result.get("fixes", []),
                        }
                    )
                except Exception as e:
                    errors.append(f"Validate error for atom {code_item['atom_id']}: {str(e)}")

        # Step 6: DEPLOY - GitHub → Cloud Build
        if auto_deploy and approved_code:
            print("[ANTIGRAVITY] Step 6: DEPLOY - GitHub → Cloud Run")
            try:
                deployment = await self.deployer.deploy(
                    code_items=approved_code, session_id=self.session_id
                )
            except Exception as e:
                errors.append(f"Deploy error: {str(e)}")

        return PipelineResult(
            session_id=self.session_id,
            success=len(errors) == 0 and len(approved_code) > 0,
            atoms_processed=len(atoms),
            code_generated=code_generated,
            consensus_results=consensus_results,
            validation_results=validation_results,
            deployment=deployment,
            errors=errors,
        )

    def build_message(
        self, to: str, atom: Atom, task_type: str, content: str
    ) -> AntigravityMessage:
        """Build a standard Antigravity message"""
        return AntigravityMessage(
            to=to,
            atom_id=atom.id,
            reasoning_chain={
                "prior_reasoning": atom.reasoning_chain,
                "evidence_found": [],
                "biz_acumen_applied": "",
                "tests_required": atom.tests,
            },
            task={
                "type": task_type,
                "content": content,
                "risk_level": atom.risk_level.value,
                "jura_tier": atom.jura_tier.value,
            },
            n-autoresearch/Kosmos/BioAgents={
                "agents_assigned": 650,
                "vote_required": True,
                "consensus_threshold": self.CONSENSUS_THRESHOLDS[atom.risk_level],
            },
        )
