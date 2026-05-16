/**
 * Thread Transfer Package System
 * Modular context preservation and restoration for AI session continuity
 */

export enum ForkStrategy {
  BEST = "BEST", // Full fork + local clone
  FAST = "FAST", // API-only access
  CHEAP = "CHEAP", // Selective fork
}

export enum RiskLevel {
  EH = "EXTREMELY_HIGH",
  H = "HIGH",
  M = "MEDIUM",
  L = "LOW",
}

export enum Probability {
  A = "A", // Almost certain
  B = "B", // Likely
  C = "C", // Possible
  D = "D", // Unlikely
  E = "E", // Rare
}

export enum Severity {
  I = "I", // Catastrophic
  II = "II", // Critical
  III = "III", // Moderate
  IV = "IV", // Negligible
}

export interface RiskFlag {
  category: string;
  description: string;
  probability: Probability;
  severity: Severity;
  level: RiskLevel;
  mitigation?: string;
}

export interface BootstrapConstraints {
  capital: number;
  slaP99Ms: number;
  roiMultiple: number;
  roiMonths: number;
  ltvCacRatio: number;
  ltvCacMonths: number;
  targetCompression: {
    from: string;
    to: string;
  };
}

export interface FrameworkConfig {
  jrEngine: {
    purpose: string;
    reasons: string[];
    brakes: string[];
  };
  atp519: {
    enabled: boolean;
    thresholds: Record<RiskLevel, string>;
  };
  bootstrap: BootstrapConstraints;
}

export interface Repository {
  org: string;
  repo: string;
  priority: "PRIMARY" | "SECONDARY" | "REFERENCE";
  purpose: string;
}

export interface SessionScope {
  domain: string;
  objective: string;
  startDate: string;
  threadId: string;
}

export interface BuildArtifact {
  type: "script" | "config" | "code" | "document";
  path: string;
  description: string;
  ready: boolean;
  dependencies?: string[];
}

export interface TechnicalContext {
  architecture: string[];
  namespaces?: string[];
  metrics?: Record<string, string | number>;
  integrations?: string[];
}

export interface StateSummary {
  sessionScope: SessionScope;
  whatWeBuilt: BuildArtifact[];
  currentState: {
    status: string;
    blockers: string[];
    nextActions: string[];
  };
  technicalContext: TechnicalContext;
}

export interface HandoffOutline {
  keyParameters: Record<string, string | number | boolean>;
  frameworksActive: FrameworkConfig;
  repositoryTargets?: Repository[];
  currentObjectives: {
    immediate: string[];
    m1to3: string[];
    m3plus: string[];
  };
  variableConventions: Record<string, string>;
  openQuestions: string[];
  riskFlags: RiskFlag[];
}

export interface RestartPrompt {
  threadId: string;
  mission: string;
  currentState: string[];
  bootstrapConstraints: string[];
  frameworksActive: string[];
  repos?: string[];
  openQuestions: string[];
  resumeFrom: string;
}

export interface TransferPackage {
  metadata: {
    version: string;
    generated: string;
    threadId: string;
  };
  part1: StateSummary;
  part2: HandoffOutline;
  part3: RestartPrompt;
  critique: {
    assumptions: string[];
    weaknesses: string[];
    whatCouldBeWrong: string[];
  };
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  completeness: number; // 0-100
}
