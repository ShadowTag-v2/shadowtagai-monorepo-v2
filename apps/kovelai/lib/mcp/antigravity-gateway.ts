/**
 * Antigravity MCP Gateway — Sovereign Brakes & Deepfake Shield
 *
 * The central interception layer between the KovelAI Agent and ALL
 * external tool calls. This gateway:
 *
 * 1. WRITE PROTECTION: ATP 5-19 risk evaluation on outbound calls
 * 2. READ PROTECTION: Injection sanitization on inbound payloads
 * 3. PROVENANCE: FRE 902 Genesis Block hashing at point of collection
 * 4. AUDIT: Every tool call logged for SOC 2 evidence
 *
 * The Agent NEVER touches Google Drive, Cloud Browsers, or CRM
 * backends directly. Everything flows through this gateway.
 */

import { randomUUID } from 'node:crypto';
import { createGenesisBlock, type GenesisBlockEntry } from '@/lib/crypto/genesis-block';
import {
  type SanitizationResult,
  sanitizePromptInjection,
  shouldQuarantine,
} from '@/lib/security/injection-shield';

// ─── Types ──────────────────────────────────────────────────────

export type RiskTier = 'OBSERVE' | 'WARN' | 'GATE' | 'DENY' | 'RKILL';

export interface ToolCallResult {
  success: boolean;
  data: unknown;
  sanitizationResult?: SanitizationResult;
  genesisBlock?: GenesisBlockEntry;
  riskTier: RiskTier;
  quarantined: boolean;
  auditId: string;
}

interface GatewayConfig {
  /** Firm ID for provenance chain */
  firmId: string;
  /** S.E.U. session ID */
  seuSessionId: string;
  /** Allowed tool names (whitelist) */
  allowedTools?: string[];
}

// ─── Tool Risk Classification ───────────────────────────────────

/** ATP 5-19 risk tiers for each tool category */
const TOOL_RISK_MAP: Record<string, RiskTier> = {
  // READ operations — low risk, but need sanitization
  google_drive_read: 'OBSERVE',
  google_drive_list: 'OBSERVE',
  web_browser_scrape: 'WARN',
  clio_read_matter: 'OBSERVE',
  clio_search_contacts: 'OBSERVE',
  westlaw_search: 'OBSERVE',
  lexis_search: 'OBSERVE',
  courtlistener_search: 'OBSERVE',

  // WRITE operations — elevated risk, need approval
  clio_create_matter: 'GATE',
  clio_attach_dossier: 'GATE',
  clio_draft_time_entry: 'GATE',
  slack_send_message: 'GATE',
  email_send: 'GATE',

  // DANGEROUS operations — require explicit approval
  clio_delete_matter: 'DENY',
  google_drive_delete: 'DENY',
  stripe_refund: 'DENY',

  // CATASTROPHIC — auto-blocked, no override
  database_drop: 'RKILL',
  file_system_write: 'RKILL',
  shell_execute: 'RKILL',
};

/** Tools whose responses need injection sanitization */
const SANITIZABLE_TOOLS = new Set([
  'google_drive_read',
  'web_browser_scrape',
  'westlaw_search',
  'lexis_search',
  'courtlistener_search',
]);

/** Tools that ingest raw evidence needing FRE 902 notarization */
const NOTARIZABLE_TOOLS = new Set(['google_drive_read', 'web_browser_scrape']);

// ─── Audit Log ──────────────────────────────────────────────────

interface AuditEntry {
  id: string;
  timestamp: string;
  toolName: string;
  riskTier: RiskTier;
  firmId: string;
  seuSessionId: string;
  quarantined: boolean;
  threatScore: number;
  genesisBlockId?: string;
  outcome: 'ALLOWED' | 'BLOCKED' | 'QUARANTINED';
}

const auditLog: AuditEntry[] = [];

// ─── Gateway ────────────────────────────────────────────────────

export class AntigravityMCPGateway {
  private config: GatewayConfig;

  constructor(config: GatewayConfig) {
    this.config = config;
  }

  /**
   * Intercepts ALL tool calls from the KovelAI Agent.
   *
   * Flow:
   * 1. Classify risk tier (ATP 5-19)
   * 2. Block RKILL/DENY operations
   * 3. Execute the tool call
   * 4. Sanitize response for injection (READ PROTECTION)
   * 5. Hash evidence for FRE 902 (PROVENANCE)
   * 6. Return clean, notarized result
   */
  async callTool(
    toolName: string,
    args: Record<string, unknown>,
    rawResponseBytes?: Buffer,
  ): Promise<ToolCallResult> {
    const auditId = randomUUID();

    // 1. Risk classification
    const riskTier = TOOL_RISK_MAP[toolName] ?? 'GATE';

    // 2. RKILL — immediate block, no override
    if (riskTier === 'RKILL') {
      this.logAudit(auditId, toolName, riskTier, false, 0, 'BLOCKED');
      return {
        success: false,
        data: {
          error: `[ANTIGRAVITY RKILL] ATP 5-19 Violation: Tool "${toolName}" is permanently blocked.`,
        },
        riskTier,
        quarantined: false,
        auditId,
      };
    }

    // 3. DENY — block unless explicit human override exists
    if (riskTier === 'DENY') {
      this.logAudit(auditId, toolName, riskTier, false, 0, 'BLOCKED');
      return {
        success: false,
        data: {
          error: `[ANTIGRAVITY DENY] Tool "${toolName}" requires explicit human authorization.`,
        },
        riskTier,
        quarantined: false,
        auditId,
      };
    }

    // 4. Whitelist check
    if (this.config.allowedTools && !this.config.allowedTools.includes(toolName)) {
      this.logAudit(auditId, toolName, riskTier, false, 0, 'BLOCKED');
      return {
        success: false,
        data: { error: `Tool "${toolName}" is not in the allowed tools whitelist.` },
        riskTier,
        quarantined: false,
        auditId,
      };
    }

    // 5. Execute the tool call (simulated — in production this calls the MCP transport)
    const rawResult = await this.executeToolCall(toolName, args);

    // 6. READ PROTECTION: Sanitize inbound data
    let sanitizationResult: SanitizationResult | undefined;
    let processedData = rawResult;

    if (SANITIZABLE_TOOLS.has(toolName) && typeof rawResult === 'string') {
      sanitizationResult = sanitizePromptInjection(rawResult);

      if (shouldQuarantine(sanitizationResult)) {
        this.logAudit(
          auditId,
          toolName,
          riskTier,
          true,
          sanitizationResult.threatScore,
          'QUARANTINED',
        );
        return {
          success: false,
          data: {
            error: '[QUARANTINED] Adversarial content detected. Payload isolated.',
            threats: sanitizationResult.detectedThreats,
          },
          sanitizationResult,
          riskTier,
          quarantined: true,
          auditId,
        };
      }

      processedData = sanitizationResult.cleanText;
    }

    // 7. PROVENANCE: FRE 902 Genesis Block
    let genesisBlock: GenesisBlockEntry | undefined;

    if (NOTARIZABLE_TOOLS.has(toolName) && rawResponseBytes) {
      const sourceType =
        toolName === 'google_drive_read'
          ? ('GOOGLE_DRIVE_API' as const)
          : ('CLOUD_BROWSER_SCRAPE' as const);

      genesisBlock = createGenesisBlock(
        rawResponseBytes,
        sourceType,
        String(args.url ?? args.fileId ?? 'unknown'),
        this.config.seuSessionId,
        this.config.firmId,
      );
    }

    // 8. Audit
    this.logAudit(
      auditId,
      toolName,
      riskTier,
      false,
      sanitizationResult?.threatScore ?? 0,
      'ALLOWED',
      genesisBlock?.id,
    );

    return {
      success: true,
      data: processedData,
      sanitizationResult,
      genesisBlock,
      riskTier,
      quarantined: false,
      auditId,
    };
  }

  /** Returns all audit entries for SOC 2 evidence export */
  getAuditLog(): readonly AuditEntry[] {
    return auditLog;
  }

  // ─── Private ────────────────────────────────────────────────

  private async executeToolCall(
    toolName: string,
    _args: Record<string, unknown>,
  ): Promise<unknown> {
    // In production, this connects to the actual MCP transport (SSE/stdio).
    // Here we return the tool name for tracing — the caller provides raw data.
    return `[MCP_RESPONSE:${toolName}]`;
  }

  private logAudit(
    id: string,
    toolName: string,
    riskTier: RiskTier,
    quarantined: boolean,
    threatScore: number,
    outcome: AuditEntry['outcome'],
    genesisBlockId?: string,
  ): void {
    auditLog.push({
      id,
      timestamp: new Date().toISOString(),
      toolName,
      riskTier,
      firmId: this.config.firmId,
      seuSessionId: this.config.seuSessionId,
      quarantined,
      threatScore,
      genesisBlockId,
      outcome,
    });
  }
}
