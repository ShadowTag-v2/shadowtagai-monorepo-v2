/**
 * V19 Archon-Bun Hyper-Core — GavelHero Isomorphic Component
 *
 * Secured by:
 *   - Firebase Auth (react-firebase-starter identity context)
 *   - GraphQL gateway access check (Spanner ledger)
 *   - Stitch Design Tokens (M3 Material 3 via stitch-bridge.tsx)
 *
 * Pattern: Kriasoft react-starter-kit component architecture
 * Runtime: Edge-rendered React + Bun backend
 */

import React, { useEffect, useRef, useState } from 'react';
import { useStitchTheme } from '../core/stitch-bridge';

// ─── Constants ────────────────────────────────────────────────────
const FRAME_COUNT = 142;
const CDN_BASE_URL = 'https://storage.googleapis.com/uphill-assets-cdn-v19';
const GRAPHQL_ENDPOINT = '/graphql';

// ─── Types ────────────────────────────────────────────────────────
interface UserAccessData {
  userAccess: boolean;
}

interface GraphQLResponse<T> {
  data?: T;
  errors?: Array<{ message: string }>;
}

// ─── GavelHero Component ──────────────────────────────────────────
export const GavelHero: React.FC<{
  firebaseUid?: string;
  onAuthRequired?: () => void;
}> = ({ firebaseUid, onAuthRequired }) => {
  const theme = useStitchTheme();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [loaded, setLoaded] = useState(false);
  const [accessGranted, setAccessGranted] = useState(false);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ─── Access Check via GraphQL Gateway ────────────────────────
  useEffect(() => {
    if (!firebaseUid) {
      setChecking(false);
      return;
    }

    fetch(GRAPHQL_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `query CheckAccess($uid: String!) { userAccess(firebaseUid: $uid) }`,
        variables: { uid: firebaseUid },
      }),
    })
      .then((res) => res.json())
      .then((result: GraphQLResponse<UserAccessData>) => {
        if (result.data?.userAccess) {
          setAccessGranted(true);
        } else {
          setError('Stripe Ledger denies access. Payment required.');
        }
      })
      .catch((err) => {
        console.error('[GavelHero] Access check failed:', err);
        setError('Gateway unreachable.');
      })
      .finally(() => setChecking(false));
  }, [firebaseUid]);

  // ─── Frame Animation ────────────────────────────────────────
  useEffect(() => {
    if (!accessGranted) return;

    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;

    let frameIndex = 0;
    let animationFrameId: number;
    let timeoutId: ReturnType<typeof setTimeout>;

    const images: HTMLImageElement[] = Array.from({ length: FRAME_COUNT }, (_, i) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.src = `${CDN_BASE_URL}/frames/frame_${String(i + 1).padStart(4, '0')}.webp`;
      return img;
    });

    const render = () => {
      const img = images[frameIndex];
      if (img.complete && img.naturalWidth > 0) {
        if (!loaded) setLoaded(true);
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        ctx.drawImage(img, 0, 0);
      }
      frameIndex = (frameIndex + 1) % FRAME_COUNT;
      timeoutId = setTimeout(() => {
        animationFrameId = requestAnimationFrame(render);
      }, 1000 / 30);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      clearTimeout(timeoutId);
    };
  }, [accessGranted, loaded]);

  // ─── Render States ──────────────────────────────────────────
  const baseStyle: React.CSSProperties = {
    position: 'relative',
    width: '100%',
    height: '100vh',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
    fontFamily: theme.typography.bodyLarge,
    color: theme.colors.onSurface,
  };

  if (checking) {
    return (
      <div style={baseStyle}>
        <div style={{
          fontFamily: theme.typography.displaySmall,
          fontSize: '1.25rem',
          opacity: 0.7,
          animation: 'pulse 2s ease-in-out infinite',
        }}>
          Authenticating Federated Edge...
        </div>
      </div>
    );
  }

  if (!firebaseUid) {
    return (
      <div style={baseStyle}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            fontFamily: theme.typography.headlineLarge,
            fontSize: '2rem',
            marginBottom: '1.5rem',
            color: theme.colors.primary,
          }}>
            V19 Archon-Bun Hyper-Core
          </div>
          <div style={{
            color: theme.colors.onSurfaceVariant,
            marginBottom: '2rem',
            fontSize: '1.1rem',
          }}>
            Identity required. Authenticate via Firebase to access the Sovereign OS.
          </div>
          <button
            type="button"
            onClick={onAuthRequired}
            style={{
              backgroundColor: theme.colors.primary,
              color: theme.colors.onPrimary,
              border: 'none',
              borderRadius: theme.shapes.cornerFull,
              padding: '14px 32px',
              fontSize: '1rem',
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: theme.elevation.level2,
              transition: 'all 0.2s ease',
              fontFamily: theme.typography.labelLarge,
            }}
          >
            Sign In with Google
          </button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={baseStyle}>
        <div style={{
          color: theme.colors.error,
          fontFamily: theme.typography.headlineMedium,
          fontSize: '1.25rem',
          textAlign: 'center',
          padding: '2rem',
        }}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div style={baseStyle}>
      {/* Loading overlay */}
      {!loaded && (
        <div style={{
          position: 'absolute',
          zIndex: 10,
          fontFamily: theme.typography.displayLarge,
          fontSize: '1.5rem',
          color: theme.colors.onSurface,
          opacity: 0.6,
          animation: 'pulse 2s ease-in-out infinite',
        }}>
          Loading V19 Archon-Bun OS...
        </div>
      )}

      {/* Frame canvas */}
      <canvas
        ref={canvasRef}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transition: 'opacity 1s ease',
          opacity: loaded ? 1 : 0,
        }}
      />

      {/* HUD overlay */}
      <div style={{
        position: 'absolute',
        top: 20,
        left: 20,
        fontSize: '0.75rem',
        opacity: 0.4,
        color: theme.colors.onSurface,
        fontFamily: 'monospace',
      }}>
        UID: {firebaseUid?.slice(0, 12)}... | Ledger: Authorized | V19 Archon
      </div>

      {/* CTA button */}
      <button
        type="button"
        style={{
          position: 'absolute',
          bottom: 40,
          backgroundColor: theme.colors.primary,
          color: theme.colors.onPrimary,
          border: 'none',
          borderRadius: theme.shapes.cornerFull,
          padding: '14px 28px',
          fontSize: '1rem',
          fontWeight: 600,
          cursor: 'pointer',
          boxShadow: theme.elevation.level2,
          transition: 'all 0.2s ease',
          fontFamily: theme.typography.labelLarge,
        }}
      >
        Execute Archon-Boot
      </button>

      {/* Pulse keyframe injection */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.4; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  );
};

export default GavelHero;
