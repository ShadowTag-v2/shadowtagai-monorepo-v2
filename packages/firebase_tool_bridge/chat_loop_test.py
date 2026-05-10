# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Tests for firebase_chat_loop.py — multi-turn function-calling dispatch."""

from __future__ import annotations

from typing import Any


from firebase_tool_bridge.bridge import CallStatus, ToolBridge
from firebase_tool_bridge.evidence import EvidenceLogger
from firebase_tool_bridge.firebase_chat_loop import (
  ChatLoopResult,
  FirebaseChatLoop,
  FunctionCallPart,
  ModelResponse,
  build_function_responses,
  dispatch_function_calls,
  extract_function_calls_from_raw,
)
from firebase_tool_bridge.registry import FunctionRegistry, RiskTier


# ── Mock fixtures ──────────────────────────────────────────────


def mock_get_weather(city: str, unit: str = "celsius") -> dict:
  """Mock weather function."""
  return {"city": city, "temp": 22, "unit": unit}


def mock_get_time(timezone: str = "UTC") -> dict:
  """Mock time function."""
  return {"timezone": timezone, "time": "14:30"}


class MockChatModel:
  """Mock chat model that returns scripted responses.

  Simulates the multi-turn pattern:
  Turn 1: User sends text → Model returns function calls
  Turn 2: User sends function responses → Model returns text
  """

  def __init__(self, responses: list[ModelResponse]) -> None:
    self._responses = list(responses)
    self._call_count = 0
    self.messages_received: list[list[dict[str, Any]]] = []

  def send_message(self, content: list[dict[str, Any]]) -> ModelResponse:
    self.messages_received.append(content)
    if self._call_count < len(self._responses):
      response = self._responses[self._call_count]
      self._call_count += 1
      return response
    return ModelResponse(text="No more responses configured")


def _make_bridge(tmp_path) -> tuple[ToolBridge, FunctionRegistry]:
  """Create a bridge with mock weather and time functions."""
  registry = FunctionRegistry()
  registry.register(
    "get_weather",
    mock_get_weather,
    RiskTier.LOW,
    description="Get weather for a city",
  )
  registry.register(
    "get_time",
    mock_get_time,
    RiskTier.LOW,
    description="Get current time",
  )
  evidence = EvidenceLogger(repo_root=tmp_path)
  bridge = ToolBridge(registry, evidence=evidence)
  return bridge, registry


# ── FunctionCallPart tests ─────────────────────────────────────


class TestFunctionCallPart:
  """Tests for FunctionCallPart dataclass."""

  def test_basic_creation(self) -> None:
    part = FunctionCallPart(name="get_weather", args={"city": "Boston"})
    assert part.name == "get_weather"
    assert part.args == {"city": "Boston"}

  def test_default_args(self) -> None:
    part = FunctionCallPart(name="no_params")
    assert part.args == {}


# ── ModelResponse tests ────────────────────────────────────────


class TestModelResponse:
  """Tests for ModelResponse dataclass."""

  def test_text_only(self) -> None:
    resp = ModelResponse(text="Hello world")
    assert not resp.has_function_calls
    assert resp.text == "Hello world"

  def test_function_calls_only(self) -> None:
    resp = ModelResponse(function_calls=[FunctionCallPart(name="fn", args={})])
    assert resp.has_function_calls
    assert resp.text is None

  def test_mixed(self) -> None:
    resp = ModelResponse(
      text="I'll check the weather",
      function_calls=[FunctionCallPart(name="get_weather", args={"city": "NYC"})],
    )
    assert resp.has_function_calls
    assert resp.text == "I'll check the weather"


# ── extract_function_calls_from_raw tests ──────────────────────


class TestExtractFromRaw:
  """Tests for extract_function_calls_from_raw()."""

  def test_single_function_call(self) -> None:
    raw = {
      "candidates": [
        {
          "content": {
            "parts": [
              {
                "functionCall": {
                  "name": "get_weather",
                  "args": {"city": "Boston"},
                }
              }
            ]
          }
        }
      ]
    }
    calls = extract_function_calls_from_raw(raw)
    assert len(calls) == 1
    assert calls[0].name == "get_weather"
    assert calls[0].args == {"city": "Boston"}

  def test_multiple_function_calls(self) -> None:
    raw = {
      "candidates": [
        {
          "content": {
            "parts": [
              {"functionCall": {"name": "get_weather", "args": {"city": "Boston"}}},
              {"functionCall": {"name": "get_time", "args": {"timezone": "EST"}}},
            ]
          }
        }
      ]
    }
    calls = extract_function_calls_from_raw(raw)
    assert len(calls) == 2
    assert calls[0].name == "get_weather"
    assert calls[1].name == "get_time"

  def test_no_function_calls(self) -> None:
    raw = {"candidates": [{"content": {"parts": [{"text": "Hello!"}]}}]}
    calls = extract_function_calls_from_raw(raw)
    assert calls == []

  def test_empty_response(self) -> None:
    calls = extract_function_calls_from_raw({})
    assert calls == []

  def test_missing_args(self) -> None:
    raw = {
      "candidates": [{"content": {"parts": [{"functionCall": {"name": "no_params"}}]}}]
    }
    calls = extract_function_calls_from_raw(raw)
    assert len(calls) == 1
    assert calls[0].args == {}


# ── build_function_responses tests ─────────────────────────────


class TestBuildFunctionResponses:
  """Tests for build_function_responses()."""

  def test_success_response(self, tmp_path) -> None:
    bridge, _ = _make_bridge(tmp_path)
    result = bridge.handle("get_weather", {"city": "Boston"})

    responses = build_function_responses([result])
    assert len(responses) == 1
    resp = responses[0]
    assert "functionResponse" in resp
    assert resp["functionResponse"]["name"] == "get_weather"
    assert "result" in resp["functionResponse"]["response"]

  def test_error_response(self, tmp_path) -> None:
    bridge, _ = _make_bridge(tmp_path)
    result = bridge.handle("nonexistent_fn", {})

    responses = build_function_responses([result])
    assert len(responses) == 1
    resp = responses[0]
    assert "functionResponse" in resp
    assert "error" in resp["functionResponse"]["response"]


# ── dispatch_function_calls tests ──────────────────────────────


class TestDispatchFunctionCalls:
  """Tests for dispatch_function_calls()."""

  def test_single_dispatch(self, tmp_path) -> None:
    bridge, _ = _make_bridge(tmp_path)
    calls = [FunctionCallPart(name="get_weather", args={"city": "London"})]

    results = dispatch_function_calls(bridge, calls)
    assert len(results) == 1
    assert results[0].status == CallStatus.SUCCESS
    assert results[0].result["city"] == "London"

  def test_parallel_dispatch(self, tmp_path) -> None:
    bridge, _ = _make_bridge(tmp_path)
    calls = [
      FunctionCallPart(name="get_weather", args={"city": "NYC"}),
      FunctionCallPart(name="get_time", args={"timezone": "EST"}),
    ]

    results = dispatch_function_calls(bridge, calls)
    assert len(results) == 2
    assert all(r.status == CallStatus.SUCCESS for r in results)

  def test_unregistered_rejection(self, tmp_path) -> None:
    bridge, _ = _make_bridge(tmp_path)
    calls = [FunctionCallPart(name="hack_system", args={})]

    results = dispatch_function_calls(bridge, calls)
    assert len(results) == 1
    assert results[0].status == CallStatus.REJECTED_UNREGISTERED


# ── FirebaseChatLoop tests ─────────────────────────────────────


class TestFirebaseChatLoop:
  """Tests for FirebaseChatLoop.send()."""

  def test_text_only_response(self, tmp_path) -> None:
    """Model responds with text immediately (no function calls)."""
    bridge, _ = _make_bridge(tmp_path)
    chat_model = MockChatModel(
      [
        ModelResponse(text="The weather is great today!"),
      ]
    )
    loop = FirebaseChatLoop(bridge, chat_model)

    result = loop.send("What's the weather?")
    assert result.text == "The weather is great today!"
    assert result.total_calls == 0
    assert result.turns_used == 1

  def test_single_turn_function_call(self, tmp_path) -> None:
    """Model calls a function, then responds with text."""
    bridge, _ = _make_bridge(tmp_path)
    chat_model = MockChatModel(
      [
        # Turn 1: Model requests function call
        ModelResponse(
          function_calls=[
            FunctionCallPart(name="get_weather", args={"city": "Boston"}),
          ]
        ),
        # Turn 2: Model responds with text after receiving function result
        ModelResponse(text="It's 22°C in Boston."),
      ]
    )
    loop = FirebaseChatLoop(bridge, chat_model)

    result = loop.send("What's the weather in Boston?")
    assert result.text == "It's 22°C in Boston."
    assert result.total_calls == 1
    assert result.turns_used == 2
    assert result.all_succeeded

    # Verify function response was sent back to model
    assert len(chat_model.messages_received) == 2
    # Second message should be functionResponse
    second_msg = chat_model.messages_received[1]
    assert any("functionResponse" in part for part in second_msg)

  def test_parallel_function_calls(self, tmp_path) -> None:
    """Model calls multiple functions in one response."""
    bridge, _ = _make_bridge(tmp_path)
    chat_model = MockChatModel(
      [
        ModelResponse(
          function_calls=[
            FunctionCallPart(name="get_weather", args={"city": "NYC"}),
            FunctionCallPart(name="get_time", args={"timezone": "EST"}),
          ]
        ),
        ModelResponse(text="NYC is 22°C and the time is 14:30 EST."),
      ]
    )
    loop = FirebaseChatLoop(bridge, chat_model)

    result = loop.send("Weather and time in NYC?")
    assert result.total_calls == 2
    assert result.all_succeeded
    assert result.text == "NYC is 22°C and the time is 14:30 EST."

  def test_multi_turn_function_calls(self, tmp_path) -> None:
    """Model calls functions across multiple turns."""
    bridge, _ = _make_bridge(tmp_path)
    chat_model = MockChatModel(
      [
        # Turn 1: weather call
        ModelResponse(
          function_calls=[
            FunctionCallPart(name="get_weather", args={"city": "Boston"}),
          ]
        ),
        # Turn 2: time call
        ModelResponse(
          function_calls=[
            FunctionCallPart(name="get_time", args={"timezone": "EST"}),
          ]
        ),
        # Turn 3: final text
        ModelResponse(text="Boston: 22°C, 14:30 EST"),
      ]
    )
    loop = FirebaseChatLoop(bridge, chat_model)

    result = loop.send("Weather and time in Boston?")
    assert result.total_calls == 2
    assert result.turns_used == 3
    assert result.text == "Boston: 22°C, 14:30 EST"

  def test_max_turns_limit(self, tmp_path) -> None:
    """Chat loop respects max_turns to prevent infinite loops."""
    bridge, _ = _make_bridge(tmp_path)
    # Model always requests function calls (infinite loop scenario)
    infinite_calls = [
      ModelResponse(
        function_calls=[
          FunctionCallPart(name="get_weather", args={"city": "Boston"}),
        ]
      )
      for _ in range(20)
    ]
    chat_model = MockChatModel(infinite_calls)
    loop = FirebaseChatLoop(bridge, chat_model, max_turns=3)

    result = loop.send("Loop forever?")
    assert result.text is None  # Never got final text
    assert result.turns_used == 3
    assert result.total_calls == 3

  def test_unregistered_function_in_loop(self, tmp_path) -> None:
    """Model requests an unregistered function."""
    bridge, _ = _make_bridge(tmp_path)
    chat_model = MockChatModel(
      [
        ModelResponse(
          function_calls=[
            FunctionCallPart(name="delete_everything", args={}),
          ]
        ),
        ModelResponse(text="Sorry, I couldn't do that."),
      ]
    )
    loop = FirebaseChatLoop(bridge, chat_model)

    result = loop.send("Delete everything")
    assert result.total_calls == 1
    assert not result.all_succeeded
    assert result.function_calls_made[0].status == CallStatus.REJECTED_UNREGISTERED


# ── send_raw tests ─────────────────────────────────────────────


class TestSendRaw:
  """Tests for FirebaseChatLoop.send_raw()."""

  def test_raw_dispatch(self, tmp_path) -> None:
    bridge, _ = _make_bridge(tmp_path)
    chat_model = MockChatModel([])  # Not used in send_raw
    loop = FirebaseChatLoop(bridge, chat_model)

    raw_response = {
      "candidates": [
        {
          "content": {
            "parts": [
              {
                "functionCall": {
                  "name": "get_weather",
                  "args": {"city": "London"},
                }
              }
            ]
          }
        }
      ]
    }

    results, response_parts = loop.send_raw(raw_response)
    assert len(results) == 1
    assert results[0].status == CallStatus.SUCCESS
    assert len(response_parts) == 1
    assert response_parts[0]["functionResponse"]["name"] == "get_weather"

  def test_raw_no_function_calls(self, tmp_path) -> None:
    bridge, _ = _make_bridge(tmp_path)
    chat_model = MockChatModel([])
    loop = FirebaseChatLoop(bridge, chat_model)

    raw_response = {"candidates": [{"content": {"parts": [{"text": "Hello!"}]}}]}

    results, response_parts = loop.send_raw(raw_response)
    assert results == []
    assert response_parts == []


# ── ChatLoopResult tests ───────────────────────────────────────


class TestChatLoopResult:
  """Tests for ChatLoopResult properties."""

  def test_empty_result(self) -> None:
    result = ChatLoopResult(text="Hello", turns_used=1)
    assert result.total_calls == 0
    assert result.all_succeeded

  def test_mixed_results(self, tmp_path) -> None:
    bridge, _ = _make_bridge(tmp_path)
    success = bridge.handle("get_weather", {"city": "NYC"})
    failure = bridge.handle("nonexistent", {})

    result = ChatLoopResult(
      text="Done",
      function_calls_made=[success, failure],
      turns_used=2,
    )
    assert result.total_calls == 2
    assert not result.all_succeeded
