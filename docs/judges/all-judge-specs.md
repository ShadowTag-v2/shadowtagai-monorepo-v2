# Complete Judge Vertical Specifications

## FinJudge - Financial Transaction Enforcement

### Overview

Binary ALLOW/BLOCK decisions for financial transactions with emphasis on $50K+ wire transfers requiring CFO approval.

### Use Cases

- Wire transfers
- Payment authorizations
- Contract financial approvals
- Vendor payments
- Capital expenditures

### Decision Logic

```python
# Rule 1: High-value wire transfer check
if action_type == "wire_transfer" and amount_usd >= 50_000:
    if is_new_vendor and not has_purchase_order:
        decision = BLOCK  # High risk
    else:
        requires_CFO_approval = True

# Rule 2: High-risk destination country
if destination_country in ["Unknown", "XX"] and amount_usd > 10_000:
    decision = BLOCK

# Rule 3: Approved vendor with PO - streamlined
if vendor_status == "approved" and has_purchase_order:
    if amount_usd < 50_000:
        decision = ALLOW  # Auto-approved
```

### Risk Assessment

**Probability Factors**:

- Vendor status (new → B, approved → D)
- Purchase order presence
- Historical payment patterns

**Severity Factors** (based on amount):

- ≥$1M: Severity I (Catastrophic)
- ≥$100K: Severity II (Critical)
- ≥$10K: Severity III (Moderate)
- <$10K: Severity IV (Negligible)

**Mitigations**:

- Verify vendor with external database (D&B, Creditsafe)
- Conduct vendor due diligence
- Require dual approval (CFO + Finance Director) for $50K+
- Verify bank account details via separate channel

### Example Request/Response

**Request**:

```json
{
  "request_id": "req_fin_001",
  "judge_type": "FinJudge",
  "action_type": "wire_transfer",
  "context": {
    "amount_usd": 75000,
    "vendor_status": "new",
    "vendor_id": "VND-12345",
    "purchase_order": null,
    "destination_country": "Unknown",
    "destination_bank": "Unknown Bank AG"
  },
  "requested_by": "john.doe@company.com"
}
```

**Response**:

```json
{
  "decision": "BLOCK",
  "risk_assessment": {
    "probability": "B",
    "severity": "II",
    "risk_level": "high",
    "requires_approval": true,
    "approval_authority": "CFO"
  },
  "approval_gate": "cfo",
  "reasoning": "Wire transfer $75K to new vendor without PO requires CFO approval",
  "semantic_trail": "wire→$75K→new_vendor→no_PO→high_risk→CFO_gate→BLOCK",
  "latency_ms": 38.2,
  "next_steps": ["Route to CFO approval queue", "Verify vendor via D&B lookup", "Request supporting documentation"]
}
```

---

## CaseJudge - Legal Case Assessment

### Overview

Binary ALLOW/BLOCK decisions for legal case strategies and actions with focus on risk/reward analysis.

### Use Cases

- Case acceptance (new client/matter intake)
- Settlement authorization ($100K+ threshold)
- Litigation strategy approval
- Discovery scope validation
- Motion filings

### Decision Logic

```python
# Rule 1: Case acceptance - conflict check
if action_type == "case_acceptance":
    if not conflict_check_passed:
        decision = BLOCK  # Ethics violation
    elif case_value < 10_000:
        decision = BLOCK  # Below minimum threshold

# Rule 2: Settlement authorization
if action_type == "settlement_approval":
    if settlement_amount >= 100_000:
        requires_partner_approval = True
    if settlement_amount < case_value * 0.2:
        decision = BLOCK  # Unfavorable settlement

# Rule 3: Litigation strategy - success probability
if probability_of_success < 0.3:
    decision = BLOCK  # Low success rate, recommend settlement
```

### Risk Assessment

**Probability Factors**:

- Conflict check failure → A (Almost certain ethics violation)
- Probability of success <30% → B (Likely to lose)
- Probability of success >70% → E (Rare to lose)

**Severity Factors**:

- Case value ≥$10M or high-profile → I (Catastrophic - reputational + financial)
- Case value ≥$1M → II (Critical)
- Case value ≥$100K → III (Moderate)
- Case value <$100K → IV (Negligible)

**Mitigations**:

- Complete comprehensive conflict of interest analysis
- Obtain ethics committee clearance
- Explore settlement options
- Obtain second opinion from senior litigator
- Document decision rationale for file

### Example

**Context**:

```json
{
  "case_value_usd": 500000,
  "case_type": "contract_dispute",
  "conflict_check_passed": false,
  "probability_of_success": 0.6,
  "statute_of_limitations_days": 45
}
```

**Decision**: BLOCK
**Reasoning**: "Conflict of interest check not passed - BLOCK"
**Risk**: Probability A × Severity III → Risk EH

---

## LawJudge - Legal Compliance Validation

### Overview

Binary ALLOW/BLOCK decisions for legal compliance and regulatory validation with emphasis on EU AI Act and CA SB 53.

### Use Cases

- EU AI Act compliance (high-risk AI systems)
- GDPR compliance (DPIA requirements)
- CA SB 53 transparency validation
- Contract legal review ($1M+ threshold)
- Export control compliance

### High-Risk AI Systems (EU AI Act)

Per Article 6, these systems require enhanced oversight:

- Biometric identification
- Critical infrastructure
- Law enforcement
- Education scoring/admission
- Employment decisions
- Essential private/public services
- Migration/asylum/border control

### Decision Logic

```python
# Rule 1: EU AI Act - high-risk systems
if compliance_area == "eu_ai_act":
    if ai_system_type in HIGH_RISK_SYSTEMS:
        if not legal_review_completed:
            decision = BLOCK  # €30M fine risk

# Rule 2: GDPR - DPIA requirement
if compliance_area == "gdpr" or jurisdiction == "EU":
    if processes_personal_data and not dpia_completed:
        decision = BLOCK  # GDPR Article 35 violation

# Rule 3: CA SB 53 - transparency disclosure
if compliance_area == "ca_sb53":
    if not transparency_disclosure:
        decision = BLOCK  # Missing required disclosure

# Rule 4: Export control
if destination_country in ["CN", "RU", "IR", "KP"]:
    if not export_license:
        decision = BLOCK  # ITAR/EAR violation
```

### Risk Assessment

**Probability Factors**:

- No legal review → B (Likely violation)
- High-risk AI system → C (Possible - complex regulations)
- Legal review complete → D (Unlikely)

**Severity Factors**:

- EU AI Act + high-risk system → I (€30M + criminal liability)
- GDPR/EU AI Act (general) → II (€20M fine + reputation)
- CA SB 53 → III (Civil penalties)
- Export control violation → I (Criminal penalties + export ban)

**Mitigations**:

- Obtain legal counsel review and opinion
- Complete Data Protection Impact Assessment (DPIA)
- Conduct AI risk assessment per EU AI Act Article 9
- Establish conformity assessment procedure
- Implement technical documentation requirements
- Prepare transparency disclosure documentation
- Publish model cards and performance metrics

### Example - High-Risk AI System

**Context**:

```json
{
  "compliance_area": "eu_ai_act",
  "ai_system_type": "biometric_identification",
  "legal_review_completed": false,
  "jurisdiction": "EU"
}
```

**Decision**: BLOCK
**Risk**: Probability B × Severity I → Risk EH
**Reasoning**: "High-risk AI system (biometric_identification) requires legal review - BLOCK"
**Penalty Risk**: Up to €30,000,000 or 6% of annual global turnover + criminal liability

---

## FraudJudge - Fraud Detection & Risk Scoring

### Overview

Binary ALLOW/BLOCK decisions for fraud prevention with ML-based scoring and multi-indicator analysis.

### Use Cases

- Payment fraud detection
- Account takeover prevention
- Identity verification
- Transaction pattern anomalies
- Vendor fraud screening

### Fraud Score Thresholds

- **High risk**: ≥0.7 → Immediate BLOCK
- **Medium risk**: 0.4-0.7 → Additional verification required
- **Low risk**: <0.4 → Monitor with standard controls

### Decision Logic

```python
# Rule 1: High fraud score - immediate block
if fraud_score >= 0.7:
    decision = BLOCK

# Rule 2: Identity verification failure
if not identity_verified and amount_usd > 1000:
    decision = BLOCK

# Rule 3: Multiple fraud indicators (≥3)
indicators = [
    geo_mismatch,
    velocity_exceeded,
    not device_fingerprint_match,
    is_new_payee and amount_usd > 5000,
    account_age_days < 30
]
if sum(indicators) >= 3:
    decision = BLOCK

# Rule 4: New account with high-value transaction
if account_age_days < 7 and amount_usd > 10_000:
    decision = BLOCK

# Rule 5: Velocity check failure
if velocity_exceeded:
    decision = BLOCK  # Possible account takeover
```

### Risk Assessment

**Probability Factors**:

- Fraud score ≥0.7 OR indicators ≥3 → A (Almost certain)
- Fraud score ≥0.5 OR indicators ≥2 → B (Likely)
- Fraud score ≥0.3 OR indicators ≥1 → C (Possible)
- Fraud score ≥0.1 → D (Unlikely)
- Fraud score <0.1 → E (Rare)

**Severity Factors**:

- Account takeover OR identity theft → I (Catastrophic)
- Amount ≥$100K → II (Critical - major financial loss)
- Amount ≥$10K → III (Moderate)
- Amount <$10K → IV (Negligible)

**Mitigations**:

- Trigger step-up authentication (MFA)
- Contact account holder via verified channel
- Require identity verification (KYC)
- Verify transaction via out-of-band communication
- Implement transaction delay/cooling-off period
- Route to manual fraud review queue
- Monitor account for 48 hours post-transaction
- Flag for behavioral analytics system

### Example - High Fraud Score

**Context**:

```json
{
  "fraud_score": 0.82,
  "identity_verified": false,
  "geo_location_mismatch": true,
  "velocity_check_failed": true,
  "device_fingerprint_match": false,
  "amount_usd": 5000,
  "account_age_days": 15
}
```

**Decision**: BLOCK
**Risk**: Probability A × Severity III → Risk EH
**Fraud Indicators**: 5 detected (score, identity, geo, velocity, device)
**Reasoning**: "High fraud score (0.82) + multiple indicators (5) detected - BLOCK"

---

## Cross-Vertical Patterns

### Common Risk Factors

All judges share these patterns:

1. **Documentation validation**: Missing docs → higher risk
2. **Authority verification**: Unverified parties → BLOCK
3. **Amount thresholds**: Higher amounts → higher severity
4. **Time urgency**: Statute of limitations, deadlines → expedite
5. **Multi-indicator analysis**: ≥3 risk flags → BLOCK

### Semantic Trail Format

All judges use consistent semantic compression:

```
action→key_factor_1→key_factor_2→risk_level→approval_gate→decision
```

**Examples**:

- FinJudge: `wire→$75K→new_vendor→no_PO→high_risk→CFO_gate→BLOCK`
- CaseJudge: `case_accept→$500K→conflict_failed→EH_risk→escalate→BLOCK`
- LawJudge: `eu_ai_act→biometric_id→no_legal_review→EH_risk→legal_gate→BLOCK`
- FraudJudge: `payment→fraud_0.82→5_indicators→EH_risk→manual_review→BLOCK`

### Performance Metrics

All judges track:

- Decision count (ALLOW vs BLOCK)
- Latency (avg, p50, p99 - target ≤90ms)
- Risk distribution (EH/H/M/L)
- Approval rate (% requiring human approval)

---

## Integration Guide

### Using Judges in Code

```python
from src.judges import JudgeFactory, JudgeRequest, JudgeType

# Create request
request = JudgeRequest(
    request_id="unique_id",
    judge_type=JudgeType.FIN,  # or CASE, LAW, FRAUD
    action_type="wire_transfer",
    context={...},
    requested_by="user@company.com"
)

# Get judge and evaluate
judge = JudgeFactory.get_judge(JudgeType.FIN)
response = judge.judge(request)

# Check decision
if response.decision == JudgeDecision.BLOCK:
    # Route to approval queue
    send_to_approval_queue(response)
else:
    # Proceed with action
    execute_action(request.context)

# Store audit trail
audit_trail = judge.create_audit_trail(response, request)
save_audit_trail(audit_trail)
```

### API Integration

```bash
# Evaluate action
curl -X POST http://localhost:8001/judges/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_001",
    "judge_type": "FinJudge",
    "action_type": "wire_transfer",
    "context": {...}
  }'

# Get audit trail
curl http://localhost:8001/judges/audit/req_001

# Get metrics
curl http://localhost:8001/judges/metrics/FinJudge
```

---

**Last Updated**: 2025-11-17
**Version**: 1.0.0
