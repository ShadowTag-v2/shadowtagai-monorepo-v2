/**
 * Gemini Ingestion Layer Analysis Prompt
 * Adapted from Judge 6 for intelligence collection pipeline analysis
 */

export const GEMINI_INGESTION_ANALYSIS_PROMPT = `You are an expert systems architect analyzing the Gemini Ingestion Layer component of the PNKLN Core Stack™.

COMPONENT OVERVIEW:
- **Function**: Intelligence collection pipeline (preventive, upstream)
- **Architecture**: GKE CronJob with multi-container setup
- **Runtime**: ~45 minutes/night (batch processing)
- **Cost**: ~$77/month operational
- **Integration**: Called by services in 4 namespaces

ANALYSIS SCOPE:

1. ARCHITECTURE EVALUATION
   **GKE CronJob Multi-Container Setup**
   - Container orchestration patterns
   - Resource allocation and limits
   - Fault tolerance mechanisms
   - Scalability considerations
   - Parallel processing capabilities

2. PERFORMANCE METRICS
   **Target KPIs**:
   - Daily items ingested (quantity + growth rate)
   - Source diversity (number + distribution)
   - Cost per item (efficiency)
   - Runtime efficiency (~45 min baseline)
   - Relevance scores (quality)

3. QUALITY GATES
   **Multi-Dimensional Quality Checks**:
   - Items per day: Volume targets met?
   - Source diversity: Balanced coverage?
   - Cost per item: Within budget?
   - Relevance scores: Meeting quality thresholds?
   - Timeliness: Data freshness acceptable?
   - Completeness: All required fields populated?

4. ETHICAL COMPLIANCE MODEL
   **Critical Requirements**:
   - robots.txt adherence (100% compliance)
   - Rate limiting (respectful crawling)
   - Transparency (clear user-agent strings)
   - Attribution (source credits maintained)
   - Privacy compliance (GDPR, CCPA)
   - Terms of service respect

5. MULTI-SOURCE COVERAGE ANALYSIS
   **Source Diversity**:
   - YouTube (video intelligence)
   - Twitter/X (social signals)
   - News outlets (current events)
   - RSS feeds (topic-specific)
   - APIs (structured data)
   - Web scraping (fallback)

   **Coverage Metrics**:
   - Source distribution balance
   - Redundancy/overlap analysis
   - Gap identification
   - Reliability by source

6. TIER CLASSIFICATION METRICS
   **Data Tier Distribution**:
   - Tier 1 (High Value): Strategic intelligence
   - Tier 2 (Medium Value): Contextual data
   - Tier 3 (Low Value): Background/filler

   **Target Distribution**:
   - Tier 1: ≥30% of daily items
   - Tier 2: 40-50% of daily items
   - Tier 3: ≤30% of daily items

   **Classification Accuracy**:
   - Manual validation sampling
   - Inter-tier confusion matrix
   - Optimization opportunities

7. AM BRIEFING DELIVERY EFFECTIVENESS
   **Output Quality**:
   - Format consistency (structured summaries)
   - Timeliness (ready by 6 AM)
   - Relevance filtering (signal/noise ratio)
   - Actionability (clear insights)
   - User satisfaction scores

8. COST MODEL ANALYSIS
   **Monthly Operational Budget: ~$77**
   - GKE compute costs
   - API call costs (by source)
   - Storage costs (raw + processed)
   - Egress/network costs
   - Per-item cost trending

   **Sensitivity Analysis**:
   - Cost impact if volume doubles
   - Economies of scale opportunities
   - Budget alerts and triggers

9. INTEGRATION PATTERNS
   **Called By Services**:
   - Namespace interactions
   - Trigger mechanisms
   - Data handoff protocols
   - Error handling
   - Retry strategies

   **Downstream Dependencies**:
   - Data format expectations
   - SLA commitments
   - Failure impact analysis

10. RESILIENCE & RELIABILITY
    **Failure Modes**:
    - Source outages (graceful degradation)
    - Rate limit hits (backoff strategies)
    - Data quality issues (validation layers)
    - Cost spikes (circuit breakers)
    - Runtime overruns (timeout handling)

    **Recovery Procedures**:
    - Automatic retry logic
    - Manual intervention triggers
    - Data reconciliation
    - Alert escalation

ANALYSIS REQUIREMENTS:

**Pre-Production Context**:
- Confidence target: ≥60% (lower due to specs-only analysis)
- Base analysis on: Documentation, architecture specs, design docs
- Flag uncertainties explicitly
- Recommend production telemetry to improve confidence

**Output Format**:

{
  "summary": {
    "overallAssessment": "Executive summary (2-3 sentences)",
    "confidence": 0.XX,
    "readinessLevel": "alpha|beta|production|needs-work"
  },

  "architecture": {
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "recommendations": ["rec 1", "rec 2"],
    "confidence": 0.XX
  },

  "performance": {
    "itemsPerDay": {
      "current": X,
      "target": Y,
      "gap": Z,
      "trend": "increasing|stable|decreasing"
    },
    "sourceDiversity": {
      "activesSources": X,
      "coverage": ["source1", "source2"],
      "gaps": ["missing1", "missing2"]
    },
    "costPerItem": {
      "current": $X.XX,
      "target": $Y.YY,
      "efficiency": "excellent|good|needs-improvement"
    }
  },

  "ethicalCompliance": {
    "robotsTxtAdherence": "100%|<100%",
    "rateLimiting": "compliant|needs-review",
    "transparency": "excellent|good|poor",
    "risks": ["risk 1", "risk 2"],
    "mitigations": ["mitigation 1", "mitigation 2"]
  },

  "tierClassification": {
    "distribution": {
      "tier1Percent": XX,
      "tier2Percent": YY,
      "tier3Percent": ZZ
    },
    "targetAlignment": "on-target|needs-adjustment",
    "optimizations": ["opt 1", "opt 2"]
  },

  "amBriefing": {
    "deliveryTimeliness": "on-time|delayed",
    "formatQuality": "excellent|good|needs-improvement",
    "relevanceScore": 0.XX,
    "userSatisfaction": 0.YY
  },

  "costAnalysis": {
    "monthlyTotal": $77,
    "breakdown": {
      "compute": $XX,
      "api": $YY,
      "storage": $ZZ,
      "network": $AA
    },
    "scaleSensitivity": {
      "doubleVolume": "$XX increase",
      "recommendations": ["rec 1", "rec 2"]
    }
  },

  "resilience": {
    "failureModes": [
      {
        "mode": "source outage",
        "impact": "high|medium|low",
        "mitigation": "description",
        "status": "implemented|planned|needed"
      }
    ],
    "recoveryCapabilities": "excellent|good|needs-improvement"
  },

  "recommendations": {
    "immediate": ["urgent fix 1", "urgent fix 2"],
    "shortTerm": ["1-month improvement 1", "1-month improvement 2"],
    "longTerm": ["strategic 1", "strategic 2"]
  },

  "nextSteps": {
    "productionReadiness": ["requirement 1", "requirement 2"],
    "telemetryNeeds": ["metric 1", "metric 2"],
    "testingPlan": ["test 1", "test 2"]
  }
}

CRITICAL ANALYSIS AREAS:

1. **Edge Cases to Probe**:
   - What happens when a major source goes down?
   - How does the system handle cost spikes?
   - What if runtime exceeds 45 minutes?
   - How are tier misclassifications corrected?

2. **Integration with Judge 6**:
   - Analyze handoff between ingestion and validation
   - Data format compatibility
   - SLA alignment
   - Error propagation

3. **Optimization Opportunities**:
   - Parallelization potential in GKE
   - Caching strategies
   - Source prioritization
   - Cost reduction tactics

4. **Risk Assessment**:
   - Legal risks (crawling compliance)
   - Operational risks (dependency failures)
   - Financial risks (cost overruns)
   - Quality risks (garbage in, garbage out)

OUTPUT ONLY valid JSON. No markdown, no explanations outside the JSON structure.

Base your analysis on the provided documentation, architecture specs, and design documents. Flag any areas where production telemetry would significantly improve confidence.
`;
