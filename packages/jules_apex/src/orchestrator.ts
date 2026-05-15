/**
 * JulesCloudRunOrchestrator — Maps Judge 6 verdicts to Cloud Run deployments.
 *
 * This is the critical bridge between the ShadowTag governance pipeline
 * (Judge 6 classifies risk) and autonomous Cloud Run deployments via Jules.
 *
 * Flow: Judge 6 Verdict → Risk Classification → Jules Session → PR/Deploy
 */

import { createApexClient, type JulesApexClient } from './client.js';
import type { SessionConfig, SessionOutput } from './types.js';

/** Judge 6 verdict structure */
export interface Judge6Verdict {
  /** Unique verdict ID */
  verdictId: string;
  /** Risk classification: SAFE, REVIEW, BLOCK */
  riskLevel: 'SAFE' | 'REVIEW' | 'BLOCK';
  /** Confidence score 0-1 */
  confidence: number;
  /** The task description that was classified */
  taskDescription: string;
  /** Files affected */
  affectedFiles?: string[];
  /** Justification from Judge 6 */
  justification: string;
  /** Timestamp */
  timestamp: string;
}

/** Cloud Run deployment configuration */
export interface DeploymentConfig {
  /** GCP project ID */
  projectId: string;
  /** Cloud Run service name */
  serviceName: string;
  /** Region */
  region: string;
  /** Whether to require PR review before merge */
  requireReview: boolean;
  /** Maximum risk level for auto-deploy */
  autoDeployMaxRisk: 'SAFE' | 'REVIEW';
}

/** Result of a deployment orchestration */
export interface DeploymentResult {
  /** Whether deployment was initiated */
  deployed: boolean;
  /** Reason if not deployed */
  reason?: string;
  /** Jules session ID if created */
  sessionId?: string;
  /** Jules session output if completed */
  output?: SessionOutput;
  /** Deployment timestamp */
  timestamp: string;
}

const DEFAULT_CONFIG: DeploymentConfig = {
  projectId: 'shadowtag-omega-v4',
  serviceName: 'counselconduit',
  region: 'us-central1',
  requireReview: true,
  autoDeployMaxRisk: 'SAFE',
};

export class JulesCloudRunOrchestrator {
  private readonly client: JulesApexClient;
  private readonly config: DeploymentConfig;

  constructor(config?: Partial<DeploymentConfig>, client?: JulesApexClient) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.client = client ?? createApexClient();
  }

  /**
   * Evaluates a Judge 6 verdict and potentially triggers a Jules session
   * for Cloud Run deployment.
   *
   * - SAFE verdicts with high confidence → auto-deploy via Jules
   * - REVIEW verdicts → create PR for human review
   * - BLOCK verdicts → reject, log, and notify
   */
  async processVerdict(verdict: Judge6Verdict): Promise<DeploymentResult> {
    const timestamp = new Date().toISOString();

    // BLOCK: Never auto-deploy
    if (verdict.riskLevel === 'BLOCK') {
      return {
        deployed: false,
        reason: `BLOCKED by Judge 6: ${verdict.justification}`,
        timestamp,
      };
    }

    // Check if risk level allows auto-deployment
    const riskOrder = { SAFE: 0, REVIEW: 1, BLOCK: 2 } as const;
    const maxAllowed = riskOrder[this.config.autoDeployMaxRisk];
    const verdictRisk = riskOrder[verdict.riskLevel];

    if (verdictRisk > maxAllowed) {
      return {
        deployed: false,
        reason: `Risk level ${verdict.riskLevel} exceeds auto-deploy maximum ${this.config.autoDeployMaxRisk}`,
        timestamp,
      };
    }

    // Confidence gate: require >0.8 for auto-deploy
    if (verdict.confidence < 0.8) {
      return {
        deployed: false,
        reason: `Confidence ${verdict.confidence} below 0.8 threshold`,
        timestamp,
      };
    }

    // Create Jules session for deployment
    const sessionConfig: SessionConfig = {
      prompt: this.buildDeployPrompt(verdict),
      automationMode: this.config.requireReview ? 'AUTO_CREATE_PR' : 'AUTO_MERGE',
      requirePlanApproval: verdict.riskLevel === 'REVIEW',
    };

    try {
      const session = await this.client.createSession(sessionConfig);

      return {
        deployed: true,
        sessionId: session.sessionId,
        timestamp,
      };
    } catch (error) {
      return {
        deployed: false,
        reason: `Jules session creation failed: ${error instanceof Error ? error.message : String(error)}`,
        timestamp,
      };
    }
  }

  /**
   * Builds the deployment prompt for Jules from a Judge 6 verdict.
   */
  private buildDeployPrompt(verdict: Judge6Verdict): string {
    const filesSection = verdict.affectedFiles?.length
      ? `\n\nAffected files:\n${verdict.affectedFiles.map((f) => `- ${f}`).join('\n')}`
      : '';

    return `Deploy the following change to Cloud Run service "${this.config.serviceName}" in project "${this.config.projectId}" (region: ${this.config.region}).

Task: ${verdict.taskDescription}

Judge 6 Classification:
- Risk Level: ${verdict.riskLevel}
- Confidence: ${verdict.confidence}
- Justification: ${verdict.justification}${filesSection}

Instructions:
1. Apply the described changes to the codebase
2. Ensure all tests pass
3. Update the Cloud Run service configuration if needed
4. Create a descriptive PR with the verdict ID: ${verdict.verdictId}`;
  }
}
