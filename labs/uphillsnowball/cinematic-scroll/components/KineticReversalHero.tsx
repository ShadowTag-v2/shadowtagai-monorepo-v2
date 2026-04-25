'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion, useAnimation, useMotionValue, useTransform, AnimatePresence } from 'framer-motion';

/**
 * KineticReversalHero — "Physics-Defying Compounding Momentum"
 *
 * Concept: A heavy, frosted-glass sphere rolling UPWARD along a sharp,
 * glowing diagonal vector line. As it ascends against gravity, it magnetically
 * absorbs floating geometric data particles, compounding its mass and
 * emitting light. This is reverse-entropy, antigravity incarnate.
 *
 * Architecture:
 * - Canvas layer: Diagonal glowing vector line (SVG)
 * - Sphere: Frosted glass with bloom, rolls upward via Framer Motion spring physics
 * - Data nodes: Floating geometric particles that get absorbed into the sphere
 * - Headline overlay: Text floating above the animation
 *
 * Design tokens: Dark mode strict #rrggbb values
 * TACSOP 7 compliant: No generate_image — pure CSS/SVG/Framer
 */

/* ── STRICT HEX TOKENS (dark mode) ── */
const C = {
  void:           '#0A0A0F',
  surfaceDim:     '#0D1117',
  surfaceCard:    '#101621',
  surfaceHigh:    '#1A1F2E',
  glowCyan:       '#00BCD4',
  glowCyanDim:    '#006064',
  glowPurple:     '#7C4DFF',
  glowPurpleDim:  '#311B92',
  glowBlue:       '#4285F4',
  white:          '#FFFFFF',
  whiteGhost:     '#8B949E',
  silverElevated: '#C9D1D9',
  sphereGlass:    '#1A2332',
  sphereBorder:   '#2A3A4E',
} as const;

/* ── DATA NODES — positions, sizes, delays for floating particles ── */
interface DataNode {
  id: number;
  x: number;       // % from left
  y: number;       // % from top
  size: number;    // px
  color: string;
  delay: number;   // seconds
  shape: 'hex' | 'circle' | 'diamond';
}

const DATA_NODES: DataNode[] = [
  { id: 1,  x: 15, y: 70, size: 12, color: C.glowCyan,   delay: 0,    shape: 'hex' },
  { id: 2,  x: 25, y: 55, size: 8,  color: C.glowBlue,   delay: 0.3,  shape: 'circle' },
  { id: 3,  x: 35, y: 80, size: 10, color: C.glowPurple,  delay: 0.6,  shape: 'diamond' },
  { id: 4,  x: 45, y: 40, size: 14, color: C.glowCyan,   delay: 0.9,  shape: 'hex' },
  { id: 5,  x: 55, y: 65, size: 9,  color: C.glowBlue,   delay: 1.2,  shape: 'circle' },
  { id: 6,  x: 65, y: 35, size: 11, color: C.glowPurple,  delay: 1.5,  shape: 'diamond' },
  { id: 7,  x: 72, y: 50, size: 7,  color: C.glowCyan,   delay: 1.8,  shape: 'hex' },
  { id: 8,  x: 82, y: 75, size: 13, color: C.glowBlue,   delay: 2.1,  shape: 'circle' },
  { id: 9,  x: 40, y: 25, size: 10, color: C.glowPurple,  delay: 2.4,  shape: 'diamond' },
  { id: 10, x: 60, y: 85, size: 8,  color: C.glowCyan,   delay: 2.7,  shape: 'hex' },
  { id: 11, x: 20, y: 30, size: 11, color: C.glowBlue,   delay: 3.0,  shape: 'circle' },
  { id: 12, x: 80, y: 20, size: 9,  color: C.glowPurple,  delay: 3.3,  shape: 'diamond' },
];

/* ── SHAPE RENDERERS ── */
function NodeShape({ shape, size, color }: { shape: DataNode['shape']; size: number; color: string }) {
  if (shape === 'hex') {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill={color} opacity={0.7}>
        <polygon points="12,2 22,8.5 22,15.5 12,22 2,15.5 2,8.5" />
      </svg>
    );
  }
  if (shape === 'diamond') {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill={color} opacity={0.7}>
        <polygon points="12,2 22,12 12,22 2,12" />
      </svg>
    );
  }
  return (
    <div style={{
      width: size,
      height: size,
      borderRadius: '50%',
      backgroundColor: color,
      opacity: 0.7,
    }} />
  );
}

/* ── MAIN COMPONENT ── */
interface KineticReversalHeroProps {
  headline?: string;
  subheadline?: string;
}

export function KineticReversalHero({
  headline = 'Uphill Snowball',
  subheadline = 'Physics-defying compounding momentum. Reverse-entropy intelligence that grows stronger with every iteration.',
}: KineticReversalHeroProps) {
  const [absorbed, setAbsorbed] = useState<Set<number>>(new Set());
  const [sphereScale, setSphereScale] = useState(1);
  const sphereControls = useAnimation();
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sphere ascent animation — rolls upward along the diagonal
  useEffect(() => {
    sphereControls.start({
      x: [0, 80, 160, 240, 320],
      y: [0, -60, -120, -180, -240],
      rotate: [0, -45, -90, -135, -180],
      transition: {
        duration: 8,
        ease: 'easeInOut',
        repeat: Infinity,
        repeatType: 'reverse' as const,
      },
    });

    // Sequentially absorb data nodes
    const absorb = (index: number) => {
      if (index >= DATA_NODES.length) {
        // Reset after all absorbed
        timerRef.current = setTimeout(() => {
          setAbsorbed(new Set());
          setSphereScale(1);
          absorb(0);
        }, 3000);
        return;
      }
      timerRef.current = setTimeout(() => {
        setAbsorbed((prev) => new Set([...prev, DATA_NODES[index].id]));
        setSphereScale((s) => Math.min(s + 0.06, 1.8));
        absorb(index + 1);
      }, DATA_NODES[index].delay * 1000 + 400);
    };
    absorb(0);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [sphereControls]);

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: '100vh',
        overflow: 'hidden',
        backgroundColor: C.void,
        fontFamily: "'Inter', system-ui, sans-serif",
      }}
      id="kinetic-reversal-hero"
    >
      {/* ── DIAGONAL VECTOR LINE (SVG) ── */}
      <svg
        style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', zIndex: 1 }}
        viewBox="0 0 1440 900"
        preserveAspectRatio="none"
      >
        <defs>
          <linearGradient id="vecGrad" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={C.glowCyanDim} stopOpacity={0} />
            <stop offset="30%" stopColor={C.glowCyan} stopOpacity={0.4} />
            <stop offset="70%" stopColor={C.glowPurple} stopOpacity={0.3} />
            <stop offset="100%" stopColor={C.glowPurpleDim} stopOpacity={0} />
          </linearGradient>
          <filter id="lineGlow">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          {/* Sphere frosted glass filter */}
          <filter id="sphereGlass">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2" />
          </filter>
          <radialGradient id="sphereGrad" cx="35%" cy="35%" r="65%">
            <stop offset="0%" stopColor={C.surfaceHigh} stopOpacity={0.9} />
            <stop offset="40%" stopColor={C.sphereGlass} stopOpacity={0.7} />
            <stop offset="100%" stopColor={C.surfaceDim} stopOpacity={0.5} />
          </radialGradient>
        </defs>

        {/* The sharp diagonal vector line */}
        <line
          x1="100"  y1="800"
          x2="1340" y2="100"
          stroke="url(#vecGrad)"
          strokeWidth="2"
          filter="url(#lineGlow)"
        />
        {/* Fainter parallel guides */}
        <line x1="80"  y1="820" x2="1320" y2="120" stroke={C.glowCyanDim} strokeWidth="0.5" opacity="0.15" />
        <line x1="120" y1="780" x2="1360" y2="80"  stroke={C.glowPurpleDim} strokeWidth="0.5" opacity="0.15" />
      </svg>

      {/* ── FLOATING DATA NODES ── */}
      <AnimatePresence>
        {DATA_NODES.map((node) => (
          !absorbed.has(node.id) && (
            <motion.div
              key={node.id}
              initial={{ opacity: 0, scale: 0 }}
              animate={{
                opacity: [0, 0.8, 0.6, 0.8],
                scale: [0, 1, 0.9, 1],
                y: [0, -8, 4, -4],
              }}
              exit={{
                opacity: 0,
                scale: 0,
                x: '40vw',
                y: '-20vh',
                transition: { duration: 0.8, ease: 'easeIn' },
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                repeatType: 'reverse',
                delay: node.delay,
              }}
              style={{
                position: 'absolute',
                left: `${node.x}%`,
                top: `${node.y}%`,
                zIndex: 2,
                pointerEvents: 'none',
              }}
            >
              <NodeShape shape={node.shape} size={node.size} color={node.color} />
            </motion.div>
          )
        ))}
      </AnimatePresence>

      {/* ── THE SPHERE — Frosted glass, rolling upward ── */}
      <motion.div
        animate={sphereControls}
        style={{
          position: 'absolute',
          left: 'calc(50% - 60px)',
          top: 'calc(50% + 40px)',
          zIndex: 5,
          width: 120,
          height: 120,
          borderRadius: '50%',
          background: `
            radial-gradient(circle at 35% 35%, 
              rgba(26, 35, 50, 0.95) 0%, 
              rgba(13, 17, 23, 0.8) 40%, 
              rgba(10, 10, 15, 0.6) 100%
            )
          `,
          border: `1px solid ${C.sphereBorder}`,
          backdropFilter: 'blur(8px)',
          WebkitBackdropFilter: 'blur(8px)',
          boxShadow: `
            0 0 ${20 + absorbed.size * 4}px rgba(0, 188, 212, ${0.15 + absorbed.size * 0.03}),
            0 0 ${40 + absorbed.size * 6}px rgba(124, 77, 255, ${0.08 + absorbed.size * 0.02}),
            inset 0 0 30px rgba(255, 255, 255, 0.05)
          `,
          transform: `scale(${sphereScale})`,
          transition: 'box-shadow 0.6s ease, transform 0.6s ease',
        }}
      >
        {/* Inner glass refraction highlight */}
        <div
          style={{
            position: 'absolute',
            top: '15%',
            left: '20%',
            width: '35%',
            height: '25%',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 100%)',
          }}
        />
        {/* Absorption counter */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: C.glowCyan,
            fontSize: 18,
            fontWeight: 800,
            fontFamily: "'JetBrains Mono', monospace",
            opacity: absorbed.size > 0 ? 0.7 : 0,
            transition: 'opacity 0.4s ease',
          }}
        >
          +{absorbed.size}
        </div>
      </motion.div>

      {/* ── CONTENT OVERLAY ── */}
      <div
        style={{
          position: 'relative',
          zIndex: 20,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          textAlign: 'center',
          padding: '0 24px',
          pointerEvents: 'none',
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2, delay: 0.4, ease: 'easeOut' }}
          style={{ pointerEvents: 'auto' }}
        >
          {/* Badge */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              backgroundColor: 'rgba(49, 27, 146, 0.3)',
              color: C.glowPurple,
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: '0.06em',
              padding: '6px 16px',
              borderRadius: 9999,
              marginBottom: 28,
              border: '1px solid rgba(124, 77, 255, 0.2)',
              textTransform: 'uppercase',
            }}
          >
            <span style={{ fontSize: 14 }}>◈</span>
            <span>REVERSE-ENTROPY ENGINE</span>
          </div>

          {/* Headline */}
          <h1
            style={{
              fontFamily: "'Inter', system-ui, sans-serif",
              fontSize: 72,
              fontWeight: 900,
              lineHeight: 1.05,
              letterSpacing: '-0.04em',
              color: C.white,
              margin: '0 0 20px',
            }}
          >
            {headline.split(' ').map((word, i) => (
              <React.Fragment key={i}>
                {i > 0 && <br />}
                <span
                  style={{
                    background: i === 1
                      ? `linear-gradient(135deg, ${C.glowCyan} 0%, ${C.glowPurple} 100%)`
                      : 'none',
                    WebkitBackgroundClip: i === 1 ? 'text' : undefined,
                    WebkitTextFillColor: i === 1 ? 'transparent' : undefined,
                  }}
                >
                  {word}
                </span>
              </React.Fragment>
            ))}
          </h1>

          {/* Subheadline */}
          <p
            style={{
              fontFamily: "'Inter', system-ui, sans-serif",
              fontSize: 18,
              fontWeight: 400,
              lineHeight: 1.6,
              color: C.whiteGhost,
              maxWidth: 560,
              margin: '0 auto 36px',
            }}
          >
            {subheadline}
          </p>

          {/* CTA */}
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
            <button
              style={{
                background: `linear-gradient(135deg, ${C.glowCyan} 0%, ${C.glowBlue} 100%)`,
                color: '#003238',
                border: 'none',
                borderRadius: 16,
                padding: '14px 36px',
                fontSize: 14,
                fontWeight: 700,
                letterSpacing: '0.02em',
                cursor: 'pointer',
                transition: 'transform 0.2s ease, box-shadow 0.2s ease',
              }}
            >
              Enter the Engine
            </button>
            <button
              style={{
                backgroundColor: 'transparent',
                color: C.glowPurple,
                border: `1px solid ${C.glowPurple}`,
                borderRadius: 16,
                padding: '14px 36px',
                fontSize: 14,
                fontWeight: 600,
                letterSpacing: '0.02em',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              View Architecture
            </button>
          </div>
        </motion.div>
      </div>

      {/* ── AMBIENT GLOW LAYERS ── */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '40%',
          background: `linear-gradient(0deg, ${C.void} 0%, transparent 100%)`,
          zIndex: 15,
          pointerEvents: 'none',
        }}
        aria-hidden="true"
      />
    </div>
  );
}

export default KineticReversalHero;
