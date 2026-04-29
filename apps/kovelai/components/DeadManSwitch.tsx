// Copyright (c) 2026 ShadowTag, Inc. All rights reserved. Dual-Licensed under CounselConduit Compliance.

/**
 * Dead Man's Switch — Auto-Logout Component
 *
 * Sprint Item #14: Session termination on inactivity.
 *
 * The Dead Man's Switch is the core anti-forensic component:
 * - 5 min inactivity → auto-wipe session
 * - Tab blur → immediate session pause, 60s to return
 * - Beforeunload → clear all local state
 * - No SessionStorage/LocalStorage persistence
 * - Screen wipe animation on logout
 *
 * @see EphemeralSearchUI.tsx — uses this component
 * @see U.S. v. Heppner — anti-forensic requirements
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

// ─── Configuration ──────────────────────────────────────────────────

interface DeadManSwitchConfig {
  inactivityTimeoutMs: number;
  warningThresholdMs: number;
  tabBlurTimeoutMs: number;
  onTimeout: () => void;
  onWarning?: () => void;
}

const DEFAULT_CONFIG: DeadManSwitchConfig = {
  inactivityTimeoutMs: 5 * 60 * 1000,
  warningThresholdMs: 4 * 60 * 1000,
  tabBlurTimeoutMs: 60 * 1000,
  onTimeout: () => {},
};

// ─── Hook ───────────────────────────────────────────────────────────

export function useDeadManSwitch(config: DeadManSwitchConfig) {
  const [timeRemaining, setTimeRemaining] = useState(config.inactivityTimeoutMs);
  const [isWarning, setIsWarning] = useState(false);
  const [isTabHidden, setIsTabHidden] = useState(false);
  const lastActivityRef = useRef(Date.now());
  const tabBlurTimerRef = useRef<NodeJS.Timeout | null>(null);

  const resetTimer = useCallback(() => {
    lastActivityRef.current = Date.now();
    setIsWarning(false);
    setTimeRemaining(config.inactivityTimeoutMs);
  }, [config.inactivityTimeoutMs]);

  // ── Inactivity Monitor ────────────────────────────────────────
  useEffect(() => {
    const interval = setInterval(() => {
      const elapsed = Date.now() - lastActivityRef.current;
      const remaining = Math.max(0, config.inactivityTimeoutMs - elapsed);

      setTimeRemaining(remaining);

      if (remaining === 0) {
        config.onTimeout();
        return;
      }

      if (elapsed >= config.warningThresholdMs && !isWarning) {
        setIsWarning(true);
        config.onWarning?.();
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [config, isWarning]);

  // ── Tab Visibility Monitor ────────────────────────────────────
  useEffect(() => {
    const handleVisibility = () => {
      if (document.hidden) {
        setIsTabHidden(true);
        tabBlurTimerRef.current = setTimeout(() => {
          config.onTimeout();
        }, config.tabBlurTimeoutMs);
      } else {
        setIsTabHidden(false);
        if (tabBlurTimerRef.current) {
          clearTimeout(tabBlurTimerRef.current);
          tabBlurTimerRef.current = null;
        }
        resetTimer();
      }
    };

    document.addEventListener('visibilitychange', handleVisibility);
    return () => document.removeEventListener('visibilitychange', handleVisibility);
  }, [config, resetTimer]);

  // ── User Activity Listeners ───────────────────────────────────
  useEffect(() => {
    const events = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'];
    for (const event of events) document.addEventListener(event, resetTimer);
    return () => {
      for (const event of events) document.removeEventListener(event, resetTimer);
    };
  }, [resetTimer]);

  // ── Beforeunload Cleanup ──────────────────────────────────────
  useEffect(() => {
    const handleUnload = () => {
      // Clear any local state
      try {
        sessionStorage.clear();
        localStorage.removeItem('kovelai_session');
      } catch {
        // Ignore errors during unload
      }
    };

    window.addEventListener('beforeunload', handleUnload);
    return () => window.removeEventListener('beforeunload', handleUnload);
  }, []);

  return {
    timeRemaining,
    isWarning,
    isTabHidden,
    resetTimer,
  };
}

// ─── Visual Component ───────────────────────────────────────────────

interface DeadManSwitchUIProps {
  config?: Partial<DeadManSwitchConfig>;
  onSessionEnd: () => void;
}

export function DeadManSwitchUI({ config, onSessionEnd }: DeadManSwitchUIProps) {
  const [showWipeAnimation, setShowWipeAnimation] = useState(false);

  const handleTimeout = useCallback(() => {
    setShowWipeAnimation(true);
    setTimeout(onSessionEnd, 1500);
  }, [onSessionEnd]);

  const fullConfig: DeadManSwitchConfig = {
    ...DEFAULT_CONFIG,
    ...config,
    onTimeout: handleTimeout,
  };

  const { timeRemaining, isWarning, isTabHidden } = useDeadManSwitch(fullConfig);

  const seconds = Math.floor(timeRemaining / 1000);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  // Screen wipe animation
  if (showWipeAnimation) {
    return (
      <div
        style={{
          position: 'fixed',
          inset: 0,
          background: '#0d1117',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          animation: 'fadeIn 0.5s ease-in',
        }}
      >
        <div
          style={{
            textAlign: 'center',
            color: '#859398',
            fontFamily: 'Space Grotesk, sans-serif',
          }}
        >
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔒</div>
          <div style={{ fontSize: '20px', fontWeight: 600 }}>Session Terminated</div>
          <div style={{ fontSize: '14px', marginTop: '8px' }}>All data has been wiped.</div>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Timer Badge */}
      <div
        style={{
          position: 'fixed',
          bottom: '16px',
          right: '16px',
          padding: '8px 16px',
          borderRadius: '6px',
          background: isWarning ? 'rgba(255, 82, 82, 0.1)' : 'rgba(62, 254, 138, 0.1)',
          border: `1px solid ${isWarning ? 'rgba(255, 82, 82, 0.3)' : 'rgba(62, 254, 138, 0.3)'}`,
          color: isWarning ? '#ff5252' : '#3efe8a',
          fontFamily: 'monospace',
          fontSize: '13px',
          zIndex: 9998,
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          transition: 'all 0.3s ease',
        }}
      >
        <span
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: isWarning ? '#ff5252' : '#3efe8a',
            animation: isWarning ? 'pulse 1s infinite' : 'none',
          }}
        />
        {minutes}:{remainingSeconds.toString().padStart(2, '0')}
        {isTabHidden && ' (paused)'}
      </div>

      {/* Warning Overlay */}
      {isWarning && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            padding: '12px',
            background: 'rgba(255, 82, 82, 0.1)',
            borderBottom: '1px solid rgba(255, 82, 82, 0.2)',
            color: '#ff5252',
            textAlign: 'center',
            fontSize: '14px',
            zIndex: 9998,
          }}
        >
          ⚠️ Session expires in {seconds}s — move your mouse to continue
        </div>
      )}

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </>
  );
}
