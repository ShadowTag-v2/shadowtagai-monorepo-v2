# Ethical Crawling Guidelines

## Overview

The Gemini Ingestion Layer adheres to strict ethical standards for web data collection. This document outlines the policies, technical implementations, and compliance measures that ensure responsible intelligence gathering.

## Core Principles

1. **Respect**: Honor website owners' wishes via robots.txt
2. **Transparency**: Clearly identify ourselves and our purpose
3. **Responsibility**: Avoid overloading servers or causing harm
4. **Legality**: Comply with all applicable laws and terms of service
5. **Privacy**: Minimize collection of personal information

## robots.txt Compliance

### Implementation

**Fetching robots.txt**:
```python
import urllib.robotparser

def check_robots_permission(url: str) -> bool:
    """Check if URL is allowed by robots.txt."""
    rp = urllib.robotparser.RobotFileParser()
    robots_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}/robots.txt"

    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("PNKLN-Ingestion-Bot", url)
    except Exception as e:
        # Default to disallow on error
        logger.warning(f"robots.txt fetch failed for {robots_url}: {e}")
        return False
```

**Caching Strategy**:
- Cache robots.txt for 24 hours
- Respect `Cache-Control` headers if present
- Refresh on cache miss or expiration

**Crawl-delay Compliance**:
- Extract `Crawl-delay` directive for our User-Agent
- Apply delay between requests to same domain
- Default to 1 second if not specified

### Policy

- **100% Compliance**: Never crawl disallowed URLs
- **Graceful Degradation**: Skip sources if robots.txt denies access
- **No Circumvention**: Never rotate User-Agents to bypass restrictions
- **Reporting**: Log all robots.txt violations (should be zero)

## Rate Limiting

### Per-Domain Limits

**Default Rates**:
- **Tier 1 Sources**: 1 request per 2 seconds (30/min)
- **Tier 2 Sources**: 1 request per 5 seconds (12/min)
- **Tier 3 Sources**: 1 request per 10 seconds (6/min)

**Adaptive Throttling**:
```python
class AdaptiveRateLimiter:
    def __init__(self, domain: str, initial_delay: float = 2.0):
        self.domain = domain
        self.delay = initial_delay
        self.last_request = 0

    async def wait(self):
        """Wait before next request, adapting to server responses."""
        elapsed = time.time() - self.last_request
        if elapsed < self.delay:
            await asyncio.sleep(self.delay - elapsed)
        self.last_request = time.time()

    def increase_delay(self):
        """Slow down on rate limit hit (429) or errors."""
        self.delay = min(self.delay * 1.5, 60.0)  # Cap at 60s
        logger.info(f"Increased rate limit delay for {self.domain} to {self.delay}s")

    def decrease_delay(self):
        """Speed up if requests consistently succeed."""
        self.delay = max(self.delay * 0.9, 1.0)  # Floor at 1s
```

**429 Response Handling**:
```python
async def handle_rate_limit_response(response, limiter):
    """Handle 429 Too Many Requests."""
    if response.status == 429:
        retry_after = response.headers.get('Retry-After', 60)
        limiter.delay = max(int(retry_after), limiter.delay * 2)
        logger.warning(f"Rate limited by {limiter.domain}, waiting {limiter.delay}s")
        await asyncio.sleep(limiter.delay)
        return True  # Retry
    return False  # Continue
```

### Global Rate Limiting

**Distributed Limiting** (across containers):
- Shared Redis counter for per-domain request tracking
- Atomic increment/decrement operations
- TTL-based sliding windows

**Circuit Breaker**:
- Opens after 5 consecutive failures
- Half-open after 5 minutes (test with 1 request)
- Closes after 3 consecutive successes

## User-Agent Transparency

### Standard User-Agent

```
PNKLN-Ingestion-Bot/1.0 (+https://pnkln.ai/bot; contact@pnkln.ai)
```

**Components**:
- **Bot Name**: `PNKLN-Ingestion-Bot`
- **Version**: `1.0`
- **Info URL**: `https://pnkln.ai/bot` (purpose, policies)
- **Contact**: `contact@pnkln.ai` (for concerns)

### Headers

**Standard Request Headers**:
```http
User-Agent: PNKLN-Ingestion-Bot/1.0 (+https://pnkln.ai/bot; contact@pnkln.ai)
From: contact@pnkln.ai
Accept: application/json, text/html, */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
```

**Purpose Declaration**:
- Include purpose in info page
- Opt-out instructions on info page
- Response to concerns within 24 hours

## Terms of Service Compliance

### Pre-Collection Review

**Checklist for New Sources**:
- [ ] Read and understand Terms of Service (ToS)
- [ ] Verify no explicit "no automated access" clause
- [ ] Check for API availability (prefer APIs over scraping)
- [ ] Document acceptable use policies
- [ ] Review data retention requirements
- [ ] Assess risk of ToS violation

**Red Flags** (Do Not Collect):
- Explicit prohibition of bots/scrapers
- Paywall circumvention required
- Authentication/login wall (public only)
- CAPTCHA enforcement (indicates unwanted automation)
- Legal threats in ToS against scrapers

### API-First Approach

**Preference Order**:
1. **Official API** (preferred)
2. **RSS/Atom Feeds** (semi-structured)
3. **Structured Data** (JSON-LD, microdata)
4. **HTML Scraping** (last resort)

**API Usage**:
- Always use official APIs when available
- Respect rate limits in API documentation
- Include API key in headers (not URL params)
- Monitor for API deprecation notices

## Privacy & Data Minimization

### PII Avoidance

**Do NOT Collect**:
- Email addresses (unless public org contacts)
- Phone numbers
- Physical addresses (unless org locations)
- Social security numbers, IDs
- Financial information
- Health information

**Scrubbing Pipeline**:
```python
import re

PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
}

def scrub_pii(text: str) -> str:
    """Remove potential PII from text."""
    for pii_type, pattern in PII_PATTERNS.items():
        text = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', text)
    return text
```

### Data Retention

**Retention Policy**:
- **Tier 1**: 90 days in GCS, metadata permanent
- **Tier 2**: 30 days in GCS, metadata permanent
- **Tier 3**: 14 days in GCS, metadata permanent

**Deletion Process**:
- Automated deletion via GCS lifecycle policies
- Manual deletion requests processed within 7 days
- Audit log of all deletions

### GDPR Compliance

**User Rights**:
- **Right to Access**: Provide data on request
- **Right to Erasure**: Delete data within 7 days
- **Right to Object**: Stop collection from specific sources
- **Right to Portability**: Export in JSON format

**Legal Basis**:
- Legitimate interest (public data intelligence)
- No consent required (public sources only)
- DPA registration (if applicable)

## Content Exclusions

### Do NOT Collect

**Prohibited Content**:
- Child sexual abuse material (CSAM)
- Illegal content (piracy, hacking, etc.)
- Private/leaked data (hacked databases)
- Paywalled content (no circumvention)
- Content behind authentication
- Copyrighted content without fair use justification

**Filtering**:
- Blacklist of known illegal/harmful sources
- Content-based filtering (keyword blacklist)
- Manual review queue for edge cases
- Immediate deletion of prohibited content

### Fair Use Justification

**Criteria for Fair Use**:
- **Purpose**: News monitoring, intelligence gathering (transformative)
- **Nature**: Publicly available factual content
- **Amount**: Snippets, metadata, headlines (not full reproduction)
- **Effect**: No market substitution (not replacing original)

**Documentation**:
- Cite Fair Use (17 U.S.C. § 107) in info page
- Limit content to 200-word excerpts
- Always link to original source
- Respect DMCA takedown requests (process within 24 hours)

## Monitoring & Enforcement

### Compliance Metrics

**Tracked Metrics**:
- robots.txt violations (target: 0)
- Rate limit hits (429 responses)
- ToS violation reports
- DMCA/legal takedown requests
- PII detection events
- Blocked source attempts

**Dashboards**:
- Real-time compliance status
- Violation trends over time
- Source-by-source compliance breakdown
- Legal request tracking

### Alerts

**Immediate Alerts** (PagerDuty):
- robots.txt violation detected
- DMCA/legal request received
- PII detected in ingested data
- Prohibited content flagged

**Warning Alerts** (Email):
- High rate limit hit rate (>10/hour)
- Source ToS change detected
- Unusual traffic patterns
- Circuit breaker opened

### Incident Response

**Violation Response Plan**:
1. **Detect**: Automated monitoring, manual reports
2. **Halt**: Immediately stop collection from source
3. **Investigate**: Root cause analysis
4. **Remediate**: Fix code, update configs, delete data
5. **Report**: Document incident, notify stakeholders
6. **Prevent**: Update checks, add tests, improve monitoring

**Legal Request Process**:
1. Receive request (DMCA, cease-and-desist, etc.)
2. Acknowledge within 4 hours
3. Consult legal counsel
4. Take action within 24 hours (delete, stop collection)
5. Document resolution
6. Follow up with requestor

## Configuration

### Ethical Crawling Config

**File**: `/config/ethical-crawling.yaml`

```yaml
ethical_crawling:
  user_agent: "PNKLN-Ingestion-Bot/1.0 (+https://pnkln.ai/bot; contact@pnkln.ai)"
  contact_email: "contact@pnkln.ai"
  info_url: "https://pnkln.ai/bot"

  robots_txt:
    enabled: true
    cache_ttl_hours: 24
    default_crawl_delay_seconds: 1

  rate_limiting:
    default_delay_seconds: 2
    min_delay_seconds: 1
    max_delay_seconds: 60
    adaptive: true

    tier_delays:
      tier_1: 2
      tier_2: 5
      tier_3: 10

  circuit_breaker:
    failure_threshold: 5
    timeout_seconds: 300
    half_open_max_requests: 1

  privacy:
    scrub_pii: true
    pii_patterns:
      - email
      - phone
      - ssn
    retention_days:
      tier_1: 90
      tier_2: 30
      tier_3: 14

  content_filtering:
    blacklisted_domains:
      - illegal-content.example
      - known-malware.example

    prohibited_keywords:
      - "child exploitation"
      - "hacked database"
      # ... (maintain separate secure list)

  compliance:
    respect_paywalls: true
    require_api_for_auth_sites: true
    fair_use_excerpt_max_words: 200
    dmca_response_hours: 24
```

## Training & Awareness

**Developer Training**:
- Annual ethical crawling training
- ToS review for new sources
- Incident response drills
- GDPR/privacy law updates

**Documentation**:
- This ethical guidelines doc
- Source-specific crawling notes
- Legal precedent library
- Incident postmortems

## External Resources

- [robots.txt Specification](https://www.robotstxt.org/)
- [GDPR Guide](https://gdpr.eu/)
- [Fair Use (17 U.S.C. § 107)](https://www.copyright.gov/fair-use/)
- [DMCA Takedown Process](https://www.dmca.com/takedown-guide/)
- [Web Scraping Legal Precedents](https://www.eff.org/issues/scraping)

## Version History

- **v1.0** (2025-11-07): Initial ethical guidelines
- Compliance target: 100% robots.txt, 0 legal violations
