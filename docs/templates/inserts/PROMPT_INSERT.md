# PROMPT INSERT — R-I-S-E Framework

Use for: LLM prompt engineering, content generation, AI task definition

---

## R-I-S-E Structure

### ROLE

**Persona**: [Who the AI should act as]

> Example: "Act as a senior Python developer with expertise in async programming"

**Capabilities**: [Specific skills to leverage]

- [ ] Code generation
- [ ] Code review
- [ ] Documentation
- [ ] Testing

---

### INPUT

**Primary Input**: [Main content to process]

```
[Paste code/text/data here]
```

**Supporting Context**:

- **File Path**: [Where this lives in codebase]
- **Related Files**: [Dependencies, imports]
- **Audience**: [Who will use the output]

---

### STEPS

**Sequential Actions**:

1. [ ] [First action with verification]
2. [ ] [Second action with verification]
3. [ ] [Third action with verification]

**Constraints**:

- Must: [Required elements]
- Must Not: [Forbidden elements]
- Should: [Preferred elements]

---

### EXPECTATION

**Output Format**:

- [ ] Code block with language tag
- [ ] Markdown documentation
- [ ] JSON structured data
- [ ] Plain text

**Quality Criteria**:

- [ ] Passes linting
- [ ] Follows style guide
- [ ] Includes error handling
- [ ] Has docstrings/comments

**Example of Good Output**:

```
[Provide example of expected output format]
```

---

## Alternative Frameworks (Reference)

### T-A-G (Task-Action-Goal)

- **Task**: [What to do]
- **Action**: [How to do it]
- **Goal**: [Measurable outcome]

### B-A-B (Before-After-Bridge)

- **Before**: [Current state problem]
- **After**: [Desired end state]
- **Bridge**: [How to get there]

### C-A-R-E (Context-Action-Result-Example)

- **Context**: [Background]
- **Action**: [What to do]
- **Result**: [Expected outcome]
- **Example**: [Reference implementation]
