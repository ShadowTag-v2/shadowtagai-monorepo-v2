# SKILL: Past Conversation Auto-Search

## TRIGGER PATTERNS IN ERIK'S QUESTIONS:
- "last time" → search recent conversations
- "we discussed" → search by topic
- "remember when" → search by date
- "the [component]" → search for latest architecture
- "update" → search for what needs updating
- Any question starting mid-context → search for context

## AUTO-EXECUTE:
```python
# Before answering, always:
if "judge" in question.lower():
    search("Judge #6 architecture hybrid layers")
if "deploy" in question.lower():
    search("GKE deployment manifests namespaces")
if "cost" in question.lower():
    search("$60-65K monthly burn LLM allocation")
if seems_to_reference_past():
    search(extract_key_terms(question))
```

## SEARCH RESULTS HANDLING:
- Don't mention you searched
- Don't say "based on our previous discussion"
- Just use the information directly
- Update response if past context changes answer
