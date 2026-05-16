# BUGFIX INSERT — Is/Is Not + 6M Cause & Effect

Use for: Bug fixes, issue diagnosis, root cause analysis

---

## 1. Problem Definition (Is/Is Not)

| Dimension | IS | IS NOT |
|-----------|----|---------|
| **WHAT** | [What is happening] | [What is not happening] |
| **WHERE** | [Where it occurs] | [Where it doesn't occur] |
| **WHEN** | [When it happens] | [When it doesn't happen] |
| **EXTENT** | [How much/many affected] | [How much/many not affected] |

### Timeline

```

[Date] - [Event/Change]
   |
[Date] - [Event/Change]
   |
[Date] - Bug first observed
   |
[Date] - Current state

```

---

## 2. Potential Causes (6M Fishbone)

### Man (People)


- [ ] User error

- [ ] Training gap

- [ ] Permission issue

### Machine (Systems)


- [ ] Hardware failure

- [ ] Resource exhaustion

- [ ] Version mismatch

### Method (Process)


- [ ] Incorrect algorithm

- [ ] Race condition

- [ ] Missing validation

### Material (Data)


- [ ] Corrupt input

- [ ] Missing data

- [ ] Wrong format

### Measurement (Monitoring)


- [ ] Incorrect metric

- [ ] Alert threshold

- [ ] Log gap

### Environment


- [ ] Config difference

- [ ] Network issue

- [ ] External service

---

## 3. Data Collection

### Existing Data Analysis


- [ ] **Process Control Chart**: [Trend analysis]

- [ ] **Pareto Analysis**: [80/20 causes]

- [ ] **Box Plots**: [Distribution check]

### Additional Data Needed

| Data Point | Collection Method | Expected Insight |
|------------|-------------------|------------------|
| | | |

---

## 4. Root Cause Identification

### Contradiction Matrix

| Potential Cause | Explains IS | Explains IS NOT | Verdict |
|-----------------|-------------|-----------------|---------|
| | Yes/No | Yes/No | Keep/Reject |

### Most Likely Root Cause

**Cause**: [Primary root cause]
**Evidence**: [Supporting data]
**Confidence**: [High/Medium/Low]

---

## 5. Corrective Actions

### Action Types


- [ ] **Elimination**: Remove the cause entirely

- [ ] **Facilitation**: Make correct behavior easier

- [ ] **Mitigation**: Reduce impact

- [ ] **Flagging**: Add warnings/alerts

- [ ] **Error Proofing**: Prevent recurrence

### Corrective Action Plan

| Action | Owner | Status | Verification |
|--------|-------|--------|--------------|
| | | | |

---

## 6. Validation & Standardization

### Verification Steps


- [ ] Reproduce original bug → confirm fixed

- [ ] Regression test suite passes

- [ ] Capability study shows improvement

### Standardization


- [ ] Update documentation

- [ ] Add to runbook

- [ ] Create regression test

- [ ] Update monitoring/alerts
