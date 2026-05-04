# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Firebase Chat Loop — multi-turn function-calling integration layer.

Implements the Firebase AI Logic multi-turn chat interaction pattern:

    User prompt
        → Model response (may contain functionCall parts)
            → Bridge dispatches each call
                → functionResponse parts sent back to model
                    → Model produces final text response

This module is SDK-agnostic: it works with both the Firebase JS/TS SDK
(via JSON interchange) and the Python google-generativeai SDK.

Architecture:
    ┌─────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
    │  User   │───▶│  Model   │───▶│ ChatLoop  │───▶│  Bridge  │
    │ Prompt  │    │ Response │    │ Dispatch  │    │ Execute  │
    └─────────┘    └──────────┘    └───────────┘    └──────────┘
         ▲                              │                 │
         │                              │                 │
         └──────────────────────────────┘                 │
              functionResponse ◀──────────────────────────┘
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol

from firebase_tool_bridge.bridge import BridgeResult, CallStatus, ToolBridge

logger = logging.getLogger(__name__)

# Maximum turns to prevent infinite loops (model keeps calling functions).
DEFAULT_MAX_TURNS = 10


class ChatModel(Protocol):
    """Protocol for chat model interaction.

    Implementations wrap the actual Firebase/Gemini SDK chat objects.
    This abstraction allows testing without live API calls.
    """

    def send_message(self, content: list[dict[str, Any]]) -> ModelResponse:
        """Send message content to the chat model.

        Args:
            content: List of content parts (text, functionResponse, etc.)

        Returns:
            ModelResponse with the model's reply.
        """
        ...


@dataclass(frozen=True, slots=True)
class FunctionCallPart:
    """A function call extracted from a model response.

    Mirrors the Firebase AI SDK FunctionCallPart structure:
        {functionCall: {name: "fn_name", args: {key: value}}}
    """

    name: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FunctionResponsePart:
    """A function response to send back to the model.

    Mirrors the Firebase AI SDK FunctionResponsePart structure:
        {functionResponse: {name: "fn_name", response: {result: ...}}}
    """

    name: str
    response: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ModelResponse:
    """Parsed model response containing text and/or function calls.

    A response can contain:
    - Only text (final answer)
    - Only function calls (model wants to use tools)
    - Both text and function calls (model narrating + calling tools)
    """

    text: str | None = None
    function_calls: list[FunctionCallPart] = field(default_factory=list)
    raw: Any = None  # Original SDK response for debugging

    @property
    def has_function_calls(self) -> bool:
        """Check if this response contains function call requests."""
        return len(self.function_calls) > 0


@dataclass(frozen=True, slots=True)
class ChatLoopResult:
    """Final result of a complete chat loop interaction.

    Contains the model's final text response plus the full audit trail
    of all function calls that were dispatched during the interaction.
    """

    text: str | None
    function_calls_made: list[BridgeResult] = field(default_factory=list)
    turns_used: int = 0

    @property
    def total_calls(self) -> int:
        """Total number of function calls dispatched."""
        return len(self.function_calls_made)

    @property
    def all_succeeded(self) -> bool:
        """Check if all function calls succeeded."""
        return all(r.status == CallStatus.SUCCESS for r in self.function_calls_made)


def extract_function_calls(response: ModelResponse) -> list[FunctionCallPart]:
    """Extract function call parts from a model response.

    Args:
        response: The model's response to parse.

    Returns:
        List of FunctionCallPart objects found in the response.
    """
    return list(response.function_calls)


def extract_function_calls_from_raw(
    raw_response: dict[str, Any],
) -> list[FunctionCallPart]:
    """Extract function calls from a raw Firebase SDK response dict.

    Handles the Firebase AI SDK response structure:
        {
            "candidates": [{
                "content": {
                    "parts": [
                        {"functionCall": {"name": "fn", "args": {...}}}
                    ]
                }
            }]
        }

    Args:
        raw_response: Raw response dict from the Firebase SDK.

    Returns:
        List of FunctionCallPart objects.
    """
    calls: list[FunctionCallPart] = []

    candidates = raw_response.get("candidates", [])
    for candidate in candidates:
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        for part in parts:
            fc = part.get("functionCall")
            if fc:
                calls.append(
                    FunctionCallPart(
                        name=fc.get("name", ""),
                        args=fc.get("args", {}),
                    )
                )

    return calls


def build_function_responses(
    results: list[BridgeResult],
) -> list[dict[str, Any]]:
    """Build Firebase SDK functionResponse content parts from bridge results.

    Creates the content parts array to send back to the model:
        [
            {
                "functionResponse": {
                    "name": "get_weather",
                    "response": {"result": {"temp": 38, "unit": "F"}}
                }
            }
        ]

    Args:
        results: List of BridgeResult from the ToolBridge.

    Returns:
        List of functionResponse content part dicts.
    """
    return [
        {
            "functionResponse": {
                "name": result.function_name,
                "response": result.to_function_response(),
            },
        }
        for result in results
    ]


def dispatch_function_calls(
    bridge: ToolBridge,
    calls: list[FunctionCallPart],
) -> list[BridgeResult]:
    """Dispatch function calls through the ToolBridge.

    Processes each function call through the bridge's validation,
    confirmation, and execution pipeline.

    Args:
        bridge: The ToolBridge instance for dispatch.
        calls: List of function calls to dispatch.

    Returns:
        List of BridgeResult, one per call.
    """
    batch = [(call.name, call.args) for call in calls]
    return bridge.handle_batch(batch)


class FirebaseChatLoop:
    """Multi-turn chat loop with function-calling dispatch.

    Orchestrates the complete interaction cycle:
    1. Send user message to model
    2. If model returns function calls, dispatch through bridge
    3. Send function responses back to model
    4. Repeat until model returns text-only response (or max turns)

    Usage:
        bridge = ToolBridge(registry)
        chat_model = GeminiChatAdapter(chat_session)
        loop = FirebaseChatLoop(bridge, chat_model)

        result = loop.send("What's the weather in Boston?")
        print(result.text)
        print(f"Made {result.total_calls} function calls")
    """

    def __init__(
        self,
        bridge: ToolBridge,
        chat_model: ChatModel,
        *,
        max_turns: int = DEFAULT_MAX_TURNS,
    ) -> None:
        """Initialize the chat loop.

        Args:
            bridge: ToolBridge for dispatching function calls.
            chat_model: Chat model implementation (SDK wrapper).
            max_turns: Maximum function-calling turns before stopping.
                Prevents infinite loops where the model keeps calling tools.
        """
        self._bridge = bridge
        self._chat_model = chat_model
        self._max_turns = max_turns

    def send(self, user_message: str) -> ChatLoopResult:
        """Send a user message and handle the full function-calling loop.

        Args:
            user_message: The user's text message.

        Returns:
            ChatLoopResult with final text and function call audit trail.
        """
        all_results: list[BridgeResult] = []
        turns = 0

        # Initial user message
        content: list[dict[str, Any]] = [{"text": user_message}]

        while turns < self._max_turns:
            turns += 1

            logger.info("Chat loop turn %d/%d", turns, self._max_turns)
            response = self._chat_model.send_message(content)

            # Check for function calls
            if not response.has_function_calls:
                # Model returned text-only — we're done
                logger.info(
                    "Chat loop complete after %d turns (%d function calls)",
                    turns,
                    len(all_results),
                )
                return ChatLoopResult(
                    text=response.text,
                    function_calls_made=all_results,
                    turns_used=turns,
                )

            # Dispatch function calls through bridge
            calls = extract_function_calls(response)
            logger.info(
                "Turn %d: dispatching %d function call(s): %s",
                turns,
                len(calls),
                [c.name for c in calls],
            )

            results = dispatch_function_calls(self._bridge, calls)
            all_results.extend(results)

            # Build function response content for next turn
            content = build_function_responses(results)

        # Max turns exhausted
        logger.warning(
            "Chat loop hit max turns (%d) with %d function calls",
            self._max_turns,
            len(all_results),
        )
        return ChatLoopResult(
            text=None,
            function_calls_made=all_results,
            turns_used=turns,
        )

    def send_raw(
        self,
        raw_response: dict[str, Any],
    ) -> tuple[list[BridgeResult], list[dict[str, Any]]]:
        """Dispatch function calls from a raw Firebase SDK response.

        Use this when you're managing the chat session externally
        (e.g., from TypeScript) and just need the Python bridge
        to process the function calls.

        Args:
            raw_response: Raw response dict from the Firebase SDK.

        Returns:
            Tuple of (bridge_results, function_response_parts).
        """
        calls = extract_function_calls_from_raw(raw_response)
        if not calls:
            return [], []

        results = dispatch_function_calls(self._bridge, calls)
        response_parts = build_function_responses(results)
        return results, response_parts
