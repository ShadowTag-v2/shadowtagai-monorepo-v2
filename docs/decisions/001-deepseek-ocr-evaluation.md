# ADR 001: DeepSeek OCR (3B) Evaluation - Decision to Defer

## Status
**DEFERRED** until scale justifies custom OCR models

## Date
2025-11-07

## Context

Evaluated DeepSeek OCR (3B) as a potential component for the Pnkln Core Stack, specifically for document processing capabilities within the AiURCM compliance automation pipeline.

### Technology Overview
- **Model**: DeepSeek OCR (3B parameters)
- **Capabilities**: Lightweight vision-language model for optical character recognition
- **Key Features**:
  - Edge-deployable size (3B parameters)
  - Fast inference for real-time processing
  - Good accuracy on standard OCR tasks
  - Open-source availability

### Revenue Pathway Analysis

Evaluated four potential integration vectors:

#### 1. AiURCM Compliance Automation (65% ROI probability)
- **Use Case**: Ingest legacy compliance documents at scale
- **Markets**: Pharma (FDA), Finance (SEC), Defense (contract T&Cs)
- **Revenue Hook**: "Cut compliance review time 80%"
- **Blocker**: Compliance = regulated verticals requiring vendor audit. DeepSeek fails CMMC/ITAR requirements.
- **Alternative**: Google Document AI (compliance-ready, native GCP integration)

#### 2. ShadowTag Video Pipeline (45% ROI probability)
- **Use Case**: Extract text from watermarked video frames
- **Revenue Hook**: Enhanced watermark enforcement for enterprise customers
- **Blocker**: DCT watermarks are frequency-domain, not text-based. Wrong tool for core use case.
- **Potential**: Could detect visible overlay text ("DRAFT", "CONFIDENTIAL")

#### 3. Digital Freeway Edge OCR (25% ROI probability)
- **Use Case**: Vehicle dashcam → road sign reading → routing
- **Revenue Hook**: Premium navigation accuracy
- **Blocker**: Year 10+ roadmap, not MVP. Tesla already has superior in-vehicle vision models.

#### 4. Internal Cost Optimization (10% ROI probability)
- **Use Case**: Pnkln internal document processing
- **Revenue Hook**: None. Cost avoidance only.
- **Blocker**: Premature optimization for bootstrapped startup.

## Decision

**DEFER** DeepSeek OCR integration. Archive as reference architecture for future evaluation.

### Rationale

1. **No Current Problem**: We don't have an OCR problem that needs solving
2. **No Volume Justification**: Document processing volume doesn't justify custom model optimization
3. **Superior Alternatives Exist**: Google Document AI provides:
   - Native GCP integration
   - Compliance-ready (CMMC, ITAR, SOC 2)
   - Free tier for MVP validation
   - "Good enough" accuracy for current needs

4. **Opportunity Cost**:
   - Integration effort: 20-40 hours
   - Expected cost savings: ~$0 (not at scale yet)
   - ROI: **NEGATIVE** until Year 2+

5. **Critical Path Conflict**: Distracts from actual revenue-generating work:
   - Judge #6 deployment on GKE
   - LangGraph orchestration
   - NS mesh architecture
   - Revenue model validation

## Consequences

### Positive
- Maintain focus on core value proposition
- Avoid premature optimization
- Use proven, compliance-ready tooling
- Faster time-to-market for MVP

### Negative
- Miss potential cost optimization opportunity (minimal at current scale)
- Dependency on Google Document AI pricing
- Less technical differentiation in OCR pipeline

### Neutral
- Archive reference architecture for future use
- Establish pattern for technology evaluation
- Document decision rationale for investors/team

## Revisit Conditions

Re-evaluate DeepSeek OCR (or similar lightweight vision models) when:

1. **Volume Threshold**: Document processing >1M docs/month
2. **Cost Threshold**: Google Document AI costs >$50K/year
3. **Strategic Threshold**: OCR accuracy becomes competitive differentiator
4. **Compliance Threshold**: Custom model can achieve required certifications

## Implementation

```bash
# Archive reference
mkdir -p ~/pnkln/research/edge-ai-patterns
# Store DeepSeek notebook link as reference

# Document in research log
echo "2025-11-07: DeepSeek OCR (3B) - Edge AI reference architecture" >> docs/research/RESEARCH_LOG.md
echo "Decision: Defer until scale justifies custom models" >> docs/research/RESEARCH_LOG.md
echo "Revisit: When doc processing >$50K/year at Google pricing" >> docs/research/RESEARCH_LOG.md
```

## References

- DeepSeek OCR (3B) Colab Notebook: [Link to be added]
- Google Document AI: https://cloud.google.com/document-ai
- Alternative: PaliGemma (Google), Gemini Nano for edge deployment

## Lessons Learned

**The Steve Jobs Question**: "Does this make the product 10x better for customers?"
- **Answer**: No. Customers buy governance, not OCR. OCR is a feature. Judge #6 is the product.

**Cool tech doesn't pay the bills. Customers solving urgent problems pay the bills.**

This decision establishes a pattern:
1. Evaluate technology against revenue pathways
2. Assess opportunity cost vs. critical path
3. Choose "good enough" proven solutions for MVP
4. Defer optimization until scale justifies investment
5. Document decision rationale for future reference

---

**Next Action**: Focus on GKE inference architecture for Judge #6 deployment.
