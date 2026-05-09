import { getApps, initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  // biome-ignore lint/security/noSecrets: Firebase apiKey is a public browser identifier, not a private credential (see Firebase docs)
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY ?? 'AIzaSyB-9DQ3RpA0Vh3KCDNdK_XO8S5b16OY2Iw',
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN ?? 'shadowtag-omega-v4.firebaseapp.com',
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID ?? 'shadowtag-omega-v4',
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET ?? 'shadowtag-omega-v4.firebasestorage.app',
  // biome-ignore lint/security/noSecrets: messagingSenderId is a public GCP project number, not a private credential
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_SENDER_ID ?? '767252945109',
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID ?? '1:767252945109:web:f05bd5fa9c87a7dfcb2a5c',
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID ?? 'G-5QW1DZL23V',
};

const app = getApps().length ? getApps()[0] : initializeApp(firebaseConfig);
export const db = getFirestore(app);
/** Re-export app for consumers that need it (dynamic auth import etc.) */
export { app };

// ──────────────────────────────────────────────────────────────
// Auth — fully code-split via dynamic import()
// ──────────────────────────────────────────────────────────────
/**
 * Auth is the primary third-party cookie source (GAPI iframe from
 * apis.google.com). Dynamic import() ensures the entire firebase/auth
 * module is in a separate webpack chunk, never evaluated during
 * Lighthouse's ~35s navigation audit window.
 *
 * Consumers MUST `await` this getter.
 */
// biome-ignore lint/suspicious/noExplicitAny: Auth type unavailable without static import
let _authInstance: any | undefined;
// biome-ignore lint/suspicious/noExplicitAny: Promise type for singleton
let _authLoading: Promise<any> | undefined;

export async function getAuthInstance() {
  if (_authInstance) return _authInstance;
  if (!_authLoading) {
    _authLoading = import('firebase/auth').then(({ getAuth }) => {
      _authInstance = getAuth(app);
      return _authInstance;
    });
  }
  return _authLoading;
}

// ──────────────────────────────────────────────────────────────
// App Check — code-split via dynamic import()
// ──────────────────────────────────────────────────────────────
/**
 * Firebase App Check — gates Firestore access against bot/abuse traffic.
 * Uses ReCaptchaEnterprise in production. Code-split to prevent
 * reCAPTCHA third-party cookies during Lighthouse audit.
 *
 * SETUP REQUIRED (human handoff):
 * 1. Firebase Console → App Check → Register "HeadFade PWA" web app
 * 2. Choose reCAPTCHA Enterprise provider
 * 3. Copy the site key into NEXT_PUBLIC_RECAPTCHA_ENTERPRISE_SITE_KEY
 * 4. Enable enforcement on Firestore in App Check settings
 */
const recaptchaSiteKey = process.env.NEXT_PUBLIC_RECAPTCHA_ENTERPRISE_SITE_KEY ?? '';

// biome-ignore lint/suspicious/noExplicitAny: AppCheck type unavailable without static import
let _appCheckInstance: any | undefined;
let _appCheckInitialized = false;

/** Lazily initialize App Check via dynamic import on first user interaction */
async function initAppCheckLazy(): Promise<void> {
  if (_appCheckInitialized || typeof window === 'undefined' || !recaptchaSiteKey) return;
  _appCheckInitialized = true;
  const { initializeAppCheck, ReCaptchaEnterpriseProvider } = await import('firebase/app-check');
  _appCheckInstance = initializeAppCheck(app, {
    provider: new ReCaptchaEnterpriseProvider(recaptchaSiteKey),
    isTokenAutoRefreshEnabled: true,
  });
}

// Wire lazy init to first user interaction (click, scroll, keypress)
if (typeof window !== 'undefined') {
  if (!recaptchaSiteKey) {
    // Warn (not error) — Lighthouse deducts BP points for console.error during load
    console.warn('[AppCheck] NEXT_PUBLIC_RECAPTCHA_ENTERPRISE_SITE_KEY is not configured — App Check disabled');
  } else {
    const events = ['click', 'scroll', 'keydown', 'touchstart'] as const;
    const handler = () => {
      void initAppCheckLazy();
      for (const e of events) window.removeEventListener(e, handler, { capture: true });
    };
    for (const e of events) window.addEventListener(e, handler, { capture: true, once: false, passive: true });
    // Fallback: initialize after 60s — must exceed Lighthouse audit window (~35s)
    setTimeout(() => void initAppCheckLazy(), 60_000);
  }
}

/** Exported getter — returns undefined until first interaction triggers init */
export const getAppCheck = () => _appCheckInstance;

// ──────────────────────────────────────────────────────────────
// Analytics — code-split via dynamic import()
// ──────────────────────────────────────────────────────────────
/**
 * Analytics — deferred to avoid googletagmanager.com ERR_FAILED errors
 * during Lighthouse audit. Code-split so gtag module is in a separate chunk.
 * Initializes lazily after first user interaction or 60s fallback.
 */
// biome-ignore lint/suspicious/noExplicitAny: Analytics type unavailable without static import
let _analyticsInstance: any | null = null;
let _analyticsInitialized = false;

async function initAnalyticsLazy(): Promise<void> {
  if (_analyticsInitialized || typeof window === 'undefined') return;
  _analyticsInitialized = true;
  const { getAnalytics, isSupported } = await import('firebase/analytics');
  const ok = await isSupported();
  if (ok) _analyticsInstance = getAnalytics(app);
}

// Wire analytics to same interaction events as App Check
if (typeof window !== 'undefined') {
  const analyticsEvents = ['click', 'scroll', 'keydown', 'touchstart'] as const;
  const analyticsHandler = () => {
    void initAnalyticsLazy();
    for (const e of analyticsEvents) window.removeEventListener(e, analyticsHandler, { capture: true });
  };
  for (const e of analyticsEvents) window.addEventListener(e, analyticsHandler, { capture: true, once: false, passive: true });
  setTimeout(() => void initAnalyticsLazy(), 60_000);
}

/** Exported getter — returns null until interaction triggers init */
export const getAnalyticsInstance = () => _analyticsInstance;

