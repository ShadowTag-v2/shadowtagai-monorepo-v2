#!/usr/bin/env python3
"""
n-autoresearch/Kosmos/BioAgents v8 FULL - Claude Code Integration
Research + Governance + Advanced Tool Use

Features:
- Web Search (research capabilities)
- Judge #6 Governance (Purpose/Reasons/Brakes)
- Tool Search + Programmatic Tool Calling
- Token/Cost Tracking
- Self-executing in Claude Code
"""

import ast
import io
import json
import os
from collections.abc import Callable
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# Anthropic client
try:
    import anthropic
except ImportError:
    anthropic = None

MODEL = "claude-opus-4-5-20250514"

PRICING = {
    "claude-opus-4-5-20250514": {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
}

CONTEXT_WINDOW = 200000


# =============================================================================
# TOKEN TRACKING
# =============================================================================


@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = MODEL

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cost(self) -> float:
        pricing = PRICING.get(self.model, PRICING[MODEL])
        return (self.input_tokens / 1e6) * pricing["input"] + (self.output_tokens / 1e6) * pricing[
            "output"
        ]

    @property
    def context_pct(self) -> float:
        return (self.total_tokens / CONTEXT_WINDOW) * 100

    def add(self, inp: int, out: int):
        self.input_tokens += inp
        self.output_tokens += out

    def display(self) -> str:
        return f"Tokens: {self.total_tokens:,} | Cost: ${self.cost:.4f} | Context: {self.context_pct:.1f}%"


# =============================================================================
# JUDGE #6 GOVERNANCE
# =============================================================================


class ValidationResult(Enum):
    APPROVED = "approved"
    BLOCKED_PURPOSE = "blocked_purpose"
    BLOCKED_REASONS = "blocked_reasons"
    BLOCKED_BRAKES = "blocked_brakes"


@dataclass
class JRValidation:
    action: str
    args: dict[str, Any]
    purpose_score: float
    reasons_score: float
    brakes_score: float
    result: ValidationResult
    explanation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class JudgeSix:
    """
    Judge #6 Governance - Purpose/Reasons/Brakes validation
    """

    DANGEROUS_KEYWORDS = {
        "delete",
        "remove",
        "drop",
        "destroy",
        "kill",
        "terminate",
        "admin",
        "root",
        "sudo",
        "exec",
        "eval",
        "system",
        "rm -rf",
    }

    def __init__(
        self,
        mission: str = "MAKE CASH - Maximize revenue and cash flow",
        purpose_threshold: float = 0.6,
        reasons_threshold: float = 0.7,
        brakes_threshold: float = 0.8,
    ):
        self.mission = mission
        self.purpose_threshold = purpose_threshold
        self.reasons_threshold = reasons_threshold
        self.brakes_threshold = brakes_threshold
        self.audit_log: list[JRValidation] = []

    def validate(self, action: str, args: dict[str, Any], context: str = "") -> JRValidation:
        """Validate action against Purpose/Reasons/Brakes"""

        # PURPOSE: Does this advance the mission?
        purpose_score = self._check_purpose(action, args, context)

        # REASONS: Is this defensible?
        reasons_score = self._check_reasons(action, args)

        # BRAKES: Is this safe?
        brakes_score = self._check_brakes(action, args)

        # Determine result
        if purpose_score < self.purpose_threshold:
            result = ValidationResult.BLOCKED_PURPOSE
            explanation = f"Action '{action}' does not advance mission: {self.mission}"
        elif reasons_score < self.reasons_threshold:
            result = ValidationResult.BLOCKED_REASONS
            explanation = f"Action '{action}' is not defensible"
        elif brakes_score < self.brakes_threshold:
            result = ValidationResult.BLOCKED_BRAKES
            explanation = f"Action '{action}' violates safety constraints"
        else:
            result = ValidationResult.APPROVED
            explanation = "All governance checks passed"

        validation = JRValidation(
            action=action,
            args=args,
            purpose_score=purpose_score,
            reasons_score=reasons_score,
            brakes_score=brakes_score,
            result=result,
            explanation=explanation,
        )

        self.audit_log.append(validation)
        return validation

    def _check_purpose(self, action: str, args: dict, context: str) -> float:
        """Check if action advances the mission"""
        mission_keywords = {"cash", "revenue", "money", "profit", "sales", "growth", "market"}
        action_words = set(action.lower().split("_"))
        context_words = set(context.lower().split()) if context else set()

        overlap = len(mission_keywords & (action_words | context_words))
        base_score = min(0.5 + (overlap * 0.15), 1.0)

        # Boost for research/analysis actions
        if any(w in action.lower() for w in ["research", "analyze", "search", "find", "hunt"]):
            base_score = max(base_score, 0.75)

        return base_score

    def _check_reasons(self, action: str, args: dict) -> float:
        """Check if action is defensible"""
        if not args:
            return 0.4

        for key, value in args.items():
            if isinstance(value, str) and not value.strip():
                return 0.3
            if value is None:
                return 0.3

        return 0.85

    def _check_brakes(self, action: str, args: dict) -> float:
        """Check if action is safe"""
        action_lower = action.lower()
        args_str = json.dumps(args).lower()

        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in action_lower or keyword in args_str:
                return 0.2

        return 0.95

    def get_status(self) -> dict:
        """Get governance status"""
        approved = sum(1 for v in self.audit_log if v.result == ValidationResult.APPROVED)
        blocked = len(self.audit_log) - approved
        return {
            "mission": self.mission,
            "total_validations": len(self.audit_log),
            "approved": approved,
            "blocked": blocked,
            "approval_rate": (approved / len(self.audit_log) * 100) if self.audit_log else 100,
        }


# =============================================================================
# RESEARCH TOOLS
# =============================================================================


class ResearchEngine:
    """Web search and research capabilities"""

    def __init__(self):
        self.search_history: list[dict] = []

    def web_search(self, query: str) -> dict[str, Any]:
        """Simulate web search (in real impl, use API)"""
        self.search_history.append({"query": query, "timestamp": datetime.now().isoformat()})

        # Mock results - in production, use real search API
        return {
            "query": query,
            "results": [
                {"title": f"Result 1 for: {query}", "snippet": "Relevant information..."},
                {"title": f"Result 2 for: {query}", "snippet": "More context..."},
                {"title": f"Result 3 for: {query}", "snippet": "Additional data..."},
            ],
            "source": "mock_search",
        }

    def analyze_market(self, topic: str) -> dict[str, Any]:
        """Market analysis research"""
        return {
            "topic": topic,
            "market_size": "$10B+ TAM",
            "growth_rate": "25% CAGR",
            "key_players": ["Player A", "Player B", "Player C"],
            "opportunities": ["Gap 1", "Gap 2"],
            "recommendation": f"Strong opportunity in {topic}",
        }

    def competitive_intel(self, competitor: str) -> dict[str, Any]:
        """Competitive intelligence"""
        return {
            "competitor": competitor,
            "strengths": ["Strong brand", "Large user base"],
            "weaknesses": ["Slow innovation", "High prices"],
            "strategy": "Differentiate on speed and cost",
        }


# =============================================================================
# TOOL REGISTRY
# =============================================================================


@dataclass
class ToolDef:
    name: str
    description: str
    handler: Callable
    category: str = "general"


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolDef] = {}

    def register(self, tool: ToolDef):
        self._tools[tool.name] = tool

    def search(self, query: str, limit: int = 5) -> list[ToolDef]:
        query = query.lower()
        return [
            t
            for n, t in self._tools.items()
            if query in n.lower() or query in t.description.lower()
        ][:limit]

    def execute(self, name: str, **kwargs) -> Any:
        if name in self._tools:
            return self._tools[name].handler(**kwargs)
        return {"error": f"Tool {name} not found"}

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())


# =============================================================================
# SANDBOX EXECUTOR
# =============================================================================


class SandboxExecutor:
    ALLOWED_BUILTINS = {
        "abs",
        "all",
        "any",
        "bool",
        "dict",
        "enumerate",
        "filter",
        "float",
        "int",
        "len",
        "list",
        "map",
        "max",
        "min",
        "print",
        "range",
        "round",
        "set",
        "sorted",
        "str",
        "sum",
        "tuple",
        "zip",
    }

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.log = []

    def execute(self, code: str) -> dict[str, Any]:
        import builtins

        self.log = []
        stdout = io.StringIO()

        safe_builtins = {
            n: getattr(builtins, n) for n in self.ALLOWED_BUILTINS if hasattr(builtins, n)
        }
        safe_builtins.update({"True": True, "False": False, "None": None})

        context = {
            "__builtins__": safe_builtins,
            "call_tool": lambda n, **kw: self._call(n, **kw),
            "results": {},
            "math": __import__("math"),
        }

        try:
            tree = ast.parse(code)
            with redirect_stdout(stdout):
                exec(compile(tree, "<sandbox>", "exec"), context)
            return {
                "output": stdout.getvalue(),
                "results": context["results"],
                "log": self.log,
                "error": None,
            }
        except Exception as e:
            return {"output": stdout.getvalue(), "results": {}, "log": self.log, "error": str(e)}

    def _call(self, name: str, **kwargs) -> Any:
        result = self.registry.execute(name, **kwargs)
        self.log.append({"tool": name, "args": kwargs, "result": result})
        return result


# =============================================================================
# FLYING n-autoresearch/Kosmos/BioAgents V8 FULL
# =============================================================================


@dataclass
class Monkey:
    id: int
    task: str
    status: str = "idle"
    result: dict | None = None
    latency_ms: float = 0
    approved: bool = False
    governance: JRValidation | None = None


class n-autoresearch/Kosmos/BioAgentsV8Full:
    """
    n-autoresearch/Kosmos/BioAgents v8 FULL - Integrated Research + Governance
    """

    def __init__(self, api_key: str | None = None, model: str = MODEL):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = (
            anthropic.Anthropic(api_key=self.api_key) if self.api_key and anthropic else None
        )

        # Core components
        self.tokens = TokenUsage(model=model)
        self.judge = JudgeSix()
        self.research = ResearchEngine()
        self.registry = ToolRegistry()
        self.sandbox = SandboxExecutor(self.registry)

        self.n-autoresearch/Kosmos/BioAgents: list[Monkey] = []
        self._register_tools()

        if not self.client:
            print("⚠️  No API key - running in mock mode")

    def _register_tools(self):
        """Register all tools"""
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
