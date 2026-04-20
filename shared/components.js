/**
 * Shared JavaScript Components for KovelAI + ShadowTagAI
 * Cookie Consent, Cloudflare Turnstile, Service Worker Registration
 */

/* ── 1. Cookie Consent ───────────────────────────────────────────────── */

function initCookieConsent() {
  if (localStorage.getItem('cookie_consent')) return;

  const banner = document.createElement('div');
  banner.className = 'cookie-banner';
  banner.id = 'cookie-banner';
  banner.innerHTML = `
    <div class="cookie-inner">
      <div class="cookie-text">
        We use essential cookies to operate this service. Analytics cookies help us improve
        your experience. Read our <a href="/privacy">Privacy Policy</a> for details.
      </div>
      <div class="cookie-actions">
        <button class="cookie-btn cookie-btn-reject" id="cookie-reject">Reject All</button>
        <button class="cookie-btn cookie-btn-accept" id="cookie-accept">Accept All</button>
      </div>
    </div>
  `;

  document.body.appendChild(banner);
  requestAnimationFrame(() => {
    requestAnimationFrame(() => banner.classList.add('visible'));
  });

  document.getElementById('cookie-accept').addEventListener('click', () => {
    localStorage.setItem('cookie_consent', 'accepted');
    banner.classList.remove('visible');
    setTimeout(() => banner.remove(), 400);
  });

  document.getElementById('cookie-reject').addEventListener('click', () => {
    localStorage.setItem('cookie_consent', 'rejected');
    banner.classList.remove('visible');
    setTimeout(() => banner.remove(), 400);
  });
}

/* ── 2. Cloudflare Turnstile ──────────────────────────────────────────── */

function initTurnstile(containerId, siteKey, callback) {
  if (!window.turnstile) {
    const script = document.createElement('script');
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js';
    script.async = true;
    script.defer = true;
    script.onload = () => renderTurnstile(containerId, siteKey, callback);
    document.head.appendChild(script);
  } else {
    renderTurnstile(containerId, siteKey, callback);
  }
}

function renderTurnstile(containerId, siteKey, callback) {
  const container = document.getElementById(containerId);
  if (!container || !window.turnstile) return;

  window.turnstile.render(container, {
    sitekey: siteKey,
    theme: 'dark',
    callback: (token) => {
      if (callback) callback(token);
    },
    'error-callback': () => {
      console.error('Turnstile verification failed');
    },
  });
}

/* ── 3. Service Worker Registration ───────────────────────────────────── */

function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => {
          console.log('[SW] Registered:', reg.scope);
          reg.addEventListener('updatefound', () => {
            const newWorker = reg.installing;
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'activated' && navigator.serviceWorker.controller) {
                console.log('[SW] New content available — refresh to update.');
              }
            });
          });
        })
        .catch((err) => console.warn('[SW] Registration failed:', err));
    });
  }
}

/* ── Auto-init ────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  initCookieConsent();
  registerServiceWorker();
});
