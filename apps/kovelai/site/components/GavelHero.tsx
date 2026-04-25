'use client';

import type React from 'react';

/**
 * GavelHero — Cinematic gavel-fall hero overlay for KovelAI
 *
 * Architecture:
 * - Layer 0 (z-0): Full-bleed background video zone (placeholder div until Veo 3.1 asset arrives)
 * - Layer 1 (z-10): Semi-transparent atmospheric-glass scrim
 * - Layer 2 (z-20): Headline + CTA floating over the impact zone
 *
 * Design tokens: KovelAI DESIGN.md atmospheric-glass dark mode
 * Video: Sized for 16:9 or 21:9 cinematic gavel descent
 * TACSOP 7: No generate_image — CSS gradient placeholder until Veo asset
 */

/* ── DESIGN TOKENS ── */
const T = {
  surface: '#0A0A0F',
  tertiary: '#00BCD4',
  onTertiary: '#003238',
  onSurface: '#FFFFFF',
  onSurfaceV: '#8B949E',
  glass: 'rgba(10, 10, 15, 0.65)',
  glassBorder: 'rgba(255, 255, 255, 0.08)',
} as const;

const styles = {
  wrapper: {
    position: 'relative' as const,
    width: '100%',
    height: '100vh',
    overflow: 'hidden',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  } satisfies React.CSSProperties,

  /* Layer 0 — Video / Gavel animation background */
  videoZone: {
    position: 'absolute' as const,
    inset: 0,
    zIndex: 0,
    /* Cinematic gavel-fall gradient placeholder (until Veo 3.1 asset is ready) */
    background: `
      radial-gradient(
        ellipse 80% 60% at 50% 40%,
        rgba(0, 188, 212, 0.08) 0%,
        transparent 70%
      ),
      linear-gradient(
        180deg,
        ${T.surface} 0%,
        #0D0D14 30%,
        #12121C 50%,
        #0A0A10 80%,
        ${T.surface} 100%
      )
    `,
  } satisfies React.CSSProperties,

  /* The gavel "impact point" — a bright cyan pulse at center-bottom */
  impactPoint: {
    position: 'absolute' as const,
    bottom: '20%',
    left: '50%',
    transform: 'translateX(-50%)',
    width: 320,
    height: 4,
    background: `linear-gradient(90deg, transparent, ${T.tertiary}, transparent)`,
    borderRadius: 2,
    zIndex: 1,
    opacity: 0.6,
    /* Pulse animation via CSS keyframes */
    animation: 'gavelPulse 3s ease-in-out infinite',
  } satisfies React.CSSProperties,

  /* Layer 1 — Atmospheric glass scrim */
  scrim: {
    position: 'absolute' as const,
    inset: 0,
    zIndex: 10,
    background:
      'linear-gradient(180deg, transparent 0%, rgba(10,10,15,0.4) 40%, rgba(10,10,15,0.85) 100%)',
    backdropFilter: 'blur(2px)',
    WebkitBackdropFilter: 'blur(2px)',
  } satisfies React.CSSProperties,

  /* Layer 2 — Content overlay */
  content: {
    position: 'relative' as const,
    zIndex: 20,
    textAlign: 'center' as const,
    maxWidth: 800,
    padding: '0 24px',
  } satisfies React.CSSProperties,

  badge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 8,
    backgroundColor: 'rgba(10, 43, 48, 0.8)',
    color: T.tertiary,
    fontSize: 12,
    fontWeight: 500,
    letterSpacing: '0.04em',
    padding: '6px 14px',
    borderRadius: 9999,
    marginBottom: 24,
    border: `1px solid ${T.glassBorder}`,
  } satisfies React.CSSProperties,

  headline: {
    fontFamily: "'Inter', system-ui, sans-serif",
    fontSize: 64,
    fontWeight: 900,
    lineHeight: 1.1,
    letterSpacing: '-0.03em',
    color: T.onSurface,
    margin: '0 0 16px',
  } satisfies React.CSSProperties,

  headlineAccent: {
    color: T.tertiary,
  } satisfies React.CSSProperties,

  subheadline: {
    fontFamily: "'Inter', system-ui, sans-serif",
    fontSize: 18,
    fontWeight: 400,
    lineHeight: 1.6,
    color: T.onSurfaceV,
    margin: '0 0 32px',
    maxWidth: 560,
    marginLeft: 'auto',
    marginRight: 'auto',
  } satisfies React.CSSProperties,

  ctas: {
    display: 'flex',
    gap: 16,
    justifyContent: 'center',
    flexWrap: 'wrap' as const,
  } satisfies React.CSSProperties,

  ctaPrimary: {
    backgroundColor: T.tertiary,
    color: T.onTertiary,
    border: 'none',
    borderRadius: 16,
    padding: '14px 32px',
    fontSize: 14,
    fontWeight: 600,
    letterSpacing: '0.02em',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  } satisfies React.CSSProperties,

  ctaGhost: {
    backgroundColor: 'transparent',
    color: T.tertiary,
    border: `1px solid ${T.tertiary}`,
    borderRadius: 16,
    padding: '14px 32px',
    fontSize: 14,
    fontWeight: 600,
    letterSpacing: '0.02em',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  } satisfies React.CSSProperties,
} as const;

/* ── CSS Keyframes (injected once) ── */
const keyframesCSS = `
@keyframes gavelPulse {
  0%, 100% { opacity: 0.3; transform: translateX(-50%) scaleX(0.7); }
  50%      { opacity: 0.8; transform: translateX(-50%) scaleX(1.0); }
}
@keyframes gavelDescent {
  0%   { transform: translateY(-120vh) rotate(-8deg); opacity: 0; }
  60%  { transform: translateY(-5vh) rotate(2deg); opacity: 0.9; }
  75%  { transform: translateY(2vh) rotate(-1deg); opacity: 1; }
  100% { transform: translateY(0) rotate(0deg); opacity: 1; }
}
`;

interface GavelHeroProps {
  /** Override headline (default: "Privilege-Protected AI") */
  headline?: React.ReactNode;
  /** Subheadline */
  subheadline?: string;
  /** When Veo 3.1 asset is ready, pass video URL here */
  videoSrc?: string;
}

export function GavelHero({
  headline,
  subheadline = 'Multi-model AI routing with cryptographic privilege attestation. Protected under United States v. Heppner.',
  videoSrc,
}: GavelHeroProps) {
  return (
    <>
      <style>{keyframesCSS}</style>
      <div style={styles.wrapper} id="gavel-hero">
        {/* Layer 0 — Video or gradient placeholder */}
        {videoSrc ? (
          <video
            style={{
              ...styles.videoZone,
              objectFit: 'cover',
              background: 'none',
            }}
            src={videoSrc}
            autoPlay
            muted
            loop
            playsInline
          />
        ) : (
          <div style={styles.videoZone} aria-hidden="true" />
        )}

        {/* Impact point glow line */}
        <div style={styles.impactPoint} aria-hidden="true" />

        {/* Layer 1 — Glass scrim */}
        <div style={styles.scrim} aria-hidden="true" />

        {/* Layer 2 — Content */}
        <div style={styles.content}>
          <div style={styles.badge}>
            <span>⚖</span>
            <span>PRIVILEGE-PRESERVING AI FOR LAW</span>
          </div>

          <h1 style={styles.headline}>
            {headline ?? (
              <>
                Deploy AI.
                <br />
                <span style={styles.headlineAccent}>Preserve Privilege.</span>
              </>
            )}
          </h1>

          <p style={styles.subheadline}>{subheadline}</p>

          <div style={styles.ctas}>
            <button type="button" style={styles.ctaPrimary}>
              Request Access
            </button>
            <button type="button" style={styles.ctaGhost}>
              Read the Brief
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default GavelHero;
