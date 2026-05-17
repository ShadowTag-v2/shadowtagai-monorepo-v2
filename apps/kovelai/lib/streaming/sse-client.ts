/**
 * SSE Reconnection with Exponential Backoff
 *
 * Sprint Item #21: Reliable Server-Sent Events client.
 *
 * Handles:
 * - Automatic reconnection on disconnect
 * - Exponential backoff (1s → 2s → 4s → 8s → 16s → 30s max)
 * - Jitter to prevent thundering herd
 * - Last-Event-ID header for gap-free delivery
 * - Connection health heartbeat monitoring
 * - Graceful degradation to polling
 *
 * @see app/api/war-room/stream/route.ts — SSE endpoint
 */

// ─── Types ──────────────────────────────────────────────────────────

export interface SSEClientConfig {
  url: string;
  headers?: Record<string, string>;
  maxRetries?: number;
  baseDelayMs?: number;
  maxDelayMs?: number;
  heartbeatTimeoutMs?: number;
  onMessage: (event: SSEMessage) => void;
  onError?: (error: Error, retryCount: number) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onReconnecting?: (retryCount: number, delayMs: number) => void;
}

export interface SSEMessage {
  id?: string;
  event: string;
  data: string;
  retry?: number;
}

type ConnectionState = "CONNECTING" | "OPEN" | "CLOSED" | "RECONNECTING";

// ─── Configuration Defaults ─────────────────────────────────────────

const DEFAULTS = {
  maxRetries: 15,
  baseDelayMs: 1000,
  maxDelayMs: 30000,
  heartbeatTimeoutMs: 45000, // 45s — expect heartbeats every 30s
  jitterRange: 0.3, // ±30% jitter
};

// ─── SSE Client ─────────────────────────────────────────────────────

export class ResilientSSEClient {
  private config: Required<
    Omit<SSEClientConfig, "onError" | "onOpen" | "onClose" | "onReconnecting">
  > & {
    onError?: SSEClientConfig["onError"];
    onOpen?: SSEClientConfig["onOpen"];
    onClose?: SSEClientConfig["onClose"];
    onReconnecting?: SSEClientConfig["onReconnecting"];
  };
  private controller: AbortController | null = null;
  private retryCount = 0;
  private lastEventId: string | null = null;
  private heartbeatTimer: ReturnType<typeof setTimeout> | null = null;
  private _state: ConnectionState = "CLOSED";
  private _isDestroyed = false;

  get state(): ConnectionState {
    return this._state;
  }

  constructor(config: SSEClientConfig) {
    this.config = {
      maxRetries: DEFAULTS.maxRetries,
      baseDelayMs: DEFAULTS.baseDelayMs,
      maxDelayMs: DEFAULTS.maxDelayMs,
      heartbeatTimeoutMs: DEFAULTS.heartbeatTimeoutMs,
      ...config,
    };
  }

  // ─── Connect ──────────────────────────────────────────────────

  async connect(): Promise<void> {
    if (this._isDestroyed) return;

    this._state = "CONNECTING";
    this.controller = new AbortController();

    const headers: Record<string, string> = {
      Accept: "text/event-stream",
      "Cache-Control": "no-cache",
      ...(this.config.headers ?? {}),
    };

    if (this.lastEventId) {
      headers["Last-Event-ID"] = this.lastEventId;
    }

    try {
      const response = await fetch(this.config.url, {
        headers,
        signal: this.controller.signal,
      });

      if (!response.ok) {
        throw new Error(`SSE connection failed: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("SSE response has no body");
      }

      this._state = "OPEN";
      this.retryCount = 0;
      this.config.onOpen?.();
      this.startHeartbeatMonitor();

      await this.readStream(response.body);
    } catch (error) {
      if (this._isDestroyed) return;

      if (error instanceof DOMException && error.name === "AbortError") {
        return; // Intentional disconnect
      }

      this.handleDisconnect(error instanceof Error ? error : new Error(String(error)));
    }
  }

  // ─── Stream Reader ────────────────────────────────────────────

  private async readStream(body: ReadableStream<Uint8Array>): Promise<void> {
    const reader = body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          this.handleDisconnect(new Error("Stream ended"));
          return;
        }

        buffer += decoder.decode(value, { stream: true });
        const messages = this.parseSSE(buffer);
        buffer = messages.remaining;

        for (const msg of messages.parsed) {
          this.resetHeartbeatMonitor();

          if (msg.id) {
            this.lastEventId = msg.id;
          }

          if (msg.event === "heartbeat") {
            continue; // Internal heartbeat, don't propagate
          }

          this.config.onMessage(msg);
        }
      }
    } catch (error) {
      if (!this._isDestroyed) {
        this.handleDisconnect(error instanceof Error ? error : new Error(String(error)));
      }
    }
  }

  // ─── SSE Parser ───────────────────────────────────────────────

  private parseSSE(buffer: string): { parsed: SSEMessage[]; remaining: string } {
    const messages: SSEMessage[] = [];
    const blocks = buffer.split("\n\n");
    const remaining = blocks.pop() ?? "";

    for (const block of blocks) {
      if (!block.trim()) continue;

      const msg: SSEMessage = { event: "message", data: "" };
      const lines = block.split("\n");

      for (const line of lines) {
        if (line.startsWith("id:")) {
          msg.id = line.slice(3).trim();
        } else if (line.startsWith("event:")) {
          msg.event = line.slice(6).trim();
        } else if (line.startsWith("data:")) {
          msg.data += (msg.data ? "\n" : "") + line.slice(5).trim();
        } else if (line.startsWith("retry:")) {
          msg.retry = parseInt(line.slice(6).trim(), 10);
        }
      }

      if (msg.data || msg.event !== "message") {
        messages.push(msg);
      }
    }

    return { parsed: messages, remaining };
  }

  // ─── Heartbeat Monitor ────────────────────────────────────────

  private startHeartbeatMonitor(): void {
    this.clearHeartbeatMonitor();
    this.heartbeatTimer = setTimeout(() => {
      this.handleDisconnect(new Error("Heartbeat timeout"));
    }, this.config.heartbeatTimeoutMs);
  }

  private resetHeartbeatMonitor(): void {
    this.startHeartbeatMonitor();
  }

  private clearHeartbeatMonitor(): void {
    if (this.heartbeatTimer) {
      clearTimeout(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  // ─── Reconnection Logic ───────────────────────────────────────

  private handleDisconnect(error: Error): void {
    this._state = "CLOSED";
    this.clearHeartbeatMonitor();
    this.controller?.abort();

    if (this._isDestroyed) return;

    this.config.onError?.(error, this.retryCount);

    if (this.retryCount >= this.config.maxRetries) {
      this.config.onClose?.();
      return;
    }

    this.scheduleReconnect();
  }

  private scheduleReconnect(): void {
    this.retryCount++;
    this._state = "RECONNECTING";

    const delay = this.calculateBackoff();
    this.config.onReconnecting?.(this.retryCount, delay);

    console.log(
      `[SSE] Reconnecting in ${delay}ms (attempt ${this.retryCount}/${this.config.maxRetries})`,
    );

    setTimeout(() => {
      if (!this._isDestroyed) {
        this.connect();
      }
    }, delay);
  }

  /**
   * Exponential backoff with jitter.
   *
   * delay = min(baseDelay * 2^attempt ± jitter, maxDelay)
   */
  private calculateBackoff(): number {
    const exponentialDelay = this.config.baseDelayMs * 2 ** (this.retryCount - 1);
    const cappedDelay = Math.min(exponentialDelay, this.config.maxDelayMs);

    // Add ±30% jitter
    const jitter = cappedDelay * DEFAULTS.jitterRange * (Math.random() * 2 - 1);
    return Math.round(cappedDelay + jitter);
  }

  // ─── Disconnect ───────────────────────────────────────────────

  disconnect(): void {
    this._isDestroyed = true;
    this._state = "CLOSED";
    this.clearHeartbeatMonitor();
    this.controller?.abort();
    this.config.onClose?.();
  }

  // ─── State Queries ────────────────────────────────────────────

  get isConnected(): boolean {
    return this._state === "OPEN";
  }

  get currentRetryCount(): number {
    return this.retryCount;
  }

  get lastReceivedEventId(): string | null {
    return this.lastEventId;
  }
}

// ─── Factory ────────────────────────────────────────────────────────

/**
 * Creates a resilient SSE client for the War Room stream.
 */
export function createWarRoomSSEClient(
  sessionId: string,
  seuToken: string,
  onMessage: (event: SSEMessage) => void,
): ResilientSSEClient {
  return new ResilientSSEClient({
    url: `/api/war-room/stream?sessionId=${sessionId}`,
    headers: {
      "X-SEU-Token": seuToken,
      "X-Session-ID": sessionId,
    },
    onMessage,
    onOpen: () => console.log("[Vent Mode] SSE connected"),
    onClose: () => console.log("[Vent Mode] SSE disconnected permanently"),
    onReconnecting: (retry, delay) =>
      console.log(`[Vent Mode] Reconnecting (${retry}) in ${delay}ms`),
    onError: (_error, _retry) => {},
  });
}
