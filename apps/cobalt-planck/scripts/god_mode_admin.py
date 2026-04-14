import argparse
import os
import subprocess
import threading
import time


class GodModeEngine:
    def __init__(self, omega_active=False, non_interactive=False):
        self.stop_event = threading.Event()
        self.omega_active = omega_active
        self.non_interactive = non_interactive
        self.toolbelt = {}
        self.log_path = "god_mode_bg.log"
        self.project_id = os.environ.get("GCP_PROJECT_ID", "UNKNOWN")
        self._log(f"Engine Init. GCP_PROJECT_ID: {self.project_id}")
        self._load_toolbelt()

    def _load_toolbelt(self):
        path = ".agent/docs/toolbelt.md"
        if not os.path.exists(path):
            return self._log(f"Error: {path} not found.")
        with open(path) as f:
            for line in f:
                if "|" in line and "npm run" in line:
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 2:
                        self.toolbelt[parts[0]] = parts[1]
        self._log(f"Toolbelt: {list(self.toolbelt.keys())}")

    def _log(self, msg):
        with open(self.log_path, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

    def _run(self, cmd):
        self._log(f"Exec: {cmd}")
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            self._log(f"OK: {cmd} - Out: {res.stdout.strip()[:100]}...")
            return True
        except subprocess.CalledProcessError as e:
            self._log(f"FAIL: {cmd} - Err: {e.stderr.strip()}")
            return False

    def _bg_worker(self):
        while not self.stop_event.is_set():
            if self.omega_active:
                self._log("Cycle Start")
                for _, cmd in self.toolbelt.items():
                    if not self.omega_active or self.stop_event.is_set():
                        break
                    if not self._run(cmd):
                        self.omega_active = False
                        break
                self._log("Cycle End")
                if self.non_interactive:
                    self.stop_event.set()
                    break
                for _ in range(10):
                    if self.stop_event.is_set() or not self.omega_active:
                        break
                    time.sleep(1)
            else:
                if self.non_interactive:
                    self.stop_event.set()
                    break
                time.sleep(1)

    def start(self, interactive=True):
        threading.Thread(target=self._bg_worker, daemon=True).start()
        if not interactive:
            while not self.stop_event.is_set():
                time.sleep(0.1)
            return
        print(
            f"God Mode Engine 3.0. Project: {self.project_id}. Commands: /omega-loop, /status, /help, /exit",
        )
        while not self.stop_event.is_set():
            try:
                line = input("god-mode> ").strip()
                if not line:
                    continue
                if line == "/omega-loop":
                    self.omega_active = not self.omega_active
                    print(f"Omega Loop: {'ENABLED' if self.omega_active else 'DISABLED'}")
                elif line == "/status":
                    print(f"Active: {self.omega_active}, Tools: {len(self.toolbelt)}")
                elif line == "/help":
                    print("Commands: /omega-loop, /status, /help, /exit")
                elif line == "/exit":
                    self.stop_event.set()
            except (KeyboardInterrupt, EOFError):
                self.stop_event.set()
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--non-interactive", action="store_true")
    parser.add_argument("--omega-loop", action="store_true")
    args = parser.parse_args()
    GodModeEngine(args.omega_loop, args.non_interactive).start(not args.non_interactive)
