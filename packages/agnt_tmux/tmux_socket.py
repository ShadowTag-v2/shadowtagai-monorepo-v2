# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
Tmux Socket Isolation
AGNT port of Claude Code's tmux socket isolation for background tasks.
Ensures AGNT's background processes do not interfere with the user's terminal environment.
"""

import os
import subprocess
import atexit


class TmuxSocketManager:
  def __init__(self, prefix: str = "agnt"):
    self.prefix = prefix
    self.socket_name = f"{prefix}-{os.getpid()}"
    self.socket_path: str | None = None
    self.server_pid: int | None = None
    self._initialized = False

  def check_availability(self) -> bool:
    """Check if tmux is installed."""
    try:
      subprocess.run(["tmux", "-V"], check=True, capture_output=True)
      return True
    except (subprocess.CalledProcessError, FileNotFoundError):
      return False

  def initialize(self):
    """Create an isolated tmux session."""
    if self._initialized:
      return

    if not self.check_availability():
      raise RuntimeError("Tmux is not available on this system.")

    # Create a detached session on the custom socket
    subprocess.run(
      ["tmux", "-L", self.socket_name, "new-session", "-d", "-s", "base"],
      check=True,
      capture_output=True,
    )

    # Set environment to skip prompt history (anti-pollution)
    subprocess.run(
      [
        "tmux",
        "-L",
        self.socket_name,
        "set-environment",
        "-g",
        "AGNT_SKIP_PROMPT_HISTORY",
        "true",
      ],
      check=True,
      capture_output=True,
    )

    # Retrieve socket path and PID
    res = subprocess.run(
      [
        "tmux",
        "-L",
        self.socket_name,
        "display-message",
        "-p",
        "#{socket_path},#{pid}",
      ],
      capture_output=True,
      text=True,
      check=True,
    )

    output = res.stdout.strip().split(",")
    if len(output) == 2:
      self.socket_path = output[0]
      self.server_pid = int(output[1])
      self._initialized = True

      # Register cleanup
      atexit.register(self.kill_server)
    else:
      raise RuntimeError(f"Failed to parse tmux socket info: {res.stdout}")

  def get_tmux_env(self) -> str | None:
    """
    Returns the TMUX environment variable value for AGNT's isolated socket.
    Format: socket_path,server_pid,pane_index
    """
    if not self._initialized:
      return None
    return f"{self.socket_path},{self.server_pid},0"

  def kill_server(self):
    """Kills the isolated tmux server on shutdown."""
    if self._initialized:
      subprocess.run(
        ["tmux", "-L", self.socket_name, "kill-server"], capture_output=True
      )
      self._initialized = False

  def exec_command(self, cmd: str) -> subprocess.CompletedProcess:
    """Executes a command within the isolated tmux socket."""
    if not self._initialized:
      self.initialize()

    return subprocess.run(
      ["tmux", "-L", self.socket_name] + cmd.split(), capture_output=True, text=True
    )
