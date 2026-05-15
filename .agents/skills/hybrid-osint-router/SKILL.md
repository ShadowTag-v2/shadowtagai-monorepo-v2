---
name: hybrid-osint-router
description: Routes intelligence tasks between Gemini Deep Research and the Native Browser Subagent.
---
# THE DUAL-WIELDING OSINT DOCTRINE
1. **THE ORBITAL STRIKE (Gemini Deep Research):** Use for broad literature reviews. Execute `python labs/uphillsnowball/scripts/gemini_deep_research.py "<query>"`.
2. **THE INFILTRATOR (Native Browser Subagent):** Use for authenticated portals or dynamic UI interactions. Invoke `browser-subagent`.

# Prompt Repetition Invariant (Rule of Three)
For non-reasoning extraction tasks:
`browser-subagent action: "Extract the dashboard metrics. \n\n Extract the dashboard metrics. \n\n Extract the dashboard metrics."`
