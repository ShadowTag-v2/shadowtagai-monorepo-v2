/**
 * V23 Firebase Dynamic Import — Canonical Auth Manager
 * Static Firebase imports are BANNED to protect P100 Lighthouse scores.
 * All auth access MUST go through this dynamic loader.
 *
 * NOTE: This is a shared utility. Consumers must call `initAuthManager(app)`
 * with their own Firebase App instance before using any auth functions.
 * Example: `initAuthManager(app)` where `app` comes from firebase.ts.
 */

import type { FirebaseApp } from "firebase/app";

// biome-ignore lint/suspicious/noExplicitAny: Auth type unavailable without static import
let authInstance: any | null = null;
let _app: FirebaseApp | null = null;

/** Initialize the auth manager with a Firebase App instance */
export function initAuthManager(app: FirebaseApp): void {
  _app = app;
}

export async function getAuthInstance() {
  if (!_app) {
    throw new Error("Auth manager not initialized. Call initAuthManager(app) first.");
  }
  if (!authInstance) {
    const { getAuth } = await import("firebase/auth");
    authInstance = getAuth(_app);
  }
  return authInstance;
}

export async function signInWithGoogle() {
  const auth = await getAuthInstance();
  const { GoogleAuthProvider, signInWithPopup } = await import("firebase/auth");
  const provider = new GoogleAuthProvider();
  return signInWithPopup(auth, provider);
}

export async function signOut() {
  const auth = await getAuthInstance();
  const { signOut: firebaseSignOut } = await import("firebase/auth");
  return firebaseSignOut(auth);
}

export async function onAuthStateChanged(callback: (user: unknown) => void) {
  const auth = await getAuthInstance();
  const { onAuthStateChanged: firebaseOnAuth } = await import("firebase/auth");
  return firebaseOnAuth(auth, callback);
}
