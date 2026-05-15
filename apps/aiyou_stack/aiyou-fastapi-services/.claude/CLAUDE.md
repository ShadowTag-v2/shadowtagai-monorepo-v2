# Claude Code Configuration - ShadowTag-v2 FastAPI Services

## Project Overview

This repository contains the PNKLN Core Stack™ implementation, focusing on the Gemini Ingestion Layer and related intelligence pipeline components.

**Tech Stack**:
- **Backend**: FastAPI (Python)
- **Infrastructure**: Google Kubernetes Engine (GKE)
- **Execution**: CronJob-based batch processing
- **AI**: Gemini 2.0 Pro for analysis and intelligence processing

## Quick Commands

```bash
# Development
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Testing
pytest
pytest --cov

# Linting
ruff check .
mypy .

# Format
ruff format .
```

## Dev Docs Workflow

### Starting Large Tasks

When exiting plan mode with an accepted plan:

1. **Create Task Directory**:
   ```bash
   mkdir -p ~/git/shadowtag_v4-fastapi-services/dev/active/[task-name]/
   ```

2. **Create Documents**:
   - `[task-name]-plan.md` - The accepted plan from planning mode
   - `[task-name]-context.md` - Key files, architectural decisions, dependencies
   - `[task-name]-tasks.md` - Checklist of specific work items

3. **Update Regularly**: Mark tasks complete immediately after finishing each one

### Continuing Tasks

- Check `/dev/active/` for existing tasks before starting work
- Read all three files (plan, context, tasks) before proceeding
- Update "Last Updated" timestamps in each file
- Add new context or tasks as they're discovered during implementation
- Move completed tasks to `/dev/completed/` when fully done

### Context File Best Practices

The context file should include:
- File paths of key components
- Architectural decisions made
- Integration points and dependencies
- Any assumptions or constraints
- Next steps or blockers

## Documentation Structure

```
docs/
├── architecture/        # System design, PNKLN stack diagrams
├── analysis/           # Gemini analysis reports, comparisons
├── prompts/            # Analysis prompts for Gemini 2.0 Pro
└── guides/             # How-to guides and runbooks

dev/
├── active/             # Current feature development (plan/context/tasks)
└── completed/          # Archived completed features
```

## Planning Process

**IMPORTANT**: Always use planning mode before implementing features.

1. **Enter Planning Mode**: Use Claude Code's planning mode or run a planning agent
2. **Research Phase**: Let Claude gather context about the codebase
3. **Review Plan**: Thoroughly review the generated plan for accuracy
4. **Create Dev Docs**: Run `/create-dev-docs` to convert plan into dev doc files
5. **Implement Incrementally**: Work through tasks one section at a time
6. **Update Context**: Keep the context file updated as you work
7. **Review Before Compaction**: Run `/update-dev-docs` when approaching context limits

## Code Quality Standards

### FastAPI Best Practices

- Use Pydantic models for all request/response schemas
- Implement dependency injection for services and repositories
- Follow REST conventions for endpoint naming
- Add OpenAPI documentation to all endpoints
- Use async/await for I/O operations

### Error Handling

- Always use try/except for external API calls
- Log errors with appropriate context
- Return appropriate HTTP status codes
- Use custom exception classes for domain errors

### Testing

- Write tests for all new endpoints
- Use pytest fixtures for common setup
- Mock external dependencies
- Aim for >80% code coverage on new code

## Ethical Compliance (Ingestion Layer)

When working on data collection components:

1. **Robots.txt Compliance**: Always respect crawler directives
2. **Rate Limiting**: Implement throttling for all external sources
3. **Transparency**: Include clear user-agent strings with contact info
4. **Error Handling**: Gracefully handle source outages or bans

## GKE Deployment

For Kubernetes-related changes:

- Test locally with Docker first
- Update manifests in `/k8s/` directory
- Follow namespace conventions (ingestion-ns, storage-ns, etc.)
- Document resource limits and requests
- Update deployment docs when changing architecture

## Project-Specific Conventions

### Tier Classification

Data sources are classified into tiers:
- **Tier 1**: High-value, authoritative sources (priority processing)
- **Tier 2**: Supplementary sources (standard processing)
- **Tier 3**: Low-priority or experimental sources (best-effort)

### AM Briefing System

When modifying briefing delivery:
- Target delivery time: 6 AM daily
- Format: Markdown with clear sections
- Include: Daily summary, trends, critical events
- Test: Validate formatting before deployment

## Common Pitfalls to Avoid

1. **Don't skip planning**: Even small features benefit from a plan
2. **Don't leave errors**: Run builds and tests before moving on
3. **Don't hardcode**: Use environment variables and config files
4. **Don't ignore ethics**: Ethical compliance is non-negotiable for crawlers
5. **Don't optimize prematurely**: Get it working, then make it fast

## Skills and Agents

### Available Skills

(To be created as needed):
- `backend-dev-guidelines` - FastAPI, Pydantic, async patterns
- `gke-deployment` - Kubernetes best practices
- `data-ingestion-patterns` - Ethical crawling, tier classification
- `testing-strategies` - Pytest patterns, mocking, fixtures

### Available Agents

(To be created as needed):
- `code-architecture-reviewer` - Reviews code for best practices
- `test-generator` - Creates pytest test cases
- `api-documenter` - Generates OpenAPI documentation

## References

- [PNKLN Core Stack Architecture](../docs/architecture/pnkln-core-stack.md)
- [Gemini Ingestion Layer Analysis](../docs/analysis/gemini-ingestion-layer-analysis.md)
- [Judge #6 vs Ingestion Comparison](../docs/analysis/judge-6-vs-ingestion-comparison.md)

## Notes

- This project follows patterns from [Claude Code hardcore use guide](https://www.reddit.com/r/ClaudeAI/comments/1oivjvm/claude_code_is_a_beast_tips_from_6_months_of/)
- We prioritize planning, documentation, and incremental implementation
- Quality > Speed: Get it right first, optimize later
- Ethics matter: Especially for data collection components

---

**Last Updated**: 2025-11-15
**Review**: Update this file when major architectural changes occur
