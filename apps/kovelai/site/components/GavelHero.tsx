"use client";

import type React from "react";
import { useEffect, useRef } from "react";

/**
 * GavelHero — Cinematic gavel-fall hero overlay for KovelAI
 *
 * Architecture:
 * - Layer 0 (z-0): Canvas scroll-driven frame engine (replaces <video> for smoothness)
 * - Layer 0.5 (z-1): SVG grain overlay for premium texture
 * - Layer 1 (z-10): Semi-transparent atmospheric-glass scrim
 * - Layer 2 (z-20): Headline + CTA floating over the impact zone
 *
 * Per scroll-experience skill:
 * - Only animate transform + opacity (GPU-friendly)
 * - rAF-throttled scroll handler
 * - prefers-reduced-motion respected
 * - Content in DOM for SEO (not canvas-only)
 *
 * Design tokens: KovelAI DESIGN.md atmospheric-glass dark mode
 * TACSOP 7: No generate_image — CSS gradient placeholder until Veo asset
 */

/* ── DESIGN TOKENS ── */
const T = {
  surface: "#0A0A0F",
  tertiary: "#00BCD4",
  onTertiary: "#003238",
  onSurface: "#FFFFFF",
  onSurfaceV: "#8B949E",
  glass: "rgba(10, 10, 15, 0.65)",
  glassBorder: "rgba(255, 255, 255, 0.08)",
} as const;

/** Total frames in scroll-driven sequence (8s @ 30fps). Update if Veo asset changes. */
const FRAME_COUNT = 240;

const styles = {
  wrapper: {
    position: "relative" as const,
    width: "100%",
    height: "100vh",
    overflow: "hidden",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  } satisfies React.CSSProperties,

  /* Layer 0 — Canvas scroll-driven frame zone (replaces <video>) */
  canvasZone: {
    position: "absolute" as const,
    inset: 0,
    zIndex: 0,
    /* Cinematic gradient placeholder (visible until frames load) */
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

  canvas: {
    width: "100%",
    height: "100%",
    objectFit: "cover" as const,
    opacity: 0.12,
  } satisfies React.CSSProperties,

  /* Grain overlay for premium texture */
  grain: {
    position: "absolute" as const,
    inset: 0,
    zIndex: 1,
    opacity: 0.04,
    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
    pointerEvents: "none" as const,
  } satisfies React.CSSProperties,

  /* The gavel "impact point" — a bright cyan pulse at center-bottom */
  impactPoint: {
    position: "absolute" as const,
    bottom: "20%",
    left: "50%",
    transform: "translateX(-50%)",
    width: 320,
    height: 4,
    background: `linear-gradient(90deg, transparent, ${T.tertiary}, transparent)`,
    borderRadius: 2,
    zIndex: 1,
    opacity: 0.6,
    /* Pulse animation via CSS keyframes */
    animation: "gavelPulse 3s ease-in-out infinite",
  } satisfies React.CSSProperties,

  /* Layer 1 — Atmospheric glass scrim */
  scrim: {
    position: "absolute" as const,
    inset: 0,
    zIndex: 10,
    background:
      "linear-gradient(180deg, transparent 0%, rgba(10,10,15,0.4) 40%, rgba(10,10,15,0.85) 100%)",
    backdropFilter: "blur(2px)",
    WebkitBackdropFilter: "blur(2px)",
  } satisfies React.CSSProperties,

  /* Layer 2 — Content overlay */
  content: {
    position: "relative" as const,
    zIndex: 20,
    textAlign: "center" as const,
    maxWidth: 800,
    padding: "0 24px",
  } satisfies React.CSSProperties,

  badge: {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    backgroundColor: "rgba(10, 43, 48, 0.8)",
    color: T.tertiary,
    fontSize: 12,
    fontWeight: 500,
    letterSpacing: "0.04em",
    padding: "6px 14px",
    borderRadius: 9999,
    marginBottom: 24,
    border: `1px solid ${T.glassBorder}`,
  } satisfies React.CSSProperties,

  headline: {
    fontFamily: "'Inter', system-ui, sans-serif",
    fontSize: 64,
    fontWeight: 900,
    lineHeight: 1.1,
    letterSpacing: "-0.03em",
    color: T.onSurface,
    margin: "0 0 16px",
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
    margin: "0 0 32px",
    maxWidth: 560,
    marginLeft: "auto",
    marginRight: "auto",
  } satisfies React.CSSProperties,

  ctas: {
    display: "flex",
    gap: 16,
    justifyContent: "center",
    flexWrap: "wrap" as const,
  } satisfies React.CSSProperties,

  ctaPrimary: {
    backgroundColor: T.tertiary,
    color: T.onTertiary,
    border: "none",
    borderRadius: 16,
    padding: "14px 32px",
    fontSize: 14,
    fontWeight: 600,
    letterSpacing: "0.02em",
    cursor: "pointer",
    transition: "all 0.2s ease",
  } satisfies React.CSSProperties,

  ctaGhost: {
    backgroundColor: "transparent",
    color: T.tertiary,
    border: `1px solid ${T.tertiary}`,
    borderRadius: 16,
    padding: "14px 32px",
    fontSize: 14,
    fontWeight: 600,
    letterSpacing: "0.02em",
    cursor: "pointer",
    transition: "all 0.2s ease",
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
  /**
   * Directory containing extracted frames (e.g., '/frames/').
   * Frames must be named frame_0001.jpg, frame_0002.jpg, ...
   * Generate with: ./scripts/extract_frames.sh <veo_video.mp4> <output_dir>
   */
  frameDir?: string;
  /** Total number of frames in the sequence (default: FRAME_COUNT = 8s @ 30fps) */
  frameCount?: number;
}

export function GavelHero({
  headline,
  subheadline = "Multi-model AI routing with cryptographic privilege attestation. Protected under United States v. Heppner.",
  frameDir = "/frames/",
  frameCount = FRAME_COUNT,
}: GavelHeroProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // Frame state
    const frames: HTMLImageElement[] = [];
    let framesLoaded = 0;
    let currentFrame = 0;
    let canvasReady = false;

    // Resize canvas to match container
    const resizeCanvas = () => {
      const rect = canvas.parentElement?.getBoundingClientRect();
      if (!rect) return;
      canvas.width = rect.width;
      canvas.height = rect.height;
      if (canvasReady && frames[currentFrame]) drawFrame(currentFrame);
    };

    // Draw a single frame with cover-fit
    const drawFrame = (idx: number) => {
      const img = frames[idx];
      if (!img?.complete) return;
      const cw = canvas.width,
        ch = canvas.height;
      const iw = img.naturalWidth,
        ih = img.naturalHeight;
      const scale = Math.max(cw / iw, ch / ih);
      const dx = (cw - iw * scale) / 2;
      const dy = (ch - ih * scale) / 2;
      ctx.clearRect(0, 0, cw, ch);
      ctx.drawImage(img, dx, dy, iw * scale, ih * scale);
    };

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas, { passive: true });

    // eslint-disable-next-line prefer-const -- assigned conditionally
    let onScroll: (() => void) | null = null;

    if (prefersReduced) {
      // prefers-reduced-motion: show static poster frame only
      const poster = new Image();
      poster.src = `${frameDir}frame_0000.png`;
      poster.onload = () => {
        canvasReady = true;
        frames[0] = poster;
        drawFrame(0);
      };
    } else {
      // Preload all frames
      for (let i = 1; i <= frameCount; i++) {
        const img = new Image();
        img.src = `${frameDir}frame_${String(i).padStart(4, "0")}.jpg`;
        img.onload = () => {
          framesLoaded++;
          if (framesLoaded === frameCount) {
            canvasReady = true;
            drawFrame(0);
          }
        };
        // If frames don't exist (pre-Veo), canvas stays transparent.
        // CSS gradient placeholder is visible behind it.
        img.onerror = () => {};
        frames[i - 1] = img;
      }

      // rAF-throttled scroll → frame mapping
      let scrollTicking = false;
      const updateScrollFrame = () => {
        if (!canvasReady) return;
        const scrollY = window.scrollY;
        const maxScroll = window.innerHeight;
        const progress = Math.min(Math.max(scrollY / maxScroll, 0), 1);
        const frameIdx = Math.floor(progress * (frameCount - 1));
        if (frameIdx !== currentFrame) {
          currentFrame = frameIdx;
          drawFrame(currentFrame);
        }
      };

      onScroll = () => {
        if (!scrollTicking) {
          requestAnimationFrame(() => {
            updateScrollFrame();
            scrollTicking = false;
          });
          scrollTicking = true;
        }
      };

      window.addEventListener("scroll", onScroll, { passive: true });
    }

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      if (onScroll) window.removeEventListener("scroll", onScroll);
    };
  }, [frameDir, frameCount]);

  return (
    <>
      <style>{keyframesCSS}</style>
      <div style={styles.wrapper} id="gavel-hero">
        {/* Layer 0 — Canvas scroll-driven frame engine (CSS gradient fallback underneath) */}
        <div style={styles.canvasZone} aria-hidden="true">
          <canvas ref={canvasRef} style={styles.canvas} />
        </div>

        {/* Grain overlay for premium texture */}
        <div style={styles.grain} aria-hidden="true" />

        {/* Impact point glow line */}
        <div style={styles.impactPoint} aria-hidden="true" />

        {/* Layer 1 — Glass scrim */}
        <div style={styles.scrim} aria-hidden="true" />

        {/* Layer 2 — Content (in DOM for SEO, per scroll-experience skill) */}
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
