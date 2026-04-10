"""
LanceDB RAG Automator
name: LanceDB RAG Automator
description: Autonomously orchestrates the ingestion of newly generated or discovered workspace artifacts directly into the LanceDB Private Vector pipeline to ensure the semantic memory remains perfectly synchronized.
"""

# LanceDB RAG Automator

## Purpose
Whenever you (Antigravity) generate a major architectural artifact, research document, or protocol update (like a new `implementation_plan`, `thread_canonicalization.md`, or `SKILL.md`), that context is trapped in markdown files scattered across the repository. This skill tells you how to autonomously feed your own generated work back into your Sovereign Memory (LanceDB) so that the Next.js Agents can immediately reason against it.

## Execution Trigger
Run this automatically at the end of **every** major task that produces long-form text, documentation, or rulesets.

## Automation Mechanism
Since the Drag-and-Drop UI is for human interaction, you as an agent can interact directly with the backend API to inject context:

### The Injection Script
Use your `run_command` tool to execute a headless python push using the native FastAPI schema. 

```bash
python3 -c "
import requests, os

# Target the newly generated artifact
FILE_PATH = '/absolute/path/to/your/new_artifact.md'
WORKSPACE_ID = 1 # or target workspace

url = f'http://127.0.0.1:8000/workspaces/{WORKSPACE_ID}/knowledge/upload'
# Assume the token is pre-placed by the auth daemon or use a local Admin bypass path if authorized
headers = {'Authorization': f'Bearer {os.environ.get(\"shadowtag-omega-v4_ADMIN_JWT\")}'}

with open(FILE_PATH, 'rb') as f:
    files = {'file': (os.path.basename(FILE_PATH), f, 'text/plain')}
    r = requests.post(url, headers=headers, files=files)
    print(r.json())
"
```

### Protocol Guidelines
1. **Self-Feeding Memory:** When you write a new protocol, you MUST instantly ingest it.
2. **Context Scope:** Do not ingest generic source code files.
3. **No Duplicates:** Verify via `search_workspace_knowledge`.
