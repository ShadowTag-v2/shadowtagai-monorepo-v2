#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
omega_port_executioner.py - The "Pickle Rick" Port Killer
Autonomously detects and annihilates zombie processes holding dev ports (3000, 8000, 5173, etc.) hostage.
Prevents EADDRINUSE failures.
"""

import subprocess
import sys

DEFAULT_PORTS = ["3000", "8000", "5173", "8080"]


def kill_ports(ports):
  for port in ports:
    print(f"Hunting zombies on port {port}...")
    try:
      # lsof -ti :<port> | xargs kill -9
      pids = (
        subprocess.check_output(["lsof", "-ti", f":{port}"])
        .decode()
        .strip()
        .split("\n")
      )
      for pid in pids:
        if pid:
          subprocess.run(["kill", "-9", pid])
          print(f"Annihilated zombie PID: {pid} holding port {port}")
    except subprocess.CalledProcessError:
      print(f"Port {port} is clear.")


if __name__ == "__main__":
  ports = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_PORTS
  kill_ports(ports)
