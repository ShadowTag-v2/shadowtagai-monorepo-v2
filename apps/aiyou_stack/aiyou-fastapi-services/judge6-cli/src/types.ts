/**
 * Type definitions for Judge #6 CLI
 */

export interface RiskLevel {
  probability: number; // 0-4
  severity: number; // 0-3
  rating: string; // RA-1 through RA-4
}

export interface DecisionValidationResponse {
  purpose: string;
  purpose_valid: boolean;
  purpose_score: number;
  reasons_valid: boolean;
  reasons_score: number;
  brakes_clear: boolean;
  brakes_score: number;
  result: "approved" | "blocked_purpose" | "blocked_reasons" | "blocked_brakes";
  explanation: string;
  risk_level?: RiskLevel;
  compressed_bytes?: number;
  timestamp: string;
}

export interface DecisionValidationRequest {
  purpose: string;
  context?: string;
  atp519?: boolean;
  mission_statement?: string;
}

export interface ValidationHistory {
  request: DecisionValidationRequest;
  response: DecisionValidationResponse;
  timestamp: string;
}
