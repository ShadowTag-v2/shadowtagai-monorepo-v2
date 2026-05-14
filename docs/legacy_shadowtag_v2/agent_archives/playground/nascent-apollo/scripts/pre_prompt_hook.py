# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# scripts/pre_prompt_hook.py
import os
import re
import sys

# Define Skill Triggers
SKILLS = {
    r"django|models\.py|views\.py": ".agent/skills/django_security.md",
    r"react|tsx|jsx": ".agent/skills/react_best_practices.md",
    r"deploy|cloud run|docker": ".agent/skills/gcp_deployment.md",
    r"test|pytest|unittest": ".agent/skills/testing_standards.md",
}


def inject_context(prompt, file_context):
    injections = []
    combined_context = prompt + " " + file_context

    for pattern, skill_file in SKILLS.items():
        if re.search(pattern, combined_context, re.IGNORECASE):
            try:
                if os.path.exists(skill_file):
                    with open(skill_file) as f:
                        injections.append(f"\n--- ACTIVE SKILL: {skill_file} ---\n{f.read()}\n")
            except Exception:
                pass

    return "\n".join(injections)


if __name__ == "__main__":
    # In a real hook, these come from stdin/env
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else ""
    # Optional: file context could be passed as arg 2
    file_context = sys.argv[2] if len(sys.argv) > 2 else ""
    print(inject_context(user_prompt, file_context))
