/**
 * V23 Firebase Dynamic Import — Canonical Auth Manager
 * Static Firebase imports are BANNED to protect P100 Lighthouse scores.
 * All auth access MUST go through this dynamic loader.
 */

import { app } from './firebase_app_init';

let authInstance: ReturnType<typeof import('firebase/auth').getAuth> | null = null;

export async function getAuthInstance() {
  if (!authInstance) {
    const { getAuth } = await import('firebase/auth');
    authInstance = getAuth(app);
    console.log("V23 Phosphor-Shift: Firebase Auth dynamically loaded. Lighthouse P100 preserved.");
  }
  return authInstance;
}

export async function signInWithGoogle() {
  const auth = await getAuthInstance();
  const { GoogleAuthProvider, signInWithPopup } = await import('firebase/auth');
  const provider = new GoogleAuthProvider();
  return signInWithPopup(auth, provider);
}

export async function signOut() {
  const auth = await getAuthInstance();
  const { signOut: firebaseSignOut } = await import('firebase/auth');
  return firebaseSignOut(auth);
}

export async function onAuthStateChanged(callback: (user: unknown) => void) {
  const auth = await getAuthInstance();
  const { onAuthStateChanged: firebaseOnAuth } = await import('firebase/auth');
  return firebaseOnAuth(auth, callback);
}
