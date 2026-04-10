# Scrapling Vue SPA Data Parser (HYBRID SCRAPER)

## Description

Advanced web scraping skill using `scrapling` and `firecrawl` to bypass anti-bot mechanisms and hydrate React/Vue single-page-applications (SPAs).

## Rules

1. Never use raw requests or BeautifulSoup for modern SPAs.
2. Always arbitrate between FireCrawl's LLM extraction and Scrapling's stealth network-idle fetching.
3. Obfuscate all web traffic via rotating `brd.superproxy.io` residential proxies.
4. Output scraped results rigidly in JSON. Strictly drop items lacking an `id_field`.

## Path

`apps/src/api/agents/skills/scrapling-vue-spa-parse/`
