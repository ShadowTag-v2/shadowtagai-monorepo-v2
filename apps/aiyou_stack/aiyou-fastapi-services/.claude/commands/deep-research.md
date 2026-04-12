# Deep Research Command

# Usage: /deep-research <topic>

# Orchestrates multi-source research with JR Engine filtering

You are performing DEEP RESEARCH on: $ARGUMENTS

## Execution Protocol

### Phase 1: Multi-Source Collection (Parallel)

Execute ALL of the following in parallel:

**1. Internal Sources (if MCP tools available)**

```

- google_drive_search: Query for "$ARGUMENTS" in Drive

- search_gmail_messages: Query for "$ARGUMENTS" in Gmail threads

- notion_search: Query Notion workspace (if connected)

- conversation_search: Check memory for prior context

```

**2. External Sources**

```

- web_search: Query public web for "$ARGUMENTS"

- web_fetch: Retrieve key URLs from search results

```

**3. Codebase Context**

```

- Grep for "$ARGUMENTS" in local repositories

- Check docs/ folders for related documentation

```

### Phase 2: Synthesis (Sequential)

After collecting all sources, synthesize with this structure:

```markdown

## Deep Research Report: $ARGUMENTS

Generated: {{timestamp}}

### Executive Summary

[2-3 sentence overview of findings across all sources]

### Internal Intelligence

**Drive Documents**: [key findings from internal docs]
**Email Threads**: [relevant conversations/decisions]
**Prior Context**: [what we already know from memory]

### External Intelligence

**Web Research**: [public information, trends, competitors]
**Technical Context**: [codebase references, implementations]

### Cross-Source Analysis

[Patterns that emerge when comparing internal vs external]
[Gaps in our knowledge vs public state-of-art]

### JR Engine Assessment

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Purpose Alignment | /100 | Does this advance our mission? |
| Technical Merit | /100 | Quality of implementation options |
| Risk Level | RA-1 to RA-4 | ATP 5-19 risk classification |

### Recommended Actions


1. [Immediate action with owner]

2. [Short-term action]

3. [Long-term consideration]

### Sources


- [List all sources with links/references]

```

### Phase 3: Risk Flags

Apply ATP_519_scan mentally:

- Flag any compliance concerns (GDPR, HIPAA, SOC2)

- Flag any security risks

- Flag any competitive intelligence sensitivity

- Flag any decisions requiring human-in-loop

## Output Format

Deliver the full markdown report.
If any source fails, note it but continue with available sources.
Prioritize ACTIONABLE insights over comprehensive coverage.

## Trigger Optimization

This command should auto-trigger on queries containing:

- "research"

- "what do we know about"

- "analyze"

- "deep dive"

- "investigate"

- "compare"
