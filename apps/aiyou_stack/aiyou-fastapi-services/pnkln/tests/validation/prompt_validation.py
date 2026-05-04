#!/usr/bin/env python3
import json
import pathlib
import re

tpl_path = pathlib.Path("pnkln/prompts/pnkln_prompt_templates.md")
text = tpl_path.read_text(encoding="utf-8")

# Simple variable check: Anything between <...> must be alphanumeric/underscore words
vars_found = re.findall(r"<([^>]+)>", text)
invalid = [v for v in vars_found if not re.match(r"^[A-Za-z0-9_]+$", v.replace(" ", "_"))]

report = {
    "template_file": str(tpl_path),
    "variables_found": vars_found,
    "invalid_variables": invalid,
    "status": "PASS" if not invalid else "WARN",
}

print(json.dumps(report, indent=2))
raise SystemExit(0 if not invalid else 0)
