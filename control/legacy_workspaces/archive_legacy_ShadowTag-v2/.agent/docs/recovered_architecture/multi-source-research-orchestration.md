# Multi-Source Research Orchestration

## Overview

**Type**: orchestration
**Enforcement**: auto-trigger
**Priority**: high

This skill automatically orchestrates parallel research across multiple data sources (Drive, Gmail, Web, Memory, Codebase) and synthesizes findings into structured intelligence reports with JR Engine assessment.

**Auto-Activation**: Triggers automatically on research intent - NO slash command required.

---

## Trigger Detection

### Keywords (immediate activation)
- `research`, `investigate`, `deep dive`
- `what do we know about`, `gather information`, `look into`
- `compare`, `evaluate`, `prior art`
- `competitive analysis`, `market research`
- `intel`, `intelligence`, `summarize from`

### Intent Patterns
- `(research|investigate|analyze) [topic]`
- `what do we know about [topic]?`
- `deep dive into [topic]`
- `compare [options]`
- `gather information on [topic]`

---

## Execution Protocol

### Phase 1: Parallel Source Collection

Execute ALL available sources simultaneously:

```
PARALLEL EXECUTION BLOCK
========================

Internal Sources (MCP tools - if available):
├─ google_drive_search / mcp__gdrive__search
│  Query: Extract key terms from user query
│  Returns: Document titles, snippets, links
│
├─ search_gmail_messages / mcp__gmail__search
│  Query: Same key terms, last 6 months default
│  Returns: Thread subjects, participants, dates
│
└─ conversation_search / memory_search
   Query: Topic keywords
   Returns: Prior context, established decisions

External Sources (always available):
├─ WebSearch
│  Query: "[topic] [current year]"
│  Returns: Public information, market data
│
└─ WebFetch (for key URLs from search)
   Retrieve: Full content of most relevant pages

Local Sources (always available):
├─ Grep
│  Pattern: Topic keywords in codebase
│  Path: Project root
│
└─ Read
   Path: docs/, README files
   Returns: Internal documentation
```

### Phase 2: Result Processing

After parallel collection completes:

1. **Aggregate** results from all sources
2. **Deduplicate** overlapping information
3. **Categorize** by source type (internal/external/local)
4. **Identify** patterns across sources
5. **Flag** gaps in coverage

### Phase 3: Synthesis & Report Generation

Generate structured output with cross-source analysis.

---

## Output Template

```markdown
## Research Report: [TOPIC]

**Generated**: [TIMESTAMP]
**Sources Queried**: [N] | **Successful**: [N]

---

### Executive Summary

[2-3 sentences synthesizing key findings across all sources]

---

### Internal Intelligence

#### Drive Documents ([N] found)

| Document | Type | Key Finding | Date |
|----------|------|-------------|------|
| [name] | [doc/sheet/slides] | [insight] | [date] |

#### Email Threads ([N] threads)

| Subject | Key Decision/Context | Participants | Date |
|---------|---------------------|--------------|------|
| [subject] | [decision] | [names] | [date] |

#### Prior Context (Memory)

- [What we've discussed before about this topic]
- [Established decisions or preferences]
- [Historical context]

---

### External Intelligence

#### Web Research ([N] results)

| Source | Key Finding | Credibility | Date |
|--------|-------------|-------------|------|
| [url] | [insight] | High/Med/Low | [date] |

#### Codebase References ([N] matches)

| File | Reference | Relevance |
|------|-----------|-----------|
| [path:line] | [snippet] | High/Med/Low |

---

### Cross-Source Analysis

**Convergent Findings** (High Confidence):
- [Finding that appears in multiple sources]

**Internal-Only Knowledge** (Proprietary):
- [What we know that public doesn't]

**External-Only Knowledge** (Gaps):
- [What public knows that we haven't captured]

**Contradictions** (Requires Resolution):
- [Internal says X, external says Y]

---

### JR Engine Assessment

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Purpose Alignment | [X]/100 | [Does this advance our mission?] |
| Technical Merit | [X]/100 | [Quality of implementation options] |
| Risk Level | RA-[1-4] | [ATP 5-19 risk classification] |

**Risk Flags**:
- [ ] Compliance concerns (GDPR, HIPAA, SOC2)
- [ ] Security risks
- [ ] Competitive intelligence sensitivity
- [ ] Requires human-in-loop decision

---

### Recommended Actions

**Immediate** (This Week):
1. [Action with owner]

**Short-Term** (This Month):
1. [Action]

**Long-Term** (Backlog):
1. [Action]

---

### Sources

**Internal**:
- [Document/email identifiers]

**External**:
- [URLs with access dates]

**Memory**:
- [Conversation references]
```

---

## Source Availability Handling

### Check Before Execution

```
Available Tools Check:
├─ google_drive_search: [available/unavailable]
├─ search_gmail_messages: [available/unavailable]
├─ conversation_search: [available/unavailable]
├─ notion_search: [available/unavailable]
├─ WebSearch: [always available]
├─ WebFetch: [always available]
├─ Grep: [always available]
└─ Read: [always available]
```

### Graceful Degradation

When MCP tools unavailable:

```markdown
**Source Availability Note**:
- Google Drive: [Not connected - MCP tool unavailable]
- Gmail: [Not connected - MCP tool unavailable]
- Memory: [Available]
- Web: [Available]
- Codebase: [Available]

*For comprehensive internal research, connect Google Drive and Gmail MCP tools.*
```

**Rules**:
- Note unavailable sources transparently
- Continue with available sources
- Never block on missing tools
- Suggest connecting unavailable tools

---

## Examples

### Example 1: Business Research

**Query**: "Research our competitor analysis for Q4 planning"

**Execution**:
```
├─ Drive: "competitor analysis Q4" → 3 docs found
├─ Gmail: "competitor analysis" → 5 threads
├─ Web: "competitor analysis [industry] 2024" → 10 results
└─ Memory: "competitor" → 2 prior discussions
```

**Result**: Synthesized report combining internal strategy docs, email discussions with stakeholders, current market data, and prior conversation context.

### Example 2: Technical Research

**Query**: "What do we know about implementing OAuth 2.0?"

**Execution**:
```
├─ Drive: "OAuth 2.0 implementation" → 2 docs
├─ Gmail: "OAuth" → 3 threads (security team)
├─ Web: "OAuth 2.0 best practices 2024" → current standards
├─ Codebase: grep "oauth" → existing implementations
└─ Memory: → prior auth discussions
```

**Result**: Report combining internal security guidelines, email decisions, current best practices, and existing OAuth code in codebase.

### Example 3: Decision Support

**Query**: "Help me understand our options for the new database"

**Execution**:
```
├─ Drive: "database selection" → architecture docs
├─ Gmail: "database" → stakeholder discussions
├─ Web: "database comparison [use case] 2024" → current options
└─ Memory: → prior database conversations
```

**Result**: Decision matrix with internal requirements, stakeholder preferences from emails, current market options, and prior context.

---

## Anti-Patterns

### DO NOT:
- Execute sources sequentially when they can run in parallel
- Provide only web results when internal sources are available
- Skip sources without noting they were unavailable
- Provide raw results without synthesis
- Wait for user to request multi-source research - DO IT AUTOMATICALLY

### DO:
- Always attempt ALL available sources
- Note unavailable sources transparently
- Synthesize across sources, don't just list results
- Highlight cross-source patterns and discrepancies
- Provide actionable recommendations

---

## Integration

**Related Skills**:
- `brainstorming` - Use research results to inform design exploration
- `writing-plans` - Use research to ground implementation plans
- `aiyoujr-judge` - Apply judgment framework to research findings

**Related Commands**:
- `/deep-research` - Explicit invocation (same behavior)

---

## Key Principles

1. **AUTOMATIC ACTIVATION**: Triggers on research intent without explicit command
2. **PARALLEL BY DEFAULT**: All sources execute simultaneously
3. **SYNTHESIS OVER LISTING**: Combine and analyze, don't just dump results
4. **TRANSPARENT LIMITATIONS**: Always note unavailable sources
5. **ACTIONABLE OUTPUT**: Research should lead to recommendations
