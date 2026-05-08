'use client';

import { useEffect } from 'react';

export function ServiceWorkerRegistrar() {
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => {
          console.log('[HeadFade] SW registered, scope:', reg.scope);
        })
        .catch((_err) => {
        });
    }
  }, []);

  return null;
}
