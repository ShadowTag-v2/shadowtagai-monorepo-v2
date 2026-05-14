# Cursor + OpenAI (Non-Azure) Setup

Follow this to fix 400 errors and get a reliable configuration.

## Provider
- Select OpenAI (not OpenAI-Compatible or Custom).

## API Key
- Paste your `sk-...` key (fresh copy, no spaces).

## Base URL
- Leave blank. Cursor defaults to `https://api.openai.com/v1`.

## Model
- Prefer `gpt-5` only if your account has access.
- Otherwise use `gpt-4.1` (or any model shown by `/v1/models`).

## Streaming
- Toggle off for now. Org verification is needed for streaming; enable later after verification.

## Sanity check outside Cursor (PowerShell)
```powershell
$env:OPENAI_API_KEY="sk-..."
curl.exe https://api.openai.com/v1/models `
  -H "Authorization: Bearer $env:OPENAI_API_KEY"
```
- If JSON with model names returns → key works.
- If 400 HTML → base URL wrong or proxy interception.

## Proxy cleanup (PowerShell)
```powershell
$env:HTTP_PROXY=""
$env:HTTPS_PROXY=""
$env:NO_PROXY="api.openai.com"
```

## Ready-to-drop settings template
Copy this file into `.cursor/settings.openai.json` and set your key in env.

```json
{
  "openai": {
    "provider": "openai",
    "apiKeyEnv": "OPENAI_API_KEY",
    "baseUrl": "",
    "model": "gpt-4.1",
    "stream": false
  }
}
```

Note: Cursor may not read this file automatically; it’s a template you can reference while configuring Cursor’s UI. Keep `OPENAI_API_KEY` in your shell or OS keychain.
