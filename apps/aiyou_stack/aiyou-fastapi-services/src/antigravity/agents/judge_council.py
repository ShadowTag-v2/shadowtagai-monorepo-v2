from google.adk.core import LlmAgent, ParallelAgent, SequentialAgent

# 1. The Panel of Judges (Run in Parallel)
security_judge = LlmAgent(
    name="SecurityJudge",
    instruction="Scan the diff for hardcoded secrets, SQL injection, and permission escalations.",
    output_key="security_verdict",
)

performance_judge = LlmAgent(
    name="PerformanceJudge",
    instruction="Scan the diff for O(n^2) loops, memory leaks, and unoptimized queries.",
    output_key="performance_verdict",
)

style_judge = LlmAgent(
    name="StyleJudge",
    instruction="Ensure code follows PEP-8 and has JSDoc/Docstrings.",
    output_key="style_verdict",
)

# 2. Fan-Out (The Swarm)
judge_swarm = ParallelAgent(
    name="JudgeSixSwarm",
    sub_agents=[security_judge, performance_judge, style_judge],
)

# 3. The Synthesizer (The Verdict)
# Combines all 3 reports into a final Go/No-Go decision
chief_justice = LlmAgent(
    name="ChiefJustice",
    instruction="""
    Review the reports from the swarm:
    - Security: {security_verdict}
    - Performance: {performance_verdict}
    - Style: {style_verdict}

    Issue a Final Verdict. If ANY critical security issue exists, REJECT.
    """,
)

# The Full Review Pipeline
review_pipeline = SequentialAgent(sub_agents=[judge_swarm, chief_justice])
