# FAA Certification Path — Aviation PNT & Edge Systems

**Target:** DO-178C / ED-12B certification for airborne PNT and edge compute modules
**Timeline:** 18–24 months
**Estimated Cost:** $8–12M

---

## 🎯 Regulatory Framework

### Applicable Standards

| Standard | Description | Scope |
|----------|-------------|-------|
| **DO-178C** | Software Considerations in Airborne Systems | All software in aircraft systems |
| **DO-254** | Hardware Considerations | FPGA/ASIC components |
| **DO-160G** | Environmental Conditions and Test Procedures | Physical unit qualification |
| **TSO-C129a** | GPS Equipment | Navigation equipment (if applicable) |
| **TSO-C145/146** | Airborne Navigation Equipment | Integrated navigation systems |

### Design Assurance Levels (DAL)

ShadowTag-v2 systems will target **DAL-C** (Major failure condition):

| DAL | Failure Impact | Objective Compliance | Development Cost |
|-----|----------------|----------------------|------------------|
| A | Catastrophic | ~100% coverage | Very High |
| B | Hazardous | ~90% coverage | High |
| **C** | **Major** | **~70% coverage** | **Medium-High** |
| D | Minor | ~50% coverage | Medium |
| E | No Safety Effect | Minimal | Low |

**Rationale:** PNT loss is "major" (degraded ops, workload increase) but not catastrophic if backup systems exist.

---

## 📋 Certification Process (18-Month Timeline)

### Phase 1: Planning & Documentation (Months 1–3)

**Deliverables:**
1. **Plan for Software Aspects of Certification (PSAC)**
   - Development process
   - Tool qualification
   - Configuration management

2. **Software Development Plan (SDP)**
   - Lifecycle model (V-model or iterative)
   - Standards and methods

3. **Software Verification Plan (SVP)**
   - Test strategies
   - Coverage objectives

4. **Software Configuration Management Plan (SCMP)**
   - Version control
   - Change tracking

5. **Software Quality Assurance Plan (SQAP)**
   - Reviews and audits
   - Problem reporting

**Cost:** $500K–$800K (consulting + internal staff)

---

### Phase 2: Requirements & Design (Months 4–8)

**Deliverables:**
1. **High-Level Requirements (HLR)**
   - Functional requirements
   - Performance requirements
   - Safety requirements
   - Traceability to system requirements

2. **Low-Level Requirements (LLR)**
   - Detailed software requirements
   - Interface definitions
   - Derived requirements

3. **Software Architecture**
   - Module decomposition
   - Data flow diagrams
   - Interface control documents (ICD)

4. **Design Description**
   - Detailed design for each module
   - Algorithm specifications

**Activities:**
- Requirements reviews (formal inspections)
- Design reviews
- Traceability matrix creation (HLR → LLR → Design)

**Cost:** $1.5M–$2.5M

---

### Phase 3: Implementation & Unit Testing (Months 9–14)

**Deliverables:**
1. **Source Code**
   - Coding standards compliance (MISRA-C, CERT-C)
   - Code reviews (structural coverage)

2. **Unit Test Procedures & Results**
   - Statement coverage (DAL-C: ~70%)
   - Branch coverage (DAL-C: ~70%)
   - MC/DC coverage (if required)

**Activities:**
- Code peer reviews
- Static analysis (Coverity, Polyspace)
- Unit testing with coverage tools (Bullseye, LDRA)

**Cost:** $2M–$3M

---

### Phase 4: Integration & Verification (Months 15–18)

**Deliverables:**
1. **Software Integration Plan**
2. **Hardware/Software Integration Tests**
3. **System-Level Test Procedures & Results**
   - Functional tests
   - Performance tests
   - Robustness tests (fault injection)

4. **Requirements-Based Test Coverage**
   - Every HLR/LLR traced to test case

5. **Verification Results**
   - Test reports
   - Coverage reports
   - Anomaly reports and resolutions

**Activities:**
- Integration testing (incremental builds)
- Iron bird testing (aircraft simulator environment)
- Environmental testing (DO-160G: temp, vibration, EMI)

**Cost:** $2.5M–$4M

---

### Phase 5: Certification Liaison (Months 12–24, overlapping)

**Deliverables:**
1. **Software Accomplishment Summary (SAS)**
   - Summary of compliance with DO-178C objectives

2. **Software Configuration Index (SCI)**
   - List of all software items delivered

3. **Software Life Cycle Environment Configuration Index (SECI)**
   - Tools, versions, environments

4. **Problem Reports**
   - All open and closed issues

**Activities:**
- FAA DER (Designated Engineering Representative) engagement
- Stage-of-Involvement (SOI) meetings
- Document reviews and audits
- Compliance findings resolution

**Cost:** $1M–$2M (DER fees + internal coordination)

---

## 🛠️ Tool Qualification

**DO-178C requires qualification of tools used to eliminate/automate verification tasks.**

| Tool Type | Examples | Qualification Level | Cost |
|-----------|----------|---------------------|------|
| Compiler | GCC, LLVM | TQL-5 (if output verified) | $200K–$500K |
| Static Analyzer | Coverity, Polyspace | TQL-2 or TQL-3 | $150K–$300K |
| Coverage Tool | Bullseye, LDRA | TQL-1 | $100K–$250K |
| Requirements Mgmt | DOORS, Jama | TQL-5 | Minimal |

**Total tool qualification:** $500K–$1M

---

## 🧪 Testing Breakdown (DAL-C Objectives)

| Test Type | Coverage Target | Effort (person-months) |
|-----------|-----------------|------------------------|
| Requirements-based tests | 100% of HLR/LLR | 12 |
| Structural coverage (statement) | ~70% | 8 |
| Structural coverage (branch) | ~70% | 6 |
| Robustness tests | Major failure modes | 6 |
| Environmental tests (DO-160G) | All conditions | 4 |
| **Total** | | **36 person-months** |

**Team:** 6 test engineers × 6 months = $900K–$1.5M

---

## 📊 Budget Summary

| Phase | Cost |
|-------|------|
| Planning & Documentation | $500K–$800K |
| Requirements & Design | $1.5M–$2.5M |
| Implementation & Unit Testing | $2M–$3M |
| Integration & Verification | $2.5M–$4M |
| Certification Liaison | $1M–$2M |
| Tool Qualification | $500K–$1M |
| **Total** | **$8M–$12M** |

**Contingency:** +20% for findings resolution, re-tests, schedule slips → **$10M–$15M fully loaded**

---

## 🚀 Fast-Track Options

### Option 1: Modular Certification
- Certify **core PNT module** first (DAL-C) → 12 months, $5M
- Edge compute as **non-certified advisory** initially
- Upgrade to full certification in Phase 2

### Option 2: Reuse Existing Certifications
- Partner with certified avionics supplier (Honeywell, Collins Aerospace)
- License their certified platform, integrate ShadowTag-v2 algorithms as "data provider"
- Reduces timeline to 9–12 months, cost to $3M–$5M

### Option 3: EASA First (EU Market)
- Pursue EASA CS-25 / CS-23 certification in parallel
- Often faster approval in EU; FAA mutual recognition possible
- Same cost, but de-risks US delays

---

## 🧩 Regulatory Strategy

### Year 1: Experimental Certificate
- **FAA Form 8130-7** (Special Airworthiness Certificate)
- Flight testing with 3–5 aircraft (non-revenue)
- Demonstrate safety, gather data
- **Cost:** $200K–$500K

### Year 2: TSO Authorization
- **Technical Standard Order (TSO)** for PNT equipment
- Allows installation on certified aircraft
- **Timeline:** 12–18 months post-experimental
- **Cost:** Included in DO-178C budget above

### Year 3: STC (Supplemental Type Certificate)
- Allows commercial operators to install ShadowTag-v2 units
- Required for airlines to use in revenue service
- **Timeline:** 6–12 months post-TSO
- **Cost:** $1M–$3M (per aircraft type)

---

## 🔒 Compliance Checkpoints

### Critical Reviews (FAA DER Involvement)

| Milestone | Review Type | FAA Engagement |
|-----------|-------------|----------------|
| Requirements complete | System Requirements Review (SRR) | SOI-1 |
| Design complete | Preliminary Design Review (PDR) | SOI-2 |
| Code complete | Critical Design Review (CDR) | SOI-3 |
| Testing complete | Test Readiness Review (TRR) | SOI-4 |
| Certification package | Certification Review | SOI-5 |

**SOI = Stage of Involvement** (FAA oversight gates)

---

## 📅 Gantt Chart (Simplified)

```
Month:  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18
Plans   ████
Req/Des          ████████
Code                      ██████████
Test                                  ████████
Review          ▓    ▓         ▓         ▓
FAA SOI         ●         ●         ●         ●
```

---

## 🎯 Success Criteria

✅ **DO-178C DAL-C compliance** (all objectives met)
✅ **TSO authorization** granted
✅ **3 airline customers** commit to STC installations
✅ **Zero critical findings** from FAA final audit

---

## 📚 References

- **DO-178C:** Software Considerations in Airborne Systems and Equipment Certification (RTCA, 2011)
- **DO-254:** Design Assurance Guidance for Airborne Electronic Hardware (RTCA, 2000)
- **DO-160G:** Environmental Conditions and Test Procedures for Airborne Equipment (RTCA, 2010)
- **FAA Order 8110.49A:** Software Approval Guidelines
- **EASA CS-ETSO:** Certification Specifications for European TSOs

---

**Next:** [DoD RMF Compliance](./dod-rmf-compliance.md) | [FCC Spectrum Filing](./fcc-spectrum-filing-template.md)
