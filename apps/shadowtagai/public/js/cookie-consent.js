/**
 * CounselConduit / KovelAI — GDPR Cookie Consent Banner
 *
 * Drop-in cookie consent banner compliant with:
 *   - GDPR (EU General Data Protection Regulation)
 *   - CCPA (California Consumer Privacy Act)
 *   - ePrivacy Directive
 *
 * Usage: Include this script before </body> on any page:
 *   <script src="/js/cookie-consent.js"></script>
 *
 * Respects user choice via localStorage key "cc_consent".
 * Emits a custom event "cc:consent" with detail = { analytics, marketing }.
 *
 * No external dependencies. No cookies set by this script itself.
 * Total size: ~4KB unminified.
 */

(() => {
  var STORAGE_KEY = 'cc_consent';
  var CONSENT_VERSION = 1; // Bump to re-prompt users

  // Check if already consented (with matching version)
  function getStoredConsent() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      if (parsed.version !== CONSENT_VERSION) return null;
      return parsed;
    } catch (_e) {
      return null;
    }
  }

  function storeConsent(analytics, marketing) {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          version: CONSENT_VERSION,
          analytics: analytics,
          marketing: marketing,
          timestamp: new Date().toISOString(),
        }),
      );
    } catch (_e) {
      // Storage full or private mode — degrade gracefully
    }
  }

  function emitConsentEvent(analytics, marketing) {
    if (typeof CustomEvent === 'function') {
      document.dispatchEvent(
        new CustomEvent('cc:consent', {
          detail: { analytics: analytics, marketing: marketing },
        }),
      );
    }
  }

  // If consent already given, emit event and exit
  var stored = getStoredConsent();
  if (stored) {
    emitConsentEvent(stored.analytics, stored.marketing);
    return;
  }

  // ── Inject Styles ───────────────────────────────────────────────────────

  var style = document.createElement('style');
  style.textContent = [
    '.cc-banner{position:fixed;bottom:0;left:0;right:0;z-index:99999;',
    'background:rgba(10,14,26,0.95);backdrop-filter:blur(20px);',
    'border-top:1px solid rgba(255,255,255,0.08);',
    'padding:20px 24px;display:flex;align-items:center;justify-content:center;gap:20px;',
    "font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;",
    'animation:cc-slide-up .4s cubic-bezier(.16,1,.3,1)}',

    '.cc-banner-inner{display:flex;align-items:center;gap:20px;max-width:1200px;width:100%}',

    '.cc-text{flex:1;font-size:13px;line-height:1.5;color:rgba(240,244,248,0.8)}',
    '.cc-text a{color:#c9a44e;text-decoration:underline}',
    '.cc-text a:hover{color:#dbba6e}',

    '.cc-actions{display:flex;gap:8px;flex-shrink:0}',

    '.cc-btn{padding:8px 18px;border:none;border-radius:6px;',
    'font-family:inherit;font-size:13px;font-weight:600;cursor:pointer;',
    'transition:all 150ms cubic-bezier(.16,1,.3,1)}',

    '.cc-btn-accept{background:#c9a44e;color:#0a0e1a}',
    '.cc-btn-accept:hover{box-shadow:0 0 20px rgba(201,164,78,0.3);transform:translateY(-1px)}',

    '.cc-btn-reject{background:rgba(255,255,255,0.06);color:rgba(240,244,248,0.7);',
    'border:1px solid rgba(255,255,255,0.1)}',
    '.cc-btn-reject:hover{background:rgba(255,255,255,0.1);color:#f0f4f8}',

    '.cc-btn-settings{background:transparent;color:rgba(240,244,248,0.5);text-decoration:underline;',
    'padding:8px 10px;font-size:12px}',
    '.cc-btn-settings:hover{color:#f0f4f8}',

    /* Settings expansion */
    '.cc-settings{display:none;margin-top:12px;padding-top:12px;',
    'border-top:1px solid rgba(255,255,255,0.06)}',
    '.cc-settings.open{display:block}',

    '.cc-toggle-row{display:flex;align-items:center;justify-content:space-between;',
    'padding:6px 0;font-size:12px;color:rgba(240,244,248,0.7)}',

    '.cc-toggle{position:relative;width:36px;height:18px;cursor:pointer}',
    '.cc-toggle input{opacity:0;width:0;height:0}',
    '.cc-slider{position:absolute;inset:0;background:rgba(255,255,255,0.1);',
    'border-radius:9px;transition:background .2s}',
    ".cc-slider:after{content:'';position:absolute;top:2px;left:2px;",
    'width:14px;height:14px;border-radius:50%;background:rgba(240,244,248,0.5);transition:all .2s}',
    '.cc-toggle input:checked+.cc-slider{background:rgba(201,164,78,0.3)}',
    '.cc-toggle input:checked+.cc-slider:after{left:18px;background:#c9a44e}',
    '.cc-toggle input:disabled+.cc-slider{opacity:0.5;cursor:not-allowed}',

    '@keyframes cc-slide-up{from{transform:translateY(100%);opacity:0}to{transform:translateY(0);opacity:1}}',

    '@media(max-width:640px){',
    '.cc-banner-inner{flex-direction:column;text-align:center}',
    '.cc-actions{flex-wrap:wrap;justify-content:center}',
    '}',
  ].join('');
  document.head.appendChild(style);

  // ── Build DOM ───────────────────────────────────────────────────────────

  var banner = document.createElement('div');
  banner.className = 'cc-banner';
  banner.setAttribute('role', 'dialog');
  banner.setAttribute('aria-label', 'Cookie consent');
  banner.id = 'cc-consent-banner';

  var analyticsChecked = true;
  var marketingChecked = false;

  banner.innerHTML = [
    '<div class="cc-banner-inner">',
    '  <div class="cc-text">',
    '    We use cookies for essential site functionality and, with your consent, ',
    '    analytics to improve your experience. We do not sell your data. ',
    '    <a href="/privacy" target="_blank" rel="noopener">Privacy Policy</a>.',
    '    <div class="cc-settings" id="cc-settings">',
    '      <div class="cc-toggle-row">',
    '        <span>Essential (required)</span>',
    '        <label class="cc-toggle">',
    '          <input type="checkbox" checked disabled/>',
    '          <span class="cc-slider"></span>',
    '        </label>',
    '      </div>',
    '      <div class="cc-toggle-row">',
    '        <span>Analytics</span>',
    '        <label class="cc-toggle">',
    '          <input type="checkbox" id="cc-analytics" checked/>',
    '          <span class="cc-slider"></span>',
    '        </label>',
    '      </div>',
    '      <div class="cc-toggle-row">',
    '        <span>Marketing</span>',
    '        <label class="cc-toggle">',
    '          <input type="checkbox" id="cc-marketing"/>',
    '          <span class="cc-slider"></span>',
    '        </label>',
    '      </div>',
    '    </div>',
    '  </div>',
    '  <div class="cc-actions">',
    '    <button class="cc-btn cc-btn-accept" id="cc-accept">Accept All</button>',
    '    <button class="cc-btn cc-btn-reject" id="cc-reject">Reject Non-Essential</button>',
    '    <button class="cc-btn cc-btn-settings" id="cc-toggle-settings">Settings</button>',
    '  </div>',
    '</div>',
  ].join('\n');

  document.body.appendChild(banner);

  // ── Event Handlers ──────────────────────────────────────────────────────

  function closeBanner(analytics, marketing) {
    storeConsent(analytics, marketing);
    emitConsentEvent(analytics, marketing);
    banner.style.animation = 'cc-slide-up .3s cubic-bezier(.16,1,.3,1) reverse forwards';
    setTimeout(() => {
      if (banner.parentNode) banner.parentNode.removeChild(banner);
    }, 300);
  }

  document.getElementById('cc-accept').addEventListener('click', () => {
    closeBanner(true, true);
  });

  document.getElementById('cc-reject').addEventListener('click', () => {
    closeBanner(false, false);
  });

  document.getElementById('cc-toggle-settings').addEventListener('click', function () {
    var settings = document.getElementById('cc-settings');
    settings.classList.toggle('open');
    this.textContent = settings.classList.contains('open') ? 'Save Preferences' : 'Settings';

    if (settings.classList.contains('open')) return;

    // Save button clicked
    var aEl = document.getElementById('cc-analytics');
    var mEl = document.getElementById('cc-marketing');
    closeBanner(aEl.checked, mEl.checked);
  });
})();
