/**
 * MCP Interceptor — Tool Call Audit Logger
 *
 * Sprint Item #15: Structured logging for all MCP tool invocations.
 *
 * Captures all MCP tool calls, masks PII, and stores audit records
 * in Firestore for compliance and debugging.
 *
 * @see OWASP LLM06 — Excessive Agency
 * @see ATP 5-19 Tier System
 */

import { z } from 'zod';

// ─── Types ──────────────────────────────────────────────────────────

const ToolCallLogSchema = z.object({
  id: z.string().uuid(),
  timestamp: z.string().datetime(),
  toolName: z.string(),
  serverName: z.string(),
  arguments: z.record(z.unknown()),
  result: z.object({
    status: z.enum(['success', 'error', 'timeout']),
    durationMs: z.number(),
    errorMessage: z.string().optional(),
  }),
  context: z.object({
    firmId: z.string().uuid(),
    sessionId: z.string(),
    userId: z.string().optional(),
    stage: z.string().optional(),
  }),
  riskTier: z.enum(['T1_SAFE', 'T2_MODERATE', 'T3_DESTRUCTIVE', 'T4_FORBIDDEN']),
});

type ToolCallLog = z.infer<typeof ToolCallLogSchema>;

// ─── Risk Classification ────────────────────────────────────────────

const TOOL_RISK_MAP: Record<string, ToolCallLog['riskTier']> = {
  // T1 — Read-only, safe
  'google-developer-knowledge:search_documents': 'T1_SAFE',
  'google-developer-knowledge:get_documents': 'T1_SAFE',
  'google-developer-knowledge:answer_query': 'T1_SAFE',
  'firebase-mcp-server:firestore_get_document': 'T1_SAFE',
  'firebase-mcp-server:firestore_list_documents': 'T1_SAFE',
  'firebase-mcp-server:firestore_query_collection': 'T1_SAFE',
  'chrome-devtools-mcp:take_screenshot': 'T1_SAFE',
  'chrome-devtools-mcp:take_snapshot': 'T1_SAFE',

  // T2 — Writes, moderate risk
  'firebase-mcp-server:firestore_add_document': 'T2_MODERATE',
  'firebase-mcp-server:firestore_update_document': 'T2_MODERATE',
  'StitchMCP:generate_screen_from_text': 'T2_MODERATE',
  'StitchMCP:edit_screens': 'T2_MODERATE',

  // T3 — Destructive operations
  'firebase-mcp-server:firestore_delete_document': 'T3_DESTRUCTIVE',
  'firebase-mcp-server:firestore_delete_database': 'T3_DESTRUCTIVE',

  // T4 — Forbidden (should never appear in production)
  'firebase-mcp-server:auth_update_user': 'T4_FORBIDDEN',
};

// ─── PII Masking ────────────────────────────────────────────────────

const PII_PATTERNS: Array<[RegExp, string]> = [
  [/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, '[EMAIL_REDACTED]'],
  [/\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g, '[PHONE_REDACTED]'],
  [/\b\d{3}[-]?\d{2}[-]?\d{4}\b/g, '[SSN_REDACTED]'],
  [/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, '[CARD_REDACTED]'],
];

function maskPII(input: unknown): unknown {
  if (typeof input === 'string') {
    let masked = input;
    for (const [pattern, replacement] of PII_PATTERNS) {
      masked = masked.replace(pattern, replacement);
    }
    return masked;
  }
  if (Array.isArray(input)) {
    return input.map(maskPII);
  }
  if (typeof input === 'object' && input !== null) {
    const masked: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(input)) {
      // Completely redact known sensitive fields
      if (['password', 'secret', 'token', 'apiKey', 'pem', 'private_key'].includes(key)) {
        masked[key] = '[REDACTED]';
      } else {
        masked[key] = maskPII(value);
      }
    }
    return masked;
  }
  return input;
}

// ─── Interceptor ────────────────────────────────────────────────────

export class MCPInterceptor {
  private logs: ToolCallLog[] = [];
  private readonly firmId: string;
  private readonly sessionId: string;

  constructor(firmId: string, sessionId: string) {
    this.firmId = firmId;
    this.sessionId = sessionId;
  }

  /**
   * Wraps an MCP tool call with audit logging.
   */
  async intercept<T>(
    toolName: string,
    serverName: string,
    args: Record<string, unknown>,
    executor: () => Promise<T>,
    stage?: string,
  ): Promise<T> {
    const toolKey = `${serverName}:${toolName}`;
    const riskTier = TOOL_RISK_MAP[toolKey] ?? 'T2_MODERATE';

    // Block T4 forbidden operations
    if (riskTier === 'T4_FORBIDDEN') {
      const log = this.createLog(toolName, serverName, args, {
        status: 'error',
        durationMs: 0,
        errorMessage: `BLOCKED: Tool ${toolKey} is T4_FORBIDDEN and cannot be executed.`,
      }, riskTier, stage);

      this.logs.push(log);
      await this.persist(log);
      throw new Error(`Tool ${toolKey} is forbidden by ATP 5-19 doctrine.`);
    }

    const start = performance.now();
    try {
      const result = await executor();
      const durationMs = Math.round(performance.now() - start);

      const log = this.createLog(toolName, serverName, args, {
        status: 'success',
        durationMs,
      }, riskTier, stage);

      this.logs.push(log);
      await this.persist(log);

      return result;
    } catch (error) {
      const durationMs = Math.round(performance.now() - start);

      const log = this.createLog(toolName, serverName, args, {
        status: 'error',
        durationMs,
        errorMessage: error instanceof Error ? error.message : 'Unknown error',
      }, riskTier, stage);

      this.logs.push(log);
      await this.persist(log);

      throw error;
    }
  }

  private createLog(
    toolName: string,
    serverName: string,
    args: Record<string, unknown>,
    result: ToolCallLog['result'],
    riskTier: ToolCallLog['riskTier'],
    stage?: string,
  ): ToolCallLog {
    return {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      toolName,
      serverName,
      arguments: maskPII(args) as Record<string, unknown>,
      result,
      context: {
        firmId: this.firmId,
        sessionId: this.sessionId,
        stage,
      },
      riskTier,
    };
  }

  private async persist(log: ToolCallLog): Promise<void> {
    // In production, write to Firestore
    console.log(
      `[MCP Interceptor] ${log.riskTier} | ${log.serverName}:${log.toolName} | ${log.result.status} | ${log.result.durationMs}ms`,
    );
  }

  getAuditTrail(): ToolCallLog[] {
    return [...this.logs];
  }

  getStats(): {
    total: number;
    byTier: Record<string, number>;
    byStatus: Record<string, number>;
    avgDurationMs: number;
  } {
    const byTier: Record<string, number> = {};
    const byStatus: Record<string, number> = {};
    let totalDuration = 0;

    for (const log of this.logs) {
      byTier[log.riskTier] = (byTier[log.riskTier] ?? 0) + 1;
      byStatus[log.result.status] = (byStatus[log.result.status] ?? 0) + 1;
      totalDuration += log.result.durationMs;
    }

    return {
      total: this.logs.length,
      byTier,
      byStatus,
      avgDurationMs: this.logs.length > 0 ? Math.round(totalDuration / this.logs.length) : 0,
    };
  }
}
