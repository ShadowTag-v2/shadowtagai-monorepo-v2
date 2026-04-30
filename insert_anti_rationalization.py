# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

with open(".claude/skills/debugging/verification-before-completion.md") as f:
    content = f.read()

anti_rationalization = """
## Anti-Rationalization & Self-Awareness Block (Claude 2.1.90 Integration)

**You are an AI, and you are inherently bad at verification.**
Recognize these 5 specific failure modes and actively counter them:
1. **The "It Looks Right" Fallacy**: Reading code is NOT verification. Code review alone CANNOT produce a PASS verdict.
2. **The "PARTIAL" Hedge**: "Partial" is NOT a valid hedge for ambiguity. It is only acceptable for hard environmental blockers.
3. **The "I Changed It So It Works" Assumption**: Do not assume your edit had the desired effect.
4. **The "One Test is Enough" Bias**: You must use adversarial probes.
5. **The "It's Probably Fine" Excuse**: When tired or lacking context, do not rationalize missing checks.

**MANDATORY ADVERSARIAL PROBES:**
At least ONE adversarial probe must be executed before declaring PASS:
- Concurrency test (race conditions)
- Boundary/limit test (off-by-one, overflow)
- Idempotency test (running it twice)
- Orphan operation test (what happens if the middle step fails?)
"""

if "Anti-Rationalization" not in content:
    with open(".claude/skills/debugging/verification-before-completion.md", "w") as f:
        f.write(content.replace("## When to Use", anti_rationalization + "\n## When to Use"))
