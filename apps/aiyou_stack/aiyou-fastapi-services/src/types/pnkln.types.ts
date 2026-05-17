/**
 * PNKLN Core Stack Types
 * Type definitions for PNKLN stack components and analysis
 */

export type PNKLNComponent =
  | "judge-6"
  | "gemini-ingestion"
  | "validator"
  | "processor"
  | "storage"
  | "api-gateway";

export type AnalysisConfidence = "low" | "medium" | "high" | "very-high";

export interface ComponentMetrics {
  // Performance Metrics
  latency?: {
    p50?: number;
    p95?: number;
    p99?: number;
    unit: "ms" | "seconds" | "minutes";
  };
  throughput?: {
    value: number;
    unit: "req/sec" | "items/day" | "ops/min";
  };
  runtime?: {
    value: number;
    unit: "minutes" | "hours";
    frequency: "per-request" | "nightly" | "hourly";
  };

  // Quality Gates
  coverage?: number; // percentage
  errorRate?: number; // percentage
  blockRate?: number; // percentage

  // Data Quality (Ingestion-specific)
  itemsPerDay?: number;
  sourceDiversity?: number;
  costPerItem?: number;
  relevanceScore?: number;
  timelinessScore?: number;
  completenessScore?: number;

  // Error Tracking
  falsePositiveRate?: number;
  falseNegativeRate?: number;
}

export interface ArchitectureSpec {
  type: "hybrid-ai" | "gke-cronjob" | "microservice" | "serverless";
  components: string[];
  integrationPattern: "caller" | "callee" | "bidirectional";
  namespaces?: string[];
  containerCount?: number;
}

export interface EthicalCompliance {
  robotsTxtRespect: boolean;
  rateLimiting: {
    enabled: boolean;
    requestsPerSecond?: number;
    requestsPerMinute?: number;
  };
  transparency: {
    userAgentIdentification: boolean;
    privacyPolicyUrl?: string;
  };
  dataRetention?: {
    maxDays: number;
    deletionPolicy: string;
  };
}

export interface TierClassification {
  tier1: { count: number; percentage: number; description: string };
  tier2: { count: number; percentage: number; description: string };
  tier3: { count: number; percentage: number; description: string };
}

export interface MultiSourceCoverage {
  sources: {
    name: string;
    type: "social" | "news" | "video" | "web" | "api";
    itemsCollected: number;
    lastUpdated: string;
    status: "active" | "inactive" | "error";
  }[];
  diversityScore: number; // 0-100
  coverageGaps?: string[];
}

export interface CostModel {
  monthly?: number;
  perOperation?: number;
  perItem?: number;
  breakdown?: {
    compute?: number;
    storage?: number;
    api?: number;
    network?: number;
  };
}

export interface ComponentAnalysisResult {
  component: PNKLNComponent;
  confidence: AnalysisConfidence;
  confidenceScore: number; // 0-100

  metrics: ComponentMetrics;
  architecture: ArchitectureSpec;

  // Component-specific
  ethicalCompliance?: EthicalCompliance;
  tierClassification?: TierClassification;
  multiSourceCoverage?: MultiSourceCoverage;
  costModel?: CostModel;

  // Analysis outputs
  strengths: string[];
  weaknesses: string[];
  risks: string[];
  optimizationOpportunities: string[];
  recommendations: {
    priority: "critical" | "high" | "medium" | "low";
    category: "performance" | "cost" | "quality" | "security" | "scalability";
    description: string;
    estimatedImpact: string;
  }[];

  // Comparison (when analyzing multiple versions)
  comparison?: {
    componentA: string;
    componentB: string;
    keyDifferences: string[];
    migrationPath?: string[];
  };
}

export interface PromptTemplate {
  id: string;
  name: string;
  version: string;
  targetComponent: PNKLNComponent;

  sections: {
    context: string;
    objectives: string[];
    analysisAreas: string[];
    outputFormat: string;
    confidenceThreshold: number;
  };

  replacements: {
    key: string;
    value: string;
    description: string;
  }[];

  adaptations: {
    from: string;
    to: string;
    rationale: string;
  }[];
}

export interface MasterPromptFramework {
  name: string;
  version: string;
  components: PNKLNComponent[];

  baseTemplate: PromptTemplate;
  componentTemplates: Map<PNKLNComponent, PromptTemplate>;

  generatePrompt: (component: PNKLNComponent, customizations?: unknown) => string;
  compareComponents: (componentA: PNKLNComponent, componentB: PNKLNComponent) => string;
  analyzeIntegration: (components: PNKLNComponent[]) => string;
}
