# Retry Timed Out Repos - One at a Time

## Task
Retry `git pull` on the 3 repos that timed out during bulk update, waiting for user confirmation between each.

## Timed Out Repos
1. `~/aiyou-stack/gemini-cli`
2. `~/aiyou-stack/aiyou-fastapi-services`
3. `~/Documents/GitHub/google-api-java-client-services`

## Execution Plan

### Step 1: gemini-cli
```bash
cd ~/aiyou-stack/gemini-cli && git pull
```
Wait for completion → Report status → Wait for user confirmation

### Step 2: aiyou-fastapi-services
```bash
cd ~/aiyou-stack/aiyou-fastapi-services && git pull
```
Wait for completion → Report status → Wait for user confirmation

### Step 3: google-api-java-client-services
```bash
cd ~/Documents/GitHub/google-api-java-client-services && git pull
```
Wait for completion → Report status → Done

## Notes
- Use longer timeout (5 minutes) since these are large repos
- These repos likely have large git histories causing slow fetches
- If still timing out, may need to shallow fetch or reset
