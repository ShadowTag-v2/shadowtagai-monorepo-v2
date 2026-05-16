/**
 * Judge #6 Types - ATP 5-19 Compliance Scanner
 */

export interface Judge6Decision {
  purpose: string;
  reasons: string[];
  brakes_violated: boolean;
  brakes_pass: boolean;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  risk: {
    probability: number; // 0-4
    severity: number; // 0-3
  };
  atp519_bytes: number;
  atp519_binary?: string;
  confidence: number;
  timestamp: string;
}

export interface ScanRequest {
  purpose: string;
  context?: Record<string, any>;
  atp519?: boolean;
}

export interface ScanResponse {
  decision: Judge6Decision;
  latency_ms: number;
  cost_usd: number;
}

export interface RiskMatrixCell {
  level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  char: string;
  color: string;
}
