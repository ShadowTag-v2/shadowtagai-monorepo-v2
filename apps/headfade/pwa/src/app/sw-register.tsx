'use client';

import { useEffect } from 'react';

export function ServiceWorkerRegistrar() {
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => {
          // eslint-disable-next-line no-console
          console.log('[HeadFade] SW registered, scope:', reg.scope);
        })
        .catch((err) => {
          // eslint-disable-next-line no-console
          console.warn('[HeadFade] SW registration failed:', err);
        });
    }
  }, []);

  return null;
}
