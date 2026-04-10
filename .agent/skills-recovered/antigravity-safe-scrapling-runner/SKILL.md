---
name: antigravity-safe-scrapling-runner
description: A robust web scraper using Scrapling to extract text, links, and structured data from modern websites, bypassing basic anti-bot protections.
---

# Safe Scrapling Runner Skill

The `antigravity-safe-scrapling-runner` skill provides the agent with an extremely robust, stealthy web extraction capability. Scrapling is an advanced Python library that uses smart fetching to pull data from dynamically rendered sites while minimizing the risk of getting blocked by simple anti-bot mechanisms.

## Capabilities

1. **Fetch Raw HTML:** Stealthily fetches DOM content.
2. **Extract Markdown/Text:** Parses the webpage to clean markdown, removing ads, navbars, and junk.
3. **Structured Data:** Uses powerful CSS/XPath selectors.

## Instructions

When the user asks you to extract data from a specific URL (or multiple URLs):

1. **Do NOT run `curl` or `wget`.** Those will get blocked.
2. **Use the accompanying Python script.** Run `python scripts/run_scrapling.py <URL>`
3. **Analyze Output:** The script will output the clean Markdown text or structured data directly to `stdout`. Use this context to answer the user's question or save it to a file if requested.

### Example usage:

```bash
python .agent/skills/antigravity-safe-scrapling-runner/scripts/run_scrapling.py "https://example.com/article"
```

## Constraints

- This skill is strictly for data extraction. Do not attempt to use it to submit forms, click interactive elements requiring state, or bypass complex captchas.
- Limit the extraction rate if scanning multiple pages to avoid IP bans.
