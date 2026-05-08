import { getAnalytics, isSupported } from 'firebase/analytics';
import {
  initializeAppCheck,
  ReCaptchaEnterpriseProvider,
} from 'firebase/app-check';
import { getApps, initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
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
export const auth = getAuth(app);

/**
 * Firebase App Check — gates Firestore access against bot/abuse traffic.
 * Uses ReCaptchaEnterprise in production; enable debug tokens via
 * `self.FIREBASE_APPCHECK_DEBUG_TOKEN = true` in browser console for local dev.
 *
 * reCAPTCHA Enterprise key registered 2026-05-07 in Firebase Console → App Check.
 * Domain: headfade.com | Provider: reCAPTCHA Enterprise
 */
export const appCheck =
  typeof window !== 'undefined'
    ? initializeAppCheck(app, {
        provider: new ReCaptchaEnterpriseProvider(
          process.env.NEXT_PUBLIC_RECAPTCHA_ENTERPRISE_SITE_KEY ??
            '6LfSBt8sAAAAALgjp7rkKxlhGCJGjVmk1NzRJa3g'
        ),
        isTokenAutoRefreshEnabled: true,
      })
    : undefined;

/** Analytics — browser only, gracefully absent in SSR/Node */
export const analyticsPromise =
  typeof window !== 'undefined'
    ? isSupported().then((ok) => (ok ? getAnalytics(app) : null))
    : Promise.resolve(null);
