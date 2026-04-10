import enum
import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================


class RiskLevel(int, enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ValidationResult(enum.Enum):
    APPROVED = "approved"
    BLOCKED = "blocked"
    FLAGGED = "flagged"


# =============================================================================
# TOOL REGISTRY (Registry Pattern)
# =============================================================================


@dataclass
class ToolDef:
    name: str
    description: str
    func: Callable
    risk_level: str = "medium"


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


# =============================================================================
# GOVERNANCE ENGINE (Judge #6)
# =============================================================================


@dataclass
class GovernanceVerdict:
    result: ValidationResult
    explanation: str
    purpose_score: float
    reasons_score: float
    brakes_score: float


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


# =============================================================================
# TOKENOMICS TRACKER
# =============================================================================


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


# =============================================================================
# RESEARCH & ANALYSIS MODULE
# =============================================================================


class ResearchModule:
    def __init__(self):
        self.search_history = []

    def web_search(self, query: str) -> dict:
        """Simulated Web Search Tool"""
        self.search_history.append(query)
        # Mock results
        return {
            "source": "google_search",
            "query": query,
            "results": [
                {"title": f"The State of {query}", "snippet": "Market is growing fast..."},
                {"title": f"Top 10 {query} Strategies", "snippet": "Use AI agents to scale..."},
            ],
        }

    def analyze_market(self, topic: str) -> dict:
        """Simulated Market Analysis"""
        return {"topic": topic, "sentiment": "bullish", "recommendation": "Build and Sell"}

    def competitive_intel(self, competitor: str) -> dict:
        """Simulated Competitive Analysis"""
        return {
            "competitor": competitor,
            "weakness": "Slow legacy tech",
            "opportunity": "Disrupt with keyless AI",
        }


# =============================================================================
# SANDBOX (Code Execution)
# =============================================================================


class CodeSandbox:
    def __init__(self):
        self.local_scope = {}

    def execute(self, code: str) -> dict:
        """Execute python code safely(ish)"""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        try:
            with redirect_stdout(f):
                exec(code, {"__builtins__": __builtins__}, self.local_scope)
            return {
                "output": f.getvalue(),
                "error": None,
                "results": self.local_scope.get("results", {}),
            }
        except Exception as e:
            return {"output": f.getvalue(), "error": str(e), "results": {}}


# =============================================================================
# n-autoresearch/Kosmos/BioAgents MANAGER (MAIN AGENT)
# =============================================================================


class n-autoresearch/Kosmos/BioAgentsV8Full:
    def __init__(self):
        self.registry = ToolRegistry()
        self.judge = JudgeSixGovernance()
        self.tokens = TokenLedger()
        self.research = ResearchModule()
        self.sandbox = CodeSandbox()

        # Configure LLM Client (Mock or Real)
        # Assuming Anthropic or Gemini client here
        self.client = None
        self.chk_api_key()

        self._register_tools()

    def chk_api_key(self):
        if "ANTHROPIC_API_KEY" in os.environ:
            # from anthropic import Anthropic
            # self.client = Anthropic()
            self.model = "claude-3-5-sonnet-20240620"
        elif "GEMINI_API_KEY" in os.environ:
            # import google.generativeai as genai
            # genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            self.model = "gemini-1.5-pro"
        else:
            print("⚠️ No API Key found. Running in MOCK mode.")

    def _register_tools(self):
        # Research tools
        self.registry.register(
            ToolDef("web_search", "Search the web", self.research.web_search, "research")
        )
        self.registry.register(
            ToolDef("market_analysis", "Analyze market", self.research.analyze_market, "research")
        )
        self.registry.register(
            ToolDef(
                "competitive_intel",
                "Get competitor intel",
                self.research.competitive_intel,
                "research",
            )
        )

        # Math tools
        self.registry.register(
            ToolDef(
                "calculator",
                "Calculate expression",
                lambda expr: eval(expr, {"__builtins__": {}}, {"math": __import__("math")}),
                "math",
            )
        )
        self.registry.register(
            ToolDef(
                "fibonacci",
                "Fibonacci number",
                lambda n: (lambda f: f(f, n))(
                    lambda s, x: x if x <= 1 else s(s, x - 1) + s(s, x - 2)
                ),
                "math",
            )
        )

    def _call_llm(self, prompt: str, system: str = None) -> tuple[str, dict]:
        """Call LLM with token tracking"""
        if not self.client:
            return '{"mock": true, "recommendation": "Mock response", "score": 75}', {
                "input": 100,
                "output": 50,
            }

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system or "You are an autonomous research agent. Mission: MAKE CASH",
            messages=[{"role": "user", "content": prompt}],
        )

        self.tokens.add(response.usage.input_tokens, response.usage.output_tokens)
        return response.content[0].text, {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        }

    def execute_with_governance(self, action: str, args: dict, context: str = "") -> dict:
        """Execute action with Judge #6 governance"""
        validation = self.judge.validate(action, args, context)

        if validation.result != ValidationResult.APPROVED:
            return {"status": "blocked", "validation": validation, "result": None}

        # Execute the action
        result = self.registry.execute(action, **args)
        return {"status": "executed", "validation": validation, "result": result}

    def research_task(self, query: str) -> dict:
        """Execute a research task with governance"""
        # Validate
        validation = self.judge.validate("research", {"query": query}, query)

        if validation.result != ValidationResult.APPROVED:
            return {"status": "blocked", "reason": validation.explanation}

        # Execute research
        search_result = self.research.web_search(query)
        market_result = self.research.analyze_market(query)

        return {
            "status": "complete",
            "query": query,
            "search": search_result,
            "market": market_result,
            "governance": {
                "approved": True,
                "scores": {
                    "purpose": validation.purpose_score,
                    "reasons": validation.reasons_score,
                    "brakes": validation.brakes_score,
                },
            },
        }

    def hunt(self, target: str, strategies: int = 5) -> dict:
        """Hunt mode with governance"""
        print(f"\n🎯 HUNT MODE: {target}")
        print(f"📊 {self.tokens.display()}")
        print("=" * 60)

        tasks = [
            ("direct_approach", {"target": target}),
            ("research", {"query": f"market opportunity {target}"}),
            ("competitive_intel", {"competitor": "market leader"}),
            ("market_analysis", {"topic": target}),
            ("quick_wins", {"goal": target}),
        ][:strategies]

        results = []
        for action, args in tasks:
            validation = self.judge.validate(action, args, target)
            status = "✅" if validation.result == ValidationResult.APPROVED else "❌"
            print(f"  {status} {action}: {validation.explanation[:50]}...")

            if validation.result == ValidationResult.APPROVED:
                if action in ["research", "market_analysis", "competitive_intel"]:
                    result = self.registry.execute(
                        action.replace("_", " ").split()[0] + "_" + action.split("_")[-1]
                        if "_" in action
                        else action,
                        **args,
                    )
                else:
                    result = {"simulated": True, "action": action}
                results.append({"action": action, "result": result, "approved": True})
            else:
                results.append(
                    {"action": action, "blocked": True, "reason": validation.explanation}
                )

        print("=" * 60)
        governance_status = self.judge.get_status()
        print(
            f"⚖️  Governance: {governance_status['approved']}/{governance_status['total_validations']} approved ({governance_status['approval_rate']:.0f}%)"
        )
        print(f"📊 {self.tokens.display()}")

        return {
            "target": target,
            "results": results,
            "governance": governance_status,
            "tokens": self.tokens.display(),
        }

    def execute_code(self, code: str) -> dict:
        """Execute code in sandbox with governance"""
        validation = self.judge.validate(
            "code_execution", {"code": code[:100]}, "programmatic tool calling"
        )

        if validation.result != ValidationResult.APPROVED:
            return {"status": "blocked", "reason": validation.explanation}

        return self.sandbox.execute(code)

    def status(self) -> dict:
        """Get full status"""
        return {
            "tokens": self.tokens.display(),
            "governance": self.judge.get_status(),
            "tools": self.registry.list_tools(),
            "research_history": len(self.research.search_history),
        }


# =============================================================================
# SELF-EXECUTION FOR CLAUDE CODE
# =============================================================================


def run_in_claude_code():
    """
    Self-executing demo for Claude Code.
    This runs the full n-autoresearch/Kosmos/BioAgents v8 stack.
    """
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         🐵 FLYING n-autoresearch/Kosmos/BioAgents v8 FULL 🐵                      ║
    ║     Research · Governance · Advanced Tool Use             ║
    ║              Running in Claude Code                       ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    fm = n-autoresearch/Kosmos/BioAgentsV8Full()

    # Demo 1: Research with Governance
    print("\n" + "=" * 60)
    print("📚 DEMO 1: Research Task with Governance")
    print("=" * 60)
    result = fm.research_task("AI agent monetization strategies")
    print(f"Status: {result['status']}")
    print(f"Market Analysis: {result.get('market', {}).get('recommendation', 'N/A')}")
    print(f"Governance: {result.get('governance', {})}")

    # Demo 2: Hunt Mode
    print("\n" + "=" * 60)
    print("🎯 DEMO 2: Hunt Mode")
    print("=" * 60)
    hunt_result = fm.hunt("$50k MRR in 30 days", strategies=4)

    # Demo 3: Code Execution
    print("\n" + "=" * 60)
    print("🧪 DEMO 3: Programmatic Tool Calling")
    print("=" * 60)
    code = """
# Research and analyze
search = call_tool("web_search", query="AI SaaS pricing models")
market = call_tool("market_analysis", topic="AI agents")

results["search_count"] = len(search.get("results", []))
results["market_opportunity"] = market.get("recommendation", "Unknown")
results["total_findings"] = 2

print(f"Found {results['search_count']} search results")
print(f"Market: {results['market_opportunity']}")
"""
    code_result = fm.execute_code(code)
    print(f"Output: {code_result.get('output', '')}")
    print(f"Results: {code_result.get('results', {})}")
    if code_result.get("error"):
        print(f"Error: {code_result['error']}")

    # Final Status
    print("\n" + "=" * 60)
    print("📊 FINAL STATUS")
    print("=" * 60)
    status = fm.status()
    print(f"Tokens: {status['tokens']}")
    print(f"Governance: {status['governance']}")
    print(f"Tools Available: {status['tools']}")

    return fm


if __name__ == "__main__":
    run_in_claude_code()
