# Ethical Compliance Guidelines for Gemini Ingestion Layer

## Overview

The Gemini Ingestion Layer adheres to strict ethical standards for web crawling and data collection. This document outlines our compliance framework, implementation guidelines, and monitoring procedures.

## Core Principles

### 1. Respect for Web Standards
- **robots.txt Compliance**: Mandatory adherence to robots.txt directives
- **Meta Robots Tags**: Honor noindex, nofollow, and noarchive directives
- **Crawl-Delay**: Respect specified crawl delays
- **Disallow Directives**: Never access disallowed paths

### 2. Rate Limiting and Resource Respect
- **Default Rate Limit**: 10 requests per second per domain
- **Adaptive Throttling**: Reduce rate on HTTP 429 (Too Many Requests)
- **Exponential Backoff**: Implement backoff on errors
- **Concurrent Connections**: Maximum 2 concurrent connections per domain

### 3. Transparency and Identification
- **User-Agent**: Clear identification as pnklnBot
- **Contact Information**: Provide contact URL in User-Agent
- **About Page**: Maintain public documentation about bot behavior
- **Opt-Out Mechanism**: Honor requests to cease crawling

### 4. Legal and Privacy Compliance
- **Copyright Respect**: Only collect publicly available information
- **GDPR Compliance**: Respect privacy regulations
- **Terms of Service**: Comply with site-specific ToS
- **API Terms**: Use official APIs where available and required

## Implementation Standards

### robots.txt Handling

#### Parse and Cache
```python
# Pseudo-code for robots.txt handling
def fetch_robots_txt(domain):
    """
    Fetch and parse robots.txt for a domain
    """
    url = f"https://{domain}/robots.txt"
    response = fetch_with_timeout(url, timeout=10)

    if response.status_code == 200:
        parse_and_cache(response.text, ttl=86400)  # 24-hour cache
    elif response.status_code == 404:
        # No robots.txt means all paths allowed
        cache_default_allow(domain, ttl=86400)
    else:
        # Error fetching - be conservative, disallow crawling
        cache_default_disallow(domain, ttl=3600)
```

#### Validation Before Crawl
- Check robots.txt cache before each request
- Refresh cache every 24 hours
- Fail closed (disallow) if robots.txt is unreachable

#### Supported Directives
- `User-agent`: Identify applicable rules
- `Disallow`: Paths to avoid
- `Allow`: Override more general disallows
- `Crawl-delay`: Minimum delay between requests (in seconds)
- `Sitemap`: Discover preferred crawl paths

### Rate Limiting Implementation

#### Per-Domain Limits
```python
# Rate limiter configuration
rate_limits = {
    "default": 10,  # requests per second
    "youtube.com": 15,  # Higher limit for APIs
    "twitter.com": 15,
    "news-sites": 20,
    "conservative": 5  # For smaller sites
}

# Adaptive throttling
if response.status_code == 429:
    current_rate = get_rate_for_domain(domain)
    new_rate = current_rate * 0.5  # Halve the rate
    update_rate_limit(domain, new_rate, duration=300)  # 5 min penalty
```

#### Error Handling with Backoff
```python
# Exponential backoff on errors
retry_delays = [2, 4, 8, 16, 32]  # seconds

for attempt, delay in enumerate(retry_delays):
    try:
        response = fetch(url)
        if response.status_code < 500:
            break  # Success or client error (don't retry)
    except Exception:
        if attempt < len(retry_delays) - 1:
            time.sleep(delay)
        else:
            mark_source_failed(url)
```

### User-Agent Standards

#### Format
```
pnklnBot/1.0 (+https://pnkln.ai/bot)
```

#### Components
- **Bot Name**: pnklnBot
- **Version**: Semantic versioning (1.0, 1.1, etc.)
- **Contact URL**: Links to documentation and contact form

#### Required Documentation at Contact URL
- Purpose of the bot
- What data is collected
- How to opt-out
- Contact information for bot operator
- Privacy policy
- Data retention policy

### Data Collection Boundaries

#### Allowed
- Publicly accessible web pages
- RSS/Atom feeds
- Official APIs (with proper authentication)
- Sitemap-listed URLs
- Public social media posts (via APIs)

#### Prohibited
- Password-protected content
- Paywalled content (beyond previews)
- Private social media profiles
- Content marked with noarchive
- CAPTCHA-protected pages
- Content requiring JavaScript execution to access (unless essential)

## Monitoring and Enforcement

### Automated Compliance Checks

#### Pre-Collection Validation
- [ ] robots.txt check passed
- [ ] Rate limit not exceeded
- [ ] User-Agent properly set
- [ ] URL not in exclusion list
- [ ] Source consent verified

#### Post-Collection Audit
- [ ] No disallowed paths accessed
- [ ] Rate limits respected (log analysis)
- [ ] Error rates within acceptable thresholds (<5%)
- [ ] No 403/451 status codes (legal restrictions)

### Metrics and Alerting

#### Compliance Metrics
```yaml
metrics:
  - name: robots_txt_violations
    threshold: 0
    action: alert_critical

  - name: rate_limit_exceeded_count
    threshold: 10 per hour
    action: alert_warning

  - name: http_403_451_count
    threshold: 5 per day
    action: investigate

  - name: error_rate
    threshold: 5%
    action: throttle_source

  - name: consent_check_failures
    threshold: 0
    action: halt_collection
```

### Manual Review Process

#### Weekly Audit
- Review crawl logs for compliance
- Check for new robots.txt restrictions
- Verify rate limit effectiveness
- Review opt-out requests

#### Quarterly Assessment
- Review legal and regulatory changes
- Update compliance policies
- Conduct external audit (if applicable)
- Update documentation

## Opt-Out and Request Handling

### Opt-Out Process
1. **Request Reception**: Via email or contact form at https://pnkln.ai/bot
2. **Immediate Action**: Add domain to exclusion list within 24 hours
3. **Data Handling**: Purge existing data if requested
4. **Confirmation**: Send confirmation email to requester

### Request Response Times
- **Opt-out requests**: 24 hours
- **Data deletion requests**: 7 days
- **General inquiries**: 3 business days

## Source-Specific Guidelines

### YouTube
- Use official YouTube Data API v3
- Respect quota limits (10,000 units/day default)
- Only collect public video metadata
- Honor channel-level restrictions

### Twitter/X
- Use official Twitter API v2
- Respect rate limits (per endpoint)
- Only collect public tweets
- Honor user privacy settings

### News Sites
- Prefer RSS feeds over crawling
- Respect paywalls (don't circumvent)
- Use news APIs where available
- Attribute sources properly

### General Web Crawling
- Start with sitemap.xml if available
- Honor meta robots tags
- Respect crawl-delay directives
- Use HEAD requests to check availability

## Data Retention and Privacy

### Retention Policy
- **Raw collected data**: 30 days
- **Processed/classified data**: 90 days
- **Aggregated metrics**: 1 year
- **Briefing outputs**: 1 year

### Privacy Safeguards
- No collection of personal identifiable information (PII)
- Automatic PII detection and redaction
- Encrypted storage at rest
- Access controls and audit logging

### GDPR Compliance
- Right to be forgotten: 7-day data purge
- Data portability: Export capability
- Purpose limitation: Only intelligence collection
- Data minimization: Collect only necessary fields

## Incident Response

### Compliance Violation Detected
1. **Immediate**: Halt collection from affected source
2. **Within 1 hour**: Assess scope of violation
3. **Within 4 hours**: Implement corrective measures
4. **Within 24 hours**: Report to stakeholders
5. **Within 7 days**: Conduct root cause analysis

### Legal Notice Received
1. **Immediate**: Acknowledge receipt
2. **Within 24 hours**: Halt collection if requested
3. **Within 3 days**: Legal review
4. **Within 7 days**: Formal response

## Training and Awareness

### Team Training
- Annual compliance training for all engineers
- Onboarding ethics module for new team members
- Quarterly updates on regulatory changes

### Documentation
- Maintain up-to-date compliance documentation
- Publish transparency reports (if applicable)
- Share best practices internally

## Version History

- **v1.0 (2025-11-15)**: Initial ethical compliance framework
- Future updates will be tracked here

## Contact and Reporting

- **Compliance Questions**: compliance@pnkln.ai
- **Opt-Out Requests**: bot-optout@pnkln.ai
- **Security Issues**: security@pnkln.ai
- **General Inquiries**: https://pnkln.ai/contact

---

*This document is reviewed quarterly and updated as needed to reflect current best practices and regulatory requirements.*
