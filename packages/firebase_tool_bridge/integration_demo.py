# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Integration Demo — end-to-end Firebase AI Logic function calling.

Demonstrates the complete 5-step workflow per Peter Friese's tutorial:
    1. Register tools with risk classification
    2. Auto-generate FunctionDeclarations from Python signatures
    3. Configure model parameters via Remote Config
    4. Run the multi-turn chat loop (Model proposes → App executes)
    5. Evidence logging for every function call

This module is self-contained and uses mock implementations for the model
and confirmation provider so it can run without a live Firebase project.

Usage:
    python -m firebase_tool_bridge.integration_demo

Reference:
    - Firebase AI Logic Function Calling: https://goo.gle/3NWbG8H
    - Tool contract: tool_contracts/firebase.ai_logic_launch.yaml
    - Bridge contract: tool_contracts/firebase.function_bridge.yaml
"""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path
from typing import Any

from firebase_tool_bridge.bridge import BridgeResult, CallStatus, ToolBridge
from firebase_tool_bridge.declarations import (
    registry_to_declarations,
)
from firebase_tool_bridge.evidence import EvidenceLogger
from firebase_tool_bridge.firebase_chat_loop import (
    FunctionCallPart,
    ModelResponse,
)
from firebase_tool_bridge.registry import FunctionRegistry, RiskTier
from firebase_tool_bridge.remote_config import ModelConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ─── Step 1: Define Tool Functions ──────────────────────────────────────────


def fetch_weather(city: str, unit: str = "celsius") -> dict[str, Any]:
    """Fetch the current weather for a city.

    Args:
        city: The name of the city to check weather for.
        unit: Temperature unit — "celsius" or "fahrenheit".

    Returns:
        Dictionary with temperature, conditions, and humidity.
    """
    # Simulated weather data (real implementation would call an API).
    weather_db = {
        "san francisco": {"temp": 18, "conditions": "foggy", "humidity": 72},
        "new york": {"temp": 25, "conditions": "sunny", "humidity": 55},
        "tokyo": {"temp": 22, "conditions": "cloudy", "humidity": 68},
        "london": {"temp": 15, "conditions": "rainy", "humidity": 85},
    }
    data = weather_db.get(city.lower(), {"temp": 20, "conditions": "unknown", "humidity": 50})
    if unit == "fahrenheit":
        data = {**data, "temp": round(data["temp"] * 9 / 5 + 32)}
    return {"city": city, "unit": unit, **data}


def search_recipes(
    query: str,
    max_results: int = 5,
    dietary_filter: str | None = None,
) -> list[dict[str, str]]:
    """Search for recipes matching a query.

    Args:
        query: The search query (e.g., "pasta with tomato sauce").
        max_results: Maximum number of recipes to return.
        dietary_filter: Optional dietary filter (e.g., "vegan", "gluten-free").

    Returns:
        List of recipe summaries with name, description, and cook time.
    """
    recipes = [
        {"name": "Classic Margherita Pizza", "description": "Traditional Neapolitan pizza", "cook_time": "25 min"},
        {"name": "Spaghetti Carbonara", "description": "Roman egg and cheese pasta", "cook_time": "20 min"},
        {"name": "Pad Thai", "description": "Thai stir-fried rice noodles", "cook_time": "30 min"},
        {"name": "Caesar Salad", "description": "Romaine lettuce with anchovy dressing", "cook_time": "15 min"},
        {"name": "Ratatouille", "description": "Provençal vegetable stew", "cook_time": "45 min"},
    ]
    # Simulate filtering
    if dietary_filter == "vegan":
        recipes = [r for r in recipes if r["name"] in ("Ratatouille", "Pad Thai")]
    return recipes[:max_results]


def save_meal_plan(
    day: str,
    breakfast: str,
    lunch: str,
    dinner: str,
) -> dict[str, str]:
    """Save a meal plan for a specific day.

    This is a MEDIUM risk action — it mutates user state.

    Args:
        day: Day of the week (e.g., "Monday").
        breakfast: Breakfast recipe name.
        lunch: Lunch recipe name.
        dinner: Dinner recipe name.

    Returns:
        Confirmation with saved plan details.
    """
    return {
        "status": "saved",
        "day": day,
        "meals": {"breakfast": breakfast, "lunch": lunch, "dinner": dinner},
    }


def delete_all_meal_plans() -> dict[str, str]:
    """Delete all saved meal plans.

    This is a CRITICAL risk action — it permanently removes data.
    Requires explicit user confirmation before execution.

    Returns:
        Confirmation that all plans were deleted.
    """
    return {"status": "deleted", "message": "All meal plans have been permanently deleted."}


# ─── Step 2: Mock Confirmation Provider ─────────────────────────────────────


def cli_confirmation_provider(function_name: str, args: dict[str, Any]) -> bool:
    """Mock confirmation provider that auto-approves for demo purposes.

    In production, this would show a modal, Slack message, or CLI prompt.
    """
    logger.info("🔐 CONFIRMATION GATE: '%s' with args %s → AUTO-APPROVED (demo mode)", function_name, list(args.keys()))
    return True


# ─── Step 3: Mock Chat Model ────────────────────────────────────────────────


class MockChatModel:
    """Simulates a Firebase AI Logic generative model for demo purposes.

    The mock follows a scripted conversation:
      Turn 1: User asks about weather → model calls fetch_weather
      Turn 2: Model receives weather → asks about recipes → calls search_recipes
      Turn 3: Model receives recipes → provides final text answer
    """

    def __init__(self) -> None:
        self.turn = 0

    def send_message(self, content: list[dict[str, Any]]) -> ModelResponse:
        """Simulate model responses with function calls."""
        self.turn += 1

        if self.turn == 1:
            # Model proposes a function call for weather
            return ModelResponse(
                text=None,
                function_calls=[
                    FunctionCallPart(
                        name="fetch_weather",
                        args={"city": "San Francisco", "unit": "celsius"},
                    )
                ],
            )
        elif self.turn == 2:
            # After receiving weather, model asks for recipes
            return ModelResponse(
                text=None,
                function_calls=[
                    FunctionCallPart(
                        name="search_recipes",
                        args={"query": "warm soup for foggy weather", "max_results": 3},
                    )
                ],
            )
        else:
            # Model provides final text answer incorporating tool results
            return ModelResponse(
                text=(
                    "Based on the current weather in San Francisco (18°C, foggy), "
                    "I'd recommend warming up with one of these recipes:\n\n"
                    "1. **Classic Margherita Pizza** — 25 min cook time\n"
                    "2. **Spaghetti Carbonara** — 20 min cook time\n"
                    "3. **Pad Thai** — 30 min cook time\n\n"
                    "Would you like me to save any of these to your meal plan?"
                ),
                function_calls=[],
            )


# ─── Step 4: Run the Full Integration Demo ──────────────────────────────────


def run_demo() -> None:
    """Execute the complete function calling integration demo.

    This demonstrates the 5-step workflow:
        1. Register tools → FunctionRegistry
        2. Generate declarations → JSON Schema
        3. Configure model → Remote Config
        4. Chat loop → Model proposes, App executes
        5. Evidence log → Audit trail
    """
    logger.info("=" * 70)
    logger.info("🚀 Firebase AI Logic Function Calling — Integration Demo")
    logger.info("=" * 70)

    # ── 1. Register Tools ────────────────────────────────────────────
    logger.info("\n📋 STEP 1: Registering tools with risk classification...")
    registry = FunctionRegistry()
    registry.register("fetch_weather", fetch_weather, RiskTier.LOW)
    registry.register("search_recipes", search_recipes, RiskTier.LOW)
    registry.register("save_meal_plan", save_meal_plan, RiskTier.MEDIUM)
    registry.register(
        "delete_all_meal_plans",
        delete_all_meal_plans,
        RiskTier.CRITICAL,
        action_tags=frozenset({"data_delete"}),
    )

    logger.info("   ✅ Registered %d tools:", len(registry))
    for reg in registry.list_all():
        logger.info("      • %s [%s]%s", reg.name, reg.risk_tier.value, " ⚠️ REQUIRES CONFIRMATION" if reg.risk_tier.requires_confirmation else "")

    # ── 2. Generate FunctionDeclarations ──────────────────────────────
    logger.info("\n📝 STEP 2: Auto-generating FunctionDeclarations from signatures...")
    declarations = registry_to_declarations(registry)

    logger.info("   ✅ Generated %d declarations:", len(declarations))
    for decl in declarations:
        params = decl.get("parameters", {})
        prop_names = list(params.get("properties", {}).keys())
        required = params.get("required", [])
        logger.info(
            "      • %s(%s) — %d params, %d required",
            decl["name"],
            ", ".join(prop_names),
            len(prop_names),
            len(required),
        )

    # Print one full declaration as an example
    logger.info("\n   📄 Example declaration (fetch_weather):")
    for line in json.dumps(declarations[0], indent=2).splitlines():
        logger.info("      %s", line)

    # ── 3. Configure Model via Remote Config ─────────────────────────
    logger.info("\n⚙️  STEP 3: Configuring model parameters...")
    # Simulate Remote Config template
    mock_template = {
        "model_name": "gemini-2.0-flash",
        "temperature": 0.0,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    system_instruction = (
        "You are a helpful meal planning assistant called Friendly Meals. "
        "Use the available tools to help users plan their meals. "
        "Always check the weather before recommending recipes."
    )
    config = ModelConfig.from_dict(mock_template)
    logger.info("   ✅ Model: %s (temperature=%.1f, deterministic tool selection)", config.model_name, config.temperature)
    logger.info("   📝 System instruction: %s...", system_instruction[:60])

    # ── 4. Run the Multi-Turn Chat Loop ──────────────────────────────
    logger.info("\n💬 STEP 4: Running multi-turn chat loop...")
    logger.info("   User prompt: 'What's the weather in San Francisco? Suggest some recipes.'")

    # Set up evidence logging in a temp directory
    evidence_root = Path(tempfile.mkdtemp())
    evidence_logger = EvidenceLogger(repo_root=evidence_root)

    # Set up bridge with confirmation provider
    bridge = ToolBridge(
        registry=registry,
        evidence=evidence_logger,
        confirmation=cli_confirmation_provider,
    )

    # Mock model for the scripted demo
    model = MockChatModel()
    all_results: list[BridgeResult] = []

    # Manual chat loop to show each step clearly
    turn = 0
    max_turns = 10

    # Initial user message
    current_content: list[dict[str, Any]] = [{"text": "What's the weather in San Francisco? Suggest some recipes."}]

    while turn < max_turns:
        turn += 1
        logger.info("\n   ─── Turn %d ───", turn)

        # Send to model
        response = model.send_message(current_content)

        if not response.has_function_calls:
            # Model produced a final text response
            logger.info("   📝 Model final response:")
            if response.text:
                for line in response.text.splitlines():
                    logger.info("      %s", line)
            break

        # Process each function call
        logger.info("   🔧 Model proposed %d function call(s):", len(response.function_calls))
        function_responses: list[dict[str, Any]] = []

        for fc in response.function_calls:
            logger.info("      → %s(%s)", fc.name, json.dumps(fc.args))

            # Dispatch through the bridge (validates + confirms + executes + logs)
            result = bridge.handle(fc.name, fc.args)
            all_results.append(result)

            logger.info("      ← status=%s", result.status)
            if result.status == CallStatus.SUCCESS:
                logger.info("      ← result=%s", json.dumps(result.result, default=str)[:200])

            # Build the functionResponse to send back to the model
            function_responses.append(
                {
                    "functionResponse": {
                        "name": fc.name,
                        "response": {"result": result.result} if result.result else {"error": result.error or "Unknown error"},
                    }
                }
            )

        # Send function responses back to model for next turn
        current_content = function_responses

    # ── 5. Evidence Audit Trail ──────────────────────────────────────
    logger.info("\n📊 STEP 5: Evidence audit trail")
    evidence_file = evidence_logger._evidence_file  # noqa: SLF001
    if evidence_file.exists():
        lines = evidence_file.read_text().strip().splitlines()
        logger.info("   ✅ %d evidence records written to %s", len(lines), evidence_file)
        for i, line in enumerate(lines, 1):
            record = json.loads(line)
            logger.info(
                "      [%d] %s → %s (risk=%s, duration=%.1fms)",
                i,
                record.get("function_name", "?"),
                "✅" if record.get("success") else "❌",
                record.get("risk_tier", "?"),
                record.get("duration_ms", 0),
            )
    else:
        logger.info("   ⚠️ No evidence file found (evidence logging may not have written yet)")

    # ── Summary ──────────────────────────────────────────────────────
    logger.info("\n" + "=" * 70)
    logger.info("📈 DEMO SUMMARY")
    logger.info("=" * 70)
    logger.info("   Tools registered:     %d", len(registry))
    logger.info("   Declarations generated: %d", len(declarations))
    logger.info("   Chat turns used:      %d", turn)
    logger.info("   Function calls made:  %d", len(all_results))
    logger.info(
        "   All calls succeeded:  %s",
        "✅ YES" if all(r.status == CallStatus.SUCCESS for r in all_results) else "❌ NO",
    )
    logger.info("   Evidence records:     %d", len(evidence_file.read_text().strip().splitlines()) if evidence_file.exists() else 0)
    logger.info("   Model configuration:  %s (temp=%.1f)", config.model_name, config.temperature)
    logger.info("=" * 70)
    logger.info("🏁 Demo complete. The bridge pattern ensures:")
    logger.info("   • Model proposes — App executes (never the reverse)")
    logger.info("   • Every call is evidence-logged (audit trail)")
    logger.info("   • Risk-tiered confirmation gating (HIGH/CRITICAL require approval)")
    logger.info("   • Unregistered functions are always rejected")
    logger.info("=" * 70)


if __name__ == "__main__":
    run_demo()
