#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Flying Monkeys: Autonomous Research Helper
Usage: ./scripts/research_helper.py <query>
"""

import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: ./scripts/research_helper.py <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"🐒 Flying Monkeys dispatched for: '{query}'")
    print("... Browsing functionality is managed by the Agent's native 'browser' tool.")
    print("... To execute: The Agent should call 'search_web' or open a browser immediately.")


if __name__ == "__main__":
    main()
