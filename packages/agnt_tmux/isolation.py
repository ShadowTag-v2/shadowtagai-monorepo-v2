"""TungstenTool tmux socket isolation logic."""

import os
import subprocess
from typing import List

class TmuxIsolationManager:
    """Manages isolated tmux sockets for agents to prevent collisions."""

    def __init__(self, base_socket_dir: str = "/tmp/tungsten_sockets"):
        """
        Initialize the isolation manager.
        
        Args:
            base_socket_dir (str): Base directory for isolated tmux sockets.
        """
        self.base_socket_dir = base_socket_dir
        os.makedirs(self.base_socket_dir, exist_ok=True)

    def get_socket_path(self, session_id: str) -> str:
        """
        Get the unique socket path for a given session.
        
        Args:
            session_id (str): The unique identifier for the agent session.
            
        Returns:
            str: Absolute path to the tmux socket.
        """
        return os.path.join(self.base_socket_dir, f"tmux_{session_id}.sock")

    def run_tmux_command(self, session_id: str, command: List[str]) -> subprocess.CompletedProcess:
        """
        Run a tmux command using the isolated socket.
        
        Args:
            session_id (str): The unique identifier for the agent session.
            command (List[str]): The tmux command to execute.
            
        Returns:
            subprocess.CompletedProcess: The result of the command execution.
        """
        socket_path = self.get_socket_path(session_id)
        full_command = ["tmux", "-S", socket_path] + command
        return subprocess.run(full_command, capture_output=True, text=True, check=False)

    def kill_session_socket(self, session_id: str) -> None:
        """
        Kill the tmux server running on the isolated socket and remove it.
        
        Args:
            session_id (str): The unique identifier for the agent session.
        """
        socket_path = self.get_socket_path(session_id)
        if os.path.exists(socket_path):
            self.run_tmux_command(session_id, ["kill-server"])
            try:
                os.remove(socket_path)
            except FileNotFoundError:
                pass
