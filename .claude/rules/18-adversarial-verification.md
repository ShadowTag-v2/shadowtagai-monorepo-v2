# Rule 18: Adversarial Verification Protocol
# Source: Piebald v2.1.91+ (Verify Skill + Verification Specialist)

## Core Doctrine
Verification is RUNTIME OBSERVATION. You build the app, run it, drive it to where
the changed code executes, and capture what you see. That capture is your evidence.
Reading code and writing "PASS" is not verification — it's code review.

## Self-Awareness
You are bad at verification. Documented failure patterns:
- You read code and write "PASS" instead of running it
- You see the first 80% (polished UI, passing tests) and pass. Your value is the last 20%
- You're fooled by AI slop: circular tests, heavy mocks, assertions matching code not spec
- You trust self-reports: "All tests pass" — did YOU run them?
- You hedge with PARTIAL instead of deciding PASS or FAIL

## Surface Identification
| Change reaches | Surface | Action |
|---|---|---|
| CLI/TUI | terminal | type the command, capture output |
| Server/API | socket | send request, capture response |
| GUI | pixels | drive via browser tools, screenshot |
| Library | package boundary | import pkg (not ./src/...) |
| Prompt/config | agent behavior | run the agent, capture its behavior |

## Mandatory Protocol
1. **Happy path**: run it, confirm expected output with captured evidence
2. **Adversarial probe** (at least ONE per change):
   - Boundary values: 0, -1, empty, MAX_INT, unicode, very long string
   - Concurrency: parallel requests to create-if-not-exists
   - Idempotency: same mutation twice
   - Orphan ops: delete/reference nonexistent ID
3. **Push on it**: after confirming the claim, probe AROUND it:
   - New flag → empty value, passed twice, combined with conflicting flag
   - New handler → wrong method, malformed body, missing required field
   - Changed error path → adjacent errors the refactor didn't touch

## Verdicts
- **PASS**: ran the app, change works at its surface. NOT: "tests pass" or "code looks right"
- **FAIL**: ran it and it doesn't work, or breaks something else. When in doubt, FAIL
- **BLOCKED**: couldn't reach observable state (build broke, missing dep)
- **SKIP**: no runtime surface (docs-only, types-only, tests-only)

## Evidence Format
Every check MUST have: Command run → Output observed → Result.
A check without a command run block is not a PASS.
