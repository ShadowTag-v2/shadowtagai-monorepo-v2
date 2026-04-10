/**
 * PNKLN Gemini Ingestion Layer - Complete Analysis Example
 *
 * This example demonstrates how to use the Master All-Agent Framework
 * to analyze a real-world intelligence pipeline system.
 *
 * System: Gemini Ingestion Layer (PNKLN Core Stack™)
 * Pattern: Single-Agent + Extended Thinking
 * Analysis Type: Pre-Production (Specs Only)
 */

import { GeminiIngestionAnalyzer } from "../../../src/agents/gemini-ingestion-analyzer";

// ==================== Example Specification Data ====================

const geminiIngestionSpec = `
# Gemini Ingestion Layer Specification

## Overview
Nightly intelligence collection pipeline running on GKE, collecting data from
multiple sources for PNKLN Core Stack™ AM Briefing delivery.

## Architecture
- **Platform**: Google Kubernetes Engine (GKE)
- **Execution Model**: CronJob (0 2 * * * - 2 AM daily)
- **Containers**: 4-container pod
  1. Controller (orchestrates workflow)
  2. YouTube Collector
  3. Twitter Collector
  4. News/RSS Collector

## Performance
- **Target Runtime**: 45 minutes (2:00 AM - 2:45 AM)
- **Current Runtime**: 47 minutes (slight overage)
- **Bottleneck**: Sequential source processing

## Data Sources
- YouTube: API-based, ~500 items/day
- Twitter: API-based, ~1,200 items/day
- News Sites: Web scraping, ~300 items/day
- RSS Feeds: XML parsing, ~200 items/day

## Quality Gates
- **Items/Day**: Target 2,000+ (currently 2,200)
- **Tier 1 %**: Target 25-30% (currently 22%)
- **Tier 2 %**: Target 40-50% (currently 53%)
- **Tier 3 %**: Target 20-30% (currently 25%)
- **Error Rate**: Target <2% (currently 1.3%)

## Cost Model
- **Compute**: $46/month (GKE cluster)
- **Network**: $15/month (egress)
- **Storage**: $8/month (persistent volumes)
- **APIs**: $8/month (YouTube, Twitter)
- **Total**: $77/month

## Ethical Compliance
- **robots.txt**: Checked and cached (24h)
- **Rate Limiting**: 2s default, 5s for rate-limited sites
- **User-Agent**: "PNKLNBot/1.0 (+https://pnkln.ai/bot; redacted@shadowtag-v4.local)"
- **Attribution**: Source URLs preserved

## Integration
- **Called By**:
  - Judge #6 (validation namespace)
  - AM Briefing (delivery namespace)
  - Analytics (metrics namespace)
  - Admin (management namespace)

## Current Issues
1. Sequential processing limits parallelization
2. Tier 1 percentage below target
3. News scraping occasionally triggers 429 errors
4. No incremental processing (full reprocess nightly)
`;

// ==================== Example GKE Configuration ====================

const gkeConfig = `
apiVersion: batch/v1
kind: CronJob
metadata:
  name: gemini-ingestion
  namespace: pnkln-ingestion
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: controller
            image: gcr.io/pnkln/controller:v1.2.3
            resources:
              requests:
                cpu: "500m"
                memory: "512Mi"
              limits:
                cpu: "1000m"
                memory: "1Gi"

          - name: youtube-collector
            image: gcr.io/pnkln/youtube:v1.2.3
            resources:
              requests:
                cpu: "250m"
                memory: "256Mi"
              limits:
                cpu: "500m"
                memory: "512Mi"

          - name: twitter-collector
            image: gcr.io/pnkln/twitter:v1.2.3
            resources:
              requests:
                cpu: "250m"
                memory: "256Mi"
              limits:
                cpu: "500m"
                memory: "512Mi"

          - name: news-collector
            image: gcr.io/pnkln/news:v1.2.3
            resources:
              requests:
                cpu: "250m"
                memory: "256Mi"
              limits:
                cpu: "500m"
                memory: "512Mi"

          restartPolicy: OnFailure
`;

// ==================== Run Analysis ====================

async function runGeminiAnalysis() {
  console.log("=== PNKLN GEMINI INGESTION LAYER ANALYSIS ===\n");

  // Save specs to temp files (in production, would read from actual files)
  const fs = require("fs").promises;
  await fs.writeFile("/tmp/gemini-spec.md", geminiIngestionSpec);
  await fs.writeFile("/tmp/gke-config.yaml", gkeConfig);

  // Create analyzer with pre-production config
  const analyzer = new GeminiIngestionAnalyzer({
    confidenceTarget: 0.6, // Pre-prod specs-only
    extendedThinking: "think hard", // Complex optimization analysis
    specDocs: ["/tmp/gemini-spec.md", "/tmp/gke-config.yaml"],
    metrics: {
      targetRuntime: 45, // minutes
      monthlyBudget: 77, // dollars
      targetConfidence: 0.6, // pre-prod
      itemsPerDay: 2200,
      activeSources: 4,
    },
  });

  try {
    console.log("[1/3] Loading specifications...");
    console.log("  ✓ Gemini Ingestion Spec (architecture, sources, costs)");
    console.log("  ✓ GKE Configuration (resources, scheduling)\n");

    console.log("[2/3] Running comprehensive analysis...");
    console.log("  → Using Claude Sonnet 4.5 with extended thinking");
    console.log(
      "  → Analyzing 6 dimensions (architecture, performance, cost, ethics, quality, integration)",
    );
    console.log("  → Target confidence: 60% (pre-production)\n");

    const analysis = await analyzer.analyzeSystem();

    console.log("[3/3] Analysis complete!\n");

    // ========== Results Display ==========

    console.log("┌─────────────────────────────────────────────────────────────┐");
    console.log("│                    ANALYSIS SUMMARY                         │");
    console.log("└─────────────────────────────────────────────────────────────┘\n");

    console.log(
      `Confidence Score: ${(analysis.confidence * 100).toFixed(1)}% ${analysis.confidence >= 0.6 ? "✓" : "✗"}`,
    );
    console.log(`Timestamp: ${analysis.timestamp}`);
    console.log(`\nSummary:\n${analysis.summary}\n`);

    console.log("┌─────────────────────────────────────────────────────────────┐");
    console.log("│                  DIMENSIONAL SCORES                          │");
    console.log("└─────────────────────────────────────────────────────────────┘\n");

    const scores = analysis.scores;
    console.log(
      `Architecture:       ${(scores.architecture * 100).toFixed(0)}/100 ${getScoreBar(scores.architecture)}`,
    );
    console.log(
      `Performance:        ${(scores.performance * 100).toFixed(0)}/100 ${getScoreBar(scores.performance)}`,
    );
    console.log(
      `Cost Efficiency:    ${(scores.costEfficiency * 100).toFixed(0)}/100 ${getScoreBar(scores.costEfficiency)}`,
    );
    console.log(
      `Ethical Compliance: ${(scores.ethicalCompliance * 100).toFixed(0)}/100 ${getScoreBar(scores.ethicalCompliance)}`,
    );
    console.log(
      `Data Quality:       ${(scores.dataQuality * 100).toFixed(0)}/100 ${getScoreBar(scores.dataQuality)}`,
    );
    console.log(
      `Integration:        ${(scores.integration * 100).toFixed(0)}/100 ${getScoreBar(scores.integration)}`,
    );
    console.log(`─────────────────────────────────────────────────────────────`);
    console.log(
      `Overall:            ${(scores.overall * 100).toFixed(0)}/100 ${getScoreBar(scores.overall)}`,
    );

    console.log("\n┌─────────────────────────────────────────────────────────────┐");
    console.log("│                TOP RECOMMENDATIONS                           │");
    console.log("└─────────────────────────────────────────────────────────────┘\n");

    const topRecs = analysis.recommendations.slice(0, 5);
    topRecs.forEach((rec, i) => {
      console.log(`${i + 1}. [${rec.priority}] ${rec.title}`);
      console.log(`   Category: ${rec.category}`);
      console.log(`   Impact: ${rec.impact}`);
      console.log(`   Effort: ${rec.effort}`);
      if (rec.estimatedSavings) {
        if (rec.estimatedSavings.runtime) {
          console.log(`   💰 Save ${rec.estimatedSavings.runtime} min/night runtime`);
        }
        if (rec.estimatedSavings.cost) {
          console.log(`   💵 Save $${rec.estimatedSavings.cost.toFixed(2)}/month`);
        }
      }
      console.log(`   Details: ${rec.details.substring(0, 120)}...`);
      console.log();
    });

    console.log("┌─────────────────────────────────────────────────────────────┐");
    console.log("│                    RISK ASSESSMENT                           │");
    console.log("└─────────────────────────────────────────────────────────────┘\n");

    if (analysis.risks.length === 0) {
      console.log("✓ No significant risks identified\n");
    } else {
      analysis.risks.forEach((risk, i) => {
        console.log(`${i + 1}. [${risk.severity}] ${risk.category}`);
        console.log(`   Likelihood: ${risk.likelihood}`);
        console.log(`   ${risk.description}`);
        console.log(`   Mitigation: ${risk.mitigation}`);
        console.log();
      });
    }

    console.log("┌─────────────────────────────────────────────────────────────┐");
    console.log("│                  TIER DISTRIBUTION                           │");
    console.log("└─────────────────────────────────────────────────────────────┘\n");

    const tierDist = analysis.tierDistribution;
    console.log(
      `Tier 1 (High-Value):   ${(tierDist.tier1 * 100).toFixed(1)}% ${getBar(tierDist.tier1)} ${tierDist.tier1 >= 0.25 ? "✓" : "⚠️  (Target: 25-30%)"}`,
    );
    console.log(
      `Tier 2 (Medium-Value): ${(tierDist.tier2 * 100).toFixed(1)}% ${getBar(tierDist.tier2)} ${tierDist.tier2 >= 0.4 && tierDist.tier2 <= 0.5 ? "✓" : "⚠️  (Target: 40-50%)"}`,
    );
    console.log(
      `Tier 3 (Low-Value):    ${(tierDist.tier3 * 100).toFixed(1)}% ${getBar(tierDist.tier3)} ${tierDist.tier3 >= 0.2 && tierDist.tier3 <= 0.3 ? "✓" : "⚠️  (Target: 20-30%)"}`,
    );

    console.log("\n┌─────────────────────────────────────────────────────────────┐");
    console.log("│                  SOURCE ANALYSIS                             │");
    console.log("└─────────────────────────────────────────────────────────────┘\n");

    Object.entries(analysis.sourceAnalysis).forEach(([source, metrics]) => {
      console.log(`${source.toUpperCase()}:`);
      console.log(`  Coverage: ${metrics.coverage}`);
      if (metrics.itemsPerDay) {
        console.log(`  Items/Day: ${metrics.itemsPerDay}`);
      }
      if (metrics.issues.length > 0) {
        console.log(`  Issues: ${metrics.issues.join(", ")}`);
      } else {
        console.log(`  Issues: None`);
      }
      console.log();
    });

    console.log("┌─────────────────────────────────────────────────────────────┐");
    console.log("│                  COST PROJECTION                             │");
    console.log("└─────────────────────────────────────────────────────────────┘\n");

    const cost = analysis.costProjection;
    console.log(`Current Monthly Cost:  $${cost.current.toFixed(2)}`);
    console.log(`Optimized Cost:        $${cost.optimized.toFixed(2)}`);
    console.log(
      `Potential Savings:     $${cost.savings.toFixed(2)}/month (${cost.savingsPercent}%)`,
    );
    console.log(`\nCost Breakdown:`);
    console.log(`  Compute:  $${cost.breakdown.compute.toFixed(2)}`);
    console.log(`  Network:  $${cost.breakdown.network.toFixed(2)}`);
    console.log(`  Storage:  $${cost.breakdown.storage.toFixed(2)}`);
    console.log(`  APIs:     $${cost.breakdown.apis.toFixed(2)}`);

    console.log("\n┌─────────────────────────────────────────────────────────────┐");
    console.log("│                    NEXT STEPS                                │");
    console.log("└─────────────────────────────────────────────────────────────┘\n");

    analysis.nextSteps.forEach((step, i) => {
      console.log(`${i + 1}. ${step}`);
    });

    console.log("\n═══════════════════════════════════════════════════════════════");
    console.log("Analysis complete! Review recommendations above.");
    console.log("Full analysis object available in code for programmatic use.");
    console.log("═══════════════════════════════════════════════════════════════\n");

    // Return full analysis for programmatic use
    return analysis;
  } catch (error) {
    console.error("\n✗ Analysis failed:", error.message);
    console.error("\nStack trace:");
    console.error(error.stack);
    process.exit(1);
  }
}

// ==================== Helper Functions ====================

function getScoreBar(score: number): string {
  const filled = Math.round(score * 20);
  const empty = 20 - filled;
  return "█".repeat(filled) + "░".repeat(empty);
}

function getBar(value: number): string {
  const filled = Math.round(value * 30);
  const empty = 30 - filled;
  return "█".repeat(filled) + "░".repeat(empty);
}

// ==================== Run ====================

if (require.main === module) {
  runGeminiAnalysis()
    .then(() => {
      console.log("Process completed successfully.");
      process.exit(0);
    })
    .catch((error) => {
      console.error("Fatal error:", error);
      process.exit(1);
    });
}

export { runGeminiAnalysis };
