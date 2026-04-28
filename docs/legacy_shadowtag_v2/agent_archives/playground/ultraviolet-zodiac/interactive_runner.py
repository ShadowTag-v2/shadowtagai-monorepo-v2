# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import pty

# The command to run
command = [
    "/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/.venv/bin/python",
    "scripts/god_mode_admin.py",
]

# Set the environment variable
os.environ["GCP_PROJECT_ID"] = "shadowtag-omega-v4"

# Change the working directory
os.chdir("/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2")

# Spawn a new pseudo-terminal
pty.spawn(command)
