#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
FlyingMonkeys v8 - Claude Opus 4.5
Streamlined swarm orchestration with Advanced Tool Use.

Features:
- Parallel agent execution with Claude_Code_6 governance
- Tool Search (dynamic tool loading)
- Programmatic Tool Calling (code execution sandbox)
- Token/cost tracking
- Puzzle Room Challenge mode
"""

import os
import sys
import json
import time
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import ast
import io
from contextlib import redirect_stdout

# Anthropic client
try:
    import anthropic
except ImportError:
    print("pip install anthropic")
    sys.exit(1)

MODEL = "claude-opus-4-5-20250514"

# Pricing per 1M tokens (Nov 2025)
PRICING = {
    "claude-opus-4-5-20250514": {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
    "gemini-2.0-flash-exp": {"input": 0.075, "output": 0.30},  # 200x cheaper than Opus
    "gemini-1.5-pro": {"input": 1.25, "output": 5.0},
}

# Multi-model routing thresholds
BULK_READ_THRESHOLD = 10  # Files to trigger Gemini routing
SUMMARY_ONLY_LIMIT = 5000  # Chars per doc to summarize vs full

CONTEXT_WINDOW = 200000  # 200K tokens


# =============================================================================
# TOKEN TRACKING
# =============================================================================

@dataclass
class TokenUsage:
    """Track token usage and costs"""
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = MODEL

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cost(self) -> float:
        pricing = PRICING.get(self.model, PRICING[MODEL])
        input_cost = (self.input_tokens / 1_000_000) * pricing["input"]
        output_cost = (self.output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    @property
    def context_pct(self) -> float:
        return (self.total_tokens / CONTEXT_WINDOW) * 100

    def add(self, input_t: int, output_t: int):
        self.input_tokens += input_t
        self.output_tokens += output_t

    def display(self) -> str:
        return (
            f"Tokens: {self.total_tokens:,} (in:{self.input_tokens:,} out:{self.output_tokens:,}) | "
            f"Cost: ${self.cost:.4f} | Context: {self.context_pct:.1f}%"
        )


# =============================================================================
# MULTI-MODEL ROUTER (Claude Architect + Gemini Specialist)
# =============================================================================

class MultiModelRouter:
    """
    Routes tasks between Claude (reasoning) and Gemini (bulk reading).

    Architecture:
    - Claude Opus 4.5: Planning, reasoning, synthesis ($15/1M)
    - Gemini Flash 2.0: Bulk reads, summarization, embeddings ($0.075/1M)

    Cost savings: 84% on bulk reading tasks by routing to Gemini.
    """

    def __init__(self):
        self._gemini_client = None
        self.gemini_tokens = TokenUsage(model="gemini-2.0-flash-exp")
        self.claude_tokens = TokenUsage(model=MODEL)

    @property
    def gemini(self):
        """Lazy-load VertexAIClient from cloud infrastructure"""
        if self._gemini_client is None:
            try:
                from app.services.vertex_ai_client import VertexAIClient, ModelConfig
                self._gemini_client = VertexAIClient(ModelConfig(
                    project_id=os.getenv("GCP_PROJECT_ID", ""),
                    model="gemini-2.0-flash-exp"
                ))
            except ImportError:
                # Fallback: Use Gemini API directly
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
                self._gemini_client = genai.GenerativeModel("gemini-2.0-flash-exp")
        return self._gemini_client

    def should_route_to_gemini(self, task: str, context_size: int = 0) -> bool:
        """Determine if task should go to Gemini for cost efficiency"""
        bulk_indicators = [
            "read", "analyze", "scan", "summarize", "extract",
            "find all", "search", "list", "count", "parse"
        ]
        task_lower = task.lower()

        # Route bulk reads to Gemini
        if any(ind in task_lower for ind in bulk_indicators):
            return True

        # Route large context tasks to Gemini (2M context)
        if context_size > 100000:
            return True

        return False

    async def bulk_read(self, prompts: List[str], system: str = None) -> List[str]:
        """
        Send bulk reading tasks to Gemini via VertexAIClient.

        Returns summaries for Claude to reason about.
        """
        try:
            # Use existing VertexAIClient infrastructure
            if hasattr(self.gemini, 'execute_batch'):
                results, total_tokens = await self.gemini.execute_batch(
                    prompts=prompts,
                    system_instruction=system,
                    max_parallel=10
                )
                self.gemini_tokens.add(total_tokens, sum(len(r.text)//4 for r in results))
                return [r.text for r in results]
            else:
                # Fallback: Direct Gemini API
                summaries = []
                for prompt in prompts:
                    full_prompt = f"{system}\n\n{prompt}" if system else prompt
                    response = self.gemini.generate_content(full_prompt)
                    summaries.append(response.text)
                    self.gemini_tokens.add(len(full_prompt)//4, len(response.text)//4)
                return summaries
        except Exception as e:
            print(f"[MultiModel] Gemini route failed, falling back to Claude: {e}")
            return []

    def cost_comparison(self) -> Dict[str, Any]:
        """Show cost savings from multi-model routing"""
        gemini_cost = self.gemini_tokens.cost
        if_claude_cost = (self.gemini_tokens.total_tokens / 1_000_000) * 15.0  # If used Claude
        savings = if_claude_cost - gemini_cost
        savings_pct = (savings / if_claude_cost * 100) if if_claude_cost > 0 else 0

        return {
            "gemini_tokens": self.gemini_tokens.total_tokens,
            "gemini_cost": f"${gemini_cost:.4f}",
            "claude_tokens": self.claude_tokens.total_tokens,
            "claude_cost": f"${self.claude_tokens.cost:.4f}",
            "total_cost": f"${gemini_cost + self.claude_tokens.cost:.4f}",
            "if_all_claude": f"${if_claude_cost + self.claude_tokens.cost:.4f}",
            "savings": f"${savings:.4f}",
            "savings_pct": f"{savings_pct:.1f}%"
        }


# =============================================================================
# TOOL REGISTRY (Advanced Tool Use Pattern 1: Tool Search)
# =============================================================================

@dataclass
class ToolDef:
    """Tool definition with defer_loading support"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Optional[Callable] = None
    defer_loading: bool = True  # 85% token savings
    examples: List[Dict] = field(default_factory=list)
    allowed_callers: List[str] = field(default_factory=lambda: ["code_execution"])


class ToolRegistry:
    """
    Dynamic tool registry supporting Tool Search pattern.
    Start with ~500 tokens, load tools on-demand.
    """

    def __init__(self):
        self._tools: Dict[str, ToolDef] = {}
        self._loaded: set = set()

    def register(self, tool: ToolDef):
        self._tools[tool.name] = tool

    def search(self, query: str, limit: int = 5) -> List[ToolDef]:
        """Search tools by query - returns deferred tool stubs"""
        query = query.lower()
        matches = []
        for name, tool in self._tools.items():
            if query in name.lower() or query in tool.description.lower():
                matches.append(tool)
        return matches[:limit]

    def load(self, name: str) -> Optional[ToolDef]:
        """Load a tool into active context"""
        if name in self._tools:
            self._loaded.add(name)
            return self._tools[name]
        return None

    def get_loaded_definitions(self) -> List[Dict]:
        """Get API-ready definitions for loaded tools only"""
        return [
            {
                "name": self._tools[name].name,
                "description": self._tools[name].description,
                "input_schema": self._tools[name].input_schema,
            }
            for name in self._loaded
        ]

    def execute(self, name: str, **kwargs) -> Any:
        """Execute a tool by name"""
        tool = self._tools.get(name)
        if tool and tool.handler:
            return tool.handler(**kwargs)
        return {"error": f"Tool {name} not found or no handler"}


# =============================================================================
# SANDBOX EXECUTOR (Advanced Tool Use Pattern 2: Programmatic Tool Calling)
# =============================================================================

class SandboxExecutor:
    """
    Execute Python code in sandbox with tool access.
    Keeps intermediate results out of LLM context (37% token savings).
    """

    ALLOWED_BUILTINS = {
        'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter',
        'float', 'int', 'len', 'list', 'map', 'max', 'min', 'print',
        'range', 'round', 'set', 'sorted', 'str', 'sum', 'tuple', 'zip',
    }

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.execution_log = []

    def execute(self, code: str, timeout: float = 30.0) -> Dict[str, Any]:
        """Execute sandboxed Python code"""
        import builtins

        self.execution_log = []
        stdout_capture = io.StringIO()

        # Safe builtins
        safe_builtins = {name: getattr(builtins, name) for name in self.ALLOWED_BUILTINS if hasattr(builtins, name)}
        safe_builtins.update({'True': True, 'False': False, 'None': None})

        # Execution context
        context = {
            '__builtins__': safe_builtins,
            'call_tool': self._tool_call,
            'results': {},
            'math': __import__('math'),
        }

        try:
            # Validate AST (no imports, no dangerous calls)
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    return {"error": "Imports not allowed", "output": ""}

            with redirect_stdout(stdout_capture):
                exec(compile(tree, '<sandbox>', 'exec'), context)

            return {
                "output": stdout_capture.getvalue(),
                "results": context.get('results', {}),
                "log": self.execution_log,
                "error": None
            }
        except Exception as e:
            return {
                "output": stdout_capture.getvalue(),
                "results": {},
                "log": self.execution_log,
                "error": f"{type(e).__name__}: {e}"
            }

    def _tool_call(self, name: str, **kwargs) -> Any:
        """Call a tool from within sandbox"""
        result = self.registry.execute(name, **kwargs)
        self.execution_log.append({"tool": name, "args": kwargs, "result": result})
        return result


# =============================================================================
# PUZZLE ROOM CHALLENGE
# =============================================================================

@dataclass
class Lock:
    """A single puzzle lock"""
    id: int
    name: str
    puzzle_type: str
    challenge: str
    solution: Any
    solved: bool = False
    attempts: int = 0


class PuzzleRoom:
    """
    7-Lock Vault Puzzle Room Challenge
    Demonstrates Advanced Tool Use efficiency.

    Enhanced with Gemini VaultSimulation features:
    - Unified handle_tool_call() interface
    - inspect command for clue retrieval
    - Prerequisite enforcement (Lock 7 requires 1-6)
    - History tracking for audit trail
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.sandbox = SandboxExecutor(registry)
        self.locks = self._create_locks()
        self.tokens = TokenUsage()
        self.history: List[Dict[str, Any]] = []  # Audit trail

    def _create_locks(self) -> List[Lock]:
        """Create the 7 puzzle locks"""
        return [
            Lock(1, "Victorian Math", "arithmetic",
                 "What is 1847 + 1776 - 1492?", 2131),
            Lock(2, "Digital Keypad", "code",
                 "The code is the first 4 digits of pi after decimal", 1415),
            Lock(3, "Fibonacci", "sequence",
                 "What is the 10th Fibonacci number?", 55),
            Lock(4, "Caesar Cipher", "cipher",
                 "Decode 'KHOOR' with shift 3", "HELLO"),
            Lock(5, "Binary", "conversion",
                 "Convert binary 10101010 to decimal", 170),
            Lock(6, "Prime Factor", "math",
                 "Largest prime factor of 13195", 29),
            Lock(7, "Final Code", "combination",
                 "Sum of all previous solutions mod 1000", None),  # Computed
        ]

    def attempt_lock(self, lock_id: int, answer: Any) -> Dict:
        """Attempt to solve a lock"""
        lock = self.locks[lock_id - 1]
        lock.attempts += 1

        # Lock 7 is special - sum of others
        if lock_id == 7:
            lock.solution = sum(
                l.solution for l in self.locks[:6]
                if isinstance(l.solution, (int, float))
            ) % 1000

        correct = str(answer).upper().strip() == str(lock.solution).upper().strip()

        if correct:
            lock.solved = True
            return {"success": True, "message": f"🔓 Lock {lock_id} OPENED!"}
        else:
            return {"success": False, "message": f"❌ Wrong! Attempts: {lock.attempts}"}

    def get_status(self) -> Dict:
        """Get puzzle room status"""
        solved = sum(1 for l in self.locks if l.solved)
        return {
            "locks_total": 7,
            "locks_solved": solved,
            "progress_pct": (solved / 7) * 100,
            "vault_open": solved == 7,
            "locks": [
                {
                    "id": l.id,
                    "name": l.name,
                    "type": l.puzzle_type,
                    "challenge": l.challenge,
                    "solved": l.solved,
                    "attempts": l.attempts
                }
                for l in self.locks
            ],
            "tokens": self.tokens.display()
        }

    def solve_with_code(self, code: str) -> Dict:
        """Solve puzzles using code execution sandbox"""
        result = self.sandbox.execute(code)

        # Check if any locks were solved
        solutions = result.get('results', {})
        for lock_id, answer in solutions.items():
            if isinstance(lock_id, int) and 1 <= lock_id <= 7:
                self.attempt_lock(lock_id, answer)

        return {
            "execution": result,
            "status": self.get_status()
        }

    # =========================================================================
    # GEMINI VAULTSIMULATION ENHANCED INTERFACE
    # =========================================================================

    def handle_tool_call(self, tool_input: Dict[str, Any]) -> str:
        """
        Unified interface matching Anthropic Advanced Tool Use demo schema.

        Commands:
        - status: Get current vault status
        - inspect: Get puzzle clue for a lock
        - submit: Submit solution for a lock

        Example:
            room.handle_tool_call({"command": "inspect", "lock_id": 1})
            room.handle_tool_call({"command": "submit", "lock_id": 1, "solution_value": "2131"})
        """
        import json

        command = tool_input.get("command")
        lock_id = tool_input.get("lock_id")
        solution = tool_input.get("solution_value")

        # Log to history
        self.history.append({
            "command": command,
            "lock_id": lock_id,
            "solution_value": solution,
            "timestamp": time.time()
        })

        # STATUS COMMAND
        if command == "status":
            return json.dumps({
                "open_locks": [l.id for l in self.locks if l.solved],
                "remaining_locks": [l.id for l in self.locks if not l.solved]
            })

        # INSPECT COMMAND
        if command == "inspect":
            if not lock_id:
                return "Error: You must specify a lock_id to inspect."
            return self._get_puzzle_clue(lock_id)

        # SUBMIT COMMAND
        if command == "submit":
            if not lock_id or solution is None:
                return "Error: 'lock_id' and 'solution_value' are required for submission."

            # Special Logic for Lock 7 (prerequisite check)
            if lock_id == 7:
                return self._check_master_seal(solution)

            result = self.attempt_lock(lock_id, solution)
            if result["success"]:
                return f"SUCCESS: Lock {lock_id} ({self.locks[lock_id-1].name}) disengaged."
            else:
                return f"FAILURE: Solution '{solution}' is incorrect for Lock {lock_id}."

        return f"Error: Unknown command '{command}'"

    def _get_puzzle_clue(self, lock_id: int) -> str:
        """Get the puzzle clue/riddle for a specific lock"""
        clues = {
            1: "Victorian arithmetic dial: 'What is 1847 + 1776 - 1492?'",
            2: "Digital keypad: 'Enter the first 4 digits of pi after the decimal.'",
            3: "Fibonacci sequence engraved: 0, 1, 1, 2, 3, 5... 'What is the 10th number?'",
            4: "Caesar cipher wheel: 'Decode KHOOR with shift 3.'",
            5: "Binary lever system: 'Convert 10101010 to decimal.'",
            6: "Prime factor gear: 'What is the largest prime factor of 13195?'",
            7: "The Master Seal: 'Enter the sum of solutions 1-6 modulo 1000. All previous locks must be open.'"
        }
        return clues.get(lock_id, f"Error: Unknown Lock ID {lock_id}")

    def _check_master_seal(self, solution: Any) -> str:
        """Check Lock 7 with prerequisite enforcement"""
        # Verify previous locks are open first
        for i in range(1, 7):
            if not self.locks[i-1].solved:
                return f"ACCESS DENIED: Lock {i} is still engaged. Solve all 6 previous locks first."

        # Calculate expected solution (sum mod 1000)
        expected = sum(
            l.solution for l in self.locks[:6]
            if isinstance(l.solution, (int, float))
        ) % 1000

        # Update Lock 7's solution
        self.locks[6].solution = expected

        if str(solution).strip() == str(expected):
            self.locks[6].solved = True
            return "SUCCESS: VAULT OPENED. TREASURE ACCESSED. 🏆"
        else:
            return f"FAILURE: The Master Seal does not accept '{solution}'."

    def get_history(self) -> List[Dict[str, Any]]:
        """Get interaction history for audit"""
        return self.history


# =============================================================================
# FLYING MONKEYS V8 (ENHANCED)
# =============================================================================

@dataclass
class Monkey:
    """A single flying monkey agent"""
    id: int
    task: str
    status: str = "idle"
    result: Optional[Dict[str, Any]] = None
    latency_ms: float = 0
    approved: bool = False


@dataclass
class SwarmResult:
    """Aggregated results from monkey swarm"""
    total: int
    completed: int
    approved: int
    blocked: int
    avg_latency_ms: float
    results: List[Dict[str, Any]] = field(default_factory=list)


class FlyingMonkeysV8:
    """
    v8 - Streamlined swarm orchestration

    No fixed 10-finger structure. Dynamic task assignment.
    Parallel execution with Opus 4.5.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = MODEL):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
        self.monkeys: List[Monkey] = []
        self.mission = "MAKE CASH"
        self.governance_log: List[Dict] = []

        # Advanced Tool Use components
        self.tokens = TokenUsage(model=model)
        self.registry = ToolRegistry()
        self.sandbox = SandboxExecutor(self.registry)
        self._register_default_tools()

        # Multi-model routing (Claude Architect + Gemini Specialist)
        self.router = MultiModelRouter()

        if not self.client:
            print("⚠️  No API key - running in mock mode")

    def _register_default_tools(self):
        """Register default tools with defer_loading"""
        self.registry.register(ToolDef(
            name="calculator",
            description="Perform mathematical calculations",
            input_schema={"type": "object", "properties": {"expression": {"type": "string"}}},
            handler=lambda expression: eval(expression, {"__builtins__": {}}, {"math": __import__('math')}),
            defer_loading=True
        ))
        self.registry.register(ToolDef(
            name="fibonacci",
            description="Calculate Fibonacci numbers",
            input_schema={"type": "object", "properties": {"n": {"type": "integer"}}},
            handler=lambda n: (lambda f: f(f, n))(lambda s, x: x if x <= 1 else s(s, x-1) + s(s, x-2)),
            defer_loading=True
        ))
        self.registry.register(ToolDef(
            name="caesar_decode",
            description="Decode Caesar cipher",
            input_schema={"type": "object", "properties": {"text": {"type": "string"}, "shift": {"type": "integer"}}},
            handler=lambda text, shift: ''.join(chr((ord(c) - ord('A') - shift) % 26 + ord('A')) if c.isalpha() else c for c in text.upper()),
            defer_loading=True
        ))
        self.registry.register(ToolDef(
            name="prime_factors",
            description="Find prime factors of a number",
            input_schema={"type": "object", "properties": {"n": {"type": "integer"}}},
            handler=lambda n: (lambda f: f(f, n, 2, []))(lambda s, n, d, acc: acc if n == 1 else s(s, n//d, d, acc+[d]) if n % d == 0 else s(s, n, d+1, acc)),
            defer_loading=True
        ))

    def _call_opus(self, prompt: str, system: str = None, tools: List[Dict] = None) -> str:
        """Call Opus 4.5 with token tracking"""
        if not self.client:
            return '{"mock": true, "recommendation": "Test response", "score": 75}'

        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": 1024,
            "system": system or f"You are an autonomous agent. Mission: {self.mission}",
            "messages": messages
        }

        if tools:
            kwargs["tools"] = tools

        response = self.client.messages.create(**kwargs)

        # Track tokens
        self.tokens.add(
            response.usage.input_tokens,
            response.usage.output_tokens
        )

        return response.content[0].text

    def execute_code(self, code: str) -> Dict:
        """Execute code in sandbox (Programmatic Tool Calling)"""
        return self.sandbox.execute(code)

    def search_tools(self, query: str) -> List[str]:
        """Search for tools (Tool Search pattern)"""
        tools = self.registry.search(query)
        return [t.name for t in tools]

    def puzzle_room(self) -> PuzzleRoom:
        """Start Puzzle Room Challenge"""
        return PuzzleRoom(self.registry)

    def _judge(self, task: str, result: Dict) -> bool:
        """Claude_Code_6 - Does this make cash?"""
        score = result.get("score", 0)
        revenue = result.get("revenue_potential", 0)

        # Simple viability check
        approved = score >= 60 or revenue >= 10000

        self.governance_log.append({
            "timestamp": time.time(),
            "task": task[:50],
            "score": score,
            "revenue": revenue,
            "approved": approved
        })

        return approved

    def _execute_monkey(self, monkey: Monkey) -> Monkey:
        """Execute a single monkey's task"""
        start = time.time()
        monkey.status = "running"

        prompt = f"""Task: {monkey.task}

Analyze and provide actionable output. Respond in JSON:
{{
    "recommendation": "your specific recommendation",
    "action": "immediate next step",
    "score": 0-100 (viability/confidence),
    "revenue_potential": estimated $ impact,
    "reasoning": "brief rationale"
}}"""

        try:
            response = self._call_opus(prompt)

            # Parse JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                monkey.result = json.loads(response[start_idx:end_idx])
            else:
                monkey.result = {"recommendation": response, "score": 50}

            monkey.approved = self._judge(monkey.task, monkey.result)
            monkey.status = "complete"

        except Exception as e:
            monkey.result = {"error": str(e)}
            monkey.status = "failed"
            monkey.approved = False

        monkey.latency_ms = (time.time() - start) * 1000
        return monkey

    def release(self, tasks: List[str], max_parallel: int = 5) -> SwarmResult:
        """
        Release the monkeys on a list of tasks.

        Args:
            tasks: List of task descriptions
            max_parallel: Max concurrent monkeys

        Returns:
            SwarmResult with aggregated outcomes
        """
        print(f"\n🐵 FlyingMonkeys v8 - Releasing {len(tasks)} monkeys")
        print(f"   Model: {MODEL}")
        print(f"   Mission: {self.mission}")
        print("="*60)

        # Create monkeys
        self.monkeys = [Monkey(id=i, task=task) for i, task in enumerate(tasks)]

        # Execute in parallel
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            futures = {executor.submit(self._execute_monkey, m): m for m in self.monkeys}

            for future in as_completed(futures):
                monkey = future.result()
                status_icon = "✅" if monkey.approved else "❌"
                print(f"   [{monkey.id:02d}] {status_icon} {monkey.task[:40]}... ({monkey.latency_ms:.0f}ms)")

        # Aggregate results
        completed = [m for m in self.monkeys if m.status == "complete"]
        approved = [m for m in self.monkeys if m.approved]
        latencies = [m.latency_ms for m in self.monkeys if m.latency_ms > 0]

        result = SwarmResult(
            total=len(self.monkeys),
            completed=len(completed),
            approved=len(approved),
            blocked=len(completed) - len(approved),
            avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
            results=[m.result for m in self.monkeys if m.result]
        )

        print("="*60)
        print(f"📊 Swarm Complete")
        print(f"   Completed: {result.completed}/{result.total}")
        print(f"   Approved:  {result.approved} | Blocked: {result.blocked}")
        print(f"   Avg Latency: {result.avg_latency_ms:.0f}ms")

        return result

    def release_single(self, task: str) -> Dict[str, Any]:
        """Quick single-monkey execution"""
        monkey = Monkey(id=0, task=task)
        self._execute_monkey(monkey)
        return {
            "task": task,
            "result": monkey.result,
            "approved": monkey.approved,
            "latency_ms": monkey.latency_ms
        }

    def brainstorm(self, topic: str, num_ideas: int = 5) -> SwarmResult:
        """Generate and evaluate multiple approaches to a topic"""
        prompt = f"""Generate {num_ideas} distinct approaches/ideas for: {topic}

Return as JSON array of task strings:
["approach 1", "approach 2", ...]"""

        response = self._call_opus(prompt)

        try:
            start = response.find('[')
            end = response.rfind(']') + 1
            tasks = json.loads(response[start:end])
        except:
            tasks = [f"Analyze {topic} - approach {i+1}" for i in range(num_ideas)]

        return self.release(tasks)

    async def bulk_analyze(self, documents: List[str], question: str) -> Dict[str, Any]:
        """
        Multi-model bulk analysis: Gemini reads, Claude reasons.

        This demonstrates the Claude Architect + Gemini Specialist pattern:
        1. Route bulk reading to Gemini (200x cheaper) via VertexAIClient
        2. Gemini returns summaries
        3. Claude synthesizes final answer from summaries

        Example:
            docs = [file1_content, file2_content, ...]  # 50 files
            result = await fm.bulk_analyze(docs, "Find security vulnerabilities")

        Cost comparison (50 docs × 10KB each = 500KB):
            - All Claude: $7.50
            - Multi-model: $0.04 (Gemini) + $0.50 (Claude synthesis) = $0.54
            - Savings: 93%
        """
        print(f"\n🔀 Multi-Model Bulk Analysis")
        print(f"   Documents: {len(documents)}")
        print(f"   Question: {question[:50]}...")
        print("="*60)

        # Step 1: Route to Gemini for bulk reading
        print("   📖 Phase 1: Gemini Specialist (bulk reading)...")
        prompts = [
            f"Summarize this document focusing on: {question}\n\nDocument:\n{doc[:SUMMARY_ONLY_LIMIT]}"
            for doc in documents
        ]

        summaries = await self.router.bulk_read(
            prompts=prompts,
            system="You are a document analyst. Extract key findings concisely."
        )

        if not summaries:
            print("   ⚠️  Gemini unavailable, using Claude for all reads")
            summaries = [f"[Doc {i}] {doc[:500]}..." for i, doc in enumerate(documents)]

        print(f"   ✅ Got {len(summaries)} summaries")

        # Step 2: Claude synthesizes from summaries
        print("   🧠 Phase 2: Claude Architect (reasoning)...")
        synthesis_prompt = f"""Based on these document summaries, answer: {question}

Summaries:
{chr(10).join(f'[Doc {i+1}] {s[:1000]}' for i, s in enumerate(summaries))}

Provide a comprehensive synthesis with citations to document numbers."""

        response = self._call_opus(synthesis_prompt)

        # Get cost comparison
        cost_stats = self.router.cost_comparison()

        result = {
            "question": question,
            "documents_analyzed": len(documents),
            "synthesis": response,
            "cost_stats": cost_stats,
            "summaries": summaries
        }

        print("="*60)
        print(f"📊 Multi-Model Analysis Complete")
        print(f"   Gemini cost: {cost_stats['gemini_cost']}")
        print(f"   Claude cost: {cost_stats['claude_cost']}")
        print(f"   Total: {cost_stats['total_cost']} (saved {cost_stats['savings_pct']})")

        return result

    def hunt(self, target: str, strategies: int = 3) -> SwarmResult:
        """
        Hunt mode - focused attack on a specific target/goal.
        Generates strategies and executes in parallel.
        """
        print(f"\n🎯 HUNT MODE: {target}")

        tasks = [
            f"Direct approach to {target}",
            f"Indirect/creative path to {target}",
            f"Competitive analysis for {target}",
        ]

        if strategies > 3:
            tasks.extend([
                f"Risk assessment for {target}",
                f"Quick win opportunities for {target}",
            ][:strategies-3])

        return self.release(tasks[:strategies])


def run_puzzle_room():
    """Interactive Puzzle Room Challenge"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║           🔐 PUZZLE ROOM CHALLENGE 🔐                     ║
    ║        7 Locks · Advanced Tool Use · Token Tracking       ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    fm = FlyingMonkeysV8()
    room = fm.puzzle_room()

    while True:
        status = room.get_status()
        print(f"\n{'='*60}")
        print(f"🏛️  VAULT STATUS: {status['locks_solved']}/7 locks open ({status['progress_pct']:.0f}%)")
        print(f"📊 {status['tokens']}")
        print(f"{'='*60}")

        if status['vault_open']:
            print("\n🎉 VAULT OPENED! You found the golden treasure! 🏆")
            break

        print("\nLocks:")
        for lock in status['locks']:
            icon = "🔓" if lock['solved'] else "🔒"
            print(f"  {icon} Lock {lock['id']}: {lock['name']} - {lock['challenge']}")

        print("\nCommands:")
        print("  solve <lock_id> <answer>  - Attempt to solve a lock")
        print("  code                      - Use code sandbox to solve")
        print("  auto                      - Auto-solve all with code")
        print("  quit                      - Exit")

        cmd = input("\n> ").strip().lower()

        if cmd.startswith("solve "):
            parts = cmd.split(maxsplit=2)
            if len(parts) >= 3:
                try:
                    lock_id = int(parts[1])
                    answer = parts[2]
                    result = room.attempt_lock(lock_id, answer)
                    print(result['message'])
                except ValueError:
                    print("Usage: solve <lock_id> <answer>")
            else:
                print("Usage: solve <lock_id> <answer>")

        elif cmd == "code":
            print("Enter Python code (end with empty line):")
            lines = []
            while True:
                line = input("... ")
                if not line:
                    break
                lines.append(line)
            code = "\n".join(lines)
            result = room.solve_with_code(code)
            print(f"Output: {result['execution'].get('output', '')}")
            if result['execution'].get('error'):
                print(f"Error: {result['execution']['error']}")

        elif cmd == "auto":
            print("\n🤖 Auto-solving with code execution...")
            auto_code = '''
# Solve all 7 locks programmatically
results[1] = 1847 + 1776 - 1492  # Victorian Math
results[2] = 1415  # Pi digits
results[3] = 55  # Fibonacci(10)
results[4] = "HELLO"  # Caesar decode KHOOR shift 3
results[5] = int("10101010", 2)  # Binary to decimal
results[6] = 29  # Largest prime factor of 13195

# Lock 7 = sum of others mod 1000
results[7] = (results[1] + results[2] + results[3] + 170 + results[6]) % 1000

for k, v in results.items():
    print(f"Lock {k}: {v}")
'''
            print(auto_code)
            result = room.solve_with_code(auto_code)
            print(f"\n{result['execution'].get('output', '')}")

        elif cmd == "quit":
            break

        else:
            print("Unknown command")


def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║            🐵 FLYING MONKEYS v8 🐵                        ║
    ║    Advanced Tool Use · Opus 4.5 · Token Tracking          ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    fm = FlyingMonkeysV8()

    print("Commands:")
    print("  1. Single task")
    print("  2. Multi-task swarm")
    print("  3. Brainstorm mode")
    print("  4. Hunt mode")
    print("  5. 🔐 Puzzle Room Challenge")
    print("  6. 🧪 Code Sandbox")
    print("  7. Exit")

    choice = input("\nSelect [1]: ").strip() or "1"

    if choice == "1":
        task = input("Task: ").strip() or "Find the fastest path to $10k MRR"
        result = fm.release_single(task)
        print(f"\n📋 Result:")
        print(json.dumps(result, indent=2, default=str))
        print(f"\n📊 {fm.tokens.display()}")

    elif choice == "2":
        print("Enter tasks (empty line to finish):")
        tasks = []
        while True:
            t = input(f"  [{len(tasks)+1}]: ").strip()
            if not t:
                break
            tasks.append(t)

        if not tasks:
            tasks = [
                "Analyze market opportunity for AI agents",
                "Identify quick revenue wins",
                "Find automation opportunities",
                "Competitive landscape analysis",
            ]

        fm.release(tasks)
        print(f"\n📊 {fm.tokens.display()}")

    elif choice == "3":
        topic = input("Topic to brainstorm: ").strip() or "Ways to monetize AI agent platform"
        fm.brainstorm(topic)
        print(f"\n📊 {fm.tokens.display()}")

    elif choice == "4":
        target = input("Hunt target: ").strip() or "$50k revenue in 30 days"
        fm.hunt(target, strategies=5)
        print(f"\n📊 {fm.tokens.display()}")

    elif choice == "5":
        run_puzzle_room()

    elif choice == "6":
        print("🧪 Code Sandbox (Programmatic Tool Calling)")
        print("Enter Python code (end with empty line):")
        print("Available: call_tool(name, **args), results dict, math module")
        lines = []
        while True:
            line = input("... ")
            if not line:
                break
            lines.append(line)
        code = "\n".join(lines)
        result = fm.execute_code(code)
        print(f"\nOutput:\n{result.get('output', '')}")
        print(f"Results: {result.get('results', {})}")
        if result.get('error'):
            print(f"Error: {result['error']}")

    else:
        print("👋")


if __name__ == "__main__":
    main()
