# Rule 24: Runtime Resilience — Watchdog, Cascade, SSRF, Secret Scan
# Source: Claude Code Source (withRetry.ts, ssrfGuard.ts, secretScanner.ts, claude.ts)

## Streaming Idle Watchdog (Pattern #5)
- Primary: 90s silence timeout kills hung TCP connections
- Secondary: 30s stall detector logs diagnostics (stall count, total stall time)
- Both exclude time-to-first-byte (initial latency is not a stall)
- Measures abort propagation delay: gap between setTimeout fire and stream loop exit
  - 0-10ms = healthy, >>1000ms = something else is blocking the event loop
- The Anthropic SDK timeout only covers initial `fetch()`, NOT the streaming body

## 529 Cascade Detection (Pattern #10)
Three consecutive 529 (overloaded) errors triggers automatic model fallback:
- Counter is PRE-SEEDED when streaming 529 → non-streaming retry path
  (streaming 529 counts toward MAX_529_RETRIES = 3)
- Background queries (summaries, titles) bail IMMEDIATELY on 529 — no retries
  - During cascades, each retry is 3-10× gateway amplification
  - User never sees background failures
  - Foreground set: `repl_main_thread`, `sdk`, `agent:*`, `compact`, `hook_*`
- Fast mode fallback: on 429/529, drop to standard speed with 30-minute cooldown
  - Short retry-after (<20s): wait and retry with fast mode still active
  - Long retry-after: enter cooldown, switch to standard model

## SSRF Guard (Pattern #12)
Custom DNS `lookup` function (validates RESOLVED IP, not just hostname):
- **Blocked IPv4**: 0.0.0.0/8, 10.0.0.0/8, 100.64.0.0/10 (CGNAT — Alibaba metadata),
  169.254.0.0/16 (cloud metadata), 172.16.0.0/12, 192.168.0.0/16
- **Blocked IPv6**: :: (unspecified), fc00::/7 (unique local), fe80::/10 (link-local),
  ::ffff:<v4> (IPv4-mapped — extracts and validates embedded v4)
- **ALLOWED**: 127.0.0.0/8, ::1 (loopback — local dev hooks)
- Global proxy configured → guard bypassed (proxy enforces its own domain allowlist)
- No DNS rebinding bypass: guard runs on resolved IP, not on hostname

## Secret Scanner (Pattern #13)
30+ credential patterns scanned BEFORE content leaves the machine:
- Curated high-confidence rules from gitleaks (MIT licensed)
- Only patterns with distinctive prefixes (near-zero false positives)
- Anthropic API key pattern assembled at runtime: `['sk', 'ant', 'api'].join('-')`
  → source code doesn't match its own detection patterns
- Matched secret text is NEVER logged or displayed — only rule ID and label
- `redactSecrets()` replaces only captured group, not full match
  (preserves boundary chars: space, quote, semicolons)
- Covers: AWS, GCP, Azure AD, GitHub PAT/OAuth/App, GitLab, Slack, Stripe,
  Shopify, OpenAI, HuggingFace, SendGrid, Twilio, npm, PyPI, PEM private keys

## Parallel Startup (Pattern #4)
- Fire keychain reads + MDM subprocess reads BEFORE imports finish
- Imports take ~135ms; by completion, both are already cached
- Uses `child_process` directly (not execa) to avoid ~58ms module init cost
- Net savings: ~65ms per macOS startup

## VCR Recording System (Pattern #9)
Deterministic test replay via "dehydration" normalization:
- File paths → `[CWD]`, `[CONFIG_HOME]`
- Timestamps → `[DURATION]`, `[COST]`
- Numeric values → `[NUM]`; Windows paths normalized
- Same fixture works across macOS/Linux/Windows and different CWDs
- Hash dehydrated input → deterministic fixture filename
