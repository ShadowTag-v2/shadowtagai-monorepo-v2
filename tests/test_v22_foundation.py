# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for v2.2.0 foundation modules: forked_agent, cron_scheduler, conversation_recovery."""

from __future__ import annotations

import asyncio
import json
import os
import tempfile


# ─── forked_agent tests ───────────────────────────────────────────────
from agnt_services.forked_agent import (
  CacheSafeParams,
  ForkedAgentResult,
  SubagentContext,
  SubagentContextOverrides,
  TokenUsage,
  accumulate_usage,
  create_subagent_context,
  extract_result_text,
  get_last_cache_safe_params,
  run_forked_agent,
  save_cache_safe_params,
)


class TestTokenUsage:
  def test_total_input_tokens(self):
    u = TokenUsage(
      input_tokens=10, cache_read_input_tokens=5, cache_creation_input_tokens=3
    )
    assert u.total_input_tokens == 18

  def test_cache_hit_rate_zero(self):
    assert TokenUsage().cache_hit_rate == 0.0

  def test_cache_hit_rate_nonzero(self):
    u = TokenUsage(input_tokens=50, cache_read_input_tokens=50)
    assert u.cache_hit_rate == 0.5


class TestAccumulateUsage:
  def test_merge(self):
    a = TokenUsage(input_tokens=10, output_tokens=5)
    b = TokenUsage(input_tokens=3, output_tokens=2, service_tier="fast")
    result = accumulate_usage(a, b)
    assert result.input_tokens == 13
    assert result.output_tokens == 7
    assert result.service_tier == "fast"


class TestSubagentContext:
  def test_auto_ids(self):
    ctx = SubagentContext()
    assert ctx.agent_id
    assert ctx.query_chain_id

  def test_create_increments_depth(self):
    ctx = create_subagent_context(parent_depth=2)
    assert ctx.query_depth == 3

  def test_overrides_applied(self):
    ctx = create_subagent_context(
      overrides=SubagentContextOverrides(agent_id="test-id", agent_type="worker"),
    )
    assert ctx.agent_id == "test-id"
    assert ctx.agent_type == "worker"


class TestCacheSafeParams:
  def test_save_and_get(self):
    params = CacheSafeParams(system_prompt="test")
    save_cache_safe_params(params)
    assert get_last_cache_safe_params() is params
    save_cache_safe_params(None)
    assert get_last_cache_safe_params() is None


class TestExtractResultText:
  def test_string_content(self):
    msgs = [{"type": "assistant", "content": "hello"}]
    assert extract_result_text(msgs) == "hello"

  def test_list_content(self):
    msgs = [{"role": "assistant", "content": [{"type": "text", "text": "world"}]}]
    assert extract_result_text(msgs) == "world"

  def test_default(self):
    assert extract_result_text([]) == "Execution completed"
    assert extract_result_text([], "custom") == "custom"


class TestRunForkedAgent:
  def test_no_query_fn(self):
    result = asyncio.run(
      run_forked_agent(
        prompt_messages=[],
        cache_safe_params=CacheSafeParams(system_prompt="x"),
        fork_label="test",
        query_source="unit",
      )
    )
    assert isinstance(result, ForkedAgentResult)
    assert result.messages == []


# ─── cron_scheduler tests ─────────────────────────────────────────────
from agnt_services.cron_scheduler import (
  CronScheduler,
  CronSchedulerOptions,
  CronTask,
  build_missed_task_notification,
  is_recurring_task_aged,
)


class TestCronTask:
  def test_created_at_s(self):
    t = CronTask(id="1", cron="* * * * *", prompt="hi", created_at=5000.0)
    assert t.created_at_s == 5.0


class TestIsRecurringTaskAged:
  def test_not_recurring(self):
    t = CronTask(id="1", cron="*", prompt="x", created_at=0.0, recurring=False)
    assert not is_recurring_task_aged(t, 999999.0, 1000)

  def test_permanent(self):
    t = CronTask(
      id="1", cron="*", prompt="x", created_at=0.0, recurring=True, permanent=True
    )
    assert not is_recurring_task_aged(t, 999999.0, 1000)

  def test_aged(self):
    t = CronTask(id="1", cron="*", prompt="x", created_at=0.0, recurring=True)
    assert is_recurring_task_aged(t, 2000.0, 1000)

  def test_unlimited(self):
    t = CronTask(id="1", cron="*", prompt="x", created_at=0.0, recurring=True)
    assert not is_recurring_task_aged(t, 999999.0, 0)


class TestCronScheduler:
  def test_add_remove(self):
    fired: list[str] = []
    sched = CronScheduler(CronSchedulerOptions(on_fire=fired.append))
    task = CronTask(id="t1", cron="*", prompt="go", created_at=0.0)
    sched.add_task(task)
    sched.remove_task("t1")
    assert sched.get_next_fire_time() is None

  def test_stop(self):
    sched = CronScheduler(CronSchedulerOptions(on_fire=lambda x: None))
    sched.start()
    sched.stop()
    assert sched._stopped


class TestBuildMissedNotification:
  def test_single(self):
    t = CronTask(id="1", cron="0 9 * * *", prompt="do stuff", created_at=0.0)
    text = build_missed_task_notification([t])
    assert "one-shot scheduled task was" in text
    assert "do stuff" in text

  def test_plural(self):
    tasks = [
      CronTask(id="1", cron="*", prompt="a", created_at=0.0),
      CronTask(id="2", cron="*", prompt="b", created_at=0.0),
    ]
    text = build_missed_task_notification(tasks)
    assert "tasks were" in text


# ─── conversation_recovery tests ──────────────────────────────────────
from agnt_services.conversation_recovery import (
  create_assistant_message,
  create_user_message,
  deserialize_messages,
  deserialize_messages_with_interrupt_detection,
  filter_orphaned_thinking_only_messages,
  filter_unresolved_tool_uses,
  filter_whitespace_only_assistant_messages,
  is_tool_use_result_message,
  load_conversation_for_resume,
  load_messages_from_jsonl_path,
  migrate_legacy_attachment_types,
  restore_skill_state_from_messages,
)


class TestCreateMessages:
  def test_user(self):
    msg = create_user_message("hello")
    assert msg["type"] == "user"
    assert msg["message"]["content"] == "hello"

  def test_user_meta(self):
    msg = create_user_message("x", is_meta=True)
    assert msg["isMeta"] is True

  def test_assistant(self):
    msg = create_assistant_message("world")
    assert msg["type"] == "assistant"


class TestIsToolUseResult:
  def test_true(self):
    msg = {"message": {"content": [{"type": "tool_result", "tool_use_id": "x"}]}}
    assert is_tool_use_result_message(msg)

  def test_false_empty(self):
    assert not is_tool_use_result_message({"message": {"content": "text"}})


class TestMigrateLegacyAttachments:
  def test_new_file(self):
    msg = {
      "type": "attachment",
      "attachment": {"type": "new_file", "filename": "/a/b.py"},
    }
    result = migrate_legacy_attachment_types(msg)
    assert result["attachment"]["type"] == "file"

  def test_new_directory(self):
    msg = {
      "type": "attachment",
      "attachment": {"type": "new_directory", "path": "/a/b"},
    }
    result = migrate_legacy_attachment_types(msg)
    assert result["attachment"]["type"] == "directory"

  def test_backfill_display_path(self):
    msg = {"type": "attachment", "attachment": {"type": "file", "filename": "/x/y.py"}}
    result = migrate_legacy_attachment_types(msg)
    assert "displayPath" in result["attachment"]

  def test_passthrough(self):
    msg = {"type": "user", "message": {"content": "hi"}}
    assert migrate_legacy_attachment_types(msg) is msg


class TestFilterUnresolvedToolUses:
  def test_keeps_resolved(self):
    msgs = [
      {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "t1"}]}},
      {
        "type": "user",
        "message": {"content": [{"type": "tool_result", "tool_use_id": "t1"}]},
      },
    ]
    assert len(filter_unresolved_tool_uses(msgs)) == 2

  def test_drops_unresolved(self):
    msgs = [
      {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "t1"}]}},
    ]
    assert len(filter_unresolved_tool_uses(msgs)) == 0


class TestFilterOrphanedThinking:
  def test_keeps_normal(self):
    msgs = [
      {"type": "assistant", "message": {"content": [{"type": "text", "text": "hi"}]}}
    ]
    assert len(filter_orphaned_thinking_only_messages(msgs)) == 1

  def test_drops_thinking_only(self):
    msgs = [
      {
        "type": "assistant",
        "message": {"content": [{"type": "thinking", "thinking": "..."}]},
      }
    ]
    assert len(filter_orphaned_thinking_only_messages(msgs)) == 0


class TestFilterWhitespace:
  def test_keeps_content(self):
    msgs = [{"type": "assistant", "message": {"content": "hello"}}]
    assert len(filter_whitespace_only_assistant_messages(msgs)) == 1

  def test_drops_whitespace(self):
    msgs = [{"type": "assistant", "message": {"content": "  \n\n  "}}]
    assert len(filter_whitespace_only_assistant_messages(msgs)) == 0


class TestDeserializeMessages:
  def test_basic(self):
    msgs = [
      create_user_message("hi"),
      create_assistant_message("hello"),
    ]
    result = deserialize_messages(msgs)
    assert len(result) >= 2

  def test_interrupted_prompt_detection(self):
    msgs = [create_user_message("what's up")]
    result = deserialize_messages_with_interrupt_detection(msgs)
    assert result.turn_interruption_state.kind == "interrupted_prompt"

  def test_completed_turn(self):
    msgs = [create_user_message("hi"), create_assistant_message("hey")]
    result = deserialize_messages_with_interrupt_detection(msgs)
    assert result.turn_interruption_state.kind == "none"


class TestLoadMessagesFromJsonl:
  def test_empty_file(self):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
      f.write("")
      path = f.name
    try:
      msgs, sid = load_messages_from_jsonl_path(path)
      assert msgs == []
    finally:
      os.unlink(path)

  def test_single_entry(self):
    entry = {
      "uuid": "aaa",
      "type": "user",
      "message": {"content": "hi"},
      "timestamp": "2026-01-01T00:00:00Z",
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
      f.write(json.dumps(entry) + "\n")
      path = f.name
    try:
      msgs, sid = load_messages_from_jsonl_path(path)
      assert len(msgs) == 1
      assert msgs[0]["type"] == "user"
    finally:
      os.unlink(path)

  def test_missing_file(self):
    msgs, sid = load_messages_from_jsonl_path("/nonexistent/path.jsonl")
    assert msgs == []


class TestLoadConversationForResume:
  def test_none_inputs(self):
    assert load_conversation_for_resume() is None

  def test_from_log_option(self):
    log = {
      "messages": [
        create_user_message("hi"),
        create_assistant_message("hey"),
      ],
      "sessionId": "sid-123",
      "agentName": "test-agent",
    }
    result = load_conversation_for_resume(log_option=log)
    assert result is not None
    assert result.session_id == "sid-123"
    assert result.metadata.agent_name == "test-agent"
    assert len(result.messages) >= 2

  def test_from_jsonl(self):
    entry = {
      "uuid": "bbb",
      "type": "user",
      "message": {"content": "resume me"},
      "timestamp": "2026-01-01T00:00:00Z",
      "sessionId": "sid-456",
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
      f.write(json.dumps(entry) + "\n")
      path = f.name
    try:
      result = load_conversation_for_resume(source_jsonl_file=path)
      assert result is not None
      assert result.session_id == "sid-456"
    finally:
      os.unlink(path)


class TestRestoreSkillState:
  def test_restores_skills(self):
    msgs = [
      {
        "type": "attachment",
        "attachment": {
          "type": "invoked_skills",
          "skills": [{"name": "s1", "path": "/p", "content": "c"}],
        },
      }
    ]
    restore_skill_state_from_messages(msgs)
    from agnt_services.conversation_recovery import get_restored_skills

    skills = get_restored_skills()
    assert any(s["name"] == "s1" for s in skills)
