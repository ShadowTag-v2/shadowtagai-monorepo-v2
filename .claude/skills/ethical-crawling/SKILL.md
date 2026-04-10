# Ethical Web Crawling Skill

## Activation Criteria

Activate this skill when analyzing, implementing, or auditing web crawling, scraping, or data collection systems that interact with external websites or APIs.

**Trigger Keywords:**
- "ethical crawling"
- "robots.txt compliance"
- "web scraping best practices"
- "rate limiting"
- "crawler compliance"
- "legal data collection"

## Skill Purpose

Provides expertise in building and auditing ethical, legal, and sustainable web crawling systems with focus on:
- robots.txt compliance
- Rate limiting and politeness
- Legal and ToS compliance
- Source attribution and transparency
- Sustainable crawling practices
- Risk mitigation

## Core Principles

### The Three Pillars of Ethical Crawling

**1. Legal Compliance**
- Respect Terms of Service
- Honor robots.txt directives
- Comply with data protection laws (GDPR, CCPA)
- Avoid accessing unauthorized data
- Maintain audit trails

**2. Technical Politeness**
- Implement rate limiting
- Respect Retry-After headers
- Use appropriate User-Agents
- Cache robots.txt
- Implement exponential backoff

**3. Transparency & Attribution**
- Clear User-Agent identification
- Contact information in requests
- Source attribution in data
- Documented crawl policies
- Response to takedown requests

## Compliance Framework

### Level 1: robots.txt Compliance (REQUIRED)

**What**: robots.txt is a standard for website crawl permissions

**Implementation:**
```python
# Check robots.txt before every new domain
def can_fetch(url):
    rp = robotparser.RobotFileParser()
    rp.set_url(f"{domain}/robots.txt")
    rp.read()
    return rp.can_fetch("YourBot/1.0", url)
```

**Best Practices:**
- Parse and cache robots.txt for 24 hours
- Respect all directives (User-agent, Disallow, Allow, Crawl-delay)
- Honor Crawl-delay directive (min wait between requests)
- Check before EVERY new domain
- Log all robots.txt decisions

**Consequences of Violation:**
- IP bans
- Legal action (CFAA violations in US)
- Reputation damage

### Level 2: Rate Limiting (REQUIRED)

**What**: Limiting request frequency to avoid overwhelming servers

**Implementation:**
```python
# Minimum delays per domain (milliseconds)
RATE_LIMITS = {
    'default': 2000,      # 2 seconds
    'rate-limited': 5000, # 5 seconds
    'conservative': 10000 # 10 seconds
}

# Exponential backoff on errors
def fetch_with_backoff(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = fetch(url)
            if response.status == 429:  # Rate limited
                wait = 2 ** attempt  # 1s, 2s, 4s
                time.sleep(wait)
                continue
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

**Best Practices:**
- Default 2-5 seconds between requests to same domain
- Respect Retry-After headers (always)
- Implement exponential backoff
- Use per-domain rate limiting (not global)
- Monitor 429 (Too Many Requests) responses
- Back off on any server errors (5xx)

**Consequences of Violation:**
- IP bans (temporary or permanent)
- Service degradation for legitimate users
- Legal liability for DDoS
- Increased infrastructure costs

### Level 3: User-Agent Identification (REQUIRED)

**What**: Clear identification of your crawler

**Implementation:**
```python
headers = {
    'User-Agent': 'YourCompanyBot/1.0 (+https://yourcompany.com/bot; bot@yourcompany.com)'
}
```

**Best Practices:**
- Include bot name and version
- Include website with bot policy
- Include contact email
- Never impersonate browsers
- Maintain consistent User-Agent

**Consequences of Violation:**
- Perceived as malicious
- IP bans
- Difficulty with support requests
- Legal complications

### Level 4: Terms of Service Review (REQUIRED)

**What**: Understanding and respecting website ToS

**Checklist:**
- [ ] Read Terms of Service completely
- [ ] Identify clauses about automated access
- [ ] Check for explicit API alternatives
- [ ] Document any ambiguities
- [ ] Seek legal review if uncertain
- [ ] Re-review quarterly

**Common ToS Restrictions:**
- No automated access without permission
- No commercial use of data
- No data resale or redistribution
- Attribution requirements
- Access limits (requests/day)

**Consequences of Violation:**
- Account termination
- Legal action (breach of contract)
- Data deletion requirements
- Financial penalties

### Level 5: Data Protection Compliance (REQUIRED for PII)

**GDPR Requirements (if collecting EU data):**
- [ ] Legal basis for collection
- [ ] Privacy notice provided
- [ ] Data minimization
- [ ] Storage limitation
- [ ] Right to erasure capability
- [ ] Data breach notification plan

**CCPA Requirements (if collecting CA data):**
- [ ] Privacy policy disclosure
- [ ] Opt-out mechanism
- [ ] Data deletion on request
- [ ] No sale without consent

**Best Practices:**
- Avoid collecting PII when possible
- Anonymize/pseudonymize immediately
- Encrypt in transit and at rest
- Implement retention policies
- Maintain processing logs

## Risk Assessment Matrix

| Risk Level | Characteristics | Examples | Mitigation |
|-----------|----------------|----------|------------|
| **Low Risk** | Public data, clear ToS allowing access, robust APIs | Government open data, RSS feeds, permitted APIs | Standard compliance |
| **Medium Risk** | Public data, ambiguous ToS, no API | News sites, blogs | Conservative crawling, legal review |
| **High Risk** | Login-required, ToS prohibits scraping, PII present | Social media, e-commerce | Seek permission, use official APIs |
| **Critical Risk** | Explicit ToS prohibition, sensitive data, past legal action | LinkedIn, Facebook | Do not crawl, find alternatives |

## Compliance Checklist

### Pre-Crawl Checklist
- [ ] robots.txt reviewed and configured
- [ ] Rate limits defined and implemented
- [ ] User-Agent properly configured
- [ ] Terms of Service reviewed
- [ ] Legal review completed (if needed)
- [ ] Contact email monitored
- [ ] Logging configured

### During-Crawl Monitoring
- [ ] Rate limit adherence verified
- [ ] Error rates monitored
- [ ] 429 responses tracked
- [ ] robots.txt changes detected
- [ ] ToS changes monitored
- [ ] Complaints reviewed daily

### Post-Crawl Audit
- [ ] robots.txt compliance report
- [ ] Rate limit violation review
- [ ] Error rate analysis
- [ ] Data quality assessment
- [ ] Storage compliance check
- [ ] Attribution verification

## Common Violations and Fixes

### Violation 1: Ignoring robots.txt
**Symptom**: Accessing disallowed paths
**Fix**: Implement robots.txt parser
**Code**:
```python
from urllib.robotparser import RobotFileParser

class EthicalCrawler:
    def __init__(self):
        self.robot_parsers = {}

    def can_crawl(self, url):
        domain = extract_domain(url)
        if domain not in self.robot_parsers:
            rp = RobotFileParser()
            rp.set_url(f"https://{domain}/robots.txt")
            rp.read()
            self.robot_parsers[domain] = rp

        return self.robot_parsers[domain].can_fetch("YourBot", url)
```

### Violation 2: Aggressive Rate Limiting
**Symptom**: High 429 error rates, IP bans
**Fix**: Implement per-domain throttling
**Code**:
```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self):
        self.last_request = defaultdict(lambda: 0)
        self.min_delay = 2.0  # seconds

    def wait_if_needed(self, domain):
        now = time.time()
        elapsed = now - self.last_request[domain]

        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)

        self.last_request[domain] = time.time()
```

### Violation 3: Missing User-Agent
**Symptom**: Blocked as suspicious traffic
**Fix**: Proper User-Agent header
**Code**:
```python
headers = {
    'User-Agent': 'CompanyBot/1.0 (+https://company.com/bot; contact@company.com)',
    'From': 'contact@company.com'
}
```

### Violation 4: Not Respecting Retry-After
**Symptom**: Continued rate limit errors
**Fix**: Honor Retry-After header
**Code**:
```python
response = requests.get(url)
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    time.sleep(retry_after)
```

## Sustainable Crawling Patterns

### Pattern 1: Incremental Crawling
**Why**: Reduces load, respects resources
**How**: Track last-crawled timestamps, fetch only updates
**Impact**: 70-90% reduction in requests

### Pattern 2: Conditional Requests
**Why**: Avoid unnecessary transfers
**How**: Use If-Modified-Since, ETag headers
**Impact**: 50-70% bandwidth reduction

### Pattern 3: API-First Approach
**Why**: Designed for programmatic access
**How**: Always check for official API before scraping
**Impact**: Ethical, reliable, often free/cheap

### Pattern 4: Distributed Crawling with IP Rotation
**Why**: Distribute load across IPs
**How**: Use multiple IPs, coordinate to avoid overlap
**Impact**: Lower per-IP load, less likely to trigger bans
**Warning**: Still must respect rate limits PER DOMAIN

## Legal Considerations

### CFAA (Computer Fraud and Abuse Act - US)
**Relevance**: Unauthorized access is criminal
**Key**: "Authorization" often defined by ToS, robots.txt
**Implication**: Violating ToS can be illegal, not just breach of contract
**Case Law**: hiQ Labs v. LinkedIn (public data may be accessible)

### GDPR (General Data Protection Regulation - EU)
**Relevance**: Processing personal data of EU citizens
**Key**: Need legal basis (consent, legitimate interest, etc.)
**Implication**: Even public data has protections if identifiable
**Requirements**: Privacy notices, deletion rights, breach reporting

### CCPA (California Consumer Privacy Act - US)
**Relevance**: Collecting data on CA residents
**Key**: Disclosure and opt-out requirements
**Implication**: Must honor deletion and opt-out requests

## Audit Procedures

### Monthly Compliance Audit
1. **robots.txt Compliance**
   - Sample 100 recent crawls
   - Verify robots.txt was checked
   - Confirm allowed paths only

2. **Rate Limit Review**
   - Check average requests/domain
   - Review 429 error rates (target: <0.1%)
   - Verify backoff implementation

3. **ToS Monitoring**
   - Review any ToS changes from crawled sites
   - Update compliance as needed

4. **Legal Risk Assessment**
   - Review any legal developments
   - Update risk matrix
   - Adjust crawling strategy

### Incident Response Plan

**If Contacted by Website:**
1. Acknowledge within 24 hours
2. Immediately pause crawling
3. Review complaint
4. Implement requested changes
5. Document interaction
6. Resume only if resolved

**If Threatened with Legal Action:**
1. Immediately cease crawling
2. Preserve all logs
3. Engage legal counsel
4. Do not delete data without counsel approval
5. Cooperate fully

## References

See `references/` directory for:
- `robots-txt-spec.md`: Full robots.txt specification
- `rate-limiting-strategies.md`: Advanced rate limiting
- `legal-frameworks.md`: CFAA, GDPR, CCPA details
- `case-law.md`: Relevant legal cases

## Tools

See `scripts/` directory for:
- `validate-compliance.sh`: Automated compliance checks
- `robots-txt-checker.py`: Batch robots.txt validation
- `rate-limit-analyzer.py`: Crawl pattern analysis

---

**Skill Maturity**: Production-Critical
**Last Updated**: 2025-11-08
**Legal Review**: Required Quarterly
**Maintainer**: Legal & Engineering Teams
