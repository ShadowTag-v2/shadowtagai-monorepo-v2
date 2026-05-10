# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Deep Hypothesis property tests for cron_scheduler.py.

Validates invariants across CronScheduler data structures and logic:
  1. is_recurring_task_aged: non-recurring/permanent never age
  2. is_recurring_task_aged: correctness for recurring non-permanent
  3. CronScheduler add/remove task consistency
  4. _check() fires one-shot tasks then removes them
  5. _check() reschedules recurring tasks
  6. get_next_fire_time is None when empty
  7. build_missed_task_notification handles 0, 1, N tasks
  8. CronTask.created_at_s = created_at / 1000.0
"""

from __future__ import annotations

import os
import sys
import time

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

sys.path.insert(0, "packages")

from agnt_services.cron_scheduler import (
  CronScheduler,
  CronSchedulerOptions,
  CronTask,
  build_missed_task_notification,
  is_recurring_task_aged,
)

_FUZZ = int(os.environ.get("HYPOTHESIS_FUZZ_MULTIPLIER", "1"))
_HC = [HealthCheck.too_slow]

pos_float = st.floats(
  min_value=0.0, max_value=1e15, allow_nan=False, allow_infinity=False
)
pos_int = st.integers(min_value=0, max_value=86400_000)
task_id_st = st.text(
  min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N"))
)


# ─── 1. is_recurring_task_aged invariants ─────────────────────────────────


class TestRecurringTaskAged:
  @given(now_ms=pos_float, max_age=pos_int, created=pos_float)
  @settings(max_examples=300 * _FUZZ, suppress_health_check=_HC)
  def test_non_recurring_never_ages(self, now_ms, max_age, created):
    """Non-recurring tasks MUST never be flagged as aged."""
    task = CronTask(
      id="t", cron="* * * * *", prompt="p", created_at=created, recurring=False
    )
    assert not is_recurring_task_aged(task, now_ms, max_age)

  @given(now_ms=pos_float, max_age=pos_int, created=pos_float)
  @settings(max_examples=300 * _FUZZ, suppress_health_check=_HC)
  def test_permanent_never_ages(self, now_ms, max_age, created):
    """Permanent tasks MUST never be flagged as aged."""
    task = CronTask(
      id="t",
      cron="* * * * *",
      prompt="p",
      created_at=created,
      recurring=True,
      permanent=True,
    )
    assert not is_recurring_task_aged(task, now_ms, max_age)

  @given(now_ms=pos_float, created=pos_float)
  @settings(max_examples=200 * _FUZZ, suppress_health_check=_HC)
  def test_zero_max_age_never_ages(self, now_ms, created):
    """max_age_ms=0 means unlimited — never ages."""
    task = CronTask(
      id="t", cron="* * * * *", prompt="p", created_at=created, recurring=True
    )
    assert not is_recurring_task_aged(task, now_ms, 0)

  @given(
    created=st.integers(min_value=0, max_value=int(1e12)).map(float),
    max_age=st.integers(min_value=1, max_value=86400_000),
  )
  @settings(max_examples=200 * _FUZZ, suppress_health_check=_HC)
  def test_aged_when_elapsed(self, created, max_age):
    """Task is aged when now_ms - created_at >= max_age_ms.

    Uses integer-valued floats for `created` to avoid IEEE 754 drift
    where (x + n) - x != n for fractional floats.  Real timestamps
    from time.time() * 1000 are integer milliseconds.
    """
    now_ms = created + max_age
    task = CronTask(
      id="t", cron="* * * * *", prompt="p", created_at=created, recurring=True
    )
    assert is_recurring_task_aged(task, now_ms, max_age)

  @given(
    created=st.integers(min_value=100, max_value=int(1e12)).map(float),
    max_age=st.integers(min_value=2, max_value=86400_000),
  )
  @settings(max_examples=200 * _FUZZ, suppress_health_check=_HC)
  def test_not_aged_before_elapsed(self, created, max_age):
    """Task is NOT aged when now_ms - created_at < max_age_ms.

    Uses integer-valued floats for `created` — see test_aged_when_elapsed.
    """
    now_ms = created + max_age - 1
    task = CronTask(
      id="t", cron="* * * * *", prompt="p", created_at=created, recurring=True
    )
    assert not is_recurring_task_aged(task, now_ms, max_age)


# ─── 2. CronTask.created_at_s ────────────────────────────────────────────


class TestCronTaskProperties:
  @given(created=pos_float)
  @settings(max_examples=200 * _FUZZ, suppress_health_check=_HC)
  def test_created_at_s_division(self, created):
    task = CronTask(id="t", cron="* * * * *", prompt="p", created_at=created)
    assert task.created_at_s == created / 1000.0

  @given(tid=task_id_st, prompt=st.text(min_size=1, max_size=200))
  @settings(max_examples=100 * _FUZZ, suppress_health_check=_HC)
  def test_roundtrip(self, tid, prompt):
    task = CronTask(id=tid, cron="0 * * * *", prompt=prompt, created_at=0.0)
    assert task.id == tid
    assert task.prompt == prompt


# ─── 3. CronScheduler add/remove ─────────────────────────────────────────


class TestSchedulerAddRemove:
  def _make_scheduler(self):
    fired = []
    opts = CronSchedulerOptions(on_fire=fired.append)
    return CronScheduler(opts), fired

  @given(n=st.integers(min_value=1, max_value=20))
  @settings(max_examples=50 * _FUZZ, suppress_health_check=_HC)
  def test_add_grows_tasks(self, n):
    sched, _ = self._make_scheduler()
    for i in range(n):
      sched.add_task(
        CronTask(id=f"t{i}", cron="* * * * *", prompt=f"p{i}", created_at=0.0)
      )
    assert len(sched._tasks) == n

  @given(n=st.integers(min_value=1, max_value=20))
  @settings(max_examples=50 * _FUZZ, suppress_health_check=_HC)
  def test_remove_shrinks_tasks(self, n):
    sched, _ = self._make_scheduler()
    for i in range(n):
      sched.add_task(
        CronTask(id=f"t{i}", cron="* * * * *", prompt=f"p{i}", created_at=0.0)
      )
    for i in range(n):
      sched.remove_task(f"t{i}")
    assert len(sched._tasks) == 0

  def test_remove_nonexistent_noop(self):
    sched, _ = self._make_scheduler()
    sched.remove_task("nonexistent")
    assert len(sched._tasks) == 0


# ─── 4. _check() fires and removes one-shot ──────────────────────────────


class TestSchedulerCheck:
  def test_one_shot_fires_and_removes(self):
    fired = []
    opts = CronSchedulerOptions(on_fire=fired.append)
    sched = CronScheduler(opts)
    now_ms = time.time() * 1000
    task = CronTask(
      id="oneshot",
      cron="* * * * *",
      prompt="do it",
      created_at=now_ms - 120_000,
      recurring=False,
    )
    sched.add_task(task)
    sched._next_fire_at["oneshot"] = now_ms - 1
    sched._check()
    assert "do it" in fired
    assert all(t.id != "oneshot" for t in sched._tasks)

  def test_recurring_reschedules(self):
    fired = []
    opts = CronSchedulerOptions(on_fire=fired.append)
    sched = CronScheduler(opts)
    now_ms = time.time() * 1000
    task = CronTask(
      id="rec",
      cron="* * * * *",
      prompt="repeat",
      created_at=now_ms - 120_000,
      recurring=True,
    )
    sched.add_task(task)
    sched._next_fire_at["rec"] = now_ms - 1
    sched._check()
    assert "repeat" in fired
    assert any(t.id == "rec" for t in sched._tasks)
    assert sched._next_fire_at["rec"] > now_ms


# ─── 5. get_next_fire_time ────────────────────────────────────────────────


class TestGetNextFireTime:
  def test_none_when_empty(self):
    sched, _ = TestSchedulerAddRemove._make_scheduler(None)
    assert sched.get_next_fire_time() is None

  def test_returns_min(self):
    fired = []
    opts = CronSchedulerOptions(on_fire=fired.append)
    sched = CronScheduler(opts)
    sched._next_fire_at = {"a": 5000.0, "b": 3000.0, "c": 9000.0}
    assert sched.get_next_fire_time() == 3000.0


# ─── 6. build_missed_task_notification ────────────────────────────────────


class TestBuildMissedNotification:
  def test_single_task(self):
    t = CronTask(id="m1", cron="0 9 * * *", prompt="morning check", created_at=0.0)
    text = build_missed_task_notification([t])
    assert "task was" in text
    assert "morning check" in text

  @given(n=st.integers(min_value=2, max_value=10))
  @settings(max_examples=20 * _FUZZ, suppress_health_check=_HC)
  def test_plural_tasks(self, n):
    tasks = [
      CronTask(id=f"m{i}", cron="* * * * *", prompt=f"p{i}", created_at=0.0)
      for i in range(n)
    ]
    text = build_missed_task_notification(tasks)
    assert "tasks were" in text
    for i in range(n):
      assert f"p{i}" in text
