/**
 * Main ShadowTagAi orchestrator
 * The only API anyone needs
 */

import { Mode, type ShadowTagAiResponse, type UserRequest } from '../types';
import { logger } from '../utils/logger';
import { metrics } from '../utils/metrics';
import { IntentClassifier } from './intent-classifier';
import { VertexOrchestrator } from './vertex-orchestrator';
import { WealthEngine } from './wealth-engine';

export class ShadowTagAi {
  private orchestrator: VertexOrchestrator;
  private classifier: IntentClassifier;
  private wealth: WealthEngine;

  constructor() {
    this.orchestrator = new VertexOrchestrator();
    this.classifier = new IntentClassifier();
    this.wealth = new WealthEngine();

    logger.info('ShadowTagAi orchestrator initialized');
  }

  /**
   * THE MAGIC METHOD
   * User types anything. We figure it out.
   */
  async execute(request: UserRequest): Promise<ShadowTagAiResponse> {
    const startTime = Date.now();
    const { input, context, userId, sessionId } = request;

    logger.info('ShadowTagAi execution started', {
      userId,
      sessionId,
      inputLength: input.length,
    });

    try {
      // STEP 1: Understand intent
      const intent = await this.classifier.classify(input);

      logger.info('Intent classified', {
        mode: intent.mode,
        confidence: intent.confidence,
      });

      // STEP 2: Route to correct mode with revenue optimization
      const enrichedResult = await this.wealth.optimize(
        async () => {
          return await this.orchestrator.execute(input, intent.mode, {
            ...context,
            intentReasoning: intent.reasoning,
            extractedParams: intent.extractedParams,
          });
        },
        { mode: intent.mode, ...context },
      );

      // STEP 3: Parse and format response
      const response = this.formatResponse(enrichedResult, intent.mode);

      const executionTime = Date.now() - startTime;

      // Record metrics
      metrics.recordRequest(intent.mode, executionTime, true);

      logger.info('ShadowTagAi execution completed', {
        mode: intent.mode,
        executionTime,
        revenueImpact: enrichedResult.netProfit,
        userId,
        sessionId,
      });

      return {
        ...response,
        executionTime,
        mode: intent.mode,
        metadata: {
          userId,
          sessionId,
          intent: intent.reasoning,
          confidence: intent.confidence,
        },
      };
    } catch (error) {
      const executionTime = Date.now() - startTime;

      metrics.recordRequest(Mode.THINK, executionTime, false);

      logger.error('ShadowTagAi execution failed', {
        error: error instanceof Error ? error.message : String(error),
        userId,
        sessionId,
        executionTime,
      });

      // Return graceful error response
      return {
        answer:
          'I encountered an error processing your request. Please try again or rephrase your question.',
        revenueImpact: '$0',
        nextSteps: [
          'Try rephrasing your request',
          'Check system status',
          'Contact support if issue persists',
        ],
        confidence: 0,
        executionTime,
        mode: Mode.THINK,
        metadata: {
          error: error instanceof Error ? error.message : String(error),
          userId,
          sessionId,
        },
      };
    }
  }

  /**
   * Format the enriched result into a user-friendly response
   */
  private formatResponse(
    enrichedResult: unknown,
    mode: Mode,
  ): Omit<ShadowTagAiResponse, 'executionTime' | 'mode' | 'metadata'> {
    try {
      // Try to parse JSON response from Claude
      const content = enrichedResult.content;
      let parsed: unknown;

      // Extract JSON from response (handle markdown code blocks)
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        parsed = JSON.parse(jsonMatch[0]);
      } else {
        // Not JSON, treat as plain text
        return {
          answer: content,
          revenueImpact: this.formatMoney(enrichedResult.netProfit),
          nextSteps: enrichedResult.recommendations || [],
          confidence: enrichedResult.confidence || 0.5,
        };
      }

      // Format based on mode
      switch (mode) {
        case Mode.THINK:
          return this.formatThinkResponse(parsed, enrichedResult);

        case Mode.BUILD:
          return this.formatBuildResponse(parsed, enrichedResult);

        case Mode.SCALE:
          return this.formatScaleResponse(parsed, enrichedResult);

        default:
          return {
            answer: content,
            revenueImpact: this.formatMoney(enrichedResult.netProfit),
            nextSteps: enrichedResult.recommendations || [],
            confidence: enrichedResult.confidence || 0.5,
          };
      }
    } catch (error) {
      logger.warn('Failed to parse structured response, returning raw content', {
        error: error instanceof Error ? error.message : String(error),
      });

      return {
        answer: enrichedResult.content,
        revenueImpact: this.formatMoney(enrichedResult.netProfit),
        nextSteps: enrichedResult.recommendations || [],
        confidence: enrichedResult.confidence || 0.5,
      };
    }
  }

  /**
   * Format THINK mode response
   */
  private formatThinkResponse(parsed: unknown, enriched: unknown): unknown {
    const answer = `
**Core Insight:** ${parsed.coreInsight || 'Analysis complete'}

**Reasoning:**
${(parsed.reasoning || []).map((r: string, i: number) => `${i + 1}. ${r}`).join('\n')}

**Recommended Action:**
${parsed.recommendedAction || 'No specific action recommended'}

**Business Judgment:** ${parsed.businessJudgment || 'Under review'}
    `.trim();

    const nextSteps = [parsed.recommendedAction, ...(enriched.recommendations || [])].filter(
      Boolean,
    );

    return {
      answer,
      revenueImpact: parsed.revenueImpact?.estimated || this.formatMoney(enriched.netProfit),
      nextSteps: nextSteps.slice(0, 5), // Limit to 5 steps
      confidence: parsed.revenueImpact?.confidence || enriched.confidence || 0.5,
    };
  }

  /**
   * Format BUILD mode response
   */
  private formatBuildResponse(parsed: unknown, enriched: unknown): unknown {
    const filesCreated = (parsed.files || []).map((f: unknown) => f.path).join(', ');
    const commandsToRun = (parsed.commands || []).join('\n');

    const answer = `
**${parsed.summary || 'Build completed'}**

**Files Created:** ${filesCreated || 'None'}

**Commands to Execute:**
\`\`\`bash
${commandsToRun || 'No commands'}
\`\`\`

**Estimated Monthly Cost:** ${parsed.estimatedCost?.monthly || '$0'}

**Revenue Projection:** ${parsed.revenueProjection?.monthly || 'TBD'}

**Security Checklist:**
${(parsed.securityChecklist || []).map((c: string) => `- ${c}`).join('\n')}
    `.trim();

    const nextSteps = [
      'Review generated files',
      'Execute deployment commands',
      'Monitor initial metrics',
      ...(enriched.recommendations || []),
    ].filter(Boolean);

    return {
      answer,
      revenueImpact: parsed.revenueProjection?.monthly || this.formatMoney(enriched.netProfit),
      nextSteps: nextSteps.slice(0, 5),
      confidence: enriched.confidence || 0.7,
    };
  }

  /**
   * Format SCALE mode response
   */
  private formatScaleResponse(parsed: unknown, enriched: unknown): unknown {
    const current = parsed.currentState || {};
    const recommendation = parsed.recommendation || {};
    const projections = parsed.projections || {};

    const answer = `
**Scaling Analysis Complete**

**Current State:**
- Pods: ${current.pods || 'Unknown'}
- CPU: ${current.cpu || 'Unknown'}
- Memory: ${current.memory || 'Unknown'}
- Revenue/Hour: ${current.revenuePerHour || '$0'}
- Cost/Hour: ${current.costPerHour || '$0'}

**Recommendation:** ${recommendation.action?.toUpperCase() || 'MONITOR'}
- Target Pods: ${recommendation.targetPods || current.pods}
- Reasoning: ${recommendation.reasoning || 'No changes needed'}

**Projections:**
- Expected Revenue Lift: ${projections.expectedRevenueLift || '$0/month'}
- Cost Increase: ${projections.costIncrease || '$0/month'}
- Net Profit Increase: ${projections.netProfitIncrease || '$0/month'}
- Confidence: ${projections.confidence || 0.5}

**Commands to Execute:**
\`\`\`bash
${(parsed.executeCommands || []).join('\n')}
\`\`\`
    `.trim();

    const nextSteps = [
      ...(parsed.executeCommands || []),
      ...(parsed.killSwitchTriggers || []),
      ...(enriched.recommendations || []),
    ]
      .filter(Boolean)
      .slice(0, 5);

    return {
      answer,
      revenueImpact: projections.netProfitIncrease || this.formatMoney(enriched.netProfit),
      nextSteps,
      confidence: projections.confidence || enriched.confidence || 0.7,
    };
  }

  /**
   * Format number as money string
   */
  private formatMoney(amount: number): string {
    if (amount === 0) return '$0';
    if (amount < 0) return `-$${Math.abs(amount).toFixed(0)}`;
    return `$${amount.toFixed(0)}`;
  }

  /**
   * Health check
   */
  async health(): Promise<any> {
    const vertexHealthy = await this.orchestrator.healthCheck();

    return {
      status: vertexHealthy ? 'healthy' : 'unhealthy',
      vertex: vertexHealthy,
      timestamp: new Date().toISOString(),
    };
  }
}
