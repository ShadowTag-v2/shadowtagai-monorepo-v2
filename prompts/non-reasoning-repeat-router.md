# Non-Reasoning Repeat Router

Apply prompt repetition when all are true:
- task is not using explicit reasoning mode
- task is accuracy-sensitive
- prompt length is comfortably below context limits
- output format is stable and deterministic

Do not apply automatically when any are true:
- explicit reasoning/thinking mode is enabled
- prompt is near context limits
- provider is sensitive to long-prompt latency
- upstream already rewrites or compresses the prompt heavily
