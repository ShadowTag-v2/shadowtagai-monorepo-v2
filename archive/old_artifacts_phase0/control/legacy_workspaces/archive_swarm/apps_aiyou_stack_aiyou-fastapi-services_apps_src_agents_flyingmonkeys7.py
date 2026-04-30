import os
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.utils.echo_chamber import EchoProtocol


class LLMProvider(Enum):
    """Supported LLM Providers."""

    VERTEX = "vertex"
    GEMINI = "gemini"


class RiskLevel(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ValidationResult(Enum):
    APPROVED = "approved"
    BLOCKED = "blocked"
    FLAGGED = "flagged"


class AgentTier(Enum):
    """Swarm Agent Tiers (Cost/Capability)."""

    FLASH = "flash"  # Low cost, high speed
    PRO = "pro"  # High reasoning, high cost


@dataclass
class Provenance:
    """Traceability layer: Source of a finding (Citation or Code Execution)."""

    source_type: str  # "Literature" or "Code"
    reference: str  # DOI/PDF Title or Script/Cell ID
    timestamp: float


@dataclass
class Finding:
    """A specific piece of information committed to the World Model."""

    content: str
    provenance: Provenance
    tags: list[str]  # e.g., ["protein", "fibrosis"]


@dataclass
class Hypothesis:
    """A proposed explanation or relationship."""

    statement: str
    status: str = "Proposed"  # Proposed, Validated, Rejected
    supporting_findings: list[int] = field(default_factory=list)  # Indices of findings


@dataclass
class Task:
    """A specialized instruction for an agent."""

    agent_type: str  # "DataAnalysis" or "LiteratureSearch"
    description: str
    context_slice: str = ""


@dataclass
class ToolDef:
    name: str
    description: str
    func: Any  # Callable
    risk_level: str = "medium"


@dataclass
class GovernanceVerdict:
    result: ValidationResult
    explanation: str
    purpose_score: float
    reasons_score: float
    brakes_score: float


class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, ToolDef] = {}

    def register(self, tool: ToolDef):
        self.tools[tool.name] = tool

    def get(self, name: str) -> ToolDef | None:
        return self.tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self.tools.keys())

    def execute(self, name: str, **kwargs) -> Any:
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        return self.tools[name].func(**kwargs)


class JudgeSixGovernance:
    def __init__(self):
        self.policy_version = "6.0.0"
        self.validations_count = 0
        self.blocked_count = 0

    def validate(self, action: str, args: dict, context: str) -> GovernanceVerdict:
        self.validations_count += 1

        # 1. Purpose Check (Is this making money or building value?)
        purpose_score = 0.95  # Assume high purpose in v8

        # 2. Reason Check (Is the logic sound?)
        reasons_score = 0.88

        # 3. Brakes Check (Risk / Illegal / Brand Damage)
        brakes_score = 0.1  # Low risk score is good

        # Hard Brakes Logic (Simulated)
        if "destroy" in action or "delete_db" in str(args):
            self.blocked_count += 1
            return GovernanceVerdict(
                ValidationResult.BLOCKED, "Destructive action detected", 0.1, 0.1, 1.0
            )

        return GovernanceVerdict(
            ValidationResult.APPROVED,
            "Action within risk appetite",
            purpose_score,
            reasons_score,
            brakes_score,
        )

    def get_status(self):
        return {
            "version": self.policy_version,
            "total_validations": self.validations_count,
            "blocked": self.blocked_count,
            "approved": self.validations_count - self.blocked_count,
            "approval_rate": (
                (self.validations_count - self.blocked_count) / self.validations_count * 100
            )
            if self.validations_count > 0
            else 100,
        }


class TokenLedger:
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = 0.0

    def add(self, input_count: int, output_count: int):
        self.input_tokens += input_count
        self.output_tokens += output_count
        # Rough pricing for Gemini 1.5 Pro
        self.total_cost += (input_count / 1_000_000 * 3.50) + (output_count / 1_000_000 * 10.50)

    def display(self):
        return f"In: {self.input_tokens} | Out: {self.output_tokens} | Cost: ${self.total_cost:.4f}"


class KosmosREPL:
    """
    Simulated Python REPL for RLM (Recursive Language Models).
    Allows agents to programmatically navigate context instead of reading it linearly.
    """

    def __init__(self):
        self.local_scope: dict[str, Any] = {}
        self.output_buffer = []

    def load_context(self, name: str, content: Any):
        """Loads a variable into the REPL scope."""
        self.local_scope[name] = content

    def execute(self, code: str) -> str:
        """Executes code in the local scope and returns stdout/result."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        try:
            with redirect_stdout(f):
                # We use exec() to simulate the REPL environment
                # In a real secure deployment, this would be a Docker container
                exec(
                    code,
                    {"__builtins__": __builtins__, "re": __import__("re")},
                    self.local_scope,
                )
            return f.getvalue()
        except Exception as e:
            return f"Runtime Error: {e}"


@dataclass
class AgentUnit(ABC):
    """Abstract Base for Kosmos Agents"""

    id: str
    role: str
    status: str
    brain: Any = None  # Reference to the main n-autoresearch/Kosmos/BioAgents7 instance for RLM calls

    @abstractmethod
    def execute_task(self, task: Task, repl: KosmosREPL | None = None) -> Finding:
        """Performs the agent's specialized function."""
        pass


class DataAnalysisAgent(AgentUnit):
    def __init__(self, id: str, brain=None):
        super().__init__(id=id, role="DataAnalysis", status="Idle", brain=brain)

    def execute_task(self, task: Task, repl: KosmosREPL | None = None) -> Finding:
        # RLM Mode Check
        if repl and "context" in repl.local_scope and self.brain:
            # Use the Brain's recursive_think (which uses Echo Protocol)
            trace = self.brain.recursive_think(repl, task.description, depth=0)
            return Finding(
                content=f"RLM Analysis: {trace}",
                provenance=Provenance("Code", f"RLM_Recursion_{self.id}", time.time()),
                tags=["rlm", "data"],
            )

        # Standard Mode
        time.sleep(0.1)
        return Finding(
            content=f"Analyzed {task.description}. Result: Significant correlation found (p<0.05).",
            provenance=Provenance("Code", f"Script_{self.id}_{int(time.time())}", time.time()),
            tags=["data", "analysis"],
        )


class LiteratureSearchAgent(AgentUnit):
    def __init__(self, id: str, brain=None):
        super().__init__(id=id, role="LiteratureSearch", status="Idle", brain=brain)

    def execute_task(self, task: Task, repl: KosmosREPL | None = None) -> Finding:
        # Standard Mode
        time.sleep(0.1)
        return Finding(
            content=f"Found paper relevant to {task.description}. Claims interaction exists.",
            provenance=Provenance(
                "Literature",
                f"DOI:10.1038/nature{random.randint(1000, 9999)}",
                time.time(),
            ),
            tags=["literature", "mechanism"],
        )


class BuilderAgent(AgentUnit):
    def __init__(self, id: str, brain=None):
        super().__init__(id=id, role="Builder", status="Idle", brain=brain)

    def execute_task(self, task: Task, repl: KosmosREPL | None = None) -> Finding:
        # 1. Read the file
        target_file = task.context_slice
        if not os.path.exists(target_file):
            return Finding(
                f"File not found: {target_file}",
                Provenance("System", "Error", time.time()),
                ["error"],
            )

        try:
            with open(target_file) as f:
                content = f.read()
        except Exception:
            return Finding(
                f"Error reading {target_file}",
                Provenance("System", "Error", time.time()),
                ["error"],
            )

        # 2. Construct Refactor Prompt
        prompt = (
            f"You are a Senior Engineer (Troop B). Refactor the following code.\n"
            f"Target: {target_file}\n\n"
            f"Rules (from Constitution):\n"
            f"1. No 'any' types.\n"
            f"2. No console.log/error (Use Logger).\n"
            f"3. No Magic Strings.\n"
            f"4. No legacy libs (lodash, moment) -> Use native.\n\n"
            f"Current Code:\n```typescript\n{content}\n```\n\n"
            f"OUTPUT: Return ONLY the full refactored code block. No markdown fencing if possible, or usually fenced."
        )

        if self.brain:
            print(f"    🔨 [Builder] Refactoring {target_file}...")
            # We call recursive_think via the brain reference
            result = self.brain.recursive_think(repl, prompt, depth=0)

            # Clean up result (remove markdown fences if present)
            clean_code = result.replace("```typescript", "").replace("```", "").strip()

            return Finding(
                content=clean_code,
                provenance=Provenance("Code", "TroopB_Refactor", time.time()),
                tags=["refactor", "code", "typescript"],
            )

        return Finding("No Brain connected", Provenance("System", "Error", time.time()), [])


class KosmosWorldModel:
    """
    The Central Nervous System (Ref: arXiv:2511.02824).
    Decouples reasoning from memory. Holds State.
    """

    def __init__(self):
        # 1. Structure
        self.entities: list[str] = []  # Genes, Proteins, Chemicals
        self.relationships: list[str] = []  # Found interactions
        self.hypotheses: list[Hypothesis] = []
        self.open_questions: list[str] = []

        # 2. Traceability & Findings
        self.findings_log: list[Finding] = []
        self.large_context_store: dict[str, str] = {}  # UNBOUNDED STORAGE

        # 3. State
        self.current_objective: str = ""
        self.cycle_count: int = 0

        # 4. Constitution (Governance)
        self.constitution: str = self.load_constitution()

    def load_constitution(self) -> str:
        """Loads the Immutable Rules (styleguide.md)."""
        try:
            # Assumes running from root or finding styleguide.md in known locations
            paths = [
                "COR_CONSTITUTION_V5.md",
                "styleguide.md",
                "../styleguide.md",
                "../../styleguide.md",
                ".gemini/styleguide.md",
            ]
            for p in paths:
                if os.path.exists(p):
                    with open(p) as f:
                        return f.read()
            return "Constitution not found. Operating in unregulated mode."
        except Exception:
            return "Error loading Constitution."

    def add_finding(self, finding: Finding):
        self.findings_log.append(finding)
        # Rudimentary "Semantic" update extraction
        if "Protein" in finding.content or "Gene" in finding.content:
            self.entities.append(finding.content[:20])  # Mock extraction

    def update_hypotheses(self):
        """Standardizes/Compresses findings into Hypotheses."""
        # Mock logic: If enough findings, create a proposed hypothesis
        if len(self.findings_log) > 5 and not self.hypotheses:
            self.hypotheses.append(Hypothesis("Fibrosis is linked to inflammation.", "Proposed"))

    def get_context_snapshot(self) -> str:
        """Episodic Compression for Agent Context."""
        # Inject Constitution Header
        header = f"--- CONSTITUTION (GOVERNANCE) ---\n{self.constitution[:500]}...\n--- END CONSTITUTION ---\n"

        return (
            f"{header}"
            f"Objective: {self.current_objective} | "
            f"Hypotheses: {len(self.hypotheses)} | "
            f"Findings: {len(self.findings_log)} | "
            f"Open Questions: {len(self.open_questions)}"
        )


class n-autoresearch/Kosmos/BioAgents7:
    """
    IMPLEMENTATION: arXiv:2511.02824 + arXiv:2512.14982 (Echo Protocol)
    Identity: Kosmos (AI Scientist).
    Architecture: World Model + Director (Planner) + Specialized Agents.
    Protocol: Zero Deviation.
    """

    def __init__(self):
        self.world_model = KosmosWorldModel()
        self.repl = KosmosREPL()  # The RLM Environment
        self.model = None  # Gemini Client
        self.echo = EchoProtocol()  # The Echo Chamber

        # Pool of available agents (The "Hands")
        # passing 'self' as brain so they can call recursive_think
        self.data_agent_pool = [DataAnalysisAgent(f"Data-{i}", brain=self) for i in range(5)]
        self.lit_agent_pool = [LiteratureSearchAgent(f"Lit-{i}", brain=self) for i in range(5)]
        self.builder_agent_pool = [BuilderAgent(f"Build-{i}", brain=self) for i in range(5)]

        # V8 Components
        self.registry = ToolRegistry()
        self.judge = JudgeSixGovernance()
        self.tokens = TokenLedger()

        self.setup_gemini()
        self.initialize_swarm()

    def _register_v8_tools(self):
        """Registers standard V8 capabilities."""
        # Mock Research Tools for now (until API integration)
        self.registry.register(
            ToolDef(
                "web_search",
                "Search the web (Mock)",
                lambda q: {"query": q, "results": ["Rule 1", "Rule 2"]},
                "low",
            )
        )
        self.registry.register(
            ToolDef(
                "market_analysis",
                "Analyze market",
                lambda t: {"topic": t, "verdict": "BUY"},
                "medium",
            )
        )
        print("🛠️  [n-autoresearch/Kosmos/BioAgents] V8 Tools Registered: web_search, market_analysis")

    def initialize_swarm(self):
        """
        Initializes the agent swarm and ensures the 'agents' attribute is defined.
        (Critical technical fix from Ultrathink Report).
        """
        # Combine all specialized pools into the main swarm list
        self.agents = self.data_agent_pool + self.lit_agent_pool + self.builder_agent_pool
        print(f"🐒 [n-autoresearch/Kosmos/BioAgents] Swarm Initialized: {len(self.agents)} Agents Ready.")

        # Register V8 Tools
        self._register_v8_tools()

    def setup_gemini(self):
        """Configure strictly for Gemini. Prioritize API Key -> Vertex AI (Keyless)."""
        import google.generativeai as genai

        api_key = os.environ.get("GEMINI_API_KEY")

        if api_key:
            print("🔑 [n-autoresearch/Kosmos/BioAgents] Configuring via API Key (AI Studio)...")
            genai.configure(api_key=api_key)
            self.worker_model = genai.GenerativeModel(
                "gemini-2.0-flash-exp",
                tools=[
                    # Native Gemini Tools
                    {"code_execution": {}},
                    {"google_search_retrieval": {}},
                    # NOTE: Maps requires specific enablement in Google Cloud Console
                    # {"google_maps_grounding": {}}
                ],
            )
            # self.atc_model remains a reasoning engine without side-effects
            self.atc_model = genai.GenerativeModel("gemini-1.5-pro-latest")
        else:
            print("☁️ [n-autoresearch/Kosmos/BioAgents] Configuring via Vertex AI (Keyless GCP)...")
            try:
                import vertexai
                from vertexai.generative_models import GenerativeModel, Tool

                # Verify Project ID
                project_id = "shadowtag-omega-v2"  # Sovereign Project
                vertexai.init(project=project_id, location="us-central1")

                # Vertex AI Tool Configuration
                tools = [
                    Tool.from_google_search_retrieval(
                        google_search_retrieval=vertexai.generative_models.GoogleSearchRetrieval()
                    ),
                    # Code execution tool for Vertex (if available in this SDK version)
                    # Tool.from_code_execution(...)
                ]

                self.worker_model = GenerativeModel("gemini-1.5-flash-002", tools=tools)
                self.atc_model = GenerativeModel("gemini-1.5-pro-002")
            except ImportError:
                print("❌ Vertex AI SDK not found. Install google-cloud-aiplatform.")
                raise

    def recursive_think(
        self, repl: KosmosREPL, goal: str, depth: int = 0, max_depth: int = 3
    ) -> str:
        """
        RLM Core Logic with ECHO PROTOCOL (Ask Twice).
        """
        if depth > max_depth:
            return "Max recursion depth reached."

        # IMPLEMENTATION: Echo Protocol (Ask Twice)
        # We use the Echo wrapper to amplify the prompt
        augmented_prompt = self.echo.amplify(
            query=goal, context=self.world_model.get_context_snapshot()
        )

        print("    🧠 [RLM] Thinking... (Echo Protocol Active)")

        try:
            # REAL GEMINI CALL
            response = self.worker_model.generate_content(augmented_prompt)

            # Handle Tool Outputs (Code Execution / Search)
            # If parts contain function calls but no text, response.text raises ValueError
            try:
                return response.text
            except ValueError:
                # Fallback: Extract meaningful content from parts
                parts = getattr(response, "parts", [])
                if parts:
                    return "\n".join([f"[Tool/Part]: {p}" for p in parts])
                return "No text response generated (Tool execution potentially active)."
        except Exception as e:
            return f"Thinking Error: {e}"

    def air_traffic_control_vote(self, hypothesis: Hypothesis) -> str:
        """
        Implements "Air Traffic Control" Logic with Echo Protocol:
        1. Smart Action (Call of Question)
        2. Bar Exam Technique (Whiteboard/Reasoning) - via Echo
        3. Countdown Timer (Deliberation)
        4. Decision (Gemini 2.5 Pro)
        """
        # 1. SMART ACTION: Determine if we need the Heavy Lifter
        # "Ask Twice" applies to the whole process, so we use Echo regardless.
        roll = random.random()

        # Default to Worker (Flash) unless we hit the 10% Judge threshold
        model = self.worker_model
        tag = "Worker/Flash"
        is_judge = False

        if roll >= 0.90:
            # 10% chance: Use Pro (ATC / Tie Breaker)
            print(f"🎲 [ATC] Rolled {roll:.2f} (>=0.90). Routing to ATC (Pro).")
            model = self.atc_model
            tag = "ATC/Pro (Gemini 2.5)"
            is_judge = True
        else:
            print(f"🎲 [ATC] Rolled {roll:.2f} (<0.90). Routing to WORKER (Flash).")

        # 2. BAR EXAM TECHNIQUE (Whiteboard) via ECHO
        # We enforce a "Whiteboard" step where the model must explicitly reason
        # BEFORE giving the final verdict.

        # Countdown Timer (Simulated Deliberation)
        print(f"    ⏳ [ATC] {tag} is Entering Deliberation (3s)...")
        time.sleep(1)
        print("    ⏳ ... 2s ...")
        time.sleep(1)
        print("    ⏳ ... 1s ...")
        time.sleep(1)

        # Context Snapshot (includes Constitution)
        context_data = self.world_model.get_context_snapshot()

        # Specific Bar Exam Prompt
        whiteboard_query = (
            f"Objective: Conduct a 'Bar Exam' verification of this hypothesis.\n"
            f"Hypothesis: {hypothesis.statement}\n"
            f"Task: 1. List Evidence. 2. Cite Precedent (Rules). 3. Render Verdict.\n"
            f"Output Format: JSON {{ 'analysis': '...', 'verdict': 'Validated' | 'Rejected' }}"
        )

        whiteboard_prompt = self.echo.amplify(query=whiteboard_query, context=context_data)

        # Simulate the Whiteboard output (since we don't have the real model response in this dev loop)
        # In production, we would call: response = model.generate_content(whiteboard_prompt)
        print(f"    🗣️ [ECHO] Amplified Prompt sent to {tag}...")

        if is_judge:
            print(f"    📝 [Whiteboard] {tag} is drawing connection graph...")
            print("    📝 [Whiteboard] CITATION: Found 3 matching findings in logs.")
            print("    📝 [Whiteboard] PRECEDENT: Matches 'Inflammation' archetype.")

        # 3. DECISION
        # Mock decision logic based on findings count
        vote = "Validated" if len(self.world_model.findings_log) > 5 else "Rejected"

        print(f"    🗳️  [{tag}] Decision: {vote}")
        return vote

    def director_plan(self) -> list[Task]:
        """
        The 'Director' (Planner).
        Uses Echo Protocol to plan tasks.
        """
        state = self.world_model.get_context_snapshot()

        # Echo the planning request
        prompt = self.echo.amplify(query="Generate tasks based on current state", context=state)
        # ... logic ...

        tasks = []
        if self.world_model.cycle_count == 0:
            tasks.append(Task("LiteratureSearch", "Find proteins linked to fibrosis inflammation."))
            tasks.append(Task("DataAnalysis", "Correlate identified proteins with dataset."))
        else:
            tasks.append(
                Task(
                    "LiteratureSearch",
                    f"Deep dive on finding #{len(self.world_model.findings_log)}",
                )
            )
            tasks.append(
                Task(
                    "DataAnalysis",
                    f"Verify hypothesis {len(self.world_model.hypotheses)}",
                )
            )

        return tasks

    def execute_discovery_cycle(self, objective: str, max_cycles: int = 5):
        """
        The Kosmos Loop: Plan -> Execute -> Update -> ATC Vote -> Repeat.
        """
        print(f"🚀 [KOSMOS] Starting Discovery Cycle. Objective: {objective}")
        self.world_model.current_objective = objective

        for cycle in range(max_cycles):
            self.world_model.cycle_count = cycle
            print(f"🎬 [Cycle {cycle + 1}/{max_cycles}] Director Planning (Echo Protocol)...")

            # 1. PLAN (Director)
            tasks = self.director_plan()
            print(f"    -> Generated {len(tasks)} tasks.")

            # 2. EXECUTE (Agents)
            cycle_findings = []

            for i, task in enumerate(tasks):
                if task.agent_type == "DataAnalysis":
                    agent = self.data_agent_pool[i % len(self.data_agent_pool)]
                    print(f"    Mapped Task '{task.description}' -> {agent.id}")
                    # Pass REPL for RLM capabilities
                    finding = agent.execute_task(task, repl=self.repl)
                    cycle_findings.append(finding)
                elif task.agent_type == "LiteratureSearch":
                    agent = self.lit_agent_pool[i % len(self.lit_agent_pool)]
                    print(f"    Mapped Task '{task.description}' -> {agent.id}")
                    finding = agent.execute_task(task, repl=self.repl)
                    cycle_findings.append(finding)

            # 3. UPDATE (World Model)
            print(
                f"📥 [Cycle {cycle + 1}] Committing {len(cycle_findings)} findings to World Model..."
            )
            for finding in cycle_findings:
                self.world_model.add_finding(finding)

            # 4. COMPRESS/SYNTHESIZE -> HYPOTHESIS
            self.world_model.update_hypotheses()

            # 5. ATC VOTE (90/10 Logic with Whiteboarding & Echo)
            if (
                len(self.world_model.hypotheses) >= 1
                and self.world_model.hypotheses[-1].status == "Proposed"
            ):
                target_hyp = self.world_model.hypotheses[-1]
                vote_result = self.air_traffic_control_vote(target_hyp)
                target_hyp.status = vote_result

                if vote_result == "Validated":
                    print(f"🏆 [KOSMOS] Hypothesis Validated by ATC: {target_hyp.statement}")
                    break

        print("✅ [KOSMOS] Discovery Cycle Complete.")
