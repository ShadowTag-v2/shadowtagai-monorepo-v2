// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * useSandboxWebSocket — Real-time WebSocket client for sandbox session state.
 *
 * Connects to the backend WebSocket endpoint (/ws/sandbox/{sessionId})
 * and pushes state transition events to the DiffView page component.
 *
 * Protocol (mirrors ws_state_push.py):
 *   Server → Client: { type: "state_change", from: "...", to: "...", ... }
 *   Client → Server: "ping" (keep-alive)
 *   Server → Client: { type: "pong", ts: "..." }
 *
 * Security:
 *   - No PII in messages (session ID prefix only)
 *   - Auto-reconnect with exponential backoff (max 30s)
 *   - Clean disconnect on unmount
 *   - Connection state exposed for UI indicators
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export type WsConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface StateChangeEvent {
  type: 'state_change';
  session_id_prefix: string;
  from: string;
  to: string;
  ts: string;
  metadata: Record<string, unknown>;
}

interface UseSandboxWebSocketOptions {
  /** Session ID to subscribe to */
  sessionId: string;
  /** Callback when a state_change event is received */
  onStateChange?: (event: StateChangeEvent) => void;
  /** Enable/disable the connection (default: true) */
  enabled?: boolean;
  /** Max reconnect attempts before giving up (default: 5) */
  maxReconnectAttempts?: number;
}

interface UseSandboxWebSocketReturn {
  /** Current connection state */
  connectionState: WsConnectionState;
  /** Last received state change event */
  lastEvent: StateChangeEvent | null;
  /** Number of reconnect attempts made */
  reconnectCount: number;
  /** Manually disconnect */
  disconnect: () => void;
  /** Manually reconnect */
  reconnect: () => void;
}

/**
 * Hook that manages a WebSocket connection to the sandbox state push endpoint.
 *
 * Auto-connects on mount, handles reconnection with exponential backoff,
 * and cleans up on unmount.
 */
export function useSandboxWebSocket({
  sessionId,
  onStateChange,
  enabled = true,
  maxReconnectAttempts = 5,
}: UseSandboxWebSocketOptions): UseSandboxWebSocketReturn {
  const [connectionState, setConnectionState] = useState<WsConnectionState>('disconnected');
  const [lastEvent, setLastEvent] = useState<StateChangeEvent | null>(null);
  const [reconnectCount, setReconnectCount] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const mountedRef = useRef(true);
  const onStateChangeRef = useRef(onStateChange);

  // Keep callback ref fresh without re-triggering connection
  useEffect(() => {
    onStateChangeRef.current = onStateChange;
  }, [onStateChange]);

  const clearTimers = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (pingTimerRef.current) {
      clearInterval(pingTimerRef.current);
      pingTimerRef.current = null;
    }
  }, []);

  const closeConnection = useCallback(() => {
    clearTimers();
    if (wsRef.current) {
      wsRef.current.onclose = null; // Prevent reconnect on intentional close
      wsRef.current.close(1000, 'client_disconnect');
      wsRef.current = null;
    }
    if (mountedRef.current) {
      setConnectionState('disconnected');
    }
  }, [clearTimers]);

  const connect = useCallback(() => {
    if (!sessionId || !enabled || !mountedRef.current) return;

    // Close any existing connection
    if (wsRef.current) {
      wsRef.current.onclose = null;
      wsRef.current.close();
    }

    clearTimers();
    setConnectionState('connecting');

    // Build WebSocket URL — handle both http and https protocols
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/sandbox/${sessionId}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      if (!mountedRef.current) return;
      setConnectionState('connected');
      setReconnectCount(0);

      // Start ping interval (every 60s)
      pingTimerRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('ping');
        }
      }, 60_000);
    };

    ws.onmessage = (event: MessageEvent) => {
      if (!mountedRef.current) return;

      try {
        const data = JSON.parse(event.data as string) as Record<string, unknown>;

        if (data.type === 'state_change') {
          const stateEvent: StateChangeEvent = {
            type: 'state_change',
            session_id_prefix: (data.session_id_prefix as string) ?? '',
            from: (data.from as string) ?? '',
            to: (data.to as string) ?? '',
            ts: (data.ts as string) ?? '',
            metadata: (data.metadata as Record<string, unknown>) ?? {},
          };

          setLastEvent(stateEvent);
          onStateChangeRef.current?.(stateEvent);
        }
        // pong messages are acknowledged silently
      } catch {
        // Malformed messages are silently dropped
      }
    };

    ws.onerror = () => {
      if (!mountedRef.current) return;
      setConnectionState('error');
    };

    ws.onclose = (event: CloseEvent) => {
      if (!mountedRef.current) return;
      clearTimers();
      setConnectionState('disconnected');

      // Don't reconnect on clean close or if exceeded max attempts
      if (event.code === 1000 || reconnectCount >= maxReconnectAttempts) return;

      // Exponential backoff: 1s, 2s, 4s, 8s, 16s, max 30s
      const delay = Math.min(1000 * 2 ** reconnectCount, 30_000);
      setReconnectCount((prev) => prev + 1);

      reconnectTimerRef.current = setTimeout(() => {
        if (mountedRef.current) {
          connect();
        }
      }, delay);
    };
  }, [sessionId, enabled, clearTimers, maxReconnectAttempts, reconnectCount]);

  // Connect on mount / when sessionId changes
  useEffect(() => {
    mountedRef.current = true;

    if (enabled && sessionId) {
      connect();
    }

    return () => {
      mountedRef.current = false;
      closeConnection();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, enabled, connect, closeConnection]);

  return {
    connectionState,
    lastEvent,
    reconnectCount,
    disconnect: closeConnection,
    reconnect: connect,
  };
}
