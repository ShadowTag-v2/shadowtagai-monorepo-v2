# Email Authentication Report — DKIM/SPF/DMARC

## DNS Records Status

### shadowtagai.com
| Record | Status | Value |
|--------|--------|-------|
| SPF | ✅ Present | `v=spf1 include:_spf.google.com ~all` |
| DKIM | ❓ Not checked | Need `google._domainkey.shadowtagai.com` |
| DMARC | ❓ Not found | `_dmarc.shadowtagai.com` — needs configuration |
| Google Verification | ✅ | `google-site-verification=1i0cMjYhA60...` |

### counselconduit.com
| Record | Status | Value |
|--------|--------|-------|
| SPF | ❌ Missing | Domain not resolving (not registered?) |
| DKIM | ❌ Missing | N/A |
| DMARC | ❌ Missing | N/A |

## Required Actions

### 1. Add DMARC to shadowtagai.com
```
_dmarc.shadowtagai.com  TXT  "v=DMARC1; p=quarantine; rua=mailto:dmarc@shadowtagai.com; pct=100"
```

### 2. Verify DKIM for Google Workspace
In Google Admin Console → Apps → Google Workspace → Gmail → Authenticate email:
1. Generate DKIM key (2048-bit)
2. Add TXT record: `google._domainkey.shadowtagai.com`
3. Start authentication

### 3. For CounselConduit transactional emails
If using a custom domain for email:
- Register `counselconduit.com` → add SPF + DKIM + DMARC
- Or use `@shadowtagai.com` for all communications

### 4. Monitoring
Set up DMARC reporting at `rua=mailto:dmarc@shadowtagai.com`
to receive aggregate reports about email authentication.

## DMARC Policy Progression
1. Start: `p=none` (monitor only, 30 days)
2. Tighten: `p=quarantine` (spam folder, 30 days)
3. Lock: `p=reject` (block unauthenticated mail)
