"""Antigravity Pipeline - Full Wire with ATP 3-20.96 Cavalry Squadron
===================================================================

Flow (Kosmos embedded per stage - ATP 3-20.96 aligned):
1. INTAKE: Gemini 2.5 Flash (2M context) + Kosmos Cavalry (430 agents)
# 2. RESEARCH: Flying minion (Gemini) + Kosmos Cavalry (430 agents)
# 3. RESEARCH: Gemini Deep Research + Kosmos Cavalry (430 agents)
4. EXECUTE: 10× Gemini Code Assist + Kosmos Cavalry (4,300 agents)
5. VALIDATE: CodePMCS scans and auto-fixes
6. DEPLOY: GitHub → Cloud Build → Cloud Run

Total: 5,590 agents (430 × 13 Kosmos instances)
Each Kosmos reaches consensus BEFORE passing to next stage.

Army Doctrine Alignment:
- ATP 3-20.96: Differentiated recon (Zone/Area/Route/Force), security (Screen/Guard/Cover)
- FM 6-0: MDMP 7-step planning, TLP 8-step for rapid ops
- ATP 5-19: 5-step CRM (Composite Risk Management)
- FM 3-0: Six Warfighting Functions (C2, Intel, Fires, Movement, Sustainment, Protection)
- FM 7-8: Battle Drills for error handling
- ADP 6-22: Agent attributes and competencies
"""

import uuid
from dataclasses import dataclass, field
from typing import Any

from .autoresearch import minion
from .deploy import DeployManager
from .execute import create_execution_pool
from .intake import GeminiIntake
from .validate import CodePMCSClient

# from core.persistent_memory import PersistentMemory as MemoryPersistence  # Removed in v2.0


@dataclass
class PipelineResult:
    run_id: str
    status: str
    output: str
    artifacts: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# Import Kosmos for embedded consensus per stage
try:
    from kosmos.core import KosmosInstance, KosmosType, create_kosmos  # noqa: F401

    KOSMOS_AVAILABLE = True
except ImportError:
    KOSMOS_AVAILABLE = False

# ... (imports remain)

# Constants
DOCTRINE_AVAILABLE = True  # Assuming Doctrine is available or should be defaulted


class AntigravityPipeline:
    """The Central Brain - Orchestrates all LLMs with ATP 3-20.96 Cavalry Squadron

    - Gemini 1.5 Pro: Intake & Execution
    - Flying minion: Autonomous Research & Tool Use
    """

    # ... (constants remain)

    def __init__(
        self,
        gemini_api_key: str,
        github_token: str,
        codepmcs_url: str | None = None,
        use_kosmos: bool = True,
        use_doctrine: bool = True,
    ):
        self.use_kosmos = use_kosmos and KOSMOS_AVAILABLE
        self.use_doctrine = use_doctrine and DOCTRINE_AVAILABLE

        # Stage 1: Gemini Intake (Gemini 1.5 Pro - "All Else")
        # Ensure we pass the API key if needed
        self.intake = GeminiIntake(api_key=gemini_api_key)
        if self.use_kosmos:
            self.intake_kosmos = create_kosmos(KosmosType.GEMINI_INTAKE)

        # Stage 2: Flying minion Autonomous Research (Gemini 1.5 Pro)
        # Replaces Perplexity/Grok with Google MCP-enabled agents
        self.minion = minion(model="gemini-3.1-flash-lite-preview")

        # Stage 3: 10× Gemini Code Assist (Gemini 2.0 Flash - "Heavy Lifting")
        self.executor = create_execution_pool(pool_size=10, model="gemini-3.1-flash-lite-preview")

        # Stage 4: Validation and deployment
        self.validator = CodePMCSClient(codepmcs_url) if codepmcs_url else None
        self.deployer = DeployManager(github_token)

        # Memory Persistence (G. Drive / Local)
        # Using a default path for now, can be parameterized
        # Memory Persistence (G. Drive / Local)
        # Using a default path for now, can be parameterized
        # self.memory = MemoryPersistence(repo_path="output/memory") # Legacy removed

    async def run(self, task: str) -> PipelineResult:
        """Execute the full cavalry squadron pipeline
        1. Intake (Gemini 1.5 Pro)
        2. Research (Flying minion)
        3. Execution (Gemini 2.0 Flash)
        4. Validation
        """
        run_id = str(uuid.uuid4())[:8]
        # start_time = datetime.now() # Unused for now

        # 0. Context Engineering Cycle: Fetch -> Prepare
        print(f"[ANTIGRAVITY] Run ID: {run_id}")

        # Initialize or Load Session (For now, new session per run, future: persist across runs)
        # Note: In a real server, this would retrieve an existing session by user_id
        from pinkln.context import ContextCompiler, MemoryManager, Session

        # Initialize Context Components
        # MemoryManager: Manages long-term knowledge (Declarative/Procedural)
        memory_manager = MemoryManager()
        # TODO: Hydrate memory_manager from self.memory (legacy persistence) if needed
        # For now, we assume a fresh manager or one that connects to an external DB

        context_compiler = ContextCompiler(memory_manager)
        current_session = Session(session_id=run_id)

        # User Input Event
        current_session.add_event("user", task)

        # 1. Compile Context (Blocking "Hot Path")
        # Fetches memories, compacts history, and builds the prompt
        compiled_context = context_compiler.compile(
            session=current_session,
            query=task,
            system_instruction="You are ANTIGRAVITY, a high-IQ autonomous capability engine.",
        )

        # Step 1: INTAKE - Decompose into atoms
        print("[ANTIGRAVITY] Step 1: INTAKE - Gemini 1.5 Pro + Kosmos (430 agents)")

        # We pass the fully compiled context to intake
        atoms = await self.intake.decompose(compiled_context)
        print(f"[ANTIGRAVITY] Decomposed into {len(atoms)} atoms")

        # Agent Response Event (Intake thought process)
        current_session.add_event(
            "model",
            f"Decomposed task into {len(atoms)} atoms.",
            type="message",
        )

        # ... (rest of pipeline)

        enriched_atoms = atoms  # Start with base atoms

        # Step 2: RESEARCH - Flying minion (Gemini 1.5 Pro + MCP)
        print("[ANTIGRAVITY] Step 2: RESEARCH - Flying minion (Gemini 1.5 Pro + Google MCP)")

        for atom in enriched_atoms:
            try:
                # minion perform deep dive based on atom content
                # Pass run_id and memory context
                monkey_result = await self.minion.execute_task(
                    f"Research and Validate: {atom.content}",
                    context={
                        "atom_id": atom.id,
                        "risk_level": str(atom.risk_level),
                        "run_id": run_id,
                        "past_context": compiled_context,  # Pass full context
                    },
                )

                if monkey_result.get("status") == "complete":
                    atom.reasoning_chain.append(f"Flying minion Plan: {monkey_result.get('plan')}")

                    # Log tool outputs to session
                    for res in monkey_result.get("results", []):
                        current_session.add_event("tool", res, type="tool_output")
                        atom.reasoning_chain.append(
                            f"Tool ({res.get('tool')}): {res.get('result')}",
                        )

            except Exception as e:
                print(f"Flying Monkey error for atom {atom.id}: {e}")
                # Use errors list if defined, otherwise print
                print(f"Research error: {e}")

        # Step 3: EXECUTE - 10× Gemini Code Assist (Gemini 2.0 Flash)
        # Kosmos consensus is EMBEDDED in GeminiCodeAssistPool - no separate step
        print("[ANTIGRAVITY] Step 3: EXECUTE - 10× Gemini Code Assist + Kosmos (4,300 agents)")
        # ... (Execution loop remains same)

        # ... (Rest of run method)

    def get_status(self) -> dict[str, Any]:
        """Get pipeline status"""
        status = {
            # ... (existing fields)
            "stages": {
                "intake": {
                    "model": "gemini-3.1-flash-lite-preview",
                    # ...
                },
                "autoresearch": {"model": "gemini-3.1-flash-lite-preview", "status": "active"},
                "execute": {
                    "model": "gemini-3.1-flash-lite-preview",
                    # ...
                },
            },
        }
        # ...
        return status
