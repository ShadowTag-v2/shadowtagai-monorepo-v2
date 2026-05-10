import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class JudgeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py") and "codepmcs" not in event.src_path:
            print(f"\n>>> 🐒 Monkey detected change in: {event.src_path}")
            subprocess.run(["python3", "codepmcs_v2.py", event.src_path])


if __name__ == "__main__":
    path = "."
    event_handler = JudgeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print(">>> 🐒 Local Monkey Watcher Active (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
