/**
 * V25 Jules Ascension — NotebookLM Epistemic Memory Hook
 *
 * Connects fleet deployment ledger, incident correlations, and triad
 * cycle results to the NotebookLM RAG pipeline for knowledge retrieval.
 * Maintains a structured memory corpus that the IPI quarantine pipeline
 * can safely ingest.
 *
 * References:
 *   - .agents/skills/cor-notebooklm-tacsop/SKILL.md (IPI quarantine)
 *   - src/orchestration/jules_fleet_orchestrator.ts (deployment data)
 *   - src/orchestration/dart_edge_bridge.ts (task data)
 *   - src/orchestration/claude_sourcemap_bridge.ts (error data)
 *   - src/agents/autoresearch_triad.py (research data)
 *
 * @module orchestration/notebooklm_hook
 * Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
 */

import type {
  DeploymentResult,
  FleetHealthReport,
} from './jules_fleet_orchestrator.js';
import type { ErrorCorrelation } from './claude_sourcemap_bridge.js';

// ============================================================================
// TYPES
// ============================================================================

export interface MemoryEntry {
  id: string;
  type: MemoryType;
  title: string;
  content: string;
  timestamp: string;
  source: string;
  tags: string[];
  ttlHours: number;
  metadata: Record<string, unknown>;
}

export type MemoryType =
  | 'deployment'
  | 'incident'
  | 'health_report'
  | 'research'
  | 'triad_cycle'
  | 'governance';

export interface MemoryCorpus {
  entries: MemoryEntry[];
  totalSize: number;
  lastUpdated: string;
  expirationPolicy: ExpirationPolicy;
}

export interface ExpirationPolicy {
  deploymentTtlHours: number;
  incidentTtlHours: number;
  healthReportTtlHours: number;
  researchTtlHours: number;
}

export interface NotebookLMIngestPlan {
  type: 'notebooklm_ingest_plan';
  entries: MemoryEntry[];
  quarantineRequired: boolean;
  trustLevel: 'internal' | 'external' | 'untrusted';
}

// ============================================================================
// DEFAULT EXPIRATION POLICY
// ============================================================================

const DEFAULT_EXPIRATION: ExpirationPolicy = {
  deploymentTtlHours: 168,  // 7 days
  incidentTtlHours: 720,    // 30 days
  healthReportTtlHours: 24,  // 1 day
  researchTtlHours: 336,    // 14 days
};

// ============================================================================
// NOTEBOOKLM EPISTEMIC MEMORY HOOK
// ============================================================================

/**
 * NotebookLMEpistemicHook — Knowledge corpus for fleet intelligence.
 *
 * Transforms deployment results, health reports, incidents, and research
 * into structured memory entries for NotebookLM RAG retrieval.
 * All data is internal (trust level = 'internal') and does NOT require
 * IPI quarantine unless augmented with external data.
 *
 * CRITICAL: This produces INGEST PLANS, not side effects.
 */
export class NotebookLMEpistemicHook {
  private readonly corpus: MemoryCorpus;
  private readonly expirationPolicy: ExpirationPolicy;

  constructor(policy: Partial<ExpirationPolicy> = {}) {
    this.expirationPolicy = { ...DEFAULT_EXPIRATION, ...policy };
    this.corpus = {
      entries: [],
      totalSize: 0,
      lastUpdated: new Date().toISOString(),
      expirationPolicy: this.expirationPolicy,
    };
  }

  // --------------------------------------------------------------------------
  // DEPLOYMENT MEMORY
  // --------------------------------------------------------------------------

  /**
   * Record a deployment result into the memory corpus.
   */
  recordDeployment(result: DeploymentResult): MemoryEntry {
    const entry: MemoryEntry = {
      id: `mem_deploy_${result.sessionId}`,
      type: 'deployment',
      title: `Deployment: ${result.serviceName}`,
      content: this.formatDeploymentContent(result),
      timestamp: new Date().toISOString(),
      source: 'jules_fleet_orchestrator',
      tags: ['deployment', result.serviceName, result.state],
      ttlHours: this.expirationPolicy.deploymentTtlHours,
      metadata: {
        sessionId: result.sessionId,
        state: result.state,
        durationMs: result.durationMs,
        pullRequestUrl: result.pullRequestUrl,
      },
    };

    this.addEntry(entry);
    return entry;
  }

  /**
   * Record a fleet health report.
   */
  recordHealthReport(report: FleetHealthReport): MemoryEntry {
    const entry: MemoryEntry = {
      id: `mem_health_${Date.now()}`,
      type: 'health_report',
      title: `Fleet Health: ${report.healthy}/${report.totalServices} healthy`,
      content: this.formatHealthContent(report),
      timestamp: report.timestamp,
      source: 'jules_fleet_orchestrator',
      tags: ['health', 'fleet'],
      ttlHours: this.expirationPolicy.healthReportTtlHours,
      metadata: {
        totalServices: report.totalServices,
        healthy: report.healthy,
        degraded: report.degraded,
        failed: report.failed,
      },
    };

    this.addEntry(entry);
    return entry;
  }

  // --------------------------------------------------------------------------
  // INCIDENT MEMORY
  // --------------------------------------------------------------------------

  /**
   * Record an error correlation as an incident memory.
   */
  recordIncident(correlation: ErrorCorrelation): MemoryEntry {
    const entry: MemoryEntry = {
      id: `mem_incident_${correlation.correlationId}`,
      type: 'incident',
      title: `Incident: ${correlation.errorPattern.slice(0, 80)}`,
      content: this.formatIncidentContent(correlation),
      timestamp: correlation.lastSeen,
      source: 'claude_sourcemap_bridge',
      tags: ['incident', ...correlation.affectedServices],
      ttlHours: this.expirationPolicy.incidentTtlHours,
      metadata: {
        correlationId: correlation.correlationId,
        occurrenceCount: correlation.occurrenceCount,
        affectedServices: correlation.affectedServices,
      },
    };

    this.addEntry(entry);
    return entry;
  }

  // --------------------------------------------------------------------------
  // RESEARCH MEMORY
  // --------------------------------------------------------------------------

  /**
   * Record a triad cycle result.
   */
  recordTriadCycle(cycleData: {
    cycleId: string;
    question: string;
    mutationCount: number;
    promotedCount: number;
    regressedCount: number;
    elapsedMs: number;
  }): MemoryEntry {
    const entry: MemoryEntry = {
      id: `mem_triad_${cycleData.cycleId}`,
      type: 'triad_cycle',
      title: `Triad: ${cycleData.question.slice(0, 60)}`,
      content: this.formatTriadContent(cycleData),
      timestamp: new Date().toISOString(),
      source: 'autoresearch_triad',
      tags: ['research', 'triad'],
      ttlHours: this.expirationPolicy.researchTtlHours,
      metadata: {
        cycleId: cycleData.cycleId,
        promotionRate: cycleData.mutationCount > 0
          ? cycleData.promotedCount / cycleData.mutationCount
          : 0,
      },
    };

    this.addEntry(entry);
    return entry;
  }

  // --------------------------------------------------------------------------
  // INGEST PLANNING
  // --------------------------------------------------------------------------

  /**
   * Plan a NotebookLM ingest batch.
   *
   * Returns a plan for the IPI quarantine pipeline.
   * Internal data bypasses quarantine; external data requires it.
   */
  planIngest(trustLevel: 'internal' | 'external' = 'internal'): NotebookLMIngestPlan {
    this.pruneExpired();

    return {
      type: 'notebooklm_ingest_plan',
      entries: [...this.corpus.entries],
      quarantineRequired: trustLevel !== 'internal',
      trustLevel,
    };
  }

  /**
   * Query the memory corpus by type and tags.
   */
  query(options: {
    type?: MemoryType;
    tags?: string[];
    limit?: number;
    since?: string;
  }): MemoryEntry[] {
    let entries = [...this.corpus.entries];

    if (options.type) {
      entries = entries.filter((e) => e.type === options.type);
    }

    if (options.tags?.length) {
      entries = entries.filter((e) =>
        options.tags!.some((tag) => e.tags.includes(tag)),
      );
    }

    if (options.since) {
      const sinceDate = new Date(options.since).getTime();
      entries = entries.filter((e) => new Date(e.timestamp).getTime() >= sinceDate);
    }

    // Sort by timestamp descending
    entries.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

    return entries.slice(0, options.limit ?? 50);
  }

  // --------------------------------------------------------------------------
  // PRIVATE HELPERS
  // --------------------------------------------------------------------------

  private addEntry(entry: MemoryEntry): void {
    // Deduplicate by ID
    const existingIdx = this.corpus.entries.findIndex((e) => e.id === entry.id);
    if (existingIdx >= 0) {
      this.corpus.entries[existingIdx] = entry;
    } else {
      this.corpus.entries.push(entry);
    }

    this.corpus.totalSize = this.corpus.entries.length;
    this.corpus.lastUpdated = new Date().toISOString();
  }

  private pruneExpired(): void {
    const now = Date.now();
    this.corpus.entries = this.corpus.entries.filter((entry) => {
      const entryTime = new Date(entry.timestamp).getTime();
      const expiresAt = entryTime + entry.ttlHours * 3600_000;
      return now < expiresAt;
    });
    this.corpus.totalSize = this.corpus.entries.length;
  }

  // --------------------------------------------------------------------------
  // CONTENT FORMATTERS
  // --------------------------------------------------------------------------

  private formatDeploymentContent(result: DeploymentResult): string {
    return `## Deployment: ${result.serviceName}

**State**: ${result.state}
**Session**: ${result.sessionId}
**Duration**: ${result.durationMs}ms
**PR**: ${result.pullRequestUrl ?? 'N/A'}

### Activities
${result.activities.map((a) => `- [${a.type}] ${a.title ?? a.message ?? ''}`).join('\n')}
`;
  }

  private formatHealthContent(report: FleetHealthReport): string {
    return `## Fleet Health

**Timestamp**: ${report.timestamp}
**Total**: ${report.totalServices} | ✅ ${report.healthy} | ⚠️ ${report.degraded} | ❌ ${report.failed} | 🔄 ${report.deploying}

### Services
${report.services.map((s) => `- ${s.name}: ${s.status} (${s.region})`).join('\n')}
`;
  }

  private formatIncidentContent(correlation: ErrorCorrelation): string {
    return `## Incident: ${correlation.errorPattern}

**Occurrences**: ${correlation.occurrenceCount}
**First Seen**: ${correlation.firstSeen}
**Last Seen**: ${correlation.lastSeen}
**Affected Services**: ${correlation.affectedServices.join(', ')}

### Root Cause
${correlation.deobfuscatedTraces[0]?.rootCauseModule ?? 'Unknown'}

### Suggested Fix
${correlation.deobfuscatedTraces[0]?.suggestedFix ?? 'Manual investigation required'}
`;
  }

  private formatTriadContent(cycleData: {
    cycleId: string;
    question: string;
    mutationCount: number;
    promotedCount: number;
    regressedCount: number;
    elapsedMs: number;
  }): string {
    const rate = cycleData.mutationCount > 0
      ? ((cycleData.promotedCount / cycleData.mutationCount) * 100).toFixed(1)
      : '0.0';

    return `## Triad Cycle: ${cycleData.cycleId}

**Question**: ${cycleData.question}
**Mutations**: ${cycleData.mutationCount}
**Promoted**: ${cycleData.promotedCount} (${rate}%)
**Regressed**: ${cycleData.regressedCount}
**Duration**: ${cycleData.elapsedMs.toFixed(0)}ms
`;
  }

  // --------------------------------------------------------------------------
  // DIAGNOSTICS
  // --------------------------------------------------------------------------

  getDiagnostics(): Record<string, unknown> {
    const entriesByType: Record<string, number> = {};
    for (const entry of this.corpus.entries) {
      entriesByType[entry.type] = (entriesByType[entry.type] ?? 0) + 1;
    }

    return {
      hook: 'notebooklm_epistemic_hook_v25',
      totalEntries: this.corpus.totalSize,
      lastUpdated: this.corpus.lastUpdated,
      entriesByType,
      expirationPolicy: this.expirationPolicy,
    };
  }
}
