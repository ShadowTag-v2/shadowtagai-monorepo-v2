/**
 * V25 Jules Ascension — Claude Sourcemap Bridge
 *
 * Maps source code deobfuscation from claude-hidden-toolkit into the
 * SRE pipeline for production stack trace analysis, error correlation,
 * and automated incident response.
 *
 * References:
 *   - external_repos/claude-hidden-toolkit/ (deobfuscation patterns)
 *   - external_repos/claude-code-reverse/ (reverse engineering)
 *   - src/agents/judge6_sentinel.py (governance gate)
 *
 * @module orchestration/claude_sourcemap_bridge
 * Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
 */

// ============================================================================
// TYPES
// ============================================================================

export interface SourcemapEntry {
  /** Obfuscated function name from production stack trace */
  obfuscatedName: string;
  /** Deobfuscated human-readable name */
  originalName: string;
  /** Source file path */
  sourceFile: string;
  /** Line number in original source */
  line: number;
  /** Column number in original source */
  column: number;
  /** Module/package the function belongs to */
  module: string;
}

export interface StackTraceFrame {
  functionName: string;
  fileName: string;
  lineNumber: number;
  columnNumber: number;
  isInternal: boolean;
}

export interface DeobfuscatedTrace {
  originalError: string;
  frames: DeobfuscatedFrame[];
  rootCauseModule: string | null;
  suggestedFix: string | null;
  correlationId: string;
  timestamp: string;
}

export interface DeobfuscatedFrame extends StackTraceFrame {
  deobfuscatedName: string | null;
  sourceFile: string | null;
  originalLine: number | null;
  originalColumn: number | null;
}

export interface ErrorCorrelation {
  correlationId: string;
  errorPattern: string;
  occurrenceCount: number;
  firstSeen: string;
  lastSeen: string;
  affectedServices: string[];
  deobfuscatedTraces: DeobfuscatedTrace[];
}

// ============================================================================
// SOURCEMAP REGISTRY
// ============================================================================

/**
 * ClaudeSourcemapBridge — Production stack trace deobfuscation.
 *
 * Maintains a registry of obfuscated → original function name mappings
 * extracted from build artifacts. When production errors occur, maps
 * minified/obfuscated stack traces back to readable source locations.
 *
 * CRITICAL: This produces ANALYSIS PLANS, not side effects.
 * Error data never leaves the local context.
 */
export class ClaudeSourcemapBridge {
  private readonly registry: Map<string, SourcemapEntry> = new Map();
  private readonly correlations: Map<string, ErrorCorrelation> = new Map();

  // --------------------------------------------------------------------------
  // REGISTRY MANAGEMENT
  // --------------------------------------------------------------------------

  /**
   * Register sourcemap entries from a build artifact.
   */
  registerSourcemap(entries: SourcemapEntry[]): void {
    for (const entry of entries) {
      this.registry.set(entry.obfuscatedName, entry);
    }
  }

  /**
   * Register sourcemap entries from a webpack/vite sourcemap file.
   *
   * Returns an MCP execution plan to read and parse the sourcemap.
   */
  planSourcemapIngestion(sourcemapPath: string): Record<string, unknown> {
    return {
      type: 'mcp_execution_plan',
      tool: 'filesystem.read',
      args: {
        path: sourcemapPath,
        encoding: 'utf-8',
      },
      postProcess: {
        action: 'parse_sourcemap',
        targetRegistry: 'claude_sourcemap_bridge',
      },
    };
  }

  // --------------------------------------------------------------------------
  // STACK TRACE DEOBFUSCATION
  // --------------------------------------------------------------------------

  /**
   * Deobfuscate a production stack trace.
   *
   * Maps each frame's function name through the registry to recover
   * the original source location.
   */
  deobfuscateTrace(
    errorMessage: string,
    frames: StackTraceFrame[],
  ): DeobfuscatedTrace {
    const correlationId = `err_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

    const deobfuscatedFrames: DeobfuscatedFrame[] = frames.map((frame) => {
      const entry = this.registry.get(frame.functionName);
      return {
        ...frame,
        deobfuscatedName: entry?.originalName ?? null,
        sourceFile: entry?.sourceFile ?? null,
        originalLine: entry?.line ?? null,
        originalColumn: entry?.column ?? null,
      };
    });

    // Identify root cause module (first non-internal frame with a mapping)
    const rootFrame = deobfuscatedFrames.find(
      (f) => !f.isInternal && f.deobfuscatedName !== null,
    );

    return {
      originalError: errorMessage,
      frames: deobfuscatedFrames,
      rootCauseModule: rootFrame ? this.registry.get(rootFrame.functionName)?.module ?? null : null,
      suggestedFix: this.suggestFix(errorMessage, rootFrame ?? null),
      correlationId,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Correlate repeated errors across services.
   */
  correlateError(
    trace: DeobfuscatedTrace,
    serviceName: string,
  ): ErrorCorrelation {
    const pattern = this.extractErrorPattern(trace.originalError);
    const existing = this.correlations.get(pattern);

    if (existing) {
      existing.occurrenceCount++;
      existing.lastSeen = trace.timestamp;
      if (!existing.affectedServices.includes(serviceName)) {
        existing.affectedServices.push(serviceName);
      }
      existing.deobfuscatedTraces.push(trace);
      return existing;
    }

    const correlation: ErrorCorrelation = {
      correlationId: trace.correlationId,
      errorPattern: pattern,
      occurrenceCount: 1,
      firstSeen: trace.timestamp,
      lastSeen: trace.timestamp,
      affectedServices: [serviceName],
      deobfuscatedTraces: [trace],
    };

    this.correlations.set(pattern, correlation);
    return correlation;
  }

  // --------------------------------------------------------------------------
  // INCIDENT RESPONSE
  // --------------------------------------------------------------------------

  /**
   * Plan an automated incident response from correlated errors.
   *
   * Returns an MCP execution plan for Jules session-based fix.
   */
  planIncidentResponse(correlation: ErrorCorrelation): Record<string, unknown> {
    const prompt = this.buildIncidentPrompt(correlation);

    return {
      type: 'mcp_execution_plan',
      tool: 'jules.session',
      args: {
        prompt,
        source: {
          github: 'ShadowTag-v2/Monorepo-Uphillsnowball',
          baseBranch: 'main',
        },
        autoPr: true,
      },
      governance: {
        requiresJ6Gate: true,
        riskLevel: correlation.occurrenceCount > 10 ? 'ELEVATED' : 'LOW',
        correlationId: correlation.correlationId,
      },
    };
  }

  // --------------------------------------------------------------------------
  // PRIVATE HELPERS
  // --------------------------------------------------------------------------

  private suggestFix(
    errorMessage: string,
    rootFrame: DeobfuscatedFrame | null,
  ): string | null {
    if (!rootFrame?.deobfuscatedName) return null;

    // Pattern-based suggestions
    if (errorMessage.includes('ECONNREFUSED')) {
      return `Check network connectivity in ${rootFrame.sourceFile}:${rootFrame.originalLine}. Verify service endpoint is reachable.`;
    }
    if (errorMessage.includes('SIGTERM')) {
      return `Graceful shutdown handler may be incomplete in ${rootFrame.deobfuscatedName}. Verify async cleanup.`;
    }
    if (errorMessage.includes('rate limit') || errorMessage.includes('429')) {
      return `Rate limiting triggered in ${rootFrame.deobfuscatedName}. Consider exponential backoff or request batching.`;
    }
    if (errorMessage.includes('permission') || errorMessage.includes('403')) {
      return `IAM permission denied in ${rootFrame.deobfuscatedName}. Verify service account roles.`;
    }

    return `Review ${rootFrame.deobfuscatedName} at ${rootFrame.sourceFile}:${rootFrame.originalLine}`;
  }

  private extractErrorPattern(errorMessage: string): string {
    // Normalize error message by removing dynamic parts (IDs, timestamps, etc.)
    return errorMessage
      .replace(/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, '<UUID>')
      .replace(/\b\d{10,13}\b/g, '<TIMESTAMP>')
      .replace(/\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/g, '<IP>')
      .replace(/:\d{4,5}\b/g, ':<PORT>')
      .trim();
  }

  private buildIncidentPrompt(correlation: ErrorCorrelation): string {
    const trace = correlation.deobfuscatedTraces[0];
    const framesList = trace.frames
      .filter((f) => f.deobfuscatedName)
      .map((f) => `  - ${f.deobfuscatedName} (${f.sourceFile}:${f.originalLine})`)
      .join('\n');

    return `## Automated Incident Response

**Error Pattern**: ${correlation.errorPattern}
**Occurrences**: ${correlation.occurrenceCount}
**Affected Services**: ${correlation.affectedServices.join(', ')}
**First Seen**: ${correlation.firstSeen}

### Deobfuscated Stack Trace
${framesList}

### Root Cause Module
${trace.rootCauseModule ?? 'Unknown'}

### Suggested Fix
${trace.suggestedFix ?? 'Manual investigation required'}

### Instructions
1. Identify the root cause from the deobfuscated trace
2. Apply a fix that addresses the error pattern
3. Add error handling/retry logic if appropriate
4. Add regression tests
5. Follow ShadowTag coding standards (AGENTS.md v11.2)
`;
  }

  // --------------------------------------------------------------------------
  // DIAGNOSTICS
  // --------------------------------------------------------------------------

  getDiagnostics(): Record<string, unknown> {
    return {
      bridge: 'claude_sourcemap_bridge_v25',
      registeredMappings: this.registry.size,
      activeCorrelations: this.correlations.size,
      topErrors: Array.from(this.correlations.values())
        .sort((a, b) => b.occurrenceCount - a.occurrenceCount)
        .slice(0, 5)
        .map((c) => ({
          pattern: c.errorPattern,
          count: c.occurrenceCount,
          services: c.affectedServices,
        })),
    };
  }
}
