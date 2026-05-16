"""Regression tests for antigravity_service parallel function calling.

Tests the critical invariant: len(FunctionResponse) == len(FunctionCall)
for every model turn, even when individual tools crash.

Reference: Gemini API 400 Bad Request when response/call count mismatch.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


# Wire the service module into sys.path
_SERVICE_DIR = str(
  Path(__file__).resolve().parent.parent
  / "apps"
  / "aiyou_stack"
  / "aiyou-fastapi-services"
)
if _SERVICE_DIR not in sys.path:
  sys.path.insert(0, _SERVICE_DIR)

import antigravity_service as svc


# ─── Helpers ─────────────────────────────────────────────────────────


def _make_fc_part(name: str, args: dict | None = None) -> dict:
  """Helper: create a FunctionCall part."""
  return {"functionCall": {"name": name, "args": args or {}}}


def _make_text_part(text: str) -> dict:
  """Helper: create a text part."""
  return {"text": text}


def _mock_dispatch(**overrides):
  """Create a patched TOOL_DISPATCH dict with mock tool functions.

  Since TOOL_DISPATCH captures function references at import time,
  we must patch the dict itself, not the module-level function names.
  """
  dispatch = dict(svc.TOOL_DISPATCH)  # copy original
  dispatch.update(overrides)
  return patch.dict(svc.TOOL_DISPATCH, dispatch, clear=True)


def _ok_fn(result="ok"):
  """Return a mock tool function that succeeds."""
  return MagicMock(return_value={"result": result})


def _crash_fn(exc):
  """Return a mock tool function that raises."""
  return MagicMock(side_effect=exc)


# ─── 1:1 Invariant Tests ────────────────────────────────────────────


class TestParallelCallInvariant:
  """Ensure the response count ALWAYS equals the call count."""

  def test_single_call_single_response(self):
    parts = [_make_fc_part("list_files_tool", {"path": "."})]
    with _mock_dispatch(list_files_tool=_ok_fn()):
      responses = svc.execute_function_calls(parts)
    assert len(responses) == 1
    assert responses[0]["functionResponse"]["name"] == "list_files_tool"

  def test_parallel_two_calls_two_responses(self):
    parts = [
      _make_fc_part("code_search_tool", {"query": "def main"}),
      _make_fc_part("list_files_tool", {"path": "/tmp"}),
    ]
    with _mock_dispatch(
      code_search_tool=_ok_fn("found"),
      list_files_tool=_ok_fn("files"),
    ):
      responses = svc.execute_function_calls(parts)
    assert len(responses) == 2
    assert responses[0]["functionResponse"]["name"] == "code_search_tool"
    assert responses[1]["functionResponse"]["name"] == "list_files_tool"

  def test_parallel_three_calls_three_responses(self):
    parts = [
      _make_fc_part("code_search_tool", {"query": "a"}),
      _make_fc_part("list_files_tool", {"path": "."}),
      _make_fc_part("code_search_tool", {"query": "b"}),
    ]
    with _mock_dispatch(
      code_search_tool=_ok_fn(),
      list_files_tool=_ok_fn(),
    ):
      responses = svc.execute_function_calls(parts)
    assert len(responses) == 3

  def test_no_function_calls_returns_empty(self):
    parts = [_make_text_part("Hello")]
    responses = svc.execute_function_calls(parts)
    assert responses == []

  def test_empty_parts_list(self):
    responses = svc.execute_function_calls([])
    assert responses == []


# ─── Crash Isolation Tests ──────────────────────────────────────────


class TestCrashIsolation:
  """Verify that one tool crashing never drops responses from the batch."""

  def test_first_tool_crashes_second_still_returns(self):
    parts = [
      _make_fc_part("code_search_tool", {"query": "crash"}),
      _make_fc_part("list_files_tool", {"path": "."}),
    ]
    with _mock_dispatch(
      code_search_tool=_crash_fn(RuntimeError("boom")),
      list_files_tool=_ok_fn(),
    ):
      responses = svc.execute_function_calls(parts)
    # CRITICAL: Both calls MUST produce a response
    assert len(responses) == 2
    # First should be an error response
    assert "error" in responses[0]["functionResponse"]["response"]
    assert "boom" in responses[0]["functionResponse"]["response"]["error"]
    # Second should succeed
    assert responses[1]["functionResponse"]["response"]["result"] == "ok"

  def test_second_tool_crashes_first_still_returns(self):
    parts = [
      _make_fc_part("list_files_tool", {"path": "."}),
      _make_fc_part("code_search_tool", {"query": "crash"}),
    ]
    with _mock_dispatch(
      list_files_tool=_ok_fn(),
      code_search_tool=_crash_fn(ValueError("segfault")),
    ):
      responses = svc.execute_function_calls(parts)
    assert len(responses) == 2
    assert responses[0]["functionResponse"]["response"]["result"] == "ok"
    assert "segfault" in responses[1]["functionResponse"]["response"]["error"]

  def test_all_tools_crash_still_returns_all_responses(self):
    parts = [
      _make_fc_part("code_search_tool", {"query": "a"}),
      _make_fc_part("list_files_tool", {"path": "."}),
    ]
    with _mock_dispatch(
      code_search_tool=_crash_fn(OSError("disk fail")),
      list_files_tool=_crash_fn(TimeoutError("timeout")),
    ):
      responses = svc.execute_function_calls(parts)
    assert len(responses) == 2
    assert "disk fail" in responses[0]["functionResponse"]["response"]["error"]
    assert "timeout" in responses[1]["functionResponse"]["response"]["error"]

  def test_exception_still_returns_error(self):
    """Even generic Exception should produce a response, not crash the loop."""
    parts = [
      _make_fc_part("code_search_tool", {"query": "x"}),
      _make_fc_part("list_files_tool", {"path": "."}),
    ]
    with _mock_dispatch(
      code_search_tool=_crash_fn(Exception("unexpected")),
      list_files_tool=_ok_fn(),
    ):
      responses = svc.execute_function_calls(parts)
    assert len(responses) == 2


# ─── Unknown Tool Tests ─────────────────────────────────────────────


class TestUnknownTool:
  """Unknown tools must return an error response, never skip."""

  def test_unknown_tool_returns_error_response(self):
    parts = [_make_fc_part("nonexistent_tool", {"x": 1})]
    responses = svc.execute_function_calls(parts)
    assert len(responses) == 1
    assert "Unknown tool" in responses[0]["functionResponse"]["response"]["error"]

  def test_mixed_known_and_unknown_tools(self):
    parts = [
      _make_fc_part("code_search_tool", {"query": "test"}),
      _make_fc_part("imaginary_tool", {"foo": "bar"}),
      _make_fc_part("list_files_tool", {"path": "."}),
    ]
    with _mock_dispatch(
      code_search_tool=_ok_fn(),
      list_files_tool=_ok_fn(),
    ):
      responses = svc.execute_function_calls(parts)
    assert len(responses) == 3
    assert "error" not in responses[0]["functionResponse"]["response"]
    assert "Unknown tool" in responses[1]["functionResponse"]["response"]["error"]
    assert "error" not in responses[2]["functionResponse"]["response"]


# ─── Mixed Parts Tests ──────────────────────────────────────────────


class TestMixedParts:
  """Model turns can contain BOTH text and functionCall parts."""

  def test_text_parts_are_ignored(self):
    parts = [
      _make_text_part("Let me search for that..."),
      _make_fc_part("code_search_tool", {"query": "main"}),
      _make_text_part("And also list files:"),
      _make_fc_part("list_files_tool", {"path": "."}),
    ]
    with _mock_dispatch(
      code_search_tool=_ok_fn(),
      list_files_tool=_ok_fn(),
    ):
      responses = svc.execute_function_calls(parts)
    assert len(responses) == 2  # Only 2 function calls, ignore 2 text parts

  def test_only_text_parts_returns_empty(self):
    parts = [_make_text_part("thinking..."), _make_text_part("done")]
    responses = svc.execute_function_calls(parts)
    assert responses == []


# ─── TOOL_DISPATCH Tests ────────────────────────────────────────────


class TestToolDispatch:
  """Verify the dispatch table routes correctly."""

  def test_dispatch_table_has_all_tools(self):
    assert "code_search_tool" in svc.TOOL_DISPATCH
    assert "list_files_tool" in svc.TOOL_DISPATCH

  def test_dispatch_table_functions_are_callable(self):
    for name, fn in svc.TOOL_DISPATCH.items():
      assert callable(fn), f"{name} is not callable"


# ─── Agent Loop Integration Tests ───────────────────────────────────


class TestAgentLoop:
  """Integration tests for run_agent_loop with mocked Gemini API."""

  def _mock_gemini_response(self, parts, finish_reason="STOP"):
    return {
      "candidates": [
        {
          "content": {"role": "model", "parts": parts},
          "finishReason": finish_reason,
        }
      ]
    }

  def test_final_text_answer_returned(self):
    text_resp = self._mock_gemini_response([{"text": "The answer is 42."}])
    with patch.object(svc, "call_gemini_turn", return_value=text_resp):
      result = svc.run_agent_loop("models/test", "What is 42?")
    assert result == "The answer is 42."

  def test_tool_call_then_final_answer(self):
    """Model calls a tool first, then gives a text answer."""
    tool_resp = self._mock_gemini_response(
      [_make_fc_part("list_files_tool", {"path": "."})]
    )
    final_resp = self._mock_gemini_response([{"text": "Found 3 files."}])

    call_count = 0

    def mock_turn(model, history, tools=None):
      nonlocal call_count
      call_count += 1
      if call_count == 1:
        return tool_resp
      return final_resp

    with (
      patch.object(svc, "call_gemini_turn", side_effect=mock_turn),
      _mock_dispatch(list_files_tool=_ok_fn("a.py\nb.py")),
    ):
      result = svc.run_agent_loop("models/test", "List files")
    assert result == "Found 3 files."
    assert call_count == 2

  def test_parallel_tool_calls_then_final_answer(self):
    """Model calls TWO tools in parallel, then gives a text answer."""
    parallel_resp = self._mock_gemini_response(
      [
        _make_fc_part("code_search_tool", {"query": "import"}),
        _make_fc_part("list_files_tool", {"path": "."}),
      ]
    )
    final_resp = self._mock_gemini_response([{"text": "All done."}])

    call_count = 0

    def mock_turn(model, history, tools=None):
      nonlocal call_count
      call_count += 1
      if call_count == 1:
        return parallel_resp
      # Verify the function turn has EXACTLY 2 responses
      func_turn = history[-1]
      assert func_turn["role"] == "function"
      assert len(func_turn["parts"]) == 2
      return final_resp

    with (
      patch.object(svc, "call_gemini_turn", side_effect=mock_turn),
      _mock_dispatch(
        code_search_tool=_ok_fn("found"),
        list_files_tool=_ok_fn("files"),
      ),
    ):
      result = svc.run_agent_loop("models/test", "Search and list")
    assert result == "All done."

  def test_max_turns_reached(self):
    """If the model keeps calling tools, we stop after max_turns."""
    loop_resp = self._mock_gemini_response(
      [_make_fc_part("list_files_tool", {"path": "."})]
    )

    with (
      patch.object(svc, "call_gemini_turn", return_value=loop_resp),
      _mock_dispatch(list_files_tool=_ok_fn()),
    ):
      result = svc.run_agent_loop("models/test", "Loop forever")
    assert "Max turns" in result

  def test_api_error_returns_error_string(self):
    with patch.object(
      svc, "call_gemini_turn", side_effect=ConnectionError("network down")
    ):
      result = svc.run_agent_loop("models/test", "Broken")
    assert "API Error" in result

  def test_no_candidates_returns_error(self):
    with patch.object(svc, "call_gemini_turn", return_value={"candidates": []}):
      result = svc.run_agent_loop("models/test", "Empty")
    assert "No candidates" in result

  def test_tool_crash_mid_parallel_preserves_history(self):
    """One tool crashing in a parallel batch must NOT corrupt conversation history."""
    parallel_resp = self._mock_gemini_response(
      [
        _make_fc_part("code_search_tool", {"query": "crash_me"}),
        _make_fc_part("list_files_tool", {"path": "."}),
      ]
    )
    final_resp = self._mock_gemini_response([{"text": "Recovered."}])

    call_count = 0

    def mock_turn(model, history, tools=None):
      nonlocal call_count
      call_count += 1
      if call_count == 1:
        return parallel_resp
      # Verify function turn has 2 responses despite crash
      func_turn = history[-1]
      assert func_turn["role"] == "function"
      assert len(func_turn["parts"]) == 2
      # First response should be an error
      assert "error" in func_turn["parts"][0]["functionResponse"]["response"]
      return final_resp

    with (
      patch.object(svc, "call_gemini_turn", side_effect=mock_turn),
      _mock_dispatch(
        code_search_tool=_crash_fn(RuntimeError("segfault")),
        list_files_tool=_ok_fn(),
      ),
    ):
      result = svc.run_agent_loop("models/test", "Crash test")
    assert result == "Recovered."


# ─── Model Picker Tests ─────────────────────────────────────────────


class TestPickModel:
  def test_defaults_to_flash_lite(self):
    assert "flash-lite" in svc.pick_model("FREE")

  def test_pro_tier(self):
    assert "flash-lite" in svc.pick_model("PRO")

  def test_none_tier(self):
    assert "flash-lite" in svc.pick_model(None)
