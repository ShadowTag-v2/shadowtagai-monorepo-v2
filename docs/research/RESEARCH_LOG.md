# ShadowTagAi Technology Research Log

## Purpose

Track technology evaluations, experiments, and decisions to maintain institutional knowledge and demonstrate decision rigor.

## Format

```
YYYY-MM-DD | Technology | Decision | Rationale | Revisit Conditions
```

---

## 2025-11-07

### DeepSeek OCR (3B) - Edge AI Reference Architecture

- **Decision**: DEFER until scale justifies custom OCR models
- **Rationale**:
  - No current OCR problem to solve
  - Google Document AI provides compliance-ready solution
  - Opportunity cost conflicts with critical path (Judge 6 GKE deployment)
  - Expected ROI negative until Year 2+
- **Revisit When**:
  - Document processing volume >1M docs/month
  - Google Document AI costs >$50K/year
  - OCR accuracy becomes competitive differentiator
- **Reference**: See ADR 001 for full analysis
- **Archived**: Future reference for edge AI deployment patterns

---

## Research Categories

### 1. Core Stack Components

Technologies directly related to ShadowTagAi Core Stack (Judge 6, LangGraph, NS mesh, ShadowTag)

### 2. Edge AI & Optimization

Lightweight models, edge deployment, inference optimization

### 3. Compliance & Security

Regulatory technology, audit tooling, watermarking, DRM

### 4. Revenue-Enabling Features

Technologies that directly enable new revenue streams

### 5. Cost Optimization

Technologies that reduce operational costs at scale

---

## Decision Framework

All technology evaluations should answer:

1. **Revenue Pathway**: Which of the 30 verticals does this enable?
2. **Strategic Fit**: Does this align with ShadowTagAi Core Stack architecture?
3. **Opportunity Cost**: What critical path work does this displace?
4. **ROI Timeline**: When does this generate positive ROI?
5. **Steve Jobs Question**: Does this make the product 10x better for customers?

If answers are unclear → DEFER and revisit later.

---

## Active Research Areas

- [ ] GKE inference architecture for Judge 6 deployment
- [ ] LangGraph orchestration patterns for multi-agent workflows
- [ ] NS mesh routing optimization
- [ ] ShadowTag DCT watermarking implementation

---

## Archived Research

| Date       | Technology        | Status   | Link                                                   |
| ---------- | ----------------- | -------- | ------------------------------------------------------ |
| 2025-11-07 | DeepSeek OCR (3B) | DEFERRED | [ADR 001](../decisions/001-deepseek-ocr-evaluation.md) |

---

**Last Updated**: 2025-11-07
