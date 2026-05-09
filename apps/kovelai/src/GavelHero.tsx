/**
 * ═══════════════════════════════════════════════════════════════
 * GavelHero — V17 Generative UI Component
 * ═══════════════════════════════════════════════════════════════
 *
 * Canvas-based hero component with Material 3 design tokens.
 * Renders frame-by-frame animation from CDN-hosted assets.
 *
 * Design tokens sourced from Design MCP (design.googleapis.com/mcp).
 * UI chassis: react-starter-kit isomorphic foundation.
 *
 * Usage:
 *   <GavelHero onBootClick={() => console.log('Hyper-Boot initiated')} />
 */

import React, { useEffect, useRef, useState, useCallback } from "react";

// ─── Material 3 Design Tokens (sourced from Design MCP) ────────
// These tokens are generated via `generate_color_scheme` and `search_fonts`
// from the uphill-design-mcp server, then hardened here for runtime use.
const M3_TOKENS = {
  colors: {
    surface: "#121212",
    surfaceVariant: "#1E1E2E",
    onSurface: "#E6E1E5",
    primary: "#D0BCFF",
    onPrimary: "#381E72",
    primaryContainer: "#4F378B",
    secondary: "#CCC2DC",
    tertiary: "#EFB8C8",
    outline: "#938F99",
    error: "#F2B8B5",
  },
  typography: {
    displayLarge: "'Outfit', 'Inter', system-ui, sans-serif",
    headlineLarge: "'Outfit', 'Inter', system-ui, sans-serif",
    bodyLarge: "'Inter', 'Roboto', system-ui, sans-serif",
    labelLarge: "'Inter', 'Roboto', system-ui, sans-serif",
  },
  shapes: {
    cornerNone: "0px",
    cornerSmall: "8px",
    cornerMedium: "12px",
    cornerLarge: "16px",
    cornerExtraLarge: "28px",
    cornerFull: "9999px",
  },
  elevation: {
    level0: "none",
    level1: "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
    level2: "0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)",
    level3: "0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)",
  },
} as const;

// ─── Configuration ──────────────────────────────────────────────
const FRAME_COUNT = 142;
const TARGET_FPS = 30;
const CDN_BASE_URL =
  "https://storage.googleapis.com/uphill-assets-cdn-v17/frames";

interface GavelHeroProps {
  /** Callback fired when the boot button is clicked */
  onBootClick?: () => void;
  /** Override CDN base URL for frame assets */
  cdnBaseUrl?: string;
  /** Total number of animation frames */
  frameCount?: number;
}

export const GavelHero: React.FC<GavelHeroProps> = ({
  onBootClick,
  cdnBaseUrl = CDN_BASE_URL,
  frameCount = FRAME_COUNT,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [loaded, setLoaded] = useState(false);
  const [loadProgress, setLoadProgress] = useState(0);
  const animationRef = useRef<number>(0);
  const frameIndexRef = useRef(0);

  // Preload all frames
  const preloadFrames = useCallback((): HTMLImageElement[] => {
    const images: HTMLImageElement[] = [];
    let loadedCount = 0;

    for (let i = 1; i <= frameCount; i++) {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.src = `${cdnBaseUrl}/frame_${String(i).padStart(4, "0")}.webp`;
      img.onload = () => {
        loadedCount++;
        setLoadProgress(Math.floor((loadedCount / frameCount) * 100));
        if (loadedCount === frameCount) {
          setLoaded(true);
        }
      };
      img.onerror = () => {
        loadedCount++;
        setLoadProgress(Math.floor((loadedCount / frameCount) * 100));
      };
      images.push(img);
    }

    return images;
  }, [cdnBaseUrl, frameCount]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const images = preloadFrames();

    const render = () => {
      const img = images[frameIndexRef.current];
      if (img.complete && img.naturalWidth > 0) {
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        ctx.drawImage(img, 0, 0);
      }
      frameIndexRef.current =
        (frameIndexRef.current + 1) % frameCount;
      animationRef.current = window.setTimeout(() => {
        requestAnimationFrame(render);
      }, 1000 / TARGET_FPS);
    };

    render();

    return () => {
      window.clearTimeout(animationRef.current);
    };
  }, [frameCount, preloadFrames]);

  return (
    <div
      style={{
        backgroundColor: M3_TOKENS.colors.surface,
        fontFamily: M3_TOKENS.typography.bodyLarge,
        position: "relative",
        width: "100%",
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        overflow: "hidden",
      }}
    >
      {/* Loading overlay */}
      {!loaded && (
        <div
          style={{
            position: "absolute",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "16px",
            zIndex: 10,
          }}
        >
          <div
            style={{
              color: M3_TOKENS.colors.onSurface,
              fontFamily: M3_TOKENS.typography.displayLarge,
              fontSize: "1.5rem",
              fontWeight: 300,
              letterSpacing: "0.02em",
            }}
          >
            Loading V17 Hyper-Core
          </div>

          {/* Progress bar */}
          <div
            style={{
              width: "200px",
              height: "4px",
              backgroundColor: M3_TOKENS.colors.surfaceVariant,
              borderRadius: M3_TOKENS.shapes.cornerFull,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${loadProgress}%`,
                height: "100%",
                backgroundColor: M3_TOKENS.colors.primary,
                borderRadius: M3_TOKENS.shapes.cornerFull,
                transition: "width 0.3s ease-out",
              }}
            />
          </div>

          <div
            style={{
              color: M3_TOKENS.colors.outline,
              fontFamily: M3_TOKENS.typography.labelLarge,
              fontSize: "0.75rem",
            }}
          >
            {loadProgress}%
          </div>
        </div>
      )}

      {/* Canvas */}
      <canvas
        ref={canvasRef}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: loaded ? 1 : 0,
          transition: "opacity 1s ease-in-out",
        }}
      />

      {/* Boot CTA */}
      <button
        type="button"
        onClick={onBootClick}
        style={{
          position: "absolute",
          bottom: "40px",
          padding: "12px 32px",
          backgroundColor: M3_TOKENS.colors.primary,
          color: M3_TOKENS.colors.onPrimary,
          border: "none",
          borderRadius: M3_TOKENS.shapes.cornerFull,
          fontFamily: M3_TOKENS.typography.labelLarge,
          fontSize: "0.875rem",
          fontWeight: 500,
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          cursor: "pointer",
          boxShadow: M3_TOKENS.elevation.level2,
          transition: "all 0.2s ease-in-out",
          opacity: loaded ? 1 : 0,
        }}
        onMouseEnter={(e) => {
          (e.target as HTMLButtonElement).style.boxShadow =
            M3_TOKENS.elevation.level3;
          (e.target as HTMLButtonElement).style.transform = "translateY(-2px)";
        }}
        onMouseLeave={(e) => {
          (e.target as HTMLButtonElement).style.boxShadow =
            M3_TOKENS.elevation.level2;
          (e.target as HTMLButtonElement).style.transform = "translateY(0)";
        }}
      >
        Execute Hyper-Boot
      </button>
    </div>
  );
};

export default GavelHero;
