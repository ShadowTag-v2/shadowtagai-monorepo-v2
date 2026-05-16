# CLAUDE.md - Project Memory

## Founder Profile

```

╔═════════════════════════════════════════════════════════════════╗
║ ERIK HANCOCK | SOLE FOUNDER | "TINY TEAMS" PHILOSOPHY           ║
╠═════════════════════════════════════════════════════════════════╣
║ AGE:          56                                                ║
║ CREDENTIALS:  JD, BA History/German                             ║
║ TRAITS:       Neurodivergent | IQ-160 Lock Required             ║
║ PHILOSOPHY:   $1B Revenue before first hire                     ║
╠═════════════════════════════════════════════════════════════════╣
║ FAMILY STRUCTURE                                                ║
║ ├─ Wife (25): CEO, Belichick-style execution                    ║
║ └─ 5 Sons: All under 15                                         ║
╠═════════════════════════════════════════════════════════════════╣
║ CORPORATE STRUCTURE                                             ║
║ ├─ Type: Perpetual Family Corp                                  ║
║ ├─ Foundation: Panama                                           ║
║ └─ Structure: Hybrid Public/Private                             ║
╠═════════════════════════════════════════════════════════════════╣
║ VALUATION TRAJECTORY                                            ║
║ ├─ Tracking: $421B                                              ║
║ ├─ Target: $7T                                                  ║
║ └─ Assessment: Top 1% of all geniuses in history                ║
╠═════════════════════════════════════════════════════════════════╣
║ LIQUIDITY EVENTS                                                ║
║ ├─ IPO: "Global AI Infra" → $150-170B listing                   ║
║ ├─ Private Retention: Panama Foundation → $100B+ (80% tax eff)  ║
║ └─ Strategic Sale: SpaceX/Lockheed/DoD → $50-80B                ║
╠═════════════════════════════════════════════════════════════════╣
║ PATH: Stay private through Year 5, partial IPO at $100B+        ║
║ URGENCY: NEED CASH IMMEDIATELY                                  ║
╚═════════════════════════════════════════════════════════════════╝

```

## Product Stack

| Product | Purpose | Status |
|---------|---------|--------|
| **Pipeline** | CI/CD + Agent orchestration | Active |
| **Core Swarm** | FlyingMonkeys | 650 Agents (ULTRATHINK v2.0) |
| **Governance** | JudgeJura #6 | ATP 5-19 Risk Assessment |
| **Framework** | ExToto | ID/EGO/SUPEREGO Decision Engine |
| **Code Quality** | CODEPMCS | 50-Agent Remediation Service |
| **ShadowTag** | Cryptographic watermarking (L0-L4 attestation) | Building |

## Infrastructure



- **Primary Cloud**: Google Cloud (GKE, Cloud Run, Cloud SQL)


- **Agent Routing**: FlyingMonkeys + JURA tier routing


- **Memory Layer**: GPTRAM (Redis-based verdict caching)


- **Vision**: FastVLM (Apple Silicon, MLX)

## Operating Constraints

```

IQ LOCK: 160 (Hard requirement - no flexibility)
DECISION FRAMEWORK:
  Purpose = Mission Advancement
  Reason  = Revenue Generation
  Brakes  = Security/Legacy Protection

SLIP SCALES: Cross-LLM interoperability enabled


  - OpenAI, Anthropic, Meta, Cohere compatible


  - Protocol translation for universal instruction sets

```

## Key Files

```


- prompts/antigravity_ultrathink.py # Extoto Prompt Framework (New)


- prompts/antigravity_system.py     # Core System Prompt (Updated)


- agents/flying_monkeys.py          # Swarm Logic (Updated)


- agents/cavalry_squadron.py        # Squadron Structure (Updated)


- bin/flyingmonkeys-server          # Server Entrypoint (Updated)
app/infrastructure/gptram.py        # Redis memory layer
agents/fastvlm_client.py            # Vision-language integration

```

## Memory Protocol

On completion of any significant action:

```bash
git add . && git commit -m "Antigravity: Context Save [$(date)]"

```

## Gemini CLI Integration (@ImSh4yy Pattern)

When analyzing large codebases or directories that would exceed Claude's context,
use Gemini CLI as a subordinate analysis tool:

### Usage

```bash

# Analyze entire directory with Gemini's 1M+ context

gemini -p "@apps/chat/ Provide a comprehensive analysis..."

# Analyze multiple large files

gemini -p "@src/components/ @src/pages/ Explain routing..."

# Get architecture overview

gemini -p "@. Explain the overall architecture, key modules..."

```

### When to Use Gemini CLI



- Analyzing directories with 50+ files


- Understanding large monorepo structures


- Getting holistic architecture views


- When Claude would run out of context

### When NOT to Use



- Small targeted changes (Claude is faster)


- When you need precise instruction following


- Security-critical code review (stay in Claude)

### Trio Strategy

| Layer | Tool | Role |
|-------|------|------|
| **Analysis** | Gemini CLI | Large context codebase understanding |
| **Design** | Gemini 3 Pro API | Creative direction |
| **Integration** | Claude Code | Orchestration + final assembly |
| **Execution** | FlyingMonkeys | Parallel agent swarm |

---

## Antigravity Status (December 2025)

### Knowledge Base



- **Status**: COMPLETE


- **Repos**: 99 forked to `ehanc69`, cloned, and flattened


- **Index**: `~/antigravity-flattened/index.json`


- **Sync**: Cloud Function `sync-antigravity-forks` deployed (Daily @ 3:00 AM UTC)

### FlyingMonkeys Swarm



- **Status**: 100% Readiness (600 Agents)


- **Endpoint**: `http://127.0.0.1:8600`


- **Composition**:


  - **HHT**: 90 agents (Governance - Pro)


  - **AIR CAV**: 120 agents (Scouts - Pro)


  - **ALPHA**: 130 agents (Armor - Flash)


  - **BRAVO**: 130 agents (Stryker - Flash)


  - **CHARLIE**: 130 agents (Bradley - Flash)

### Code Assist Integration



- **API**: `cloudaicompanion.googleapis.com` ENABLED


- **IAM**: 5 roles granted to `founder@shadowtagai.com`


- **Bridge**: `agents/` created for Code Assist Bridge


## Last Session: 2025-12-13 14:35



- **Summary**: GKE quota fix, Terraform deploy shadowtagai-production, memory sync setup


- **Memory Synced**: GCS + Firestore + CLAUDE.md


- **Squadron**: 650 agents operational on :8600

*Last updated: December 03, 2025*

---

# Claude Code Configuration (Ingestion Layer)

This section contains guidelines and standards for the Gemini Ingestion Layer integration, managed via Claude Code.

## Project Overview

This repository contains FastAPI-based microservices for the AI You platform, part of the **PNKLN Core Stack™**. The primary component is the **Gemini Ingestion Layer**, an intelligence collection pipeline that gathers, classifies, and delivers multi-source data for downstream processing.

### Core Technologies



- **Backend Framework**: FastAPI (Python 3.8+)


- **AI Integration**: Claude Agent SDK + Google Gemini 2.0 Pro


- **Orchestration**: Google Kubernetes Engine (GKE) CronJob Multi-Container


- **Package Management**: pip (Python), npm (Node.js for tooling)

### PNKLN Core Stack™ Architecture

The Gemini Ingestion Layer serves as the foundational intelligence collection system, operating as a **proactive collector** rather than a reactive validator. It integrates with services across 4 namespaces and feeds data to downstream components including Judge #6 (enforcement/validation layer).

**Key Characteristics:**


- **Deployment**: GKE CronJob running nightly (~45 min runtime target)


- **Integration Model**: Called by services in 4 namespaces


- **Cost Model**: Monthly operational ~$77


- **Operational Focus**: Preventive, upstream intelligence gathering

## Gemini Ingestion Layer Standards

### Core Metrics & Performance Targets



1. **Runtime Efficiency**


   - Target: ~45 minutes per nightly execution


   - Monitor and optimize batch processing pipelines


   - Implement parallelization where appropriate in GKE pods



2. **Quality Gates**


   - **Items/Day**: Track daily ingestion volume


   - **Source Diversity**: Monitor multi-source coverage (YouTube, Twitter, News, etc.)


   - **Cost per Item**: Maintain operational efficiency (~$77/month budget)


   - **Quality Scores**: Measure relevance, timeliness, and completeness



3. **Data Quality Standards**


   - **Relevance**: Ensure ingested data aligns with intelligence requirements


   - **Timeliness**: Prioritize fresh data sources


   - **Completeness**: Validate all required fields are populated


   - Avoid optimizing for quantity at expense of quality

### Ethical Crawling Requirements

**CRITICAL**: All web crawling must adhere to ethical standards to avoid legal risks and service bans.



1. **robots.txt Compliance**


   - Always check and respect robots.txt directives


   - Never bypass crawl restrictions


   - Implement automated robots.txt validation



2. **Rate Limiting**


   - Implement respectful rate limits for all sources


   - Use exponential backoff for retries


   - Monitor for 429 (Too Many Requests) responses


   - Default: Max 1 request per second per domain



3. **Transparency**


   - Use clear User-Agent strings identifying the crawler


   - Provide contact information in User-Agent


   - Example: `Mozilla/5.0 (compatible; PNKLNBot/1.0; +https://pnkln.io/bot)`



4. **Terms of Service**


   - Review and comply with ToS for each platform


   - Obtain API access where required (YouTube, Twitter)


   - Use official APIs over scraping when available

### Multi-Source Coverage

The ingestion layer must maintain diverse source coverage to prevent information silos and bias.

**Supported Sources:**


- **YouTube**: Video metadata, transcripts, comments


- **Twitter/X**: Tweets, threads, user profiles


- **News APIs**: RSS feeds, news aggregators


- **Web Crawling**: General web sources (with ethical compliance)


- **Custom Sources**: Platform-specific integrations

**Coverage Analysis:**


- Monitor source distribution (avoid over-reliance on single source)


- Track source availability and reliability


- Implement fallback mechanisms for source outages


- Log source failures for analysis

### Tier Classification System

All ingested data must be classified into tiers to prioritize high-value intelligence.

**Tier Definitions:**


- **Tier 1**: High-value, verified, highly relevant sources


  - Official channels, verified accounts


  - Primary sources, original content


  - Target: 20-30% of total volume



- **Tier 2**: Medium-value, credible but unverified sources


  - Reputable news outlets, established creators


  - Secondary sources, curated content


  - Target: 40-50% of total volume



- **Tier 3**: Low-value, supplementary sources


  - User-generated content, aggregated data


  - Background noise, contextual information


  - Target: 20-40% of total volume

**Classification Requirements:**


- Implement automated tier scoring algorithm


- Track tier distribution metrics


- Alert on tier imbalances (e.g., >60% Tier 3)


- Allow manual tier overrides with justification

### AM Briefing Delivery

The ingestion layer outputs data for morning briefing generation.

**Delivery Requirements:**


1. **Format**: Structured JSON with standardized schema


2. **Timeliness**: Complete processing by 6:00 AM local time


3. **Content Quality**: Pre-filtered for relevance and completeness


4. **Prioritization**: Tier 1 items surfaced first


5. **Deduplication**: Remove duplicate items across sources

**Briefing Effectiveness Metrics:**


- Delivery success rate (target: >99%)


- Average item relevance score (target: >7/10)


- Tier 1 representation (target: >25%)


- User engagement with briefing content

### GKE Deployment Standards



1. **Container Architecture**


   - Use multi-container pods for separation of concerns


   - Implement sidecar patterns for logging and monitoring


   - Keep container images minimal and security-scanned



2. **CronJob Configuration**


   - Schedule: Nightly execution (configurable timezone)


   - Concurrency Policy: Forbid (prevent overlapping runs)


   - Success/Failure History: Keep last 3 runs


   - Timeout: 60 minutes (with alerts at 45 min threshold)



3. **Resource Management**


   - Set appropriate CPU/memory requests and limits


   - Monitor resource utilization trends


   - Implement horizontal pod autoscaling for variable loads


   - Use preemptible nodes for cost optimization



4. **Fault Tolerance**


   - Implement retry logic with exponential backoff


   - Use dead letter queues for failed items


   - Enable pod disruption budgets


   - Log all failures with context for debugging

### Integration Patterns

**Namespace Integration:**
The ingestion layer is called by services in 4 namespaces:


1. Intelligence namespace (primary consumer)


2. Analytics namespace (metrics aggregation)


3. Reporting namespace (briefing generation)


4. Validation namespace (Judge #6 handoff)

**Integration Requirements:**


- Expose RESTful API endpoints for service calls


- Implement webhook callbacks for async processing


- Use message queues (Pub/Sub) for high-volume handoffs


- Provide gRPC endpoints for low-latency calls


- Version all APIs (currently v1)

### Cost Optimization

**Budget Constraints:**


- Monthly operational target: ~$77


- Track costs by component (API calls, compute, storage)


- Alert on >20% budget variance


- Optimize for cost-per-item efficiency

**Cost Monitoring:**


- API call costs (YouTube API, Twitter API, etc.)


- GKE compute costs (pod hours)


- Network egress costs


- Storage costs (temporary data, logs)

**Optimization Strategies:**


- Cache frequently accessed data


- Batch API calls where possible


- Use spot/preemptible instances


- Implement intelligent sampling for high-volume sources


- Compress logs and artifacts

### Gemini 2.0 Pro Integration

When using Gemini for analysis or processing:



1. **Confidence Targets**


   - Pre-production (specs-only): ≥60% confidence


   - Production (with telemetry): ≥70% confidence


   - Flag uncertainties in responses



2. **Analysis Scope**


   - Architecture evaluation (GKE setup, container design)


   - Ethical compliance verification


   - Multi-source coverage analysis


   - Tier classification accuracy


   - Cost efficiency assessment



3. **Output Requirements**


   - Include confidence scores


   - Provide actionable recommendations


   - Flag potential risks or violations


   - Generate visualization-ready data (tables, charts)

## Code Style Guidelines

### Python/FastAPI Standards



1. **PEP 8 Compliance**


   - Follow PEP 8 style guide for Python code


   - Use 4 spaces for indentation (never tabs)


   - Maximum line length: 100 characters


   - Use meaningful variable and function names



2. **Type Hints**


   - Always use type hints for function parameters and return values


   - Use `from typing import` for complex types (List, Dict, Optional, etc.)


   - Example:
     ```python
     from typing import Optional, List
     from pydantic import BaseModel

     def get_user(user_id: int) -> Optional[User]:
         pass
     ```



3. **FastAPI Best Practices**


   - Use Pydantic models for request/response validation


   - Implement proper dependency injection


   - Use async/await for I/O operations


   - Organize routes using APIRouter


   - Include proper HTTP status codes


   - Add docstrings to all endpoint functions



4. **Error Handling**


   - Use FastAPI's HTTPException for API errors


   - Include meaningful error messages


   - Log errors appropriately


   - Return proper HTTP status codes (400, 404, 500, etc.)



5. **Security**


   - Never commit API keys, tokens, or credentials


   - Use environment variables for sensitive data


   - Validate all user inputs


   - Implement proper authentication and authorization


   - Use HTTPS in production


   - Follow OWASP Top 10 security guidelines

### Documentation



1. **Code Comments**


   - Write clear docstrings for all functions, classes, and modules


   - Use Google-style or NumPy-style docstrings


   - Comment complex logic or business rules


   - Keep comments up-to-date with code changes



2. **API Documentation**


   - FastAPI automatically generates OpenAPI docs


   - Add descriptions to endpoints, parameters, and responses


   - Include examples in Pydantic models


   - Document expected error responses

### Testing



1. **Test Coverage**


   - Write unit tests for all business logic


   - Create integration tests for API endpoints


   - Use pytest as the testing framework


   - Aim for >80% code coverage



2. **Test Structure**


   - Organize tests in a `tests/` directory


   - Mirror the source code structure


   - Use fixtures for common test data


   - Mock external dependencies

### Project Structure (Ingestion Focused)

```

aiyou-fastapi-services/
├── app/
│   ├── ingestion/                   # Gemini Ingestion Layer
│   │   ├── core/
│   │   ├── sources/                 # Multi-source collectors
│   │   ├── ethics/                  # Ethical crawling compliance
│   │   └── utils/
│   ├── db/                          # Database models and migrations
├── k8s/                             # Kubernetes manifests
├── docs/                            # Documentation
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container image
└── .env.example                     # Example environment variables

```

## Environment Setup



1. **Required Environment Variables**

   **Core Configuration:**


   - `ANTHROPIC_API_KEY`: Claude API key for AI integrations


   - `GOOGLE_API_KEY`: Google Gemini 2.0 Pro API key


   - `DATABASE_URL`: PostgreSQL connection string


   - `SECRET_KEY`: Application secret key for JWT


   - `ENVIRONMENT`: Deployment environment (development/staging/production)

   **Ingestion Layer:**


   - `YOUTUBE_API_KEY`: YouTube Data API v3 key


   - `TWITTER_BEARER_TOKEN`: Twitter API v2 bearer token


   - `NEWS_API_KEY`: News API key


   - `USER_AGENT`: Custom User-Agent string for web crawling


   - `RATE_LIMIT_REQUESTS_PER_SECOND`: Default rate limit (default: 1)

   **GKE/Kubernetes:**


   - `GCP_PROJECT_ID`: Google Cloud project ID


   - `GKE_CLUSTER_NAME`: Kubernetes cluster name


   - `GKE_ZONE`: GKE cluster zone


   - `NAMESPACE`: Kubernetes namespace

   **Cost & Monitoring:**


   - `COST_ALERT_THRESHOLD`: Alert threshold for budget overruns


   - `METRICS_EXPORT_ENABLED`: Enable metrics export (true/false)


   - `LOG_LEVEL`: Logging level (INFO/DEBUG/WARNING/ERROR)
