# Plan Mode Command

Generate an execution-ready plan using the Plan Mode Style Guide v1.0.

## Instructions

You are now in **Plan Mode**. Follow the PLAN_MODE_TEMPLATE.md style guide strictly.

### Core Rules:
- Sacrifice grammar for concision
- One action per line
- Use imperative verbs only
- Keep lines ≤60 chars
- End with "Unresolved Qs:" section
- No prose explanations

### Output Format:

```
<module or package>:
- <action> → <target>
- <action> → <target>

Impl:
- <short description of method>
- <compat or interim strategy>
- <future phase trigger or boundary>

Unresolved Qs:
- <question 1>?
- <question 2>?

Options:
1. Proceed + auto-accept edits
2. Proceed + manual approve
3. Hold + keep planning
```

### Symbols:
- → = transform / migrate
- = = set / define
- + = add / include
- - = remove / deprecate
- ? = question / decision needed
- ⚠️ = risk / dependency
- // = brief inline note

### Task:
Analyze the request and generate a plan following the template above.

**Request:** {{prompt}}
