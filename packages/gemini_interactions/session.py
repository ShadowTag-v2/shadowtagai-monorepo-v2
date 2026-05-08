# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ConversationSession — Auto-chaining conversation manager for Interactions API.

Implements the Google-recommended best practices for Interactions API:
  - Cache hit rate: Auto-chains via previous_interaction_id for implicit caching
  - Mixed interactions: Switch models mid-conversation (Agent → Model → Agent)
  - Stateful tracking: Maintains full interaction history for audit/replay

Reference: https://ai.google.dev/gemini-api/docs/interactions

Usage:
    client = InteractionsClient(api_key="...")
    session = ConversationSession(client, model="gemini-3-flash-preview")

    # Auto-chained turns — each uses the previous interaction ID
    r1 = session.send("What is quantum entanglement?")
    r2 = session.send("Explain it to a 5 year old.")  # auto-chains to r1

    # Mixed interactions: switch model mid-conversation
    r3 = session.send(
        "Summarize the above in JSON.",
        model="gemini-2.5-pro",  # different model, same chain
    )

    # Fork a branch for parallel exploration
    branch = session.fork(model="gemini-3-pro-preview")
    r4 = branch.send("What are practical applications?")

    # Session history
    print(session.history_ids)  # ['int-1', 'int-2', 'int-3']
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from typing import Any

from gemini_interactions.client import (
    InteractionsClient,
    InteractionResult,
    StreamEvent,
)

logger = logging.getLogger(__name__)


class ConversationSession:
    """Auto-chaining conversation manager.

    Wraps InteractionsClient to automatically pass ``previous_interaction_id``
    on each turn. This enables:

    1. **Implicit caching** — the server reuses conversation history,
       reducing latency and cost.
    2. **Mixed interactions** — switch between models or agents within
       a single conversation chain (e.g., Deep Research for data
       collection, then standard Gemini for summarization).
    3. **Branching** — fork the conversation at any point to explore
       alternatives without losing the main thread.

    Args:
        client: An initialized InteractionsClient.
        model: Default model for this session. Can be overridden per-turn.
        system_instruction: Default system instruction for all turns.
    """

    def __init__(
        self,
        client: InteractionsClient,
        *,
        model: str | None = None,
        system_instruction: str | None = None,
    ) -> None:
        self._client = client
        self._model = model
        self._system_instruction = system_instruction
        self._interaction_ids: list[str] = []

    @property
    def last_interaction_id(self) -> str | None:
        """The most recent interaction ID, or None if no turns yet."""
        return self._interaction_ids[-1] if self._interaction_ids else None

    @property
    def history_ids(self) -> list[str]:
        """All interaction IDs in chronological order."""
        return list(self._interaction_ids)

    @property
    def turn_count(self) -> int:
        """Number of completed turns."""
        return len(self._interaction_ids)

    def send(
        self,
        input: str | list[Any],
        *,
        model: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        system_instruction: str | None = None,
        generation_config: dict[str, Any] | None = None,
        response_format: dict[str, Any] | None = None,
        response_modalities: list[str] | None = None,
    ) -> InteractionResult:
        """Send a turn and auto-chain to the previous interaction.

        Always sets ``store=True`` to enable server-side caching and
        interaction retrieval. The ``previous_interaction_id`` is
        automatically set to the last interaction in this session.

        Args:
            input: Text string or content list.
            model: Override model for this turn (enables mixed interactions).
            tools: Tool definitions for this turn.
            system_instruction: Override system instruction for this turn.
            generation_config: Model configuration.
            response_format: JSON schema for structured output.
            response_modalities: Output modalities.

        Returns:
            InteractionResult with auto-updated session state.
        """
        result = self._client.create(
            input=input,
            model=model or self._model,
            previous_interaction_id=self.last_interaction_id,
            tools=tools,
            system_instruction=system_instruction or self._system_instruction,
            generation_config=generation_config,
            response_format=response_format,
            response_modalities=response_modalities,
            store=True,  # Required for caching + chaining
        )

        if result.id:
            self._interaction_ids.append(result.id)
            logger.debug(
                "Session turn %d: interaction_id=%s, model=%s",
                self.turn_count,
                result.id,
                model or self._model,
            )

        return result

    def stream_send(
        self,
        input: str | list[Any],
        *,
        model: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        system_instruction: str | None = None,
        generation_config: dict[str, Any] | None = None,
        thinking_summaries: str = "auto",
    ) -> Generator[StreamEvent]:
        """Stream a turn with auto-chaining.

        The interaction ID is captured from the ``interaction.created`` event
        and added to the session history. Use a ``StreamAccumulator`` to
        reconstruct steps.

        Args:
            input: Text string or content list.
            model: Override model for this turn.
            tools: Tool definitions.
            system_instruction: Override system instruction.
            generation_config: Model configuration.
            thinking_summaries: "auto" or "none".

        Yields:
            StreamEvent objects.
        """
        captured_id: str | None = None

        for event in self._client.stream(
            input=input,
            model=model or self._model,
            previous_interaction_id=self.last_interaction_id,
            tools=tools,
            system_instruction=system_instruction or self._system_instruction,
            generation_config=generation_config,
            thinking_summaries=thinking_summaries,
        ):
            # Capture interaction_id from the start event
            if event.interaction_id and not captured_id:
                captured_id = event.interaction_id
                self._interaction_ids.append(captured_id)
                logger.debug(
                    "Session stream turn %d: interaction_id=%s",
                    self.turn_count,
                    captured_id,
                )

            yield event

    def function_call_loop(
        self,
        *,
        input: str | list[Any],
        tools: list[dict[str, Any]],
        tool_handlers: dict[str, Any],
        model: str | None = None,
        system_instruction: str | None = None,
        generation_config: dict[str, Any] | None = None,
        max_rounds: int = 10,
    ) -> InteractionResult:
        """Auto-chained function call loop.

        Delegates to InteractionsClient.function_call_loop() but auto-chains
        to the previous interaction and tracks the final interaction ID.

        Args:
            input: Initial input.
            tools: Tool definitions.
            tool_handlers: Dict mapping function names to callables.
            model: Override model.
            system_instruction: Override system instruction.
            generation_config: Model config.
            max_rounds: Safety limit.

        Returns:
            Final InteractionResult after function calls resolve.
        """
        # Inject previous_interaction_id into the first create() call
        # by temporarily monkey-patching is not clean — instead, we
        # do the first create ourselves, then delegate the loop.
        first_result = self._client.create(
            input=input,
            model=model or self._model,
            previous_interaction_id=self.last_interaction_id,
            tools=tools,
            system_instruction=system_instruction or self._system_instruction,
            generation_config=generation_config,
            store=True,
        )

        if first_result.id:
            self._interaction_ids.append(first_result.id)

        # If no function calls, return immediately
        items = first_result.steps or first_result.outputs
        function_calls = [o for o in items if getattr(o, "type", None) == "function_call"]
        if not function_calls:
            return first_result

        # Continue the function call loop from the first result
        import json

        result = first_result
        for _round in range(max_rounds):
            items = result.steps or result.outputs
            fc_outputs = [o for o in items if getattr(o, "type", None) == "function_call"]
            if not fc_outputs:
                break

            function_results: list[dict[str, Any]] = []
            for fc in fc_outputs:
                fc_name = getattr(fc, "name", "")
                fc_id = getattr(fc, "id", "")
                handler = tool_handlers.get(fc_name)
                if handler:
                    try:
                        call_result = handler(**getattr(fc, "arguments", {}))
                    except Exception as exc:
                        logger.warning("Tool '%s' raised: %s", fc_name, exc)
                        call_result = f"Error executing {fc_name}: {exc}"
                else:
                    call_result = f"No handler registered for function '{fc_name}'"

                if isinstance(call_result, (str, list)):
                    serialized = call_result
                elif isinstance(call_result, dict):
                    serialized = json.dumps(call_result)
                else:
                    serialized = str(call_result)

                function_results.append(
                    {
                        "type": "function_result",
                        "name": fc_name,
                        "call_id": fc_id,
                        "result": serialized,
                    }
                )

            result = self._client.create(
                input=function_results,
                model=model or self._model,
                tools=tools,
                system_instruction=system_instruction or self._system_instruction,
                generation_config=generation_config,
                previous_interaction_id=result.id,
                store=True,
            )
            if result.id:
                self._interaction_ids.append(result.id)

        return result

    def fork(
        self,
        *,
        model: str | None = None,
        system_instruction: str | None = None,
    ) -> ConversationSession:
        """Fork the conversation at the current point.

        Creates a new ConversationSession that starts from the same
        ``previous_interaction_id`` as the current position. Turns
        in the fork do NOT affect the parent session.

        This enables the "mixing interactions" pattern: fork with
        a different model to explore alternatives.

        Args:
            model: Model for the forked session (defaults to parent's model).
            system_instruction: System instruction for the fork.

        Returns:
            A new ConversationSession branching from this point.
        """
        forked = ConversationSession(
            self._client,
            model=model or self._model,
            system_instruction=system_instruction or self._system_instruction,
        )
        # Copy the interaction history so fork starts from same position
        forked._interaction_ids = list(self._interaction_ids)
        return forked

    def reset(self) -> None:
        """Clear session history, starting a fresh conversation."""
        self._interaction_ids.clear()
