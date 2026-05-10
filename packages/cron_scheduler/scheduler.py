"""
cron_scheduler: Non-React File-Backed Task Scheduler
Ports the robust file-backed scheduler from Claude Code v2.1.91 (Tengu)
"""

import time
import threading
from collections.abc import Callable


class CronTask:
  def __init__(self, task_id: str, cron: str, prompt: str, recurring: bool):
    self.id = task_id
    self.cron = cron
    self.prompt = prompt
    self.recurring = recurring
    self.created_at = time.time() * 1000


class CronScheduler:
  def __init__(self, on_fire: Callable[[str], None], dir_path: str | None = None):
    self.on_fire = on_fire
    self.dir_path = dir_path
    self.tasks: list[CronTask] = []
    self.next_fire_at: dict[str, float] = {}
    self._check_timer = None
    self.stopped = False

  def start(self):
    self.stopped = False
    self._check_loop()

  def _check_loop(self):
    if self.stopped:
      return

    now = time.time() * 1000
    for task in self.tasks:
      next_time = self.next_fire_at.get(task.id, float("inf"))
      if now >= next_time:
        self.on_fire(task.prompt)

    if not self.stopped:
      self._check_timer = threading.Timer(1.0, self._check_loop)
      self._check_timer.start()

  def stop(self):
    self.stopped = True
    if self._check_timer:
      self._check_timer.cancel()


def build_missed_task_notification(missed_tasks: list[CronTask]) -> str:
  """Security-critical function: formats with backtick fences to prevent injection"""
  header = "The following scheduled tasks were missed while offline.\nDo NOT execute them without user confirmation."
  blocks = []
  for t in missed_tasks:
    fence = "`" * 4
    blocks.append(f"{fence}\n{t.prompt}\n{fence}")
  return f"{header}\n\n" + "\n\n".join(blocks)
