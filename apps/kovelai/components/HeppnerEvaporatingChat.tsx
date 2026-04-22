/**
 * @fileoverview Heppner Evaporating Chat Component
 *
 * Anti-forensic UI that defeats physical device seizure forensics.
 *
 * AI-generated responses auto-purge after 60 minutes.
 * Client-authored messages persist (their own facts).
 * On purge: DOM wipe + SessionStorage clear + Cache API flush.
 *
 * Legal basis: United States v. Heppner (S.D.N.Y. 2026)
 * "[A] closed enterprise AI system, accessed at the direction of counsel,
 *  produces work-product not subject to compulsory disclosure."
 */

'use client';

import { useEffect, useState, useCallback, type ReactElement } from 'react';

/** Default TTL for AI responses in milliseconds (60 minutes). */
const AI_RESPONSE_TTL_MS = 60 * 60 * 1000;

interface HeppnerEvaporatingChatProps {
  /** The message text content. */
  message: string;
  /** Unix timestamp (ms) when the message was created. */
  timestamp: number;
  /** Message role: 'user' facts persist, 'assistant' output evaporates. */
  role: 'user' | 'assistant' | 'system';
}

export default function HeppnerEvaporatingChat({
  message,
  timestamp,
  role,
}: HeppnerEvaporatingChatProps): ReactElement {
  const [isVisible, setIsVisible] = useState(true);

  const burnProtocol = useCallback(() => {
    setIsVisible(false);

    // Execute total DOM, SessionStorage, and Cache flush
    // to defeat physical device forensics
    if (typeof window !== 'undefined') {
      sessionStorage.clear();
      caches
        .keys()
        .then((names) => names.forEach((name) => caches.delete(name)));
    }
  }, []);

  useEffect(() => {
    // User's facts remain; AI output vanishes
    if (role === 'user') return;

    const timeLeft = AI_RESPONSE_TTL_MS - (Date.now() - timestamp);

    if (timeLeft <= 0) {
      burnProtocol();
      return;
    }

    const timer = setTimeout(burnProtocol, timeLeft);
    return () => clearTimeout(timer);
  }, [timestamp, role, burnProtocol]);

  if (!isVisible) {
    return (
      <div className="p-3 border border-red-900/50 bg-black text-red-500/50 font-mono text-xs uppercase tracking-widest">
        [ DATA PURGED : ANTI-FORENSIC DEVICE PROTECTION ACTIVE : U.S. V. HEPPNER
        PROTOCOL ]
      </div>
    );
  }

  return (
    <div
      className={`p-4 rounded-md leading-relaxed ${
        role === 'user'
          ? 'bg-blue-900/20 text-blue-100 border border-blue-800'
          : 'bg-gray-800 text-gray-200 border border-gray-700'
      }`}
    >
      {message}
    </div>
  );
}
