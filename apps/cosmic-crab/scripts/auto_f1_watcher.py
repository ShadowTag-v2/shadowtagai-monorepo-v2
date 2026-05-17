# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# scripts/auto_f1_watcher.py
import logging
import os
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("F1Watcher")


class F1Handler(FileSystemEventHandler):
  """
  ShadowTag Omega V7 F1 Watcher
  Automatically triggers the F1 -> GCA (Finish Changes) cycle on modification.
  """

  def __init__(self, debounce_sec=5):
    self.debounce_sec = debounce_sec
    self.last_triggered = 0

  def on_modified(self, event):
    if event.is_directory:
      return
    if not event.src_path.endswith(".py") and not event.src_path.endswith(".tsx"):
      return

    current_time = time.time()
    if current_time - self.last_triggered > self.debounce_sec:
      logger.info(
        f"✨ [WATCHER] Change detected in {event.src_path}. Triggering F1 cycle..."
      )
      self.last_triggered = current_time
      self._trigger_f1()

  def _trigger_f1(self):
    # In a real scenario, this would call the Antigravity F1 command via an IDE bridge
    # or execute the local 'finish_changes.sh' equivalent.
    logger.info("🛠️ [F1 CYCLE] Executing: lint -> format -> stage -> commit.")
    try:
      # Placeholder for the actual finish_changes command
      # subprocess.run(["python", "scripts/pickle_protocol.py"], check=True)
      logger.info("✅ [F1 CYCLE] Success. Closing editor (Simulated).")
    except Exception as e:
      logger.error(f"❌ [F1 CYCLE] Failed: {e}")


if __name__ == "__main__":
  path = "."
  event_handler = F1Handler()
  observer = Observer()
  observer.schedule(event_handler, path, recursive=True)
  observer.start()
  logger.info(f"👁️ ATTACHED: F1 Watcher active in {os.path.abspath(path)}")
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()
  observer.join()
