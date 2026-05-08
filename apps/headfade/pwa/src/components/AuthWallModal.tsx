'use client';
/**
 * AuthWallModal — The Cognitive Gate
 *
 * Surfaces when an unauthenticated user taps [REAL] or [AI] or opens comments.
 * UX strategy: humans are psychologically compelled to know if they were right.
 * The modal withholds the truth UNTIL they authenticate — maximising conversion.
 *
 * B2B data purity: forces Google/Apple SSO so every vote maps to a distinct,
 * verified human identity, protecting the Human Deception Index from bot poisoning.
 *
 * Auth: signInWithPopup → GoogleAuthProvider. Apple provider wired but requires
 * Apple Developer account configuration in Firebase console.
 */

import { useState } from 'react';
import {
  signInWithPopup,
  GoogleAuthProvider,
  OAuthProvider,
  type AuthError,
} from 'firebase/auth';
import { auth } from '@/lib/firebase';

interface AuthWallModalProps {
  isOpen: boolean;
  onClose: () => void;
  /** Called after a successful sign-in so the parent can refresh state. */
  onSignedIn?: () => void;
}

const googleProvider = new GoogleAuthProvider();
const appleProvider = new OAuthProvider('apple.com');

export function AuthWallModal({ isOpen, onClose, onSignedIn }: AuthWallModalProps) {
  const [loading, setLoading] = useState<'google' | 'apple' | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  async function handleSignIn(provider: 'google' | 'apple') {
    setLoading(provider);
    setError(null);
    try {
      const p = provider === 'google' ? googleProvider : appleProvider;
      await signInWithPopup(auth, p);
      onClose();
      onSignedIn?.();
    } catch (err) {
      const ae = err as AuthError;
      // User closed the popup — not an error worth surfacing
      if (ae.code !== 'auth/popup-closed-by-user' && ae.code !== 'auth/cancelled-popup-request') {
        setError('Sign-in failed. Try again or check your network.');
      }
    } finally {
      setLoading(null);
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="auth-wall-title"
      aria-describedby="auth-wall-desc"
      className="fixed inset-0 z-[9999] flex items-center justify-center px-4"
      style={{ backgroundColor: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)' }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      onKeyDown={(e) => { if ((e.key === 'Escape' || e.key === 'Enter') && e.target === e.currentTarget) onClose(); }}
      tabIndex={-1}
    >
      <div
        className="relative w-full max-w-[420px] rounded-2xl overflow-hidden"
        style={{
          background: 'linear-gradient(145deg,#0F0A1E 0%,#1A0A2E 60%,#0A1A2E 100%)',
          border: '1px solid rgba(124,58,237,0.4)',
          boxShadow: '0 24px 80px rgba(124,58,237,0.35), 0 0 0 1px rgba(124,58,237,0.1)',
        }}
      >
        {/* Purple glow accent top */}
        <div
          className="absolute top-0 left-0 right-0 h-[3px]"
          style={{ background: 'linear-gradient(90deg,#7C3AED,#0891B2)' }}
        />

        <div className="p-8 flex flex-col items-center gap-5 text-center">
          {/* Icon */}
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl"
            style={{ background: 'rgba(124,58,237,0.2)', border: '1px solid rgba(124,58,237,0.4)' }}
          >
            🔒
          </div>

          {/* Headline */}
          <div className="flex flex-col gap-1">
            <h2
              id="auth-wall-title"
              className="text-white text-[24px] font-black leading-tight"
            >
              Your vote is locked.
            </h2>
            <p className="text-[13px] font-bold" style={{ color: '#A78BFA' }}>
              COGNITIVE GATE ACTIVE
            </p>
          </div>

          {/* Body */}
          <p
            id="auth-wall-desc"
            className="text-[14px] leading-relaxed"
            style={{ color: 'rgba(255,255,255,0.65)' }}
          >
            Authenticate to join the{' '}
            <span className="text-white font-semibold">Forensics Tribunal</span> and reveal
            the truth. Were your eyes deceived?
          </p>

          {/* Stakes callout */}
          <div
            className="w-full rounded-xl px-4 py-3 text-left"
            style={{ background: 'rgba(124,58,237,0.12)', border: '1px solid rgba(124,58,237,0.25)' }}
          >
            <p className="text-[12px] font-bold text-white mb-1">
              Why sign in?
            </p>
            <ul className="text-[12px] space-y-1" style={{ color: 'rgba(255,255,255,0.72)' }}>
              <li>⚡ Earn your <strong className="text-white">Forensic Elo</strong> rating</li>
              <li>🏆 Climb the global detection leaderboard</li>
              <li>🔬 See second-by-second heatmaps of where humans look</li>
              <li>🚫 Your votes help keep bot data out of the Tribunal</li>
            </ul>
          </div>

          {/* Error message */}
          {error && (
            <p className="text-[13px] text-red-400 font-medium">{error}</p>
          )}

          {/* SSO Buttons */}
          <div className="flex flex-col gap-3 w-full">
            <button
              id="auth-wall-google-btn"
              type="button"
              data-testid="auth-wall-google"
              onClick={() => handleSignIn('google')}
              disabled={loading !== null}
              className="flex items-center justify-center gap-3 w-full py-3 rounded-xl text-[15px] font-semibold transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-60 disabled:cursor-wait"
              style={{ backgroundColor: 'white', color: '#1A1A1A' }}
            >
              {loading === 'google' ? (
                <span className="w-5 h-5 border-2 border-gray-300 border-t-gray-700 rounded-full animate-spin" />
              ) : (
                <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none" aria-hidden="true">
                  <title>Google logo</title>
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05" />
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                </svg>
              )}
              Continue with Google
            </button>

            <button
              id="auth-wall-apple-btn"
              type="button"
              data-testid="auth-wall-apple"
              onClick={() => handleSignIn('apple')}
              disabled={loading !== null}
              className="flex items-center justify-center gap-3 w-full py-3 rounded-xl text-[15px] font-semibold transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-60 disabled:cursor-wait"
              style={{ backgroundColor: '#1C1C1E', color: 'white', border: '1px solid rgba(255,255,255,0.15)' }}
            >
              {loading === 'apple' ? (
                <span className="w-5 h-5 border-2 border-gray-600 border-t-white rounded-full animate-spin" />
              ) : (
                <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current" aria-hidden="true">
                  <title>Apple logo</title>
                  <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
                </svg>
              )}
              Continue with Apple
            </button>
          </div>

          {/* Ghost viewer notice */}
          <p className="text-[12px]" style={{ color: 'rgba(255,255,255,0.5)' }}>
            Browse freely as a ghost · Sign in only to vote
          </p>

          {/* Close */}
          <button
            type="button"
            aria-label="Close authentication modal"
            onClick={onClose}
            className="absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center transition-colors"
            style={{ backgroundColor: 'rgba(255,255,255,0.08)', color: 'rgba(255,255,255,0.5)' }}
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
}
