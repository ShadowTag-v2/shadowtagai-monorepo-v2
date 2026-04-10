# Prompt Repetition Doctrine

## Purpose

Use prompt repetition as a cheap quality upgrade for non-reasoning tasks where the full request benefits from a second pass through the model input.

## Default rule

For non-reasoning tasks, prefer:

```text
<QUERY>

--- REPEAT ---

<QUERY>
```

## When to use it

Use repetition by default for:

- extraction
- classification
- grounded retrieval QA without chain-of-thought prompting
- structured transformation
- slot filling
- rubric-based evaluation without explicit reasoning mode
- long options-first or context-first prompts where important tokens appear before the actual question

## When not to use it blindly

Avoid blind repetition when:

- the model is already in explicit reasoning / thinking mode
- the prompt is near the context window limit
- the request is extremely long and prefill cost matters
- the model/provider shows latency sensitivity for long prompts
- the application already rewrites, reorders, or compresses the prompt upstream
