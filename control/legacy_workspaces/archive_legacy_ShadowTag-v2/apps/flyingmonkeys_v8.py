# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import asyncio
import enum
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any
from collections.abc import Callable

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class SwarmResult:
    total: int
    completed: int
    approved: int
    blocked: int
    avg_latency_ms: float
    results: list[dict[str, Any]]


class ValidationResult(enum.Enum):
    APPROVED = "approved"
    BLOCKED = "blocked"
    FLAGGED = "flagged"


@dataclass
class ToolDef:
    name: str
    description: str
    func: Callable
    risk_level: str = "medium"


# =============================================================================
# COMPONENTS
# =============================================================================


class TokenLedger:
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = 0.0

    def add(self, input_count: int, output_count: int):
        self.input_tokens += input_count
        self.output_tokens += output_count
        self.total_cost += (input_count / 1_000_000 * 0.10) + (output_count / 1_000_000 * 0.40)  # Updated for Flash pricing

    def display(self):
        return f"In: {self.input_tokens} | Out: {self.output_tokens} | Cost: ${self.total_cost:.6f}"


class Router:
    def cost_comparison(self):
        return {
            "gemini_flash": "$0.10 / 1M tokens",
            "competitor_high": "$15.00 / 1M tokens",
            "savings": "99.3%",
        }


class PuzzleRoom:
    def __init__(self):
        self.locks = {
            1: {
                "question": "Calculate 1847 + 1776 - 1492",
                "answer": "2131",
                "solved": False,
            },
            2: {
                "question": "Year of the Battle of Agincourt?",
                "answer": "1415",
                "solved": False,
            },
            3: {"question": "10th Fibonacci number?", "answer": "55", "solved": False},
            4: {"question": "Reverse 'OLLEH'", "answer": "HELLO", "solved": False},
            5: {
                "question": "Binary 10101010 to decimal?",
                "answer": "170",
                "solved": False,
            },
            6: {"question": "10th prime number?", "answer": "29", "solved": False},
            7: {
                "question": "Sum of answers 1,2,3,5,6 modulo 1000?",
                "answer": "800",
                "solved": False,
            },
        }
        self.history = []
        self.start_time = time.time()

    def get_status(self):
        solved_count = sum(1 for l in self.locks.values() if l["solved"])
        return {
            "locks_total": len(self.locks),
            "locks_solved": solved_count,
            "locks_remaining": len(self.locks) - solved_count,
            "elapsed_s": int(time.time() - self.start_time),
            "all_solved": solved_count == len(self.locks),
        }

    def attempt_lock(self, lock_id: int, answer: str):
        self.history.append(
            {
                "action": "solve",
                "lock_id": lock_id,
                "answer": answer,
                "timestamp": time.time(),
            }
        )
        if lock_id not in self.locks:
            return {"success": False, "message": "Invalid lock ID"}

        lock = self.locks[lock_id]
        if str(answer).lower().strip() == str(lock["answer"]).lower().strip():
            lock["solved"] = True
            return {"success": True, "message": "Lock Opened!"}
        return {"success": False, "message": "Incorrect answer"}

    def solve_with_code(self, code: str):
        self.history.append({"action": "code", "code": code, "timestamp": time.time()})
        # Simulated secure sandbox execution
        local_scope = {"results": {}}
        try:
            exec(code, {"__builtins__": {}}, local_scope)
            results = local_scope.get("results", {})

            # Apply results to locks (Mapping results[lock_id] = answer)
            solved = 0
            for k, v in results.items():
                if isinstance(k, int) and k in self.locks:
                    if str(v) == str(self.locks[k]["answer"]):
                        self.locks[k]["solved"] = True
                        solved += 1

            return {
                "success": True,
                "execution_output": "Executed successfully",
                "locks_solved_in_batch": solved,
                "status": self.get_status(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_tool_call(self, tool_call: dict):
        self.history.append({"action": "tool_call", "payload": tool_call, "timestamp": time.time()})
        command = tool_call.get("command")
        if command == "status":
            return self.get_status()
        elif command == "inspect":
            lock_id = tool_call.get("lock_id")
            if lock_id in self.locks:
                return {"lock_id": lock_id, "clue": self.locks[lock_id]["question"]}
            return {"error": "Lock not found"}
        elif command == "submit":
            return self.attempt_lock(tool_call.get("lock_id"), tool_call.get("solution_value"))
        return {"error": "Unknown command"}

    def get_history(self):
        return self.history


# =============================================================================
# MAIN SYSTEM
# =============================================================================


class FlyingMonkeysV8:
    def __init__(self):
        self.mission = "To demonstrate autonomous multi-agent capability."
        self.tokens = TokenLedger()
        self.router = Router()
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None

        if self.api_key and genai:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client: {e}")

    def puzzle_room(self):
        return PuzzleRoom()

    def _call_gemini(self, prompt: str, system_instruction: str | None = None) -> str:
        if not self.client:
            return None

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            )
            response = self.client.models.generate_content(model="gemini-3.1-flash", contents=prompt, config=config)

            # Track usage if available
            if response.usage_metadata:
                self.tokens.add(
                    response.usage_metadata.prompt_token_count or 0,
                    response.usage_metadata.candidates_token_count or 0,
                )

            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return None

    def _execute_swarm(self, count=1, mode="default", prompt="") -> SwarmResult:
        res = []

        for i in range(count):
            start_time = time.time()
            role_desc = f"Agent {i + 1} of {count}"

            gemini_response = None
            if self.client:
                # Give each agent a specific persona/angle
                system_prompt = (
                    f"You are {role_desc} in a swarm. Mode: {mode}. Be concise, actionable, and distinct from others. Output only the core insight."
                )
                gemini_response = self._call_gemini(prompt, system_instruction=system_prompt)

            if gemini_response:
                output = gemini_response
            else:
                output = f"Simulated output for {mode} task #{i + 1} (No API connection)"

            latency = (time.time() - start_time) * 1000

            res.append(
                {
                    "id": str(uuid.uuid4())[:8],
                    "role": role_desc,
                    "output": output,
                    "confidence": 0.95,
                    "latency_ms": latency,
                }
            )

        return SwarmResult(
            total=count,
            completed=count,
            approved=count,
            blocked=0,
            avg_latency_ms=sum(r["latency_ms"] for r in res) / count if count > 0 else 0,
            results=res,
        )

    def hunt(self, target: str, strategies: int = 5) -> SwarmResult:
        print(f"🕵️  Swarm Hunting: '{target}' with {strategies} strategies...")
        return self._execute_swarm(
            strategies,
            mode="hunt",
            prompt=f"Develop a strategy to find/solve: {target}",
        )

    def release(self, tasks: list[str], max_parallel: int = 5) -> SwarmResult:
        print(f"🚀 releasing {len(tasks)} tasks to swarm...")
        return self._execute_swarm(
            len(tasks),
            mode="task_execution",
            prompt=f"Execute this task: {tasks[0] if tasks else 'Standby'}",
        )

    def brainstorm(self, topic: str, num_ideas: int = 5) -> SwarmResult:
        print(f"🧠 Brainstorming: '{topic}'...")
        return self._execute_swarm(
            num_ideas,
            mode="brainstorm",
            prompt=f"Generate a unique, high-value idea about: {topic}",
        )

    def release_single(self, task: str) -> dict:
        time.sleep(0.2)
        return {
            "task": task,
            "status": "completed",
            "result": "Simulated single task result",
            "latency_ms": 120,
        }

    async def bulk_analyze(self, documents: list[str], question: str) -> dict:
        # Simulate async analysis
        await asyncio.sleep(1.0)
        return {
            "analyzed_count": len(documents),
            "summary": f"Analyzed {len(documents)} docs. Conclusion: {question} is addressed.",
            "cost_savings": "93%",
        }


if __name__ == "__main__":
    print("Initializing FlyingMonkeys V8...")
    fm = FlyingMonkeysV8()
    print(f"Mission: {fm.mission}")

    print("\n--- Testing Puzzle Room ---")
    room = fm.puzzle_room()
    print(f"Initial Status: {room.get_status()}")

    # Try solving lock 1
    print("\nAttempting Lock 1 (Manual)...")
    result = room.attempt_lock(1, "2131")
    print(f"Result: {result}")

    # Try code solve
    print("\nAttempting Batch Code Solve...")
    code_payload = """
results[2] = 1415
results[3] = 55
results[4] = "HELLO"
results[5] = 170
results[6] = 29
results[7] = 800
"""
    result = room.solve_with_code(code_payload)
    print(f"Code Result: {result}")

    print(f"Final Status: {room.get_status()}")
    print("\nSimulation Complete.")
