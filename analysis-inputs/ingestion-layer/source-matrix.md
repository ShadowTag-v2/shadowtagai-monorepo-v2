# Source Configuration Matrix

**Version**: 1.0-draft
**Status**: Pre-Production
**Last Updated**: 2025-11-15

---

## Active Sources (8 configured)

### 1. YouTube
**Type**: Video platform
**Access Method**: YouTube Data API v3
**Rate Limit**: 10 requests/second
**Daily Quota**: 10,000 API units
**Authentication**: API key

**Crawl Targets**:
- Trending videos (Technology, News categories)
- Specific channel uploads (top 20 tech channels)
- Video comments (top 100 per video)

**Expected Items/Night**: 300-400
**Expected Tier 1 Ratio**: 25% (video metadata), 35% (trending tech)
**Cost/Item**: ~$0.03 (API quota costs)

**robots.txt Compliance**: N/A (using official API)
**Rate Limiting Strategy**: Token bucket (10/sec sustained, burst 20)

---

### 2. Twitter/X
**Type**: Social media
**Access Method**: Twitter API v2 (Elevated access)
**Rate Limit**: 1 request/second (strict)
**Daily Quota**: 500,000 tweets/month
**Authentication**: Bearer token (OAuth 2.0)

**Crawl Targets**:
- Key accounts: @elonmusk, @sama, @ylecun, @ID_AA_Carmack (50 accounts total)
- Trending hashtags: #AI, #ML, #GKE, #Kubernetes
- Search: "breaking news" OR "announcement"

**Expected Items/Night**: 250-300
**Expected Tier 1 Ratio**: 40% (breaking news), 20% (general tweets)
**Cost/Item**: ~$0.05 (API costs at scale)

**robots.txt Compliance**: N/A (using official API)
**Rate Limiting Strategy**: Fixed 1 req/sec with queue

---

### 3. News Aggregators (RSS)
**Type**: News feeds
**Access Method**: RSS/Atom feeds (public)
**Rate Limit**: 20 requests/second (self-imposed)
**Daily Quota**: Unlimited (public feeds)
**Authentication**: None

**Crawl Targets** (15 feeds):
- AP News: https://apnews.com/rss
- Reuters: https://www.reutersagency.com/feed/
- BBC News: http://feeds.bbci.co.uk/news/rss.xml
- TechCrunch: https://techcrunch.com/feed/
- Ars Technica: https://arstechnica.com/feed/
- The Verge: https://www.theverge.com/rss/index.xml
- Hacker News: https://news.ycombinator.com/rss
- (8 more feeds)

**Expected Items/Night**: 400-500
**Expected Tier 1 Ratio**: 30% (breaking news), 50% (tech news)
**Cost/Item**: ~$0.01 (bandwidth + processing)

**robots.txt Compliance**: Feeds are public, no robots.txt restrictions
**Rate Limiting Strategy**: 1 req/5sec per feed (polite crawling)

---

### 4. Reddit
**Type**: Social news aggregation
**Access Method**: Reddit API (PRAW)
**Rate Limit**: 5 requests/second
**Daily Quota**: 60 requests/minute/client
**Authentication**: OAuth 2.0 (client ID + secret)

**Crawl Targets** (10 subreddits):
- r/technology (3.5M subscribers)
- r/worldnews (32M subscribers)
- r/programming (6M subscribers)
- r/artificial (500K subscribers)
- r/MachineLearning (2.8M subscribers)
- r/kubernetes (180K subscribers)
- r/GoogleCloud (50K subscribers)
- (3 more subreddits)

**Expected Items/Night**: 200-250
**Expected Tier 1 Ratio**: 25% (highly upvoted posts)
**Cost/Item**: ~$0.02 (API + processing)

**robots.txt Compliance**: Using official API (compliant)
**Rate Limiting Strategy**: 5 req/sec with exponential backoff on 429

---

### 5. Hacker News
**Type**: Tech news aggregator
**Access Method**: Hacker News API (Firebase)
**Rate Limit**: No official limit (self-imposed 10/sec)
**Daily Quota**: Unlimited
**Authentication**: None

**Crawl Targets**:
- Front page stories (top 30)
- Ask HN posts
- Show HN posts
- Comments on trending stories

**Expected Items/Night**: 150-200
**Expected Tier 1 Ratio**: 45% (curated tech content)
**Cost/Item**: ~$0.01 (Firebase reads + processing)

**robots.txt Compliance**: API-based (compliant)
**Rate Limiting Strategy**: 10 req/sec max

---

### 6. arXiv (Academic Preprints)
**Type**: Research papers
**Access Method**: arXiv API (OAI-PMH)
**Rate Limit**: 1 request/3 seconds (per guidelines)
**Daily Quota**: Unlimited (bulk downloads discouraged)
**Authentication**: None

**Crawl Targets**:
- cs.AI (Artificial Intelligence)
- cs.LG (Machine Learning)
- cs.CL (Computation and Language/NLP)
- Daily new submissions

**Expected Items/Night**: 50-100
**Expected Tier 1 Ratio**: 60% (peer-reviewed research)
**Cost/Item**: ~$0.01 (processing only)

**robots.txt Compliance**: API usage complies with arXiv terms
**Rate Limiting Strategy**: 1 req/3sec strict

---

### 7. Government/Public Data
**Type**: Official announcements
**Access Method**: Data.gov APIs, agency RSS feeds
**Rate Limit**: Varies by agency (typically 10-50/min)
**Daily Quota**: Agency-specific
**Authentication**: API keys (where required)

**Crawl Targets**:
- Data.gov API: https://api.data.gov/
- NIST announcements
- CISA cybersecurity alerts
- Federal Register (tech-related notices)

**Expected Items/Night**: 30-50
**Expected Tier 1 Ratio**: 70% (official, high-credibility)
**Cost/Item**: ~$0.01 (processing only)

**robots.txt Compliance**: Public data, API-based
**Rate Limiting Strategy**: Agency-specific limits respected

---

### 8. Specialized Forums
**Type**: Niche communities
**Access Method**: Web scraping (ethical, with permission where possible)
**Rate Limit**: 1 request/10 seconds per site
**Daily Quota**: Self-imposed max 100 items/site
**Authentication**: None (public forums)

**Crawl Targets**:
- Stack Overflow (tagged: kubernetes, gke, machine-learning)
- GitHub Discussions (selected repos)
- GitLab Forums
- Security forums (with permission)

**Expected Items/Night**: 100-150
**Expected Tier 1 Ratio**: 20% (signal-to-noise challenge)
**Cost/Item**: ~$0.02 (scraping overhead)

**robots.txt Compliance**: CRITICAL - check robots.txt before every crawl
**Rate Limiting Strategy**: Very conservative (1 req/10sec)

---

## Source Priority Tiers

### High Priority (Crawl First)
1. News RSS (fast, high Tier 1 yield)
2. Hacker News (fast, high Tier 1 yield)
3. Government/Public Data (high credibility)

### Medium Priority
4. Twitter (slow due to rate limits, but timely)
5. Reddit (moderate Tier 1 yield)
6. arXiv (high quality, but niche)

### Low Priority (Crawl Last)
7. YouTube (slow API, mixed quality)
8. Specialized Forums (scraping overhead, low Tier 1)

---

## Coverage Analysis (Pre-Production)

### Geographic Coverage
- **US-centric**: 70% (News, Government, Hacker News)
- **Global**: 30% (BBC, Reuters, arXiv)
- **Gap**: Underrepresented regions (APAC, LATAM)

### Language Coverage
- **English**: 95%
- **Other**: 5% (minimal non-English sources)
- **Gap**: Need multilingual sources for global intelligence

### Topic Coverage
- **Technology**: 60% (strong)
- **General News**: 25% (moderate)
- **Academic/Research**: 10% (niche)
- **Security**: 5% (weak - needs expansion)

### Source Reliability
- **High Credibility** (Tier 1 sources): News RSS, Government, arXiv (50%)
- **Medium Credibility**: Reddit, Hacker News, YouTube (35%)
- **Low Credibility**: Specialized Forums (15% - requires validation)

---

## Redundancy Matrix

| Category | Primary Sources | Backup Sources | Risk Level |
|----------|----------------|----------------|------------|
| **Breaking News** | News RSS, Twitter | Reddit, Hacker News | Low |
| **Tech News** | Hacker News, TechCrunch | Reddit, Twitter | Low |
| **Research** | arXiv | YouTube (lectures), Forums | Medium |
| **Security** | Government, CISA | Forums, Reddit | High (gaps) |
| **Community Insights** | Reddit, Forums | Twitter, Hacker News | Medium |

**Critical Gap**: If Twitter AND Reddit fail, community insights severely limited.

---

## Planned Source Additions (Future)

### Next 3 Months
1. **Telegram Channels** (breaking news, crypto/tech communities)
2. **Discord Servers** (dev communities - with permission)
3. **Medium** (long-form tech articles)

### Next 6-12 Months
4. **Non-English News** (BBC World Service, Al Jazeera, etc.)
5. **Podcasts** (transcriptions of tech podcasts)
6. **Academic Journals** (beyond arXiv - IEEE, ACM with subscriptions)

---

## Source Health Monitoring

### Metrics Tracked per Source
- **Availability**: % uptime (target: 95%+)
- **Item Yield**: Items/night (vs expected)
- **Tier 1 Ratio**: % Tier 1 items (vs expected)
- **Cost Efficiency**: $/item (vs budget)
- **Rate Limit Hits**: # of 429 errors (target: 0)
- **robots.txt Violations**: # of violations (target: 0)

### Auto-Prune Criteria
Remove source if:
- Availability <80% for 7 consecutive days
- Tier 1 ratio <5% for 30 days
- Cost/item >$0.10 sustained
- robots.txt violations >0 (immediate removal)

### Auto-Discover (Future)
- Monitor Hacker News/Reddit for trending new sources
- A/B test new sources (1 week trial)
- Promote to permanent if Tier 1 ratio >20%

---

## Ethical Compliance Checklist

### Pre-Crawl (Automated)
- [ ] Check robots.txt (cache for 24 hours)
- [ ] Verify API quota available
- [ ] Confirm rate limit tokens available
- [ ] Log crawl start (audit trail)

### During Crawl
- [ ] Respect rate limits (enforce with token bucket)
- [ ] Handle 429/503 errors with exponential backoff
- [ ] Stop crawling if robots.txt changes mid-crawl
- [ ] Anonymize PII (social media handles, emails)

### Post-Crawl
- [ ] Log crawl completion (items, duration, errors)
- [ ] Report rate limit hits (Slack alert if >5%)
- [ ] Flag any robots.txt violations for review
- [ ] Store attribution metadata (source URL, timestamp)

---

## Open Questions (for Analysis)

1. **Is 8 sources sufficient**, or should we onboard more to reach 2000 items/night?
2. **Are Tier 1 yield estimates realistic** (25-70% range)?
3. **Should we deprioritize low-yield sources** (e.g., YouTube at 25%)?
4. **What's the risk of over-reliance on News RSS** (40%+ of total volume)?
5. **How do we handle source outages** (Twitter API down for 24 hours)?
6. **Should we add real-time sources** (WebSockets for breaking news)?

---

**Status**: Draft configuration for analysis review
**Next Steps**: Gemini 2.0 Pro analysis of coverage gaps, redundancy, ethics
