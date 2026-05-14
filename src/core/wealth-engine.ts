/**
 * Wealth Engine - Revenue optimization layer
 * Every operation analyzed for profit potential
 */

import type { EnrichedResult, MonteCarloResult, Opportunity, RevenueMetrics } from "../types";
import { logger } from "../utils/logger";
import { metrics } from "../utils/metrics";

export class WealthEngine {
  private readonly MIN_LTV_CAC = parseFloat(process.env.MIN_LTV_CAC_RATIO || "4.0");
  private readonly MIN_ROI = parseFloat(process.env.MIN_ROI_THRESHOLD || "3.0");
  private readonly MIN_CONFIDENCE = parseFloat(process.env.MIN_CONFIDENCE || "0.70");

  /**
   * Wrap any operation with revenue optimization
   */
  async optimize<T>(
    operation: () => Promise<T>,
    context?: Record<string, unknown>,
  ): Promise<EnrichedResult<T>> {
    const startTime = Date.now();

    // BEFORE: Capture baseline metrics
    const beforeMetrics = await this.captureMetrics();

    // BEFORE: Identify revenue opportunity
    const opportunity = await this.scanForMoney(context);

    logger.info("Revenue opportunity identified", {
      type: opportunity.type,
      estimatedRevenue: opportunity.estimatedRevenue,
      roi: opportunity.roi,
    });

    // DURING: Execute operation
    let result: T;
    try {
      result = await operation();
    } catch (error) {
      logger.error("Operation failed during wealth optimization", {
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }

    // AFTER: Capture post-execution metrics
    const afterMetrics = await this.captureMetrics();

    // AFTER: Calculate actual impact
    const impact = this.calculateRevenueImpact(beforeMetrics, afterMetrics, opportunity);

    // RECOMMEND: Next money move
    const recommendations = await this.suggestScalePlay(impact, result);

    // Record to monitoring
    metrics.recordRevenueImpact(impact.netProfit);

    const executionTime = Date.now() - startTime;

    logger.info("Operation completed with revenue impact", {
      netProfit: impact.netProfit,
      confidence: impact.confidence,
      executionTime,
    });

    return {
      content: result,
      moneyMade: impact.afterRevenue - impact.beforeRevenue,
      costIncurred: impact.costIncurred,
      netProfit: impact.netProfit,
      recommendations,
      confidence: impact.confidence,
      metrics: impact,
    };
  }

  /**
   * Scan for revenue opportunities in the operation context
   */
  private async scanForMoney(context?: Record<string, unknown>): Promise<Opportunity> {
    // Simple heuristic-based opportunity detection
    // In production, this could use ML models

    const baseOpportunity: Opportunity = {
      type: "optimization",
      estimatedRevenue: 0,
      requiredInvestment: 0,
      roi: 0,
      confidence: 0.5,
      timeToRealization: 1,
    };

    if (!context) {
      return baseOpportunity;
    }

    // Detect opportunity types from context
    if (context.mode === "scale") {
      return {
        type: "scaling",
        estimatedRevenue: 5000, // $5k/month estimate
        requiredInvestment: 1000, // $1k investment
        roi: 5.0,
        confidence: 0.75,
        timeToRealization: 2,
      };
    } else if (context.mode === "build") {
      return {
        type: "new_feature",
        estimatedRevenue: 10000,
        requiredInvestment: 3000,
        roi: 3.33,
        confidence: 0.65,
        timeToRealization: 3,
      };
    }

    return baseOpportunity;
  }

  /**
   * Capture current revenue metrics
   */
  private async captureMetrics(): Promise<Partial<RevenueMetrics>> {
    // In production, query GCP Monitoring for actual metrics
    // For now, return mock data that will be replaced with real metrics

    return {
      beforeRevenue: 0,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Calculate revenue impact of the operation
   */
  private calculateRevenueImpact(
    before: Partial<RevenueMetrics>,
    _after: Partial<RevenueMetrics>,
    opportunity: Opportunity,
  ): RevenueMetrics {
    // Simplified calculation
    // In production, use actual GCP Billing API data

    const estimatedRevenue = opportunity.estimatedRevenue;
    const estimatedCost = opportunity.requiredInvestment;

    return {
      beforeRevenue: before.beforeRevenue || 0,
      afterRevenue: estimatedRevenue,
      costIncurred: estimatedCost,
      netProfit: estimatedRevenue - estimatedCost,
      confidence: opportunity.confidence,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Suggest next scaling plays based on impact
   */
  private async suggestScalePlay<T>(impact: RevenueMetrics, _result: T): Promise<string[]> {
    const recommendations: string[] = [];

    // High profit, high confidence = aggressive scaling
    if (impact.netProfit > 5000 && impact.confidence > 0.8) {
      recommendations.push("SCALE IMMEDIATELY: High profit + high confidence detected");
      recommendations.push("Consider multi-region deployment for 3-5x growth");
      recommendations.push("Implement A/B testing to optimize further");
    }

    // Positive profit, medium confidence = cautious scaling
    else if (impact.netProfit > 1000 && impact.confidence > 0.6) {
      recommendations.push(
        "SCALE GRADUALLY: Positive indicators, validate before aggressive growth",
      );
      recommendations.push("Monitor metrics for 24-48 hours before next scale");
      recommendations.push("Set up kill-switch triggers at error_rate > 2%");
    }

    // Low/negative profit = investigate or kill
    else if (impact.netProfit < 0) {
      recommendations.push("INVESTIGATE: Negative profit detected - review costs");
      recommendations.push("Consider kill-switch if metrics dont improve in 24h");
      recommendations.push("Analyze what competitors are doing differently");
    }

    // Default
    else {
      recommendations.push("MONITOR: Continue observing metrics before scaling");
      recommendations.push("Gather more data to increase confidence");
    }

    return recommendations;
  }

  /**
   * Run Monte Carlo simulation for decision confidence
   */
  async runMonteCarlo(
    baseValue: number,
    variance: number,
    simulations: number = 10000,
  ): Promise<MonteCarloResult> {
    const results: number[] = [];

    for (let i = 0; i < simulations; i++) {
      // Simple normal distribution simulation
      const random = this.normalRandom();
      const value = baseValue + random * variance;
      results.push(value);
    }

    // Calculate statistics
    const sorted = results.sort((a, b) => a - b);
    const mean = results.reduce((a, b) => a + b, 0) / results.length;
    const variance_actual =
      results.reduce((sum, val) => sum + (val - mean) ** 2, 0) / results.length;

    // 95% confidence interval
    const lowerIdx = Math.floor(simulations * 0.025);
    const upperIdx = Math.floor(simulations * 0.975);

    const positiveCount = results.filter((v) => v > 0).length;
    const probability = positiveCount / simulations;

    return {
      expectedValue: mean,
      variance: variance_actual,
      confidenceInterval: [sorted[lowerIdx], sorted[upperIdx]],
      probability,
      simulations,
    };
  }

  /**
   * Generate normal random number (Box-Muller transform)
   */
  private normalRandom(): number {
    const u1 = Math.random();
    const u2 = Math.random();
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  }

  /**
   * Business Judgment Rule check
   */
  async passesBusinessJudgment(roi: number, ltvCac: number, confidence: number): Promise<boolean> {
    const checks = {
      roiCheck: roi >= this.MIN_ROI,
      ltvCacCheck: ltvCac >= this.MIN_LTV_CAC,
      confidenceCheck: confidence >= this.MIN_CONFIDENCE,
    };

    logger.info("Business Judgment Rule check", checks);

    return checks.roiCheck && checks.ltvCacCheck && checks.confidenceCheck;
  }
}
