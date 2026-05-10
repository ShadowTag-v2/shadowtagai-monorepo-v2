'use client';

import { useEffect, useState } from 'react';
import AgentSpinner from './AgentSpinner';

/**
 * KovelSpinner — Client-side loading overlay for KovelAI.
 *
 * Shows the AgentSpinner with kovelai theme on initial page mount,
 * auto-dismisses after hydration + a brief settle delay.
 * Uses CSS opacity/pointer-events for a smooth fade-out.
 */
export default function KovelSpinner() {
  const [active, setActive] = useState(true);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    // Dismiss after hydration + 1.2s settle
    const timer = setTimeout(() => {
      setActive(false);
      // Keep DOM mounted briefly for fade-out
      const fadeTimer = setTimeout(() => setVisible(false), 500);
      return () => clearTimeout(fadeTimer);
    }, 1200);
    return () => clearTimeout(timer);
  }, []);

  if (!visible) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        background: 'rgba(7, 19, 37, 0.95)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'opacity 0.5s ease-out',
        opacity: active ? 1 : 0,
        pointerEvents: active ? 'auto' : 'none',
      }}
      role="status"
      aria-live="polite"
      aria-label="Loading KovelAI"
    >
      <AgentSpinner active={active} theme="kovelai" label="INITIALIZING PRIVILEGE SHIELD" />
    </div>
  );
}
