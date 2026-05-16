# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# src/shield/rkill_daemon.py
import logging
import os
import time

import psutil
from agents.legal_whiteboard import whiteboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RkillDaemon")


class RkillDaemon:
  """
  ShadowTag Omega V7 Rkill Daemon
  Enforces the "Three Strikes of Death" policy to prevent rogue agent behavior.
  Integrated with Memory Beads (Whiteboard Patterns).
  """

  def __init__(self, memory_limit_gb=1.0, time_limit_sec=300):
    self.whiteboard = whiteboard
    self.memory_limit = memory_limit_gb * 1024 * 1024 * 1024  # Convert to bytes
    self.time_limit = time_limit_sec
    self.strikes = {}  # pid: {memory: int, time: int, boundary: int}
    self.blacklist_paths = [
      "/etc/passwd",
      "/etc/shadow",
      "~/.ssh/id_rsa",
      "/var/log/auth.log",
    ]
    # Dynamically load blacklist from whiteboard patterns (Memory Beads)
    self._load_dynamic_boundaries()

  def _load_dynamic_boundaries(self):
    for p in self.whiteboard.state.get("patterns", []):
      pattern = p.get("pattern", "")
      if "path" in pattern.lower() or "/" in pattern:
        if pattern not in self.blacklist_paths:
          self.blacklist_paths.append(pattern)
    logger.info(f"🛡️ RKILL: Loaded {len(self.blacklist_paths)} boundary rules.")

  def monitor(self):
    logger.info("💀 RKILL DAEMON: Monitoring initiated.")
    while True:
      self._load_dynamic_boundaries()  # Hot-reload patterns
      for proc in psutil.process_iter(
        ["pid", "name", "memory_info", "create_time", "open_files"]
      ):
        try:
          pid = proc.info["pid"]
          if pid == os.getpid():
            continue

          # Strike 1: Memory Violation
          mem_usage = (
            proc.info.get("memory_info").rss if proc.info.get("memory_info") else 0
          )
          if mem_usage > self.memory_limit:
            self._add_strike(pid, "memory")
            logger.warning(
              f"⚠️ [STRIKE] PID {pid} exceeded memory limit: {mem_usage / 1024 / 1024:.2f} MB"
            )

          # Strike 2: Temporal Violation
          uptime = time.time() - proc.info["create_time"]
          if uptime > self.time_limit:
            self._add_strike(pid, "time")
            logger.warning(f"⚠️ [STRIKE] PID {pid} exceeded time limit: {uptime:.2f}s")

          # Strike 3: Boundary Violation
          if proc.info.get("open_files"):
            for f in proc.info["open_files"]:
              if any(p in f.path for p in self.blacklist_paths):
                self._add_strike(pid, "boundary")
                logger.warning(
                  f"⚠️ [STRIKE] PID {pid} accessed blacklisted path: {f.path}"
                )

          # Check for termination
          if sum(self.strikes.get(pid, {}).values()) >= 3:
            logger.error(f"❌ [KILL] PID {pid} reached 3 strikes. Terminating.")
            proc.terminate()
            del self.strikes[pid]

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
          pass

      time.sleep(5)

  def _add_strike(self, pid, strike_type):
    if pid not in self.strikes:
      self.strikes[pid] = {"memory": 0, "time": 0, "boundary": 0}
    self.strikes[pid][strike_type] += 1


if __name__ == "__main__":
  daemon = RkillDaemon()
  daemon.monitor()
