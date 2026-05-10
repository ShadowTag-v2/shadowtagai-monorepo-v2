"""
JuraProtocol - "Jura" Gatekeeper (German for Judge).
Prevents dumb agents from polluting memory.
Supports atomic chat reconfiguration for dynamic context injection.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import redis

from agents.legal_whiteboard import LegalWhiteboard
from src.ShadowTag-v2.services.gemini_core import GeminiAntigravity


@dataclass
class ChatMessage:
    """Single message in conversation."""

    role: str  # "system", "user", "assistant"
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AtomicChatConfig:
    """Atomic reconfiguration state for mid-conversation injection."""

    system_prompt: str = ""
    cursor_rules: str = ""
    injected_context: list[ChatMessage] = field(default_factory=list)
    conversation_history: list[ChatMessage] = field(default_factory=list)
    active_commands: list[str] = field(default_factory=list)  # jura, musk-filter, bootstrap
    temperature: float = 1.0
    thinking_level: str = "high"

    def to_prompt(self) -> str:
        """Compile all context into single prompt."""
        parts = []

        if self.system_prompt:
            parts.append(f"SYSTEM: {self.system_prompt}")

        if self.cursor_rules:
            parts.append(f"CURSOR RULES:\n{self.cursor_rules}")

        if self.active_commands:
            parts.append(f"ACTIVE COMMANDS: {', '.join(self.active_commands)}")

        for msg in self.injected_context:
            parts.append(f"[INJECTED {msg.role.upper()}]: {msg.content}")

        for msg in self.conversation_history:
            parts.append(f"{msg.role.upper()}: {msg.content}")

        return "\n\n".join(parts)


LEVEL_CRITERIA = {
    0: "Basic Execution: Can the agent complete a defined task without syntax errors?",
    1: "Pattern Recognition: Can the agent identify recurring errors?",
    2: "Optimization: Can the agent refactor code to reduce token usage by >10%?",
}


class JuraProtocol:
    """Jura - The German Judge. ATP 5-19 risk assessment gatekeeper."""

    def __init__(
        self, project_id: str = None, redis_host: str = "10.85.19.187", redis_port: int = 6379
    ):
        self.whiteboard = LegalWhiteboard()
        self.jura = GeminiAntigravity(project_id=project_id)
        self.config = AtomicChatConfig()

        # Redis for atomic state (optional - graceful fallback)
        try:
            self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis.ping()
            self._redis_available = True
        except:
            self.redis = None
            self._redis_available = False

        # Load cursor rules if available
        self._load_cursor_rules()

    def _load_cursor_rules(self):
        """Load .cursorrules from project root."""
        cursor_path = Path(__file__).parent.parent / ".cursorrules"
        if cursor_path.exists():
            self.config.cursor_rules = cursor_path.read_text()

    # === ATOMIC RECONFIGURATION METHODS ===

    def inject_system_prompt(self, prompt: str) -> "JuraProtocol":
        """Hot-swap system prompt mid-conversation."""
        self.config.system_prompt = prompt
        if self._redis_available:
            self.redis.set("jura:system_prompt", prompt)
        return self

    def inject_context(self, role: str, content: str, metadata: dict = None) -> "JuraProtocol":
        """Inject user/assistant context on the fly."""
        msg = ChatMessage(role=role, content=content, metadata=metadata or {})
        self.config.injected_context.append(msg)
        if self._redis_available:
            self.redis.rpush("jura:injected", json.dumps({"role": role, "content": content}))
        return self

    def add_message(self, role: str, content: str) -> "JuraProtocol":
        """Add to conversation history."""
        self.config.conversation_history.append(ChatMessage(role=role, content=content))
        return self

    def activate_command(self, command: str) -> "JuraProtocol":
        """Activate jura/musk-filter/bootstrap command."""
        if command not in self.config.active_commands:
            self.config.active_commands.append(command)
        return self

    def set_thinking(self, level: str) -> "JuraProtocol":
        """Set thinking level: high, medium, low."""
        self.config.thinking_level = level
        return self

    def clear_injected(self) -> "JuraProtocol":
        """Clear injected context but keep history."""
        self.config.injected_context = []
        if self._redis_available:
            self.redis.delete("jura:injected")
        return self

    def reset(self) -> "JuraProtocol":
        """Full reset to base state."""
        self.config = AtomicChatConfig()
        self._load_cursor_rules()
        if self._redis_available:
            self.redis.delete("jura:system_prompt", "jura:injected")
        return self

    def evaluate_with_context(self, query: str) -> dict:
        """Run evaluation with full atomic context."""
        full_prompt = self.config.to_prompt() + f"\n\nCURRENT QUERY: {query}"

        prompt = f"""
        {full_prompt}

        ACT AS: Jura (German Judge).
        Apply ATP 5-19 risk assessment.
        OUTPUT JSON: {{"verdict": "APPROVE/DENY", "reasoning": "...", "risk_tier": 1-5, "confidence": 0-100}}
        """

        try:
            response = self.jura.model.generate_content(
                prompt,
                generation_config=self.jura._get_generation_config(
                    thinking_level=self.config.thinking_level, json_output=True
                ),
            )
            result = json.loads(response.text.replace("```json", "").replace("```", ""))

            # Add to history
            self.add_message("user", query)
            self.add_message("assistant", json.dumps(result))

            return result
        except Exception as e:
            return {"error": str(e), "risk_tier": 5, "verdict": "DENY"}

    def administer_exam(self, candidate_id: str, current_level: int, proof_of_work: dict) -> tuple:
        target_level = current_level + 1
        criteria = LEVEL_CRITERIA.get(target_level, "Unknown Level")

        print(f"///▞ JURA EXAM START :: Candidate {candidate_id} -> Level {target_level}")
        prompt = f"""
        ACT AS: Jura (German Judge).
        TASK: Evaluate Proof of Work against Criteria using ATP 5-19.
        CRITERIA: {criteria}
        PROOF: {json.dumps(proof_of_work, default=str)}
        OUTPUT JSON ONLY: {{"verdict": "PASS" or "FAIL", "reasoning": "...", "risk_tier": 1-5, "confidence": 0-100}}
        """

        try:
            # Use Gemini 3 high thinking for complex evaluation
            response = self.jura.model.generate_content(
                prompt,
                generation_config=self.jura._get_generation_config(
                    thinking_level="high", json_output=True
                ),
            )
            raw = response.text.replace("```json", "").replace("```", "")
            result = json.loads(raw)

            if result.get("verdict") == "PASS":
                self.whiteboard.record_learning(
                    candidate_id, f"Passed Level {target_level}", result
                )
                return True, result.get("reasoning")
            return False, result.get("reasoning")
        except Exception as e:
            return False, f"System Error: {str(e)}"

    def quick_assess(self, code_snippet: str) -> dict:
        """Fast risk assessment without full exam - uses low thinking."""
        prompt = f"""
        ACT AS: Jura. Quick ATP 5-19 assessment.
        CODE: {code_snippet[:2000]}
        OUTPUT JSON: {{"risk_tier": 1-5, "issues": ["..."], "recommendation": "APPROVE/DENY"}}
        """

        try:
            response = self.jura.model.generate_content(
                prompt,
                generation_config=self.jura._get_generation_config(
                    thinking_level="low", json_output=True
                ),
            )
            return json.loads(response.text.replace("```json", "").replace("```", ""))
        except Exception as e:
            return {"error": str(e), "risk_tier": 5, "recommendation": "DENY"}
