# ShadowTag Insurance Alliance — Integration Spec
#
# Defines the technical integration between CounselConduit
# and legal malpractice insurance carriers (ALPS, CNA, Crum & Forster).
#
# @see OMNIBUS_STRATEGIC_BLUEPRINT.md §Phase 2 — Insurance Alliance
# @see VC_MASTER_DECK.md — Slide 8 Traction

## 1. Business Case

### The Proposal to Insurers

> "Firms using CounselConduit's Kovel-compliant AI portal have provably
> zero Heppner exposure. They deserve a 5-15% premium discount."

### Why Insurers Agree:
1. **Quantifiable Risk Reduction**: Heppner-compliant firms = zero AI privilege claims
2. **Audit Trail**: Kovel Attestation Receipts = cryptographic proof of compliance
3. **Reduced Reserves**: No need to reserve for "unknown AI exposure" claims
4. **Competitive Moat**: First insurer to offer discount captures the market

---

## 2. Technical Integration Points

### 2a. Compliance Attestation API

```yaml
# API provided BY CounselConduit TO insurers
# Read-only compliance verification endpoint

POST /api/insurance/verify-compliance
X-Insurance-API-Key: ${INSURER_API_KEY}

Request:
  firm_bar_number: "CA-123456"
  policy_number: "ALPS-2026-78901"

Response:
  compliance_status: "compliant"
  verification_timestamp: "2026-04-22T04:30:00Z"
  controls_verified:
    kovel_gate_active: true
    evaporating_chat_enabled: true
    seu_token_binding: true
    brief_ttl_30_days: true
    advance_fee_routing: true
  attestation_hash: "sha256:abc123..."
  attestation_url: "https://verify.counselconduit.com/attest/abc123"
  firm_tier: "growth_afa"
  last_audit: "2026-04-15T00:00:00Z"
  next_audit: "2026-05-15T00:00:00Z"
```

### 2b. Monthly Compliance Report

```yaml
# Generated monthly and delivered to insurer portal or via SFTP

report_type: "monthly_compliance"
period: "2026-04"
firm_id: "firm_sterling_assoc"
firm_name: "Sterling & Associates"
bar_state: "CA"
bar_number: "CA-123456"

metrics:
  total_sessions: 47
  sessions_with_kovel_receipt: 47  # 100% coverage
  sessions_evaporated: 47          # All data expired
  privilege_challenges: 0          # Zero privilege issues
  client_complaints: 0

security_posture:
  seu_tokens_issued: 47
  seu_tokens_expired_normally: 47
  seu_tokens_revoked_early: 0
  security_incidents: 0

advance_fee_compliance:
  state: "CA"
  routing_destination: "trust_with_exception"
  all_fees_properly_routed: true
  signed_agreements_on_file: true
```

### 2c. Real-Time Risk Alerts

```yaml
# Webhook sent to insurer when a firm LOSES compliance

POST https://api.alps-insurance.com/webhooks/risk-alerts
X-Webhook-Signature: hmac-sha256:${SIGNATURE}

event: "compliance_lapsed"
firm_bar_number: "CA-123456"
reason: "Kovel gate disabled by admin"
risk_level: "medium"
recommended_action: "Contact firm within 48 hours"
lapse_timestamp: "2026-04-22T10:00:00Z"
```

---

## 3. Discount Tiers

| Compliance Level | ALPS Discount | CNA Discount | Requirements |
|-----------------|---------------|-------------|--------------|
| **Gold** (Full) | 15% | 12% | All controls active, monthly audit pass |
| **Silver** (Partial) | 8% | 6% | Kovel gate + SEU active, some controls pending |
| **Bronze** (Basic) | 5% | 3% | Kovel gate active, no advanced controls |
| **None** | 0% | 0% | No CounselConduit integration |

### Discount Qualification Criteria

**Gold Tier** (maximum discount):
- [x] Kovel Directive Gate active on all client portals
- [x] Evaporating Chat with < 60-min TTL
- [x] S.E.U. token binding enabled
- [x] Advance fee routing per state bar rules
- [x] GDPR 30-day brief TTL enforcement
- [x] Monthly compliance reports delivered
- [x] Zero unresolved risk alerts

**Silver Tier** (partial discount):
- [x] Kovel Directive Gate active
- [x] S.E.U. token binding enabled
- [ ] Some advanced controls may be pending setup
- [x] Quarterly compliance reports delivered

---

## 4. Carrier Onboarding Sequence

### Phase 1: ALPS (Primary Target)
- ALPS insures ~40% of solo/small firm lawyers
- Existing technology partnership program
- Decision cycle: 60-90 days
- **Contact**: Risk Engineering Department

### Phase 2: CNA
- CNA LawyerGuard is the largest program
- Requires actuarial review of risk reduction data
- Decision cycle: 90-120 days

### Phase 3: Crum & Forster / Swiss Re
- Excess/surplus lines
- Interested in novel risk quantification
- Decision cycle: 120 days

---

## 5. Data Sharing Agreement (Template)

### Section 4.1: Scope of Data Shared
CounselConduit shares ONLY the following with Insurance Carrier:
- Compliance status (binary: compliant/non-compliant)
- Attestation hashes (cryptographic, no content)
- Session counts (aggregate, no content)
- Advance fee routing compliance status
- Risk alert events (compliance lapses only)

### Section 4.2: Data NOT Shared
CounselConduit does NOT share and CANNOT share:
- Client names or identities
- Case details or legal strategies
- Chat transcripts (they don't exist — stateless)
- Billing amounts or fee structures
- Attorney-client communications (protected)

### Section 4.3: Audit Rights
Insurance Carrier may audit CounselConduit's compliance verification
system annually. Audit is limited to the verification API and
attestation cryptographic chain. Source code and internal systems
are excluded.
