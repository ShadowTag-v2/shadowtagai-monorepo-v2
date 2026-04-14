import logging
import os
import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# CONFIG
WATCH_PATHS = ["src", "scripts"]
EXTENSIONS = [".py"]


class PolishHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_run = {}
        self.cooldown = 2.0  # Seconds between runs for same file

    def on_modified(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        _, ext = os.path.splitext(filepath)

        if ext not in EXTENSIONS:
            return

        # Debounce
        now = time.time()
        if filepath in self.last_run:
            if now - self.last_run[filepath] < self.cooldown:
                return
        self.last_run[filepath] = now

        logging.info(f"⚡ Detected change in: {filepath}")
        self.polish_file(filepath)

    def polish_file(self, filepath):
        try:
            # 1. Format (Black)
            subprocess.run(["black", "-q", filepath], check=False)

            # 2. Sort Imports (Isort)
            subprocess.run(["isort", "-q", filepath], check=False)

            # 3. Lint (Pylint) - Optional, just check, don't block
            # subprocess.run(["pylint", "--errors-only", filepath], check=False)

            # 4. Git Stage
            subprocess.run(["git", "add", filepath], check=True)

            logging.info(f"✅ Polished & Staged: {filepath}")

        except Exception as e:
            logging.exception(f"❌ Failed to polish {filepath}: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S")

    event_handler = PolishHandler()
    observer = Observer()

    for path in WATCH_PATHS:
        if os.path.exists(path):
            observer.schedule(event_handler, path, recursive=True)
            logging.info(f"👀 Watching: {path}/")
        else:
            logging.warning(f"⚠️ Path not found: {path}")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
