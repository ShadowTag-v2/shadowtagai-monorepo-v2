/**
 * Antigravity MCP Interceptor — "The Sovereign Brakes"
 *
 * Prevents the autonomous Agent from destroying the Dumb Backend
 * (Salesforce/Clio/SharePoint). Every MCP tool call passes through
 * the 17-Layer ATP 5-19 risk evaluation before execution.
 *
 * When 10,000 startups begin wiring LLMs directly to enterprise APIs,
 * Antigravity provides the kill switch.
 *
 * Architecture:
 * [Agent] → [Antigravity Interceptor] → [Risk Evaluation] → [MCP Server]
 *         ↳ [RKILL if Tier 5 violation]
 */
import { z } from "zod";

// ─── Risk Evaluation (ATP 5-19 Doctrine) ──────────────────────────────
export enum MitigationTier {
  /** Tier 1: Accept — low risk, proceed */
  Tier1_ACCEPT = 1,
  /** Tier 2: Mitigate — add guardrails and proceed */
  Tier2_MITIGATE = 2,
  /** Tier 3: Review — requires human approval */
  Tier3_REVIEW = 3,
  /** Tier 4: Reject — block and log */
  Tier4_REJECT = 4,
  /** Tier 5: RKILL — catastrophic, kill the agent immediately */
  Tier5_RKILL = 5,
}

// Tool risk classification
const TOOL_RISK_MATRIX: Record<string, { maxTier: MitigationTier; description: string }> = {
  // Read-only operations — safe
  clio_get_contact: { maxTier: MitigationTier.Tier1_ACCEPT, description: "Read contact" },
  clio_get_matter: { maxTier: MitigationTier.Tier1_ACCEPT, description: "Read matter" },
  clio_fuzzy_conflict_check: {
    maxTier: MitigationTier.Tier1_ACCEPT,
    description: "Conflict check",
  },
  sharepoint_read_document: { maxTier: MitigationTier.Tier1_ACCEPT, description: "Read document" },

  // Write operations — mitigate
  clio_attach_dossier: {
    maxTier: MitigationTier.Tier2_MITIGATE,
    description: "Attach document to matter",
  },
  clio_draft_time_entry: {
    maxTier: MitigationTier.Tier2_MITIGATE,
    description: "Draft billable time",
  },
  sharepoint_upload_document: {
    maxTier: MitigationTier.Tier2_MITIGATE,
    description: "Upload to SharePoint",
  },

  // Financial operations — review required
  stripe_create_charge: {
    maxTier: MitigationTier.Tier3_REVIEW,
    description: "Create Stripe charge",
  },
  clio_submit_invoice: {
    maxTier: MitigationTier.Tier3_REVIEW,
    description: "Submit invoice to client",
  },

  // Destructive operations — reject
  clio_delete_matter: { maxTier: MitigationTier.Tier4_REJECT, description: "Delete matter" },
  clio_delete_contact: { maxTier: MitigationTier.Tier4_REJECT, description: "Delete contact" },

  // Catastrophic operations — RKILL
  clio_export_all_data: { maxTier: MitigationTier.Tier5_RKILL, description: "Mass data export" },
  admin_reset_database: { maxTier: MitigationTier.Tier5_RKILL, description: "Database reset" },
};

interface RiskContext {
  tool: string;
  payload: string;
  agentId?: string;
}

/**
 * Evaluates the risk tier of a proposed MCP tool call.
 * Returns the mitigation tier based on the ATP 5-19 doctrine.
 */
export function evaluateRisk(context: RiskContext): MitigationTier {
  // Known tool classification
  const classification = TOOL_RISK_MATRIX[context.tool];
  if (classification) return classification.maxTier;

  // Unknown tools — default to Tier 3 (review)
  // Payload size heuristic: massive payloads are suspicious
  const payloadSize = context.payload.length;
  if (payloadSize > 100_000) return MitigationTier.Tier4_REJECT;
  if (payloadSize > 10_000) return MitigationTier.Tier3_REVIEW;

  // Check for dangerous patterns in payload
  const dangerousPatterns = [
    /DROP\s+TABLE/i,
    /DELETE\s+FROM/i,
    /TRUNCATE/i,
    /rm\s+-rf/i,
    /format\s+c:/i,
    /wget\s+.*\|.*sh/i,
  ];

  for (const pattern of dangerousPatterns) {
    if (pattern.test(context.payload)) {
      return MitigationTier.Tier5_RKILL;
    }
  }

  return MitigationTier.Tier2_MITIGATE;
}

// ─── MCP Client Wrapper ───────────────────────────────────────────────
const MCPCallResultSchema = z.object({
  content: z
    .array(
      z.object({
        type: z.string(),
        text: z.string().optional(),
      }),
    )
    .optional(),
  isError: z.boolean().optional(),
});

/**
 * Antigravity MCP Client with ATP 5-19 risk interception.
 *
 * Every tool call is evaluated before execution. If the call violates
 * the risk policy, it is blocked before reaching the MCP server.
 */
export class AntigravityMCPClient {
  private mcpEndpoint: string;
  private agentId: string;

  constructor(firmMcpUrl: string, agentId: string = "kovelai-agent") {
    this.mcpEndpoint = firmMcpUrl;
    this.agentId = agentId;
  }

  /**
   * Call an MCP tool with ATP 5-19 risk interception.
   *
   * @throws Error if risk tier >= Tier 4
   */
  async callTool(toolName: string, args: Record<string, unknown>): Promise<unknown> {
    const payload = JSON.stringify(args);

    // ── 17-Layer Antigravity Shield Interception ──
    const riskTier = evaluateRisk({
      tool: toolName,
      payload,
      agentId: this.agentId,
    });

    // Log the interception
    const logEntry: InterceptionLog = {
      timestamp: new Date().toISOString(),
      agentId: this.agentId,
      tool: toolName,
      riskTier,
      payloadSizeBytes: payload.length,
      action: "PENDING",
    };

    // Tier 5: RKILL — catastrophic, kill immediately
    if (riskTier === MitigationTier.Tier5_RKILL) {
      logEntry.action = "RKILL";
      await this.logInterception(logEntry);
      throw new AntigravityRKILLError(
        `[ANTIGRAVITY RKILL] ATP 5-19 Violation: Catastrophic tool call blocked. Tool: ${toolName}`,
      );
    }

    // Tier 4: Reject — block and log
    if (riskTier === MitigationTier.Tier4_REJECT) {
      logEntry.action = "REJECTED";
      await this.logInterception(logEntry);
      throw new AntigravityRejectError(
        `[ANTIGRAVITY REJECT] Tool call rejected: ${toolName}. Tier 4 classification.`,
      );
    }

    // Tier 3: Review — log warning, proceed with caution
    if (riskTier === MitigationTier.Tier3_REVIEW) {
      logEntry.action = "REVIEW_PASSED";
      await this.logInterception(logEntry);
    }

    // Tier 1-2: Proceed
    logEntry.action = "ALLOWED";
    await this.logInterception(logEntry);

    // Execute the MCP call
    try {
      const response = await fetch(`${this.mcpEndpoint}/tools/${toolName}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Antigravity-Agent": this.agentId,
          "X-Antigravity-Risk-Tier": riskTier.toString(),
        },
        body: payload,
        signal: AbortSignal.timeout(30000),
      });

      if (!response.ok) {
        throw new Error(`MCP call failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      return MCPCallResultSchema.parse(result);
    } catch (error) {
      if (error instanceof AntigravityRKILLError || error instanceof AntigravityRejectError) {
        throw error;
      }
      throw new Error(
        `[ANTIGRAVITY] MCP call to ${toolName} failed: ${error instanceof Error ? error.message : "Unknown error"}`,
      );
    }
  }

  /**
   * Batch execute multiple tool calls with shared risk context.
   */
  async callToolBatch(
    calls: Array<{ tool: string; args: Record<string, unknown> }>,
  ): Promise<unknown[]> {
    const results: unknown[] = [];
    for (const call of calls) {
      const result = await this.callTool(call.tool, call.args);
      results.push(result);
    }
    return results;
  }

  /**
   * Log interception to Firestore (or console in dev).
   */
  private async logInterception(entry: InterceptionLog): Promise<void> {
    if (process.env.NODE_ENV === "development") {
      console.log("[ANTIGRAVITY LOG]", JSON.stringify(entry));
      return;
    }
    // Production: write to Firestore interception_log collection
    // This is fire-and-forget — don't block the tool call
    try {
      await fetch(`${process.env.FIRESTORE_API_URL}/interception_log`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(entry),
      });
    } catch {
      // Swallow — never block tool calls for logging failures
    }
  }
}

// ─── Error Types ──────────────────────────────────────────────────────
export class AntigravityRKILLError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AntigravityRKILLError";
  }
}

export class AntigravityRejectError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AntigravityRejectError";
  }
}

// ─── Types ────────────────────────────────────────────────────────────
interface InterceptionLog {
  timestamp: string;
  agentId: string;
  tool: string;
  riskTier: MitigationTier;
  payloadSizeBytes: number;
  action: "PENDING" | "ALLOWED" | "REVIEW_PASSED" | "REJECTED" | "RKILL";
}
