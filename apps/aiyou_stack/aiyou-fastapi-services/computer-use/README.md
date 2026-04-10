# Computer-Use Agent (Gemini + Playwright)

Safe, sandboxed browser automation using Gemini's computer-use capabilities.

## What It Does

Runs a Computer-Use loop where the model:

1. Views a screenshot of the browser

2. Proposes UI actions (click, type, navigate, etc.)

3. We execute them via Playwright

4. Repeat until goal achieved or max turns reached

## Quickstart (Local / Codespaces)

```bash

# Install dependencies

pip install -r computer-use/requirements.txt
playwright install chromium

# Set environment variables

export GOOGLE_API_KEY=your-google-api-key
export CU_GOAL="Open example.com and verify the title"
export CU_START_URL="https://example.com"

# Run agent

python -m computer_use.agent

```

## Outputs

- `.ci/computer_use_audit.jsonl` - Every turn/action logged

- `.ci/computer_use_final.html` - Final DOM snapshot

## Safety

- **Allowlist enforced** in `allowlist.yaml` - only permitted domains

- **Hard caps** for turns & clicks

- **Audit trail** for every action

- Always run in sandboxed environment (container/VM/Codespace)

## Environment Variables

| Variable         | Default                               | Description                  |
| ---------------- | ------------------------------------- | ---------------------------- |
| `GOOGLE_API_KEY` | (required)                            | Google AI API key            |
| `CU_MODEL`       | `gemini-2.5-computer-use-preview-...` | Gemini model to use          |
| `CU_GOAL`        | "Navigate to example.com..."          | Task goal for the agent      |
| `CU_START_URL`   | `https://example.com`                 | Starting URL                 |
| `CU_HTML_OUT`    | `.ci/computer_use_final.html`         | Path for final HTML snapshot |

## Integration

### GitHub Actions

See `.github/workflows/ui-smoke.yml` for nightly smoke tests.

### Cursor Task

Add to `.cursor/tasks.json`:

```json
{
  "name": "cu:run",
  "cmd": "python -m computer_use.agent",
  "description": "Run Computer-Use agent"
}
```

## Advanced

- Extend `run_action()` in `agent.py` for custom actions

- Adjust `allowlist.yaml` for your domains

- Use `CU_GOAL` to parameterize different tasks

## Troubleshooting

- **"GOOGLE_API_KEY not set"** - Export the environment variable

- **Navigation blocked** - Check `allowlist.yaml` domains

- **Chromium not found** - Run `playwright install chromium`

- **Actions not working** - Check audit log for errors

## References

- [Gemini Computer-Use Docs](https://ai.google.dev/gemini-api/docs/computer-use)

- [Playwright Python Docs](https://playwright.dev/python)
