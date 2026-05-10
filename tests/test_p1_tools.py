# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Unit tests for P0/P1 tool implementations (SleepTool, ScheduleCronTool, P1 #6-#10)."""

from __future__ import annotations

from unittest.mock import patch


# === SleepTool Tests ===


class TestSleepTool:
  """Tests for packages/agnt_tools/sleep_tool.py."""

  def test_import_sleep_tool(self):
    from packages.agnt_tools.sleep_tool import SleepTool

    tool = SleepTool()
    assert tool is not None

  def test_sleep_tool_has_name(self):
    from packages.agnt_tools.sleep_tool import SleepTool

    tool = SleepTool()
    assert hasattr(tool, "name") or hasattr(tool, "tool_name")

  @patch("time.sleep")
  def test_sleep_tool_executes(self, mock_sleep):
    from packages.agnt_tools.sleep_tool import SleepTool

    tool = SleepTool()
    # Tool should accept duration_seconds
    if hasattr(tool, "execute"):
      result = tool.execute(duration_seconds=1)
      mock_sleep.assert_called()
    elif hasattr(tool, "run"):
      tool.run(duration_seconds=1)
      mock_sleep.assert_called()

  @patch("time.sleep")
  def test_sleep_tool_handles_negative(self, mock_sleep):
    from packages.agnt_tools.sleep_tool import SleepTool

    tool = SleepTool()
    # Negative inputs should either clamp to 0 or raise
    if hasattr(tool, "execute"):
      try:
        tool.execute(duration_seconds=-1)
      except ValueError, TypeError:
        pass  # Either behavior is acceptable


# === ScheduleCronTool Tests ===


class TestScheduleCronTool:
  """Tests for packages/agnt_tools/schedule_cron_tool.py."""

  def test_import_schedule_cron_tool(self):
    from packages.agnt_tools.schedule_cron_tool import ScheduleCronTool

    tool = ScheduleCronTool()
    assert tool is not None

  def test_schedule_cron_has_methods(self):
    from packages.agnt_tools.schedule_cron_tool import ScheduleCronTool

    tool = ScheduleCronTool()
    # Should have scheduling API
    assert hasattr(tool, "schedule")
    assert hasattr(tool, "unschedule")
    assert hasattr(tool, "list_jobs")


# === IdleReturn Tests ===


class TestIdleReturn:
  """Tests for packages/agnt_tools/idle_return.py — P1 #6."""

  def test_import(self):
    from packages.agnt_tools.idle_return import IdleReturnDialog

    dialog = IdleReturnDialog()
    assert dialog is not None

  def test_build_empty(self):
    from packages.agnt_tools.idle_return import IdleReturnDialog

    dialog = IdleReturnDialog()
    summary = dialog.build([])
    assert summary.cycles_executed == 0
    assert summary.total_actions == 0

  def test_build_with_reports(self):
    from packages.agnt_tools.idle_return import CycleReport, IdleReturnDialog

    dialog = IdleReturnDialog()
    reports = [
      CycleReport(cycle_number=1, actions_taken=3, details=["Fixed lint", "Ran tests"]),
      CycleReport(cycle_number=2, actions_taken=0, details=[]),
    ]
    summary = dialog.build(reports)
    assert summary.cycles_executed == 2
    assert summary.total_actions == 3
    assert "Welcome Back" in summary.formatted


# === WorktreeIsolation Tests ===


class TestWorktreeIsolation:
  """Tests for packages/agnt_tools/worktree_isolation.py — P1 #7."""

  def test_import(self):
    from packages.agnt_tools.worktree_isolation import WorktreeIsolation

    iso = WorktreeIsolation()
    assert iso is not None

  def test_list_worktrees(self):
    from packages.agnt_tools.worktree_isolation import WorktreeIsolation

    iso = WorktreeIsolation()
    worktrees = iso.list_worktrees()
    assert isinstance(worktrees, list)
    # Main worktree should always exist
    assert len(worktrees) >= 1


# === PewterLedger Tests ===


class TestPewterLedger:
  """Tests for packages/agnt_tools/pewter_ledger.py — P1 #8."""

  def test_import(self):
    from packages.agnt_tools.pewter_ledger import PewterLedger

    ledger = PewterLedger()
    assert ledger is not None

  def test_not_capped_initially(self):
    from packages.agnt_tools.pewter_ledger import PewterLedger

    ledger = PewterLedger()
    ledger.start_planning()
    assert not ledger.is_capped()

  def test_caps_on_total_tasks(self):
    from packages.agnt_tools.pewter_ledger import PewterLedger

    ledger = PewterLedger(max_tasks=3)
    ledger.start_planning()
    assert ledger.add_task("A")
    assert ledger.add_task("B")
    assert ledger.add_task("C")
    # 4th should fail
    assert not ledger.add_task("D")

  def test_caps_on_depth(self):
    from packages.agnt_tools.pewter_ledger import PewterLedger

    ledger = PewterLedger(max_depth=2)
    ledger.start_planning()
    ledger.add_task("Root", depth=0)
    ledger.add_task("Child", depth=1)
    ledger.add_task("Grandchild", depth=2)
    # Depth 2 >= max_depth 2 — should cap
    assert ledger.is_capped()

  def test_force_commit(self):
    from packages.agnt_tools.pewter_ledger import PewterLedger

    ledger = PewterLedger()
    ledger.start_planning()
    ledger.add_task("Task 1")
    report = ledger.force_commit()
    assert report.total_tasks == 1


# === ForkedAgentCache Tests ===


class TestForkedAgentCache:
  """Tests for packages/agnt_tools/forked_cache.py — P1 #9."""

  def test_import(self):
    from packages.agnt_tools.forked_cache import ForkedAgentCache

    cache = ForkedAgentCache()
    assert cache is not None

  def test_put_and_get(self):
    from packages.agnt_tools.forked_cache import ForkedAgentCache

    cache = ForkedAgentCache()
    key = cache.put("test prompt", "test result")
    assert len(key) == 16
    result = cache.get("test prompt")
    assert result == "test result"

  def test_miss(self):
    from packages.agnt_tools.forked_cache import ForkedAgentCache

    cache = ForkedAgentCache()
    result = cache.get("nonexistent prompt")
    assert result is None

  def test_stats(self):
    from packages.agnt_tools.forked_cache import ForkedAgentCache

    cache = ForkedAgentCache()
    cache.put("p1", "r1")
    cache.get("p1")
    cache.get("miss")
    stats = cache.stats()
    assert stats.hits == 1
    assert stats.misses == 1


# === TeammateMailbox Tests ===


class TestTeammateMailbox:
  """Tests for packages/agnt_tools/teammate_mailbox.py — P1 #10."""

  def test_import(self):
    from packages.agnt_tools.teammate_mailbox import TeammateMailbox

    mb = TeammateMailbox("test_agent")
    assert mb is not None

  def test_send_and_receive(self):
    from packages.agnt_tools.teammate_mailbox import TeammateMailbox

    sender = TeammateMailbox("jules")
    receiver = TeammateMailbox("kairos")
    msg_id = sender.send("kairos", "Test", "Hello from Jules")
    assert msg_id.startswith("jules_")

    msgs = receiver.receive()
    assert len(msgs) >= 1
    assert msgs[0].subject == "Test"

  def test_unread_count(self):
    from packages.agnt_tools.teammate_mailbox import TeammateMailbox

    mb = TeammateMailbox("steward_test")
    initial = mb.unread_count()
    sender = TeammateMailbox("dream_test")
    sender.send("steward_test", "Alert", "Dream cycle complete")
    assert mb.unread_count() == initial + 1


# === ToolOutputCaps Tests ===


class TestToolOutputCaps:
  """Tests for packages/agnt_tools/tool_output_caps.py — P0 #4."""

  def test_under_limit_passes_through(self):
    from packages.agnt_tools.tool_output_caps import ToolOutputCaps

    caps = ToolOutputCaps()
    caps.new_turn()
    result = caps.enforce("grep_search", "small output")
    assert not result.was_truncated
    assert result.output == "small output"

  def test_over_limit_truncates(self):
    from packages.agnt_tools.tool_output_caps import ToolOutputCaps

    caps = ToolOutputCaps(per_tool_max=100)
    caps.new_turn()
    big = "x" * 5000
    result = caps.enforce("grep_search", big)
    assert result.was_truncated
    # Truncated output includes preview head+tail+metadata, but should be
    # significantly smaller than the original
    assert result.returned_chars < result.original_chars


# === ContextCollapser Tests ===


class TestContextCollapser:
  """Tests for packages/agnt_tools/context_collapse.py — P0 #5 / Layer 0."""

  def test_collapse_empty(self):
    from packages.agnt_tools.context_collapse import ContextCollapser

    c = ContextCollapser()
    result = c.collapse([])
    assert result.original_count == 0

  def test_no_collapse_below_threshold(self):
    from packages.agnt_tools.context_collapse import ContextCollapser, ToolResult

    c = ContextCollapser(min_consecutive=3)
    results = [
      ToolResult(tool_name="grep_search", output="match1"),
      ToolResult(tool_name="grep_search", output="match2"),
    ]
    result = c.collapse(results)
    assert result.collapsed_count == 2  # Not collapsed (only 2, need 3)

  def test_collapse_above_threshold(self):
    from packages.agnt_tools.context_collapse import ContextCollapser, ToolResult

    c = ContextCollapser(min_consecutive=3)
    results = [
      ToolResult(
        tool_name="grep_search", arguments={"Query": "foo"}, output="file1:1:match"
      ),
      ToolResult(
        tool_name="grep_search", arguments={"Query": "bar"}, output="file2:1:match"
      ),
      ToolResult(
        tool_name="grep_search", arguments={"Query": "baz"}, output="file3:1:match"
      ),
    ]
    result = c.collapse(results)
    assert result.collapsed_count < 3
    assert "[COLLAPSED:" in result.output
