# TECHNICAL_SLA - Performance Standards & Core Stack Specifications

**Version**: 1.0
**Last Updated**: 2025-11-14
**Purpose**: Define technical performance requirements, architecture principles, and stack standards for Pnkln systems

---

## OVERVIEW

This document establishes the technical service level agreements (SLAs), performance targets, and architectural standards that govern all Pnkln engineering decisions.

**Core Principle**: Technical choices must support bootstrap constraints (cost-efficient), customer needs (performant), and strategic goals (scalable within limits).

---

## PRIMARY SYSTEM: JUDGE #6 (Cor Decision Engine)

### Performance Targets

**Latency Requirements**:

```

p99 (99th percentile): ≤90ms
p95 (95th percentile): ≤60ms
p50 (median):          ≤30ms
p90 (90th percentile): ≤45ms

```

**Current Status** (as of 2025-11-14):

```

p99: ~150ms (67ms OVER target ❌)
p50: ~35ms  (5ms OVER target ⚠️)

```

**Target Achievement**: 30-day sprint to reach p99≤90ms

**Availability**:

```

Monthly Uptime SLA: 99.9% (≤43 minutes downtime per month)
Target Uptime:      99.95% (≤22 minutes downtime per month)
Maximum Consecutive Downtime: 15 minutes

```

**Throughput**:

```

Concurrent Decisions: 100 simultaneous requests
Peak Load:            500 requests per minute
Sustained Load:       200 requests per minute (average)

```

**Error Rate**:

```

Maximum Error Rate: 0.1% of requests
Target Error Rate:  <0.05% of requests
Critical Errors:    <0.01% (data loss, corruption, security)

```

### Measurement & Monitoring

**Latency Tracking**:

- **Tool**: Datadog APM (or equivalent observability platform)

- **Frequency**: Real-time monitoring, 1-minute aggregation

- **Alerting**:

  - p99 >120ms for 5 minutes → WARNING

  - p99 >150ms for 10 minutes → CRITICAL

  - p99 >200ms for 7 days → KILL-SWITCH (rollback changes)

**Uptime Tracking**:

- **Tool**: Uptime monitoring (Pingdom, UptimeRobot, or similar)

- **Frequency**: 1-minute health checks

- **Alerting**:

  - 5 consecutive failed checks → ALERT

  - 15 minutes downtime → CRITICAL

  - 99.5% monthly uptime → REVIEW (missed target)

**Error Rate Tracking**:

- **Tool**: Application logs + error tracking (Sentry, Rollbar)

- **Frequency**: Real-time error capture

- **Alerting**:

  - Error rate >0.2% for 10 minutes → WARNING

  - Critical error detected → IMMEDIATE ALERT

  - 3+ critical errors in 24 hours → INCIDENT

### Performance Budget

Every feature/change must declare its **performance budget**:

```

FEATURE: [Name]
LATENCY IMPACT: [+/- Xms on p99]
JUSTIFICATION: [Why this cost is acceptable]
MITIGATION: [How we'll minimize impact]

```

**Example**:

```

FEATURE: Add ERCOT price history lookup
LATENCY IMPACT: +15ms on p99 (database query)
JUSTIFICATION: Customer-requested, enables $50K ARR feature
MITIGATION:

  - Cache recent history (reduces 80% of queries to <5ms)

  - Index on timestamp + market_id (ensures query <10ms)

  - Async prefetch for predicted requests (eliminates wait)

  - NET IMPACT: +5ms p99 (within acceptable tolerance)

```

**Approval Rules**:

- **<10ms impact**: Auto-approve (document only)

- **10-25ms impact**: Requires mitigation plan

- **>25ms impact**: Requires JR_ENGINE review + compensation (what gets faster?)

---

## CORE STACK REQUIREMENTS

### Language & Runtime

**Primary Language: Python**

```

Version:      3.11+ (minimum)
Preferred:    3.12 (latest stable)
Rationale:    Performance improvements, type hints, ecosystem maturity
Constraints:  Avoid bleeding-edge (3.13) until 6 months post-release

```

**Secondary Language: TypeScript**

```

Version:      5.0+ (minimum)
Preferred:    5.3+ (latest stable)
Use Cases:    Tooling, SDK, web interfaces
Rationale:    Type safety, ecosystem, team familiarity

```

**Language Selection Criteria**:

- **Python**: Backend APIs, data processing, ML/AI, core logic

- **TypeScript**: Frontend, tooling, SDKs, integrations

- **Avoid**: Ruby, PHP, Java (team unfamiliar, ecosystem overhead)

- **Evaluate**: Go, Rust (only if performance critical AND Python insufficient)

### Web Framework

**API Framework: FastAPI**

```

Version:      0.100+ (minimum)
Rationale:    Async performance, type safety, OpenAPI auto-gen, Python 3.11+ support
Alternatives: Flask (too slow), Django (too heavy), Raw ASGI (too low-level)

```

**Frontend Framework: React**

```

Version:      18+ (minimum)
Rationale:    Ecosystem, team familiarity, component reusability
State:        Zustand or Jotai (avoid Redux complexity)
Routing:      React Router v6+

```

**Framework Constraints**:

- No framework churn (stick with chosen framework for 12+ months)

- Avoid pre-1.0 frameworks (stability risk)

- Prefer boring, proven technology

### Database

**Primary Database: PostgreSQL**

```

Version:      15+ (minimum, prefer 16+)
Rationale:    ACID compliance, JSON support, performance, reliability
Use Cases:    Primary data storage (users, transactions, decisions)
Constraints:  Single instance (bootstrap), no sharding until 100K+ rows

```

**Caching Layer: Redis**

```

Version:      7.0+ (minimum)
Rationale:    In-memory speed, key-value simplicity, Python ecosystem
Use Cases:    Session storage, rate limiting, hot data cache
Constraints:  <10GB memory footprint (cost control)

```

**Data Warehouse: Deferred**

```

Decision:     Defer until 50+ customers or 1M+ rows
Rationale:    PostgreSQL sufficient for bootstrap scale
Future:       BigQuery, Snowflake, or Clickhouse (evaluate when needed)

```

**Database Principles**:

- **Indexes**: Every query must have supporting index (auto-explain plans)

- **Migrations**: Versioned, reversible, tested in staging

- **Backups**: Daily automated backups, 30-day retention, tested restore

- **Scaling**: Vertical first (bigger instance), horizontal only if required

### Infrastructure

**Cloud Provider: Cloud-Agnostic (AWS preferred)**

```

Primary:      AWS (current)
Rationale:    Ecosystem, tooling, team familiarity
Constraint:   Avoid vendor lock-in (use portable patterns)
Portability:  Code must run on AWS, GCP, Azure, or bare metal

```

**Deployment: Containerized (Docker)**

```

Orchestration: Kubernetes (deferred), Docker Compose (bootstrap)
Rationale:     Portability, reproducibility, simplicity at scale
Constraint:    No Kubernetes until 10+ services or 24/7 ops required

```

**CI/CD: GitHub Actions**

```

Pipeline:     Lint → Test → Build → Deploy
Frequency:    On every push (main branch), manual prod deploy
Rationale:    Free for public repos, tight GitHub integration

```

**Infrastructure Principles**:

- **Boring Technology**: Prefer 5+ year old, well-understood tools

- **Cost-Conscious**: Optimize for $/performance, not absolute performance

- **Portable**: Avoid lock-in, use open standards (Postgres, not DynamoDB)

- **Automated**: Infrastructure as code (Terraform, CloudFormation)

### Observability

**Logging**:

```

Format:       Structured JSON (logs parseable by machines)
Levels:       DEBUG, INFO, WARNING, ERROR, CRITICAL
Retention:    30 days (free tier) → 90 days (paid, when profitable)
Tool:         CloudWatch Logs (AWS), or equivalent

```

**Metrics**:

```

What:         Request latency, error rates, throughput, DB query time
Frequency:    1-minute aggregation
Tool:         Datadog (current), Prometheus + Grafana (future cost optimization)

```

**Tracing**:

```

What:         Distributed traces for multi-service requests
Sampling:     10% (bootstrap), 100% for errors
Tool:         Datadog APM, OpenTelemetry (when vendor-agnostic needed)

```

**Alerting**:

```

Channels:     Slack (low urgency), PagerDuty (high urgency, when funded)
Response:     <5 minutes acknowledge, <30 minutes mitigate, <24 hours resolve
On-Call:      Founder-only (bootstrap), rotate when team >3 engineers

```

**Observability Principles**:

- **Default to Observable**: All services emit logs, metrics, traces

- **Alert on Symptoms**: User impact (latency, errors), not causes (CPU, memory)

- **Runbooks**: Every alert has runbook (diagnosis + mitigation steps)

- **Blameless Postmortems**: Learn from incidents, improve systems

---

## ARCHITECTURE PRINCIPLES

### 1. Modularity

**Principle**: Components should be testable in isolation.

**Practice**:

- **Interfaces**: Define clear contracts (APIs, function signatures, types)

- **Dependency Injection**: Pass dependencies explicitly (avoid global state)

- **Unit Tests**: Every module has unit tests (80%+ coverage target)

- **Integration Tests**: Cross-module behavior tested separately

**Anti-Pattern**:

- Tight coupling (Module A directly imports Module B internals)

- Circular dependencies (A depends on B, B depends on A)

- Untestable code (requires production database to test)

### 2. Resilience

**Principle**: Systems should degrade gracefully under failure.

**Practice**:

- **Circuit Breakers**: Fail fast when downstream service unavailable

- **Retries**: Exponential backoff for transient failures (3 retries max)

- **Timeouts**: Every external call has timeout (5s default, 30s max)

- **Fallbacks**: Serve stale data or degraded experience vs. complete failure

**Example**:

```python

# Good: Circuit breaker + fallback

try:
    price = fetch_ercot_price(timeout=5s)
except Timeout:
    price = get_cached_price()  # Fallback to 15-min-old cache
except ServiceUnavailable:
    price = None  # Degrade gracefully, show "unavailable"

```

**Anti-Pattern**:

- No timeouts (hang forever on slow external service)

- Fail entire request if one non-critical component fails

- Retry indefinitely (amplifies downstream failure)

### 3. Efficiency

**Principle**: Optimize for p99 latency, not just average.

**Practice**:

- **Profile Before Optimize**: Measure where time is spent (Datadog, cProfile)

- **Cache Aggressively**: Hot data in Redis, cold data in Postgres

- **Batch Operations**: Reduce round-trips (fetch 100 rows, not 100×1 row)

- **Async I/O**: Use async/await for I/O-bound operations (FastAPI native)

**Latency Budget Breakdown** (Judge 6 target p99≤90ms):

```

API Gateway:           5ms
Authentication:        5ms
Request Validation:    5ms
Business Logic:       10ms
Database Query:       30ms
Response Serialization: 5ms
Network Overhead:     10ms
Buffer (safety):      20ms
TOTAL:                90ms

```

**Anti-Pattern**:

- Premature optimization (optimize before measuring)

- N+1 queries (loop over 100 items, query DB each time)

- Synchronous I/O in async context (blocks event loop)

### 4. Simplicity

**Principle**: Prefer boring technology, avoid premature complexity.

**Practice**:

- **Monolith First**: Single codebase until clear service boundaries

- **SQL Over NoSQL**: Postgres until proven insufficient

- **Standard Patterns**: Use well-known patterns (MVC, Repository, Factory)

- **Delete Code**: Best code is no code (remove unused features)

**Complexity Checklist** (before adding complexity):

1. Is there a simpler solution? (probably yes)

2. Can we defer this decision? (probably yes)

3. What's the cost of being wrong? (usually low)

4. Can we reverse this easily? (prefer reversible)

**Anti-Pattern**:

- Microservices prematurely (adds network, deployment, coordination overhead)

- Novel architecture (unproven, team learning curve, hard to hire for)

- Over-engineering (YAGNI: You Ain't Gonna Need It)

### 5. Security

**Principle**: Security is not optional, but must be risk-appropriate.

**Practice**:

- **Authentication**: OAuth2 + JWT tokens (short-lived, refresh flow)

- **Authorization**: Role-based access control (RBAC), least privilege

- **Encryption**: TLS for transit, encryption at rest for PII

- **Input Validation**: Sanitize all user input (prevent injection attacks)

- **Secrets Management**: Never commit secrets (use env vars, secret managers)

- **Dependency Scanning**: Automated CVE scanning (Dependabot, Snyk)

**Risk-Appropriate Security**:

- **High Risk**: Financial transactions, PII → Full security stack

- **Medium Risk**: Business data → Standard security practices

- **Low Risk**: Public data, non-sensitive → Basic security hygiene

**Anti-Pattern**:

- Storing passwords in plaintext (use bcrypt, Argon2)

- SQL injection vulnerable (use parameterized queries)

- Secrets in code/commits (use environment variables)

- No rate limiting (vulnerable to DoS)

---

## TECHNICAL DEBT MANAGEMENT

### Definition

**Technical Debt**: Code/architecture shortcuts taken to ship faster, with intention to refactor later.

**Types**:

1. **Deliberate**: Conscious decision to defer quality for speed (acceptable if documented)

2. **Accidental**: Didn't know better at the time (learn and improve)

3. **Bit Rot**: Code aging as ecosystem evolves (dependencies, security)

### Tracking

**Debt Register** (maintain in codebase):

```

TECHNICAL DEBT LOG
==================

[DEBT-001] ERCOT integration uses synchronous HTTP (should be async)

  - Created: 2025-11-01

  - Impact: Adds ~20ms to p99 latency

  - Mitigation: Acceptable for MVP, refactor when >50 customers

  - Effort: 2 days

  - Priority: Medium (after revenue validation)

[DEBT-002] No automated integration tests for Judge 6

  - Created: 2025-10-15

  - Impact: Risky deploys, manual testing required

  - Mitigation: Founder testing each deploy

  - Effort: 3 days

  - Priority: High (schedule in Q1 2026)

```

### Repayment Strategy

**Budget**: 20% of engineering time for debt repayment

- **Every Sprint**: Reserve 1 day/week for refactoring, tests, upgrades

- **Quarterly**: Dedicate 1 week to major debt items

- **Opportunistic**: Pay debt when touching related code

**Prioritization**:

1. **Critical**: Blocks revenue, security risk, or SLA violation → FIX NOW

2. **High**: Slows development, risky, or accumulating interest → SCHEDULE

3. **Medium**: Quality-of-life, maintainability → OPPORTUNISTIC

4. **Low**: Nice-to-have, cosmetic → DEFER (maybe never)

**Anti-Pattern**:

- Ignoring debt until crisis (interest compounds)

- Rewriting everything (expensive, risky, delays revenue)

- Perfect code (diminishing returns, delays shipping)

---

## PERFORMANCE OPTIMIZATION PLAYBOOK

### When p99 Latency Exceeds Target (>90ms for Judge 6)

**STEP 1: Measure** (1 day)

- Enable detailed profiling (Datadog APM, cProfile)

- Identify slowest 10 requests (p99+ outliers)

- Breakdown: API → DB → Logic → Network

**STEP 2: Identify Bottleneck** (1 day)

- **If DB >50ms**: Query optimization (indexes, N+1, batch)

- **If Logic >20ms**: Algorithm optimization (caching, precompute)

- **If Network >20ms**: Reduce payload size, compression, CDN

**STEP 3: Optimize** (3-5 days)

- **Database**: Add indexes, query tuning, connection pooling

- **Caching**: Redis for hot data, memoization for expensive functions

- **Algorithm**: Replace O(n²) with O(n log n), precompute when possible

- **Infrastructure**: Upgrade instance size (vertical scaling)

**STEP 4: Validate** (1 day)

- Deploy to staging, load test with production-like traffic

- Measure p99 improvement (target: 30%+ reduction)

- Check for regressions (other metrics didn't degrade)

**STEP 5: Deploy + Monitor** (ongoing)

- Canary deploy (10% → 50% → 100% traffic)

- Monitor p99 for 7 days

- Document optimization in debt register

**Example Optimization**:

```

BEFORE: p99 = 150ms

  - DB query: 80ms (no index on timestamp column)

  - Logic: 30ms (JSON serialization)

  - API: 40ms (overhead + network)

OPTIMIZATIONS:

  1. Add index on timestamp → DB query 15ms (65ms saved)

  2. Cache serialized JSON → Logic 10ms (20ms saved)

AFTER: p99 = 65ms (85ms saved, target ≤90ms ACHIEVED ✅)

```

---

## KILL-SWITCH CRITERIA (Technical)

**Latency Kill-Switch**:

- **Trigger**: p99 >200ms for 7 consecutive days

- **Action**: Rollback last 3 deploys, emergency optimization sprint

**Uptime Kill-Switch**:

- **Trigger**: Availability <99.5% for 30 days

- **Action**: Incident review, architectural changes required

**Error Rate Kill-Switch**:

- **Trigger**: Error rate >1% for 24 hours

- **Action**: Rollback to last stable version, hotfix within 48 hours

**Security Kill-Switch**:

- **Trigger**: Critical CVE in dependency (CVSS ≥9.0) OR active exploit

- **Action**: Immediate patch deployment, customer notification if data exposed

---

## INTEGRATION WITH OTHER FRAMEWORKS

**TECHNICAL_SLA** provides:

- **BRAKES** for **JR_ENGINE** (performance constraints, tech debt limits)

- **Cost inputs** for **BOOTSTRAP_GATES** (infrastructure spend, efficiency)

- **Risk factors** for **RISK_FRAMEWORK** (technical risks, failure modes)

**Workflow**:

1. Technical decision proposed (e.g., add feature, change architecture)

2. Check TECHNICAL_SLA compliance (latency budget, stack requirements)

3. Run JR_ENGINE with TECHNICAL_SLA as BRAKES input

4. Monitor SLA metrics post-deployment (validate assumptions)

---

## MAINTENANCE

**Update Schedule**:

- **Monthly**: Latency targets (if improved), error rates (actual vs. target)

- **Quarterly**: Stack versions (upgrade to latest stable), debt register review

- **Ad-hoc**: SLA thresholds (if business needs change, e.g., enterprise customers)

**Change Log**:

- Track all changes to SLA targets, stack requirements, architecture principles

- Document rationale (why did we change p99 target from 100ms → 90ms?)

- Version control in Cor_vX.md

---

## QUICK REFERENCE

**Judge 6 SLA**:

- p99≤90ms, p50≤30ms, 99.9% uptime, <0.1% errors, 100 concurrent

**Core Stack**:

- Python 3.11+, FastAPI, PostgreSQL 15+, Redis 7+, Docker

- Cloud-agnostic (AWS preferred), GitHub Actions CI/CD

- Datadog (observability), structured logging

**Architecture**:

- Modular (testable), Resilient (circuit breakers), Efficient (p99 focus), Simple (boring tech), Secure (risk-appropriate)

**Technical Debt**:

- 20% time budget, tracked in debt register, prioritize critical/high

**Kill-Switches**:

- p99>200ms for 7 days, uptime<99.5% for 30 days, errors>1% for 24 hours, critical CVE

---

**END TECHNICAL_SLA.md**
