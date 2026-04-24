/**
 * CounselConduit SSE Reconnect Module (Item #18)
 *
 * Client-side exponential backoff reconnect for Vent Mode SSE streams.
 * Prevents thundering herd on server restart and handles graceful degradation.
 *
 * Usage:
 *   import { createSSEClient } from './sse-reconnect.js';
 *   const client = createSSEClient('/api/vent-mode/stream', {
 *     onMessage: (data) => console.log(data),
 *     onError: (err) => console.error(err),
 *     maxRetries: 10,
 *   });
 *   client.connect();
 *   // Later: client.disconnect();
 */

const DEFAULT_CONFIG = {
  initialDelayMs: 1000,
  maxDelayMs: 30000,
  backoffMultiplier: 2,
  jitterFactor: 0.3,
  maxRetries: 15,
  heartbeatTimeoutMs: 45000,
};

/**
 * Create an SSE client with exponential backoff reconnect.
 * @param {string} url - SSE endpoint URL
 * @param {Object} options - Configuration options
 * @returns {Object} SSE client with connect/disconnect methods
 */
export function createSSEClient(url, options = {}) {
  const config = { ...DEFAULT_CONFIG, ...options };
  let eventSource = null;
  let retryCount = 0;
  let reconnectTimer = null;
  let heartbeatTimer = null;
  let isManualDisconnect = false;

  function calculateDelay() {
    const baseDelay = Math.min(
      config.initialDelayMs * config.backoffMultiplier ** retryCount,
      config.maxDelayMs,
    );
    // Add jitter to prevent thundering herd
    const jitter = baseDelay * config.jitterFactor * (Math.random() * 2 - 1);
    return Math.max(0, Math.floor(baseDelay + jitter));
  }

  function resetHeartbeatTimer() {
    if (heartbeatTimer) clearTimeout(heartbeatTimer);
    heartbeatTimer = setTimeout(() => {
      if (eventSource) {
        eventSource.close();
        scheduleReconnect();
      }
    }, config.heartbeatTimeoutMs);
  }

  function scheduleReconnect() {
    if (isManualDisconnect || retryCount >= config.maxRetries) {
      if (retryCount >= config.maxRetries) {
        config.onMaxRetriesExceeded?.();
      }
      return;
    }

    const delay = calculateDelay();
    console.log(
      `[SSE] Reconnecting in ${delay}ms (attempt ${retryCount + 1}/${config.maxRetries})`,
    );
    config.onReconnecting?.({ attempt: retryCount + 1, delay });

    reconnectTimer = setTimeout(() => {
      retryCount++;
      connect();
    }, delay);
  }

  function connect() {
    isManualDisconnect = false;

    if (eventSource) {
      eventSource.close();
    }

    try {
      eventSource = new EventSource(url);

      eventSource.onopen = () => {
        console.log('[SSE] Connected');
        retryCount = 0;
        resetHeartbeatTimer();
        config.onConnect?.();
      };

      eventSource.onmessage = (event) => {
        resetHeartbeatTimer();
        try {
          const data = JSON.parse(event.data);
          config.onMessage?.(data);
        } catch {
          config.onMessage?.(event.data);
        }
      };

      eventSource.addEventListener('heartbeat', () => {
        resetHeartbeatTimer();
      });

      eventSource.addEventListener('error_event', (event) => {
        const data = JSON.parse(event.data);
        config.onServerError?.(data);
      });

      eventSource.onerror = () => {
        if (heartbeatTimer) clearTimeout(heartbeatTimer);
        eventSource.close();
        config.onError?.({ type: 'connection_error', attempt: retryCount });
        scheduleReconnect();
      };
    } catch (err) {
      config.onError?.({ type: 'creation_error', error: err });
      scheduleReconnect();
    }
  }

  function disconnect() {
    isManualDisconnect = true;
    if (reconnectTimer) clearTimeout(reconnectTimer);
    if (heartbeatTimer) clearTimeout(heartbeatTimer);
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
    retryCount = 0;
    config.onDisconnect?.();
  }

  return {
    connect,
    disconnect,
    getState: () => ({
      connected: eventSource?.readyState === EventSource.OPEN,
      retryCount,
      maxRetries: config.maxRetries,
    }),
  };
}
