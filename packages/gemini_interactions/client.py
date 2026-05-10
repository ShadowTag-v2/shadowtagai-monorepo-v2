# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Gemini Interactions API Client — Live pair-programming transport.

Wraps google-genai SDK's `client.interactions` with:
  - Automatic retry/reconnection for streaming
  - Typed response wrappers (InteractionResult, StreamEvent)
  - Stateful conversation chaining via previous_interaction_id
  - Function call loop with automatic tool result submission
  - StreamAccumulator for index-based step/output reconstruction
  - Configuration validation before API calls

Usage:
    client = InteractionsClient(api_key="...")
    result = client.create(
        model="gemini-3-flash-preview",
        input="Explain quantum entanglement.",
    )
    print(result.text)

    # Streaming:
    for event in client.stream(
        model="gemini-3-flash-preview",
        input="Write a haiku.",
    ):
        if event.type == "text":
            print(event.text, end="", flush=True)

    # Streaming with output reconstruction:
    acc = StreamAccumulator()
    for event in client.stream(...):
        acc.feed(event)
    print(acc.steps)     # [{"type": "model_output", "content": [...]}]
    print(acc.outputs)   # legacy compat: [{"type": "text", "text": "..."}]
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from collections.abc import Generator

from .telemetry import NullTelemetry, TelemetryCallback, Timer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Typed wrappers
# ---------------------------------------------------------------------------


class EventType(StrEnum):
  """Stream event types from the Interactions API SSE.

  Supports both legacy (pre-May 2026) and new step-based schema.
  See: https://ai.google.dev/gemini-api/docs/interactions-breaking-changes-may-2026
  """

  # New schema (May 2026+)
  INTERACTION_CREATED = "interaction.created"
  INTERACTION_IN_PROGRESS = "interaction.in_progress"
  INTERACTION_REQUIRES_ACTION = "interaction.requires_action"
  STEP_START = "step.start"
  STEP_DELTA = "step.delta"
  STEP_STOP = "step.stop"
  INTERACTION_COMPLETED = "interaction.completed"
  INTERACTION_ERROR = "interaction.error"

  # Legacy aliases (removed after June 8, 2026)
  INTERACTION_START = "interaction.start"
  STATUS_UPDATE = "interaction.status_update"
  CONTENT_START = "content.start"
  CONTENT_DELTA = "content.delta"
  CONTENT_STOP = "content.stop"
  INTERACTION_COMPLETE = "interaction.complete"
  ERROR = "error"


# Map legacy event names → new event names for dual-schema support
_LEGACY_EVENT_MAP: dict[str, str] = {
  "interaction.start": "interaction.created",
  "content.start": "step.start",
  "content.delta": "step.delta",
  "content.stop": "step.stop",
  "interaction.complete": "interaction.completed",
  "error": "interaction.error",
  "interaction.status_update": "interaction.in_progress",
}


@dataclass
class StreamEvent:
  """A single streaming event from the Interactions API.

  Attributes:
      event_type: The SSE event type.
      event_id: Server-assigned event ID for reconnection.
      index: Content block index (for step.*/content.* events).
      delta_type: Type of delta (text, thought_summary, thought_signature, function_call, image).
      text: Text content (if delta_type == "text").
      thought: Thought summary text (if delta_type == "thought_summary").
      signature: Thought verification signature (if delta_type == "thought_signature").
      function_call: Function call data (if delta_type == "function_call").
      content_type: Step type from step.start (e.g., "model_output", "thought").
      interaction_id: Interaction ID (set on interaction.created).
      usage: Usage metadata (set on interaction.completed).
      raw: The raw chunk object from the SDK.
  """

  event_type: str
  event_id: str | None = None
  index: int | None = None
  delta_type: str | None = None
  text: str | None = None
  thought: str | None = None
  signature: str | None = None
  function_call: dict[str, Any] | None = None
  content_type: str | None = None
  interaction_id: str | None = None
  usage: dict[str, Any] | None = None
  raw: Any = None


@dataclass
class InteractionResult:
  """Typed wrapper around a completed Interactions API response.

  Supports both legacy (outputs) and new (steps) response schemas.

  Attributes:
      id: Server-assigned interaction ID.
      status: Completion status (completed, failed, cancelled).
      steps: List of step objects from the new schema response.
      outputs: Legacy list of output objects (populated from steps if needed).
      text: Convenience accessor for the last text output.
      function_calls: Convenience list of function_call steps/outputs.
      annotations: Inline citation annotations from text outputs.
      usage: Token usage metadata.
      raw: The raw interaction object from the SDK.
  """

  id: str
  status: str
  steps: list[Any] = field(default_factory=list)
  outputs: list[Any] = field(default_factory=list)
  text: str | None = None
  function_calls: list[Any] = field(default_factory=list)
  annotations: list[dict[str, Any]] = field(default_factory=list)
  usage: dict[str, Any] | None = None
  raw: Any = None

  @classmethod
  def from_interaction(cls, interaction: Any) -> InteractionResult:
    """Create from a raw SDK interaction object.

    Handles both legacy (outputs) and new (steps) schemas.
    """
    # New schema: steps array; legacy: outputs array
    steps = getattr(interaction, "steps", None) or []
    outputs = getattr(interaction, "outputs", None) or []
    use_steps = bool(steps)
    items = steps if use_steps else outputs

    text = None
    func_calls: list[Any] = []
    annotations: list[dict[str, Any]] = []

    for item in items:
      item_type = getattr(item, "type", None)

      if item_type == "function_call":
        func_calls.append(item)

      elif item_type == "model_output" and use_steps:
        # New schema: steps have content[] array
        content_list = getattr(item, "content", []) or []
        for content_item in content_list:
          if getattr(content_item, "type", None) == "text":
            text = getattr(content_item, "text", None)
            cls._extract_annotations(content_item, annotations)

      elif item_type == "text" and not use_steps:
        # Legacy schema: direct text output
        text = getattr(item, "text", None)
        cls._extract_annotations(item, annotations)

    usage_obj = getattr(interaction, "usage", None)
    usage_dict = None
    if usage_obj:
      usage_dict = {
        "total_tokens": getattr(usage_obj, "total_tokens", 0),
        "prompt_tokens": getattr(usage_obj, "prompt_tokens", 0),
        "completion_tokens": getattr(usage_obj, "completion_tokens", 0),
      }

    return cls(
      id=getattr(interaction, "id", ""),
      status=getattr(interaction, "status", "unknown"),
      steps=list(steps),
      outputs=list(outputs) if outputs else list(steps),
      text=text,
      function_calls=func_calls,
      annotations=annotations,
      usage=usage_dict,
      raw=interaction,
    )

  @staticmethod
  def _extract_annotations(item: Any, annotations: list[dict[str, Any]]) -> None:
    """Extract inline citation annotations from a content item."""
    item_annotations = getattr(item, "annotations", None)
    if not item_annotations:
      return
    for ann in item_annotations:
      if isinstance(ann, dict):
        annotations.append(ann)
      else:
        annotations.append(
          {
            "type": getattr(ann, "type", "unknown"),
            "file_name": getattr(ann, "file_name", None),
            "document_uri": getattr(ann, "document_uri", None),
            "source": getattr(ann, "source", None),
            "url": getattr(ann, "url", None),
            "title": getattr(ann, "title", None),
            "start_index": getattr(ann, "start_index", None),
            "end_index": getattr(ann, "end_index", None),
          }
        )


# ---------------------------------------------------------------------------
# StreamAccumulator — index-based output reconstruction
# ---------------------------------------------------------------------------


class StreamAccumulator:
  """Reconstruct steps from streaming step.start/delta/stop events.

  Supports both legacy (content.*) and new (step.*) event schemas.
  The interaction.completed event does NOT contain steps when streaming.
  Use this accumulator to collect deltas by index.

  Usage:
      acc = StreamAccumulator()
      for event in client.stream(...):
          acc.feed(event)
      print(acc.steps)     # [{"type": "model_output", "content": [...]}]
      print(acc.outputs)   # legacy compat alias
      print(acc.usage)     # {"total_tokens": 123}
  """

  def __init__(self) -> None:
    self._blocks: dict[int, dict[str, Any]] = {}
    self.interaction_id: str | None = None
    self.usage: dict[str, Any] | None = None
    self.status: str | None = None

  def feed(self, event: StreamEvent) -> None:
    """Process a single StreamEvent (supports both legacy and new schemas)."""
    # Normalize event type to new schema for uniform handling
    etype = _LEGACY_EVENT_MAP.get(event.event_type, event.event_type)

    if etype in (EventType.INTERACTION_CREATED, EventType.INTERACTION_START):
      if event.interaction_id:
        self.interaction_id = event.interaction_id

    elif etype in (EventType.STEP_START, EventType.CONTENT_START):
      idx = event.index if event.index is not None else 0
      self._blocks[idx] = {"type": event.content_type or "unknown"}

    elif etype in (EventType.STEP_DELTA, EventType.CONTENT_DELTA):
      idx = event.index if event.index is not None else 0
      block = self._blocks.setdefault(idx, {"type": "unknown"})

      if event.delta_type == "text":
        block["text"] = block.get("text", "") + (event.text or "")
      elif event.delta_type == "thought_summary":
        block["summary"] = block.get("summary", "") + (event.thought or "")
      elif event.delta_type == "thought_signature":
        block["signature"] = event.signature
      elif event.delta_type == "function_call":
        if event.function_call:
          block.update(event.function_call)
      elif event.delta_type == "arguments_delta":
        # New schema: streaming function call arguments
        block["arguments_json"] = block.get("arguments_json", "") + (
          getattr(event.raw, "arguments_delta", "") if event.raw else ""
        )

    elif etype in (EventType.INTERACTION_COMPLETED, EventType.INTERACTION_COMPLETE):
      if event.interaction_id:
        self.interaction_id = event.interaction_id
      self.usage = event.usage
      self.status = "completed"

  @property
  def steps(self) -> list[dict[str, Any]]:
    """Return reconstructed steps sorted by index."""
    return [self._blocks[i] for i in sorted(self._blocks)]

  @property
  def outputs(self) -> list[dict[str, Any]]:
    """Legacy compatibility alias for steps."""
    return self.steps


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

# Supported models for the Interactions API
SUPPORTED_MODELS = frozenset(
  {
    "gemini-3-flash-preview",
    "gemini-3-pro-preview",
    "gemini-3-pro-image-preview",
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-3.1-flash-tts-preview",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-computer-use-preview-10-2025",
  }
)

DEFAULT_MODEL = "gemini-3-flash-preview"
MAX_STREAM_RECONNECT_ATTEMPTS = 3
RECONNECT_BACKOFF_SECONDS = 2.0


class InteractionsClient:
  """Client for the Gemini Interactions API.

  Provides create(), get(), stream(), and function_call_loop() methods
  for interacting with Gemini models through the unified Interactions API.

  Args:
      api_key: Gemini API key. Falls back to GEMINI_API_KEY env var.
      default_model: Default model for requests.
      api_revision: Optional Api-Revision date string (e.g., '2026-05-20') to
          opt-in to the new step-based schema before the June 8, 2026 cutover.
          When set, the SDK sends the Api-Revision header and the API returns
          new-schema events (step.start/delta/stop instead of content.*).
          See: https://ai.google.dev/gemini-api/docs/interactions-breaking-changes-may-2026
  """

  # The Api-Revision date that triggers new step-based schema responses.
  # Set this to opt-in before June 8, 2026 mandatory cutover.
  NEW_SCHEMA_REVISION = "2026-05-20"

  def __init__(
    self,
    *,
    api_key: str | None = None,
    default_model: str = DEFAULT_MODEL,
    telemetry: TelemetryCallback | None = None,
    api_revision: str | None = None,
  ) -> None:
    self._api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
    self._default_model = default_model
    self._telemetry = telemetry or NullTelemetry()
    self._api_revision = api_revision
    self._client: Any | None = None  # Lazy init

  @property
  def client(self) -> Any:
    """Lazily initialize the google-genai Client."""
    if self._client is None:
      try:
        from google import genai

        kwargs: dict[str, Any] = {}
        if self._api_key:
          kwargs["api_key"] = self._api_key
        if self._api_revision:
          kwargs["http_options"] = {"headers": {"Api-Revision": self._api_revision}}
        self._client = genai.Client(**kwargs)
      except ImportError as exc:
        msg = "google-genai SDK not installed. Run: pip install google-genai>=1.47.0"
        raise ImportError(msg) from exc
    return self._client

  def create(
    self,
    *,
    input: str | list[Any],
    model: str | None = None,
    previous_interaction_id: str | None = None,
    tools: list[dict[str, Any]] | None = None,
    system_instruction: str | None = None,
    generation_config: dict[str, Any] | None = None,
    response_format: dict[str, Any] | None = None,
    response_modalities: list[str] | None = None,
    store: bool = True,
  ) -> InteractionResult:
    """Create a synchronous (non-streaming) interaction.

    Args:
        input: Text string or list of content objects.
        model: Model name. Defaults to self._default_model.
        previous_interaction_id: Chain to a prior interaction for stateful chat.
        tools: List of tool definitions (dicts).
        system_instruction: System prompt.
        generation_config: Model config (temperature, thinking_level, etc.).
        response_format: JSON schema for structured output.
        response_modalities: Output modalities (e.g., ["image", "text"]).
        store: Whether to store the interaction server-side (default True).

    Returns:
        InteractionResult with typed accessors.
    """
    kwargs = self._build_kwargs(
      input=input,
      model=model,
      previous_interaction_id=previous_interaction_id,
      tools=tools,
      system_instruction=system_instruction,
      generation_config=generation_config,
      response_format=response_format,
      response_modalities=response_modalities,
      store=store,
    )

    resolved_model = model or self._default_model
    self._telemetry.on_request_start(
      method="create",
      model=resolved_model,
      is_streaming=False,
      has_tools=bool(tools),
      previous_interaction_id=previous_interaction_id,
    )

    timer = Timer()
    with timer:
      try:
        interaction = self.client.interactions.create(**kwargs)
      except Exception as exc:
        self._telemetry.on_request_error(
          method="create",
          model=resolved_model,
          error=exc,
          latency_ms=timer.elapsed_ms,
        )
        raise

    result = InteractionResult.from_interaction(interaction)
    self._telemetry.on_request_complete(
      method="create",
      model=resolved_model,
      interaction_id=result.id,
      latency_ms=timer.elapsed_ms,
      usage=result.usage,
      status=result.status,
    )
    return result

  def get(
    self, interaction_id: str, *, include_input: bool = False
  ) -> InteractionResult:
    """Retrieve a previously created interaction.

    Args:
        interaction_id: The interaction ID to retrieve.
        include_input: Whether to include the original input.

    Returns:
        InteractionResult with typed accessors.
    """
    kwargs: dict[str, Any] = {}
    if include_input:
      kwargs["include_input"] = True

    self._telemetry.on_request_start(
      method="get",
      model=self._default_model,
      is_streaming=False,
      has_tools=False,
      previous_interaction_id=None,
    )

    timer = Timer()
    with timer:
      try:
        interaction = self.client.interactions.get(interaction_id, **kwargs)
      except Exception as exc:
        self._telemetry.on_request_error(
          method="get",
          model=self._default_model,
          error=exc,
          latency_ms=timer.elapsed_ms,
        )
        raise

    result = InteractionResult.from_interaction(interaction)
    self._telemetry.on_request_complete(
      method="get",
      model=self._default_model,
      interaction_id=result.id,
      latency_ms=timer.elapsed_ms,
      usage=result.usage,
      status=result.status,
    )
    return result

  def list(
    self,
    *,
    page_size: int = 20,
    page_token: str | None = None,
    filter: str | None = None,
  ) -> list[InteractionResult]:
    """List previous interactions.

    Args:
        page_size: Maximum number of interactions to return.
        page_token: Pagination token from a previous list call.
        filter: Optional filter string (e.g., "model=gemini-3-flash-preview").

    Returns:
        List of InteractionResult wrappers.
    """
    kwargs: dict[str, Any] = {"page_size": page_size}
    if page_token:
      kwargs["page_token"] = page_token
    if filter:
      kwargs["filter"] = filter

    response = self.client.interactions.list(**kwargs)
    results: list[InteractionResult] = []
    for interaction in getattr(response, "interactions", []):
      results.append(InteractionResult.from_interaction(interaction))
    return results

  def stream(
    self,
    *,
    input: str | list[Any],
    model: str | None = None,
    previous_interaction_id: str | None = None,
    tools: list[dict[str, Any]] | None = None,
    system_instruction: str | None = None,
    generation_config: dict[str, Any] | None = None,
    thinking_summaries: str = "auto",
  ) -> Generator[StreamEvent]:
    """Create a streaming interaction with automatic reconnection.

    Yields StreamEvent objects for each SSE event. Automatically reconnects
    if the connection drops (up to MAX_STREAM_RECONNECT_ATTEMPTS times).

    Args:
        input: Text string or content list.
        model: Model name.
        previous_interaction_id: Chain to prior interaction.
        tools: Tool definitions.
        system_instruction: System prompt.
        generation_config: Model config.
        thinking_summaries: "auto" to receive thought summaries, "none" to disable.

    Yields:
        StreamEvent objects.
    """
    gen_config = dict(generation_config or {})
    gen_config.setdefault("thinking_summaries", thinking_summaries)

    kwargs = self._build_kwargs(
      input=input,
      model=model,
      previous_interaction_id=previous_interaction_id,
      tools=tools,
      system_instruction=system_instruction,
      generation_config=gen_config,
      store=True,
    )
    kwargs["stream"] = True

    resolved_model = model or self._default_model
    self._telemetry.on_request_start(
      method="stream",
      model=resolved_model,
      is_streaming=True,
      has_tools=bool(tools),
      previous_interaction_id=previous_interaction_id,
    )

    interaction_id: str | None = None
    last_event_id: str | None = None
    is_complete = False
    usage_dict = None
    status_str = "completed"

    timer = Timer()
    timer.__enter__()
    try:
      for attempt in range(MAX_STREAM_RECONNECT_ATTEMPTS + 1):
        try:
          if attempt == 0:
            raw_stream = self.client.interactions.create(**kwargs)
          elif interaction_id:
            # Reconnection
            self._telemetry.on_stream_reconnect(
              attempt=attempt,
              max_attempts=MAX_STREAM_RECONNECT_ATTEMPTS,
              interaction_id=interaction_id,
              last_event_id=last_event_id,
            )
            reconnect_kwargs: dict[str, Any] = {"stream": True}
            if last_event_id:
              reconnect_kwargs["last_event_id"] = last_event_id
            raw_stream = self.client.interactions.get(
              interaction_id, **reconnect_kwargs
            )
          else:
            break

          for chunk in raw_stream:
            event = self._parse_chunk(chunk)

            if event.interaction_id:
              interaction_id = event.interaction_id
            if event.event_id:
              last_event_id = event.event_id

            yield event

            if event.event_type in (
              EventType.INTERACTION_COMPLETED,
              EventType.INTERACTION_COMPLETE,
            ):
              is_complete = True
              usage_dict = event.usage
              return
            elif event.event_type in (
              EventType.INTERACTION_ERROR,
              EventType.ERROR,
            ):
              is_complete = True
              status_str = "failed"
              return

          # Stream ended without completion — check status
          if interaction_id and not is_complete:
            status = self.client.interactions.get(interaction_id)
            if getattr(status, "status", "") != "in_progress":
              usage_obj = getattr(status, "usage", None)
              if usage_obj:
                usage_dict = {
                  "total_tokens": getattr(usage_obj, "total_tokens", 0),
                  "prompt_tokens": getattr(usage_obj, "prompt_tokens", 0),
                  "completion_tokens": getattr(usage_obj, "completion_tokens", 0),
                }
              return
          else:
            return

        except Exception:
          if attempt == MAX_STREAM_RECONNECT_ATTEMPTS:
            raise
          logger.warning(
            "Stream connection dropped (attempt %d/%d), reconnecting...",
            attempt + 1,
            MAX_STREAM_RECONNECT_ATTEMPTS,
          )
          time.sleep(RECONNECT_BACKOFF_SECONDS * (attempt + 1))
    except GeneratorExit:
      status_str = "cancelled"
      pass
    except Exception as exc:
      timer.__exit__(None, None, None)
      self._telemetry.on_request_error(
        method="stream",
        model=resolved_model,
        error=exc,
        latency_ms=timer.elapsed_ms,
      )
      raise
    finally:
      timer.__exit__(None, None, None)
      if interaction_id:
        self._telemetry.on_request_complete(
          method="stream",
          model=resolved_model,
          interaction_id=interaction_id,
          latency_ms=timer.elapsed_ms,
          usage=usage_dict,
          status=status_str if is_complete else "cancelled",
        )

  def function_call_loop(
    self,
    *,
    input: str | list[Any],
    model: str | None = None,
    tools: list[dict[str, Any]],
    tool_handlers: dict[str, Any],
    system_instruction: str | None = None,
    generation_config: dict[str, Any] | None = None,
    max_rounds: int = 10,
  ) -> InteractionResult:
    """Automatic function call loop with parallel function call support.

    Submits the initial request, then automatically executes any
    function_call outputs using the provided handlers, and submits
    ALL results back in a single input list. Supports both sequential
    and parallel function calls (multiple function_call outputs per turn).

    When a handler returns a dict, it is serialized with json.dumps().
    When a handler returns a list (for multimodal results like Computer Use),
    it is passed through directly as the result field.
    When a handler returns a string, it is passed through as-is.

    Args:
        input: Initial input.
        model: Model name.
        tools: Tool definitions.
        tool_handlers: Dict mapping function names to callables.
        system_instruction: System prompt.
        generation_config: Model config.
        max_rounds: Safety limit on function call rounds.

    Returns:
        Final InteractionResult after all function calls are resolved.
    """
    resolved_model = model or self._default_model

    self._telemetry.on_request_start(
      method="function_call_loop",
      model=resolved_model,
      is_streaming=False,
      has_tools=bool(tools),
      previous_interaction_id=None,
    )
    timer = Timer()
    timer.__enter__()

    try:
      result = self.create(
        input=input,
        model=model,
        tools=tools,
        system_instruction=system_instruction,
        generation_config=generation_config,
      )

      for _round in range(1, max_rounds + 1):
        items = result.steps or result.outputs
        function_calls = [
          o for o in items if getattr(o, "type", None) == "function_call"
        ]
        if not function_calls:
          break  # No more function calls — done

        self._telemetry.on_function_call_round(
          round_number=_round,
          function_names=[getattr(fc, "name", "") for fc in function_calls],
          interaction_id=result.id,
        )

        # Execute ALL function calls and collect results
        function_results: list[dict[str, Any]] = []
        for fc in function_calls:
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

          # Serialize result per API contract:
          # - str → pass through
          # - list → pass through (multimodal: [{type: text/image, ...}])
          # - dict → json.dumps()
          # - other → str()
          if isinstance(call_result, str):
            serialized = call_result
          elif isinstance(call_result, list):
            serialized = call_result  # Multimodal function_result
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

        # Submit ALL results back in a single input list
        result = self.create(
          input=function_results,
          model=model,
          tools=tools,
          system_instruction=system_instruction,
          generation_config=generation_config,
          previous_interaction_id=result.id,
        )
    except Exception as exc:
      timer.__exit__(None, None, None)
      self._telemetry.on_request_error(
        method="function_call_loop",
        model=resolved_model,
        error=exc,
        latency_ms=timer.elapsed_ms,
      )
      raise

    timer.__exit__(None, None, None)
    self._telemetry.on_request_complete(
      method="function_call_loop",
      model=resolved_model,
      interaction_id=result.id if result else "",
      latency_ms=timer.elapsed_ms,
      usage=result.usage if result else None,
      status=result.status if result else "failed",
    )

    return result

  # ---------------------------------------------------------------------------
  # Private helpers
  # ---------------------------------------------------------------------------

  def _build_kwargs(
    self,
    *,
    input: str | list[Any],
    model: str | None = None,
    previous_interaction_id: str | None = None,
    tools: list[dict[str, Any]] | None = None,
    system_instruction: str | None = None,
    generation_config: dict[str, Any] | None = None,
    response_format: dict[str, Any] | None = None,
    response_modalities: list[str] | None = None,
    store: bool = True,
  ) -> dict[str, Any]:
    """Build kwargs dict for client.interactions.create()."""
    kwargs: dict[str, Any] = {
      "model": model or self._default_model,
      "input": input,
    }

    if previous_interaction_id:
      kwargs["previous_interaction_id"] = previous_interaction_id
    if tools:
      kwargs["tools"] = tools
    if system_instruction:
      kwargs["system_instruction"] = system_instruction
    if generation_config:
      kwargs["generation_config"] = generation_config
    if response_format:
      kwargs["response_format"] = response_format
    if response_modalities:
      kwargs["response_modalities"] = response_modalities
    if store is not None:
      kwargs["store"] = store

    return kwargs

  @staticmethod
  def _parse_chunk(chunk: Any) -> StreamEvent:
    """Parse a raw SDK stream chunk into a typed StreamEvent.

    Handles both legacy and new (May 2026) SSE event types:
    Legacy: interaction.start, content.start/delta/stop, interaction.complete
    New:    interaction.created, step.start/delta/stop, interaction.completed
    """
    raw_type = getattr(chunk, "event_type", "unknown")
    event = StreamEvent(
      event_type=raw_type,
      event_id=getattr(chunk, "event_id", None),
      raw=chunk,
    )

    # Normalize to new schema for uniform parsing
    etype = _LEGACY_EVENT_MAP.get(raw_type, raw_type)

    if etype == EventType.INTERACTION_CREATED:
      interaction = getattr(chunk, "interaction", None)
      if interaction:
        event.interaction_id = getattr(interaction, "id", None)

    elif etype == EventType.STEP_START:
      event.index = getattr(chunk, "index", None)
      # New schema: step object; Legacy: content object
      step = getattr(chunk, "step", None) or getattr(chunk, "content", None)
      if step:
        event.content_type = getattr(step, "type", None)

    elif etype == EventType.STEP_DELTA:
      delta = getattr(chunk, "delta", None)
      if delta:
        event.delta_type = getattr(delta, "type", None)
        event.index = getattr(chunk, "index", None)

        if event.delta_type == "text":
          event.text = getattr(delta, "text", "")
        elif event.delta_type == "thought_summary":
          content = getattr(delta, "content", None)
          if content:
            event.thought = getattr(content, "text", "")
        elif event.delta_type == "thought_signature":
          event.signature = getattr(delta, "signature", None)
        elif event.delta_type == "function_call":
          event.function_call = {
            "id": getattr(delta, "id", ""),
            "name": getattr(delta, "name", ""),
            "arguments": getattr(delta, "arguments", {}),
          }

    elif etype == EventType.STEP_STOP:
      event.index = getattr(chunk, "index", None)

    elif etype == EventType.INTERACTION_COMPLETED:
      interaction = getattr(chunk, "interaction", None)
      if interaction:
        event.interaction_id = getattr(interaction, "id", None)
        usage = getattr(interaction, "usage", None)
        if usage:
          event.usage = {
            "total_tokens": getattr(usage, "total_tokens", 0),
            "prompt_tokens": getattr(usage, "prompt_tokens", 0),
            "completion_tokens": getattr(usage, "completion_tokens", 0),
          }

    return event
