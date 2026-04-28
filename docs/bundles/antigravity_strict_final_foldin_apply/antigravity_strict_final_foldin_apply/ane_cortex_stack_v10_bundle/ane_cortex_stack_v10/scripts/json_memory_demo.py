# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from service.app.adapters.json_memory import JsonMemoryStore

store = JsonMemoryStore()
store.append(
    {
        "type": "decision",
        "subject": "ANE fallback policy",
        "summary": "ANE first, Metal fallback on validation mismatch",
        "body": "Editor-blocking flows hit ANE first but must fail over on compile errors, unsupported ops, timeouts, or validation mismatches.",
        "tags": ["ane", "fallback", "editor"],
        "repo_id": "ane",
    }
)
print(store.search("fallback metal validation"))
