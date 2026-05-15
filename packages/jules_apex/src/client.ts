/**
 * JulesApexClient — ShadowTag orchestration wrapper for the Jules API.
 *
 * Provides session lifecycle management, artifact extraction, and
 * integration with the ShadowTag Judge 6 governance pipeline.
 *
 * API endpoint: https://jules.googleapis.com/v1alpha/sessions
 * Auth: X-Goog-Api-Key header (JULES_API_KEY from Secret Manager)
 */

import type { SessionConfig, SessionOutput, SessionState } from './types.js';

const JULES_API_BASE = 'https://jules.googleapis.com/v1alpha';
const DEFAULT_TIMEOUT_MS = 30_000;
const DEFAULT_POLL_INTERVAL_MS = 5_000;
const DEFAULT_MAX_POLL_DURATION_MS = 600_000; // 10 minutes

export interface ApexClientOptions {
  /** Jules API key (from GCP Secret Manager) */
  apiKey: string;
  /** API base URL override (for testing) */
  baseUrl?: string;
  /** Request timeout in ms */
  timeoutMs?: number;
  /** GitHub repository in "owner/repo" format */
  repo?: string;
  /** Starting branch for sessions */
  defaultBranch?: string;
}

export interface ApexSession {
  /** Session identifier */
  sessionId: string;
  /** Current state */
  state: SessionState;
  /** Raw response from the API */
  raw: Record<string, unknown>;
}

/**
 * Creates a new JulesApexClient instance.
 * Reads JULES_API_KEY from environment if not provided.
 */
export function createApexClient(options?: Partial<ApexClientOptions>): JulesApexClient {
  const apiKey = options?.apiKey ?? process.env.JULES_API_KEY;
  if (!apiKey) {
    throw new Error(
      'JULES_API_KEY is required. Set it via GCP Secret Manager or pass apiKey option.',
    );
  }
  return new JulesApexClient({
    apiKey,
    repo: options?.repo ?? 'ShadowTag-v2/Monorepo-Uphillsnowball',
    defaultBranch: options?.defaultBranch ?? 'main',
    ...options,
  });
}

export class JulesApexClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly timeoutMs: number;
  private readonly repo: string;
  private readonly defaultBranch: string;

  constructor(options: ApexClientOptions) {
    this.apiKey = options.apiKey;
    this.baseUrl = options.baseUrl ?? JULES_API_BASE;
    this.timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
    this.repo = options.repo ?? 'ShadowTag-v2/Monorepo-Uphillsnowball';
    this.defaultBranch = options.defaultBranch ?? 'main';
  }

  /**
   * Creates a new Jules session with the given prompt.
   * Maps to POST /v1alpha/sessions
   */
  async createSession(config: SessionConfig): Promise<ApexSession> {
    const payload = {
      prompt: config.prompt,
      sourceContext: config.sourceContext ?? {
        source: `sources/github/${this.repo}`,
        githubRepoContext: {
          startingBranch: this.defaultBranch,
        },
      },
      requirePlanApproval: config.requirePlanApproval ?? false,
      automationMode: config.automationMode ?? 'AUTO_CREATE_PR',
    };

    const response = await this.request<Record<string, unknown>>('sessions', 'POST', payload);

    return {
      sessionId: (response.name as string) ?? '',
      state: (response.state as SessionState) ?? 'PENDING',
      raw: response,
    };
  }

  /**
   * Polls a session until it reaches a terminal state.
   * Terminal states: COMPLETED, FAILED, CANCELLED
   */
  async waitForCompletion(
    sessionId: string,
    options?: {
      pollIntervalMs?: number;
      maxDurationMs?: number;
      onPoll?: (state: SessionState, elapsed: number) => void;
    },
  ): Promise<SessionOutput> {
    const pollInterval = options?.pollIntervalMs ?? DEFAULT_POLL_INTERVAL_MS;
    const maxDuration = options?.maxDurationMs ?? DEFAULT_MAX_POLL_DURATION_MS;
    const startTime = Date.now();

    const terminalStates: SessionState[] = ['COMPLETED', 'FAILED', 'CANCELLED'];

    while (Date.now() - startTime < maxDuration) {
      const response = await this.request<Record<string, unknown>>(`sessions/${sessionId}`, 'GET');

      const state = (response.state as SessionState) ?? 'PENDING';
      options?.onPoll?.(state, Date.now() - startTime);

      if (terminalStates.includes(state)) {
        return {
          sessionId,
          state,
          artifacts: response.artifacts as SessionOutput['artifacts'],
          pullRequest: response.pullRequest as SessionOutput['pullRequest'],
          plan: response.plan as SessionOutput['plan'],
        };
      }

      await this.sleep(pollInterval);
    }

    throw new Error(`Session ${sessionId} did not complete within ${maxDuration}ms`);
  }

  /**
   * Lists recent sessions.
   */
  async listSessions(pageSize = 10): Promise<Array<Record<string, unknown>>> {
    const response = await this.request<{
      sessions?: Array<Record<string, unknown>>;
    }>(`sessions?pageSize=${pageSize}`, 'GET');
    return response.sessions ?? [];
  }

  // --- Internal helpers ---

  private async request<T>(
    endpoint: string,
    method: 'GET' | 'POST' | 'DELETE',
    body?: Record<string, unknown>,
  ): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const url = `${this.baseUrl}/${endpoint}`;
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'X-Goog-Api-Key': this.apiKey,
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorText = await response.text().catch(() => '');
        throw new Error(
          `Jules API ${method} ${endpoint} failed: ${response.status} ${response.statusText} - ${errorText}`,
        );
      }

      const text = await response.text();
      return text ? (JSON.parse(text) as T) : ({} as T);
    } finally {
      clearTimeout(timeoutId);
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
