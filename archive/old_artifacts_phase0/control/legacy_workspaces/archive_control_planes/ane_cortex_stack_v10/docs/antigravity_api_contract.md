# Antigravity API contract

## POST /api/search

Request:
{
  "query": "why does qwen3_06b use 10 kernels per layer",
  "repo_id": "ane",
  "limit": 8
}

Response:
{
  "query": "why does qwen3_06b use 10 kernels per layer",
  "repo_id": "ane",
  "exact": [],
  "semantic": [],
  "memory": [],
  "tasks": []
}

## POST /api/context

Request:
{
  "query": "can I rely on ANE on my M1 Pro for production local embedding inference?",
  "repo_id": "ane"
}

Response:
{
  "query": "can I rely on ANE on my M1 Pro for production local embedding inference?",
  "repo_id": "ane",
  "prompt_context": "USER QUERY: ...",
  "selected_ids": {
    "exact": [],
    "semantic": [],
    "memory": [],
    "tasks": []
  }
}
