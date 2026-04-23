import { useCallback, useEffect, useState } from 'react';

/**
 * useDecayTimer
 * Implements the Anti-Forensic UI pattern for Kovel Doctrine compliance.
 * Automatically purges sensitive attorney-client AI execution data from the DOM.
 */
export function useDecayTimer(ttlSeconds: number, onPurge: () => void) {
  const [timeLeft, setTimeLeft] = useState(ttlSeconds);
  const [isPurged, setIsPurged] = useState(false);

  const triggerPurge = useCallback(() => {
    setIsPurged(true);

    // 1. Purge browser storage
    localStorage.clear();
    sessionStorage.clear();

    // 2. Erase browser history state
    try {
      window.history.replaceState({}, document.title, '/locked');
    } catch {
      // History push may fail in some environments
    }

    // 3. Clear cookies
    document.cookie.split(';').forEach((c) => {
      document.cookie = c
        .replace(/^ +/, '')
        .replace(/=.*/, `=;expires=${new Date().toUTCString()};path=/`);
    });

    // 4. Trigger application state wipe callback
    onPurge();
  }, [onPurge]);

  useEffect(() => {
    if (timeLeft <= 0) {
      triggerPurge();
      return;
    }
    const timer = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);

    // Activity handlers reset the decay clock
    const resetTimer = () => setTimeLeft(ttlSeconds);
    const events: string[] = ['mousemove', 'keydown', 'scroll', 'click', 'touchstart'];
    events.forEach((e) => window.addEventListener(e, resetTimer));

    return () => {
      clearInterval(timer);
      events.forEach((e) => window.removeEventListener(e, resetTimer));
    };
  }, [timeLeft, ttlSeconds, triggerPurge]);

  return { timeLeft, isPurged, forcePurge: triggerPurge };
}
