# DNS Records — DMARC / SPF / DKIM

## Required DNS TXT Records

These records should be added to both `shadowtagai.com` and `kovelai.com` domains.

### SPF (Sender Policy Framework)

```
; Allow Google Workspace + Firebase to send email
; Replace with your actual domain
shadowtagai.com.  IN  TXT  "v=spf1 include:_spf.google.com include:_spf.firebasemail.com ~all"
kovelai.com.      IN  TXT  "v=spf1 include:_spf.google.com include:_spf.firebasemail.com ~all"
```

### DMARC (Domain-based Message Authentication)

```
; Reject policy with aggregate reporting to founder@shadowtagai.com
_dmarc.shadowtagai.com.  IN  TXT  "v=DMARC1; p=reject; rua=mailto:dmarc-reports@shadowtagai.com; ruf=mailto:dmarc-reports@shadowtagai.com; fo=1; adkim=s; aspf=s"
_dmarc.kovelai.com.      IN  TXT  "v=DMARC1; p=reject; rua=mailto:dmarc-reports@shadowtagai.com; ruf=mailto:dmarc-reports@shadowtagai.com; fo=1; adkim=s; aspf=s"
```

### DKIM (DomainKeys Identified Mail)

DKIM is configured through Google Workspace Admin Console:
1. Go to `admin.google.com` → Apps → Google Workspace → Gmail → Authenticate Email
2. Generate DKIM key (2048-bit recommended)
3. Add the generated TXT record to DNS as `google._domainkey.shadowtagai.com`

### MX Records (Already Configured)

```
; Google Workspace MX
shadowtagai.com.  IN  MX  1   ASPMX.L.GOOGLE.COM.
shadowtagai.com.  IN  MX  5   ALT1.ASPMX.L.GOOGLE.COM.
shadowtagai.com.  IN  MX  5   ALT2.ASPMX.L.GOOGLE.COM.
shadowtagai.com.  IN  MX  10  ALT3.ASPMX.L.GOOGLE.COM.
shadowtagai.com.  IN  MX  10  ALT4.ASPMX.L.GOOGLE.COM.
```

## Verification Commands

```bash
# Check SPF
dig TXT shadowtagai.com +short

# Check DMARC
dig TXT _dmarc.shadowtagai.com +short

# Check DKIM
dig TXT google._domainkey.shadowtagai.com +short

# Check MX
dig MX shadowtagai.com +short
```

## Status

- [x] MX records configured (Google Workspace)
- [ ] SPF record — add to DNS provider
- [ ] DMARC record — add to DNS provider
- [ ] DKIM — generate via Google Workspace Admin Console
