# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from unittest.mock import patch, MagicMock
from agnt_tmux.tmux_socket import TmuxSocketManager


def test_check_availability():
  with patch("subprocess.run") as mock_run:
    mock_run.return_value = MagicMock(returncode=0)
    manager = TmuxSocketManager()
    assert manager.check_availability() is True


def test_initialize():
  manager = TmuxSocketManager(prefix="test")

  with patch("subprocess.run") as mock_run:
    # Mocking the initialization calls
    mock_run.side_effect = [
      MagicMock(returncode=0),  # check_availability
      MagicMock(returncode=0),  # new-session
      MagicMock(returncode=0),  # set-environment
      MagicMock(returncode=0, stdout="/tmp/tmux,12345\n"),  # display-message
    ]

    manager.initialize()
    assert manager._initialized is True
    assert manager.socket_path == "/tmp/tmux"
    assert manager.server_pid == 12345
    assert manager.get_tmux_env() == "/tmp/tmux,12345,0"
