/**
 * Custom error classes for Universal Copilot
 */

/**
 * Base error class for all copilot errors
 */
export class CopilotError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly retryable: boolean = false,
    public readonly details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = 'CopilotError';
    Object.setPrototypeOf(this, CopilotError.prototype);
  }
}

/**
 * Provider-specific errors
 */
export class ProviderError extends CopilotError {
  constructor(
    message: string,
    public readonly provider: string,
    retryable: boolean = false,
    details?: Record<string, unknown>,
  ) {
    super(message, 'PROVIDER_ERROR', retryable, { ...details, provider });
    this.name = 'ProviderError';
    Object.setPrototypeOf(this, ProviderError.prototype);
  }
}

/**
 * Rate limit exceeded
 */
export class RateLimitError extends CopilotError {
  constructor(
    message: string,
    public readonly retryAfterMs?: number,
    details?: Record<string, unknown>,
  ) {
    super(message, 'RATE_LIMIT_EXCEEDED', true, { ...details, retryAfterMs });
    this.name = 'RateLimitError';
    Object.setPrototypeOf(this, RateLimitError.prototype);
  }
}

/**
 * Governance rejection
 */
export class GovernanceError extends CopilotError {
  constructor(
    message: string,
    public readonly riskLevel: string,
    public readonly violatedAxioms: string[],
    details?: Record<string, unknown>,
  ) {
    super(message, 'GOVERNANCE_REJECTED', false, {
      ...details,
      riskLevel,
      violatedAxioms,
    });
    this.name = 'GovernanceError';
    Object.setPrototypeOf(this, GovernanceError.prototype);
  }
}

/**
 * Validation error
 */
export class ValidationError extends CopilotError {
  constructor(message: string, details?: Record<string, unknown>) {
    super(message, 'VALIDATION_ERROR', false, details);
    this.name = 'ValidationError';
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}

/**
 * Patch application error
 */
export class PatchError extends CopilotError {
  constructor(message: string, details?: Record<string, unknown>) {
    super(message, 'PATCH_ERROR', false, details);
    this.name = 'PatchError';
    Object.setPrototypeOf(this, PatchError.prototype);
  }
}

/**
 * Timeout error
 */
export class TimeoutError extends CopilotError {
  constructor(
    message: string,
    public readonly timeoutMs: number,
  ) {
    super(message, 'TIMEOUT', true, { timeoutMs });
    this.name = 'TimeoutError';
    Object.setPrototypeOf(this, TimeoutError.prototype);
  }
}
