# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging
import os
import sys

# Configure path to find libs
sys.path.append(os.path.abspath("ShadowTag-Omega/libs"))

# Set up logging to see the "Traffic Cop" at work
logging.basicConfig(level=logging.INFO, format="%(message)s")

print(">>> 🧠 INIT: Loading RoutingAgent...")
try:
    from shadowtag_v4.proxies.routing_agent import RoutingAgent
except ImportError as e:
    print(f"!!! FATAL: Import Failed. {e}")
    sys.exit(1)

agent = RoutingAgent()

test_cases = [
    "Fix the typo in the README file.",
    "Research the top 5 competitors for a hospitality AI and refactor the entire authentication system to use JWTs.",
    "Change the button color to blue.",
    "Analyze the entire codebase for security vulnerabilities and implement a fix.",
]

print("\n>>> 🚦 RUNNING ECHO PROTOCOL TESTS...\n")

for i, query in enumerate(test_cases, 1):
    print(f"--- TEST CASE {i} ---")
    print(f"INPUT: '{query}'")
    try:
        decision = agent.dispatch(query)
        print(f"OUTPUT: {decision['route']} -> {decision['target']}")
    except Exception as e:
        print(f"ERROR: {e}")
    print()
