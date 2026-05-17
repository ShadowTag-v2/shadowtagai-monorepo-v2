/**
 * Judge 6 API Client
 *
 * Handles HTTP communication with FastAPI backend.
 */

import fetch from "node-fetch";
import type { DecisionValidationRequest, DecisionValidationResponse } from "./types.js";

export class Cor.Claude_Code_6ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  /**
   * Validate a decision using Judge 6.
   */
  async validate(request: DecisionValidationRequest): Promise<DecisionValidationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = (await response.json()) as { detail: string };
        throw new Error(`API Error: ${error.detail || response.statusText}`);
      }

      return (await response.json()) as DecisionValidationResponse;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to validate decision: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Health check.
   */
  async health(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}
