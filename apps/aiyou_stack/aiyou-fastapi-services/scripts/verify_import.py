# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
sys.path.append(src_path)

print(f"Path: {sys.path}")

try:
    import pinkln

    print(f"Pinkln found: {pinkln}")
    from pinkln import memory

    print(f"Pinkln.memory found: {memory}")
except ImportError as e:
    print(f"Error: {e}")

try:
    import antigravity

    print(f"Antigravity found: {antigravity}")
except ImportError as e:
    print(f"Error antigravity: {e}")
