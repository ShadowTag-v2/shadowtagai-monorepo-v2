/**
 * Core type definitions for shadowtagai orchestrator
 */

export enum Mode {
  THINK = 'think',
  BUILD = 'build',
  SCALE = 'scale',
  RESEARCH = 'research', // Multi-source research orchestration
}

export interface UserRequest {
  input: string;
  context?: Record<string, any>;
  userId?: string;
  sessionId?: string;
}

export interface IntentClassification {
  mode: Mode;
  confidence: number;
  reasoning: string;
  extractedParams: Record<string, any>;
}

export interface RevenueMetrics {
  beforeRevenue: number;
  afterRevenue: number;
  costIncurred: number;
  netProfit: number;
  confidence: number;
  timestamp: string;
}

export interface Opportunity {
  type: string;
  estimatedRevenue: number;
  requiredInvestment: number;
  roi: number;
  confidence: number;
  timeToRealization: number; // months
}

export interface EnrichedResult<T> {
  content: T;
  moneyMade: number;
  costIncurred: number;
  netProfit: number;
  recommendations: string[];
  confidence: number;
  metrics?: RevenueMetrics;
}

export interface ShadowTagAiResponse {
  answer: string;
  revenueImpact: string;
  nextSteps: string[];
  confidence: number;
  executionTime: number;
  mode: Mode;
  metadata?: Record<string, any>;
}

export interface SinglePointOfTruth {
  requirements: string[];
  constraints: string[];
  successCriteria: string[];
  source: 'supergrok' | 'claude' | 'system';
  createdAt: string;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  uptime: number;
  version: string;
  vertexConnected: boolean;
  metrics: {
    requestsProcessed: number;
    averageResponseTime: number;
    errorRate: number;
    revenueGenerated: number;
  };
}

export interface MonteCarloResult {
  expectedValue: number;
  variance: number;
  confidenceInterval: [number, number];
  probability: number;
  simulations: number;
}

export interface BusinessJudgmentAnalysis {
  decision: 'APPROVE' | 'REJECT' | 'DEFER';
  roiExpected: number;
  ltvCacRatio: number;
  paybackMonths: number;
  npvProbability: number;
  reasoning: string;
  monteCarlo: MonteCarloResult;
}
