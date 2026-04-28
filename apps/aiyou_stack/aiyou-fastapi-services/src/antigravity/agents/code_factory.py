# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from google.adk.core import LlmAgent, LoopAgent

# 1. The Writer (Generator)
writer = LlmAgent(
    name="CodeWriter",
    instruction="Generate the Python code for the requested feature. If you receive {feedback}, fix the errors.",
    output_key="draft_code",
)

# 2. The Linter (Critic)
# This agent runs 'pylint' or checks syntax
critic = LlmAgent(
    name="CodeCritic",
    instruction="""
    Review the {draft_code}.
    Check for:
    1. Syntax Errors
    2. Missing Imports (ModuleNotFoundError)
    3. Security leaks (Hardcoded keys)

    If valid, output 'PASS'.
    If invalid, output the specific error details to {feedback}.
    """,
    output_key="feedback",
)

# 3. The Loop (The Factory Floor)
# It will keep rewriting until the Critic says PASS (or hits 5 tries)
code_factory_loop = LoopAgent(
    name="CodeValidationLoop",
    sub_agents=[writer, critic],
    condition_key="feedback",
    exit_condition="PASS",
    max_iterations=5,
)
