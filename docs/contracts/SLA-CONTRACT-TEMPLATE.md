# SLA CONTRACT TEMPLATE - FORCE MAJEURE EDITION

## Service Level Agreement (SLA) Section

### Performance Commitment

**Pnkln commits to p99≤90ms latency SLA for all agent decisions, measured monthly.**

This means that 99% of all agent decision requests will complete within 90 milliseconds, calculated on a monthly basis across all customer traffic.

---

## Force Majeure Exclusions

The following events are excluded from SLA breach calculations and penalty provisions:

### 1. Third-Party API Provider Outages

Outages or performance degradation of third-party LLM API providers (Google/Gemini, Anthropic/Claude, OpenAI/GPT, xAI/Grok) are excluded from SLA calculations **EXCEPT** where Pnkln's multi-vendor failover architecture prevents the breach.

**Automatic Exclusion Trigger**: If ≥2 API providers are simultaneously experiencing outages or degraded performance, the affected period is automatically excluded from SLA calculations.

**Customer Notification**: Pnkln will notify customers within 2 hours of any force majeure event affecting service performance.

### 2. Infrastructure Failures Beyond Pnkln Control

- Internet backbone failures affecting ≥3 major ISPs simultaneously
- Cloud provider infrastructure outages (AWS, GCP, Azure regional failures)
- DNS infrastructure failures affecting major providers
- Submarine cable cuts affecting international connectivity

### 3. Force Majeure Events (Legal Standard)

- Acts of God (earthquakes, floods, hurricanes, wildfires)
- War, terrorism, civil unrest
- Government action, sanctions, embargoes
- Pandemic or epidemic-related restrictions

### 4. Security Events

Cyber attacks, DDoS attacks, or security incidents that exceed NIST 800-53 High baseline defense capabilities are excluded from SLA calculations during the active incident and recovery period (up to 48 hours post-incident).

---

## Remedy for SLA Breach (Non-Force Majeure)

When SLA breaches occur that do NOT qualify for force majeure exclusion, the following remedies apply:

### Monthly Credit Schedule

| Breach Scenario | Remedy |
|----------------|---------|
| Month 1 breach (first occurrence) | 10% monthly fee credit |
| Month 2 consecutive breach | 25% monthly fee credit |
| Month 3 consecutive breach | Customer may terminate contract without penalty + 25% final month credit |

### Important Terms

- **No Cumulative Penalties**: Credits do not accumulate. Consecutive breach counter resets after any compliant month.
- **Credit Application**: Credits are automatically applied to the following month's invoice.
- **Maximum Liability**: Pnkln's total liability for SLA breaches is capped at 3 months of fees per customer, maximum $300,000 per customer per calendar year.
- **Exclusive Remedy**: SLA credits are the exclusive remedy for performance issues. Customer waives all other claims related to latency performance.

---

## SLA Measurement Methodology

### Calculation Method

```
p99 Latency = 99th percentile of all API response times during the measurement period

Measurement Period = Calendar month (UTC timezone)

Included in Measurement:
✅ Time from Pnkln API receives request
✅ Processing time within Pnkln infrastructure
✅ Time to return response to customer API endpoint

Excluded from Measurement:
❌ Customer-side network delays
❌ Customer application processing time
❌ Requests during force majeure events
❌ Requests flagged as customer-induced errors (4xx status codes)
```

### Transparency & Monitoring

1. **Real-Time Dashboard**: Customers have 24/7 access to a real-time SLA dashboard showing:
   - Current month p99 latency (updated hourly)
   - Historical monthly performance
   - Ongoing force majeure events (if any)
   - Individual request latency distribution

2. **Monthly Reporting**: Pnkln provides detailed monthly SLA reports by the 5th business day of the following month, including:
   - Final p99 latency calculation
   - Total request volume
   - Any force majeure exclusions applied
   - Credits applied (if any)

3. **Audit Rights**: Customers may audit SLA calculations with 30 days written notice, up to once per quarter.

---

## Failover Architecture Disclosure

Pnkln's ability to maintain p99≤90ms SLA is enabled by our proprietary 4-layer failover architecture:

```
Layer 1: Primary LLM (Gemini) - 40% capacity allocation
         ↓ (failover on timeout/error)
Layer 2: Secondary LLM (Claude) - +10% capacity buffer
         ↓ (failover on timeout/error)
Layer 3: Tertiary LLM (GPT-5) - +5% capacity buffer
         ↓ (failover on timeout/error)
Layer 4: Local PyTorch + Rules Engine (deterministic, always available)
```

This architecture ensures that no single API provider outage can breach the SLA, as automatic failover occurs within milliseconds.

---

## Service Credits - Claiming Process

### Automatic Credits

SLA breaches are automatically detected and credits are applied without customer action required.

### Dispute Process

If customer disagrees with SLA calculation:

1. Customer submits dispute via support portal within 15 days of monthly report
2. Pnkln engineering reviews calculation within 5 business days
3. If dispute is valid, additional credits applied to next invoice
4. If dispute cannot be resolved, escalate to executive review (CTO + Customer executive)

---

## Contract Modification

Pnkln reserves the right to modify SLA terms with 90 days written notice. Modifications that reduce customer protections (e.g., increasing p99 threshold, reducing credits) give customer the right to terminate without penalty during the 90-day notice period.

---

## Legal Interpretation

This SLA section is governed by the laws of [JURISDICTION] without regard to conflict of law principles. Force majeure provisions follow the legal standard established in [RELEVANT CASE LAW].

In the event of conflict between this SLA section and other contract terms, this section takes precedence for all performance-related matters.

---

## Contact for SLA Issues

**SLA Escalation Contact**:
- Email: sla-team@pnkln.com
- Phone: [24/7 SLA hotline]
- Slack Connect: [Enterprise customers only]

**Response Time for SLA Inquiries**:
- Critical (ongoing breach): 15 minutes
- High (potential breach): 2 hours
- Normal (monthly report questions): 1 business day

---

**Document Version**: 1.0
**Effective Date**: [CONTRACT_START_DATE]
**Last Updated**: 2025-11-15
**Approved By**: Legal, Engineering, Finance

---

## Appendix A: Sample SLA Calculation

**Example Month**: October 2025

**Total Requests**: 50,000,000
**p99 Request Position**: Request #49,500,000 (when sorted by latency)
**Latency at p99**: 87ms
**Result**: ✅ SLA MET (87ms < 90ms threshold)

**Force Majeure Events**:
- Oct 15, 14:00-18:00 UTC: Anthropic API outage (4 hours)
- Requests during this period: 500,000
- Excluded from calculation: Yes (single provider outage, failover successful)

**Credit Applied**: $0 (SLA met)

---

## Appendix B: Infrastructure Provider Diversity

To minimize correlated failure risk, Pnkln uses the following infrastructure diversity:

| Component | Provider | Region | Backup |
|-----------|----------|--------|--------|
| Primary Compute | AWS | us-east-1 | GCP us-central1 |
| LLM - Gemini | Google Cloud | Multi-region | N/A (fails to Claude) |
| LLM - Claude | Anthropic | Multi-region | N/A (fails to GPT-5) |
| LLM - GPT-5 | OpenAI/Azure | Multi-region | N/A (fails to Local) |
| Local Inference | On-prem PyTorch | Edge nodes | Redundant clusters |
| Database | AWS RDS | Multi-AZ | Cross-region replica |

This diversity ensures that no single infrastructure provider failure can trigger SLA breach.
