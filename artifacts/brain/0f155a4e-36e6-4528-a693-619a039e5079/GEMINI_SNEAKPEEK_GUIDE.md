# How to Run: Claude Sneakpeek + Gemini 3 Flash

You can now run **Claude Sneakpeek** (Swarm Mode enabled) powered entirely by **Gemini 3 Flash** (via `gemini-2.0-flash`).

## 🚀 Quick Start

Run the following command from the project root:

```bash
./scripts/launch_sneakpeek_gemini.sh
```

### What happens?
1.  **Starts the Bridge**: `claude-code-router` starts in the background (port 3456) and **stays running** (logged to `router.log`).
2.  **Configures Sneakpeek**: Sets up the `gemini-swarm` variant.
3.  **Ready to Run**: You can then run `gemini-swarm` anytime without re-running the script.

## ⚙️ Configuration

The bridge configuration is located at:
`libs/external/claude-code-router/config.json`

Currently mapped as:
- `Anthropic Sonnet 3.7` -> `google/gemini-2.0-flash`
- `Anthropic Opus 3` -> `google/gemini-2.0-flash`
- `Anthropic Haiku 3` -> `google/gemini-2.0-flash`

To use a different Gemini model (e.g., `gemini-1.5-pro`), edit this JSON file.

## 🐛 Troubleshooting

**"Provider Connection Failed"**
- Ensure `libs/external/claude-code-router` has `node_modules` installed (`npm install`).
- Check if port `3456` is already in use.

**"Auth Error"**
- The router uses standard Google Cloud auth. Ensure you have active credentials:
  ```bash
  gcloud auth application-default login
  ```
