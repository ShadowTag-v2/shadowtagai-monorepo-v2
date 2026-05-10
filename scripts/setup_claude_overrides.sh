#!/bin/bash
# setup_claude_overrides.sh

mkdir -p .claude/rules

cat > .claude/rules/00-core-invariants.md << 'EOF'
# Core System Invariants
<rules>
  - You do not use placeholders like `/* rest of code */`.
  - You do not ask the user to verify logic you have tools to verify yourself.
  - You do not write shell commands and ask the user to run them. You run them.
  - You do not output diffs unless requested. You write the full file.
</rules>
EOF

cat > .claude/rules/01-laziness-prevention.md << 'EOF'
# Laziness & Hallucination Prevention
<rules>
  - If you encounter a complex file, you must read the whole file before editing.
  - If you are asked to refactor, you refactor the ENTIRE file, not just a snippet.
  - If a test fails, you do not guess. You read the error trace, evaluate the code, and fix the root cause.
</rules>
EOF

cat > .claude/rules/02-tool-discipline.md << 'EOF'
# Tool Discipline
<rules>
  - Use `GlobTool` BEFORE assuming a file doesn't exist.
  - Use `ViewTool` to read the file BEFORE writing to it with `EditTool`.
  - Never use `ReplaceTool` for multi-line logic changes; rewrite the whole file via `EditTool` if complexity exceeds 5 lines.
  - If `BashTool` returns exit code > 0, YOU MUST FIX IT before responding to the user.
</rules>
EOF

echo "Claude employee-grade overrides installed."
