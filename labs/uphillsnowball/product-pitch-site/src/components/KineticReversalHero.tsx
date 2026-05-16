'use client';

import React, { useEffect, useRef, useMemo } from 'react';
import { motion, useMotionValue, useTransform, animate } from 'framer-motion';

/**
 * KineticReversalHero — "Physics-Defying Compounding Momentum"
 *
 * A heavy, frosted-glass sphere rolling UPWARD along a sharp, glowing
 * diagonal vector line, absorbing floating data nodes as it ascends.
 * The sphere compounds mass and emits light — the visual metaphor for
 * reverse-entropy, the Uphill Snowball.
 *
 * Design tokens: atmospheric-glass dark mode (#rrggbb strict).
 * Animation: Framer Motion physics with spring dynamics.
 */

/* ── Design Tokens (atmospheric-glass dark mode, strict #rrggbb) ── */
const TOKENS = {
  /* Surfaces */
  bgPrimary: '#050508',
  bgGradientStart: '#050508',
  bgGradientEnd: '#0A0E1A',
  surfaceGlass: 'rgba(255, 255, 255, 0.04)',
  surfaceGlassHover: 'rgba(255, 255, 255, 0.08)',

  /* Vector line */
  vectorGlow: '#00E5FF',
  vectorGlowDim: '#004D56',
  vectorLine: '#003840',

  /* Sphere */
  sphereCore: '#0D1B2A',
  sphereFrost: 'rgba(0, 229, 255, 0.12)',
  sphereGlow: '#00BCD4',
  sphereInnerGlow: 'rgba(0, 188, 212, 0.25)',
  sphereRim: 'rgba(0, 229, 255, 0.35)',

  /* Data particles */
  particlePrimary: '#00E5FF',
  particleSecondary: '#7C4DFF',
  particleTertiary: '#FFD600',
  particleDim: 'rgba(0, 229, 255, 0.3)',

  /* Text */
  textPrimary: '#FFFFFF',
  textSecondary: '#8B949E',
  textAccent: '#00E5FF',

  /* Emission */
  emissionPulse: 'rgba(0, 229, 255, 0.15)',
} as const;

/* ── Data particle config ── */
interface DataNode {
  id: number;
  x: number;        // % from left
  y: number;        // % from top
  size: number;     // px
  color: string;
  delay: number;    // animation delay in seconds
  label: string;
}

const DATA_NODES: DataNode[] = [
  { id: 1, x: 15, y: 25, size: 8, color: TOKENS.particlePrimary, delay: 0,   label: 'ML' },
  { id: 2, x: 25, y: 60, size: 6, color: TOKENS.particleSecondary, delay: 0.3, label: 'NLP' },
  { id: 3, x: 70, y: 15, size: 10, color: TOKENS.particleTertiary, delay: 0.6, label: 'RAG' },
  { id: 4, x: 80, y: 45, size: 7, color: TOKENS.particlePrimary, delay: 0.9, label: 'LLM' },
  { id: 5, x: 35, y: 80, size: 9, color: TOKENS.particleSecondary, delay: 1.2, label: 'AGI' },
  { id: 6, x: 60, y: 70, size: 5, color: TOKENS.particleTertiary, delay: 1.5, label: 'MCP' },
  { id: 7, x: 45, y: 35, size: 8, color: TOKENS.particlePrimary, delay: 1.8, label: 'A2A' },
  { id: 8, x: 90, y: 25, size: 6, color: TOKENS.particleSecondary, delay: 2.1, label: 'SK' },
  { id: 9, x: 10, y: 50, size: 7, color: TOKENS.particleTertiary, delay: 2.4, label: 'ADK' },
  { id: 10, x: 55, y: 90, size: 9, color: TOKENS.particlePrimary, delay: 2.7, label: 'VEO' },
  { id: 11, x: 78, y: 75, size: 5, color: TOKENS.particleSecondary, delay: 3.0, label: 'GEN' },
  { id: 12, x: 42, y: 12, size: 8, color: TOKENS.particleTertiary, delay: 3.3, label: 'SRE' },
];

/* ── Floating Data Particle ── */
const FloatingParticle: React.FC<{ node: DataNode; sphereProgress: number }> = ({
  node,
  sphereProgress,
}) => {
  // As the sphere ascends (progress 0→1), particles drift toward the diagonal center
  const attractX = 50 + (50 - node.x) * sphereProgress * 0.6;
  const attractY = 50 + (50 - node.y) * sphereProgress * 0.4;
  const opacity = 1 - sphereProgress * 0.7;
  const scale = 1 - sphereProgress * 0.5;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{
        opacity: [0, opacity, opacity * 0.6, opacity],
        scale: [0, scale, scale * 0.8, scale],
        x: `${attractX - node.x}%`,
        y: `${attractY - node.y}%`,
      }}
      transition={{
        duration: 4,
        delay: node.delay,
        repeat: Infinity,
        repeatType: 'reverse',
        ease: 'easeInOut',
      }}
      style={{
        position: 'absolute',
        left: `${node.x}%`,
        top: `${node.y}%`,
        width: node.size * 2,
        height: node.size * 2,
        borderRadius: '50%',
        background: `radial-gradient(circle, ${node.color} 0%, transparent 70%)`,
        boxShadow: `0 0 ${node.size * 3}px ${node.color}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        pointerEvents: 'none',
        zIndex: 2,
      }}
    >
      <span
        style={{
          fontSize: 8,
          fontFamily: "'JetBrains Mono', 'SF Mono', monospace",
          color: TOKENS.textPrimary,
          opacity: 0.7,
          letterSpacing: '0.5px',
          userSelect: 'none',
        }}
      >
        {node.label}
      </span>
    </motion.div>
  );
};

/* ── The Sphere ── */
const FrostedSphere: React.FC<{ progress: number }> = ({ progress }) => {
  // Sphere starts bottom-right, ascends to top-left along the diagonal
  // progress: 0 = bottom-right, 1 = top-left
  const x = 70 - progress * 55; // 70% → 15%
  const y = 75 - progress * 60; // 75% → 15%
  const sphereSize = 80 + progress * 40; // grows as it absorbs data
  const glowIntensity = 0.3 + progress * 0.5;

  return (
    <motion.div
      style={{
        position: 'absolute',
        left: `${x}%`,
        top: `${y}%`,
        transform: 'translate(-50%, -50%)',
        width: sphereSize,
        height: sphereSize,
        borderRadius: '50%',
        zIndex: 10,
      }}
    >
      {/* Outer glow pulse */}
      <motion.div
        animate={{
          scale: [1, 1.3, 1],
          opacity: [glowIntensity * 0.3, glowIntensity * 0.1, glowIntensity * 0.3],
        }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          position: 'absolute',
          inset: -30,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${TOKENS.emissionPulse} 0%, transparent 70%)`,
        }}
      />

      {/* Main sphere body — frosted glass */}
      <div
        style={{
          width: '100%',
          height: '100%',
          borderRadius: '50%',
          background: `
            radial-gradient(
              ellipse 60% 50% at 35% 30%,
              ${TOKENS.sphereFrost} 0%,
              transparent 60%
            ),
            radial-gradient(
              circle at 50% 50%,
              ${TOKENS.sphereInnerGlow} 0%,
              ${TOKENS.sphereCore} 50%,
              #000000 100%
            )
          `,
          border: `1px solid ${TOKENS.sphereRim}`,
          boxShadow: `
            0 0 ${40 * glowIntensity}px ${TOKENS.sphereGlow},
            inset 0 0 ${20 * glowIntensity}px ${TOKENS.sphereInnerGlow},
            0 8px 32px rgba(0, 0, 0, 0.6)
          `,
          backdropFilter: 'blur(20px)',
        }}
      />

      {/* Specular highlight */}
      <div
        style={{
          position: 'absolute',
          top: '12%',
          left: '20%',
          width: '35%',
          height: '20%',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 100%)',
          filter: 'blur(4px)',
        }}
      />
    </motion.div>
  );
};

/* ── The Diagonal Vector Line ── */
const VectorLine: React.FC<{ progress: number }> = ({ progress }) => {
  const glowWidth = 2 + progress * 2;

  return (
    <svg
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        zIndex: 1,
      }}
    >
      <defs>
        <linearGradient id="vectorGradient" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={TOKENS.vectorGlowDim} stopOpacity={0.2} />
          <stop offset={`${progress * 100}%`} stopColor={TOKENS.vectorGlow} stopOpacity={0.8} />
          <stop offset="100%" stopColor={TOKENS.vectorGlowDim} stopOpacity={0.1} />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="1.5" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Base line (dim) */}
      <line
        x1="85" y1="90" x2="15" y2="10"
        stroke={TOKENS.vectorLine}
        strokeWidth="0.3"
        strokeDasharray="2 2"
      />

      {/* Active glow line */}
      <line
        x1="85" y1="90" x2="15" y2="10"
        stroke="url(#vectorGradient)"
        strokeWidth={glowWidth * 0.15}
        filter="url(#glow)"
        strokeLinecap="round"
      />

      {/* Progress marker arrow */}
      <polygon
        points={`${85 - progress * 70 - 1},${90 - progress * 80 - 1.5} ${85 - progress * 70 + 1.5},${90 - progress * 80} ${85 - progress * 70 - 1},${90 - progress * 80 + 1.5}`}
        fill={TOKENS.vectorGlow}
        opacity={0.8}
      />
    </svg>
  );
};

/* ── Main Hero Component ── */
export default function KineticReversalHero() {
  const progress = useMotionValue(0);
  const [progressValue, setProgressValue] = React.useState(0);

  useEffect(() => {
    // Animate sphere ascent on a 6-second loop
    const controls = animate(progress, 1, {
      duration: 6,
      ease: [0.25, 0.46, 0.45, 0.94], // custom easeOutQuad
      repeat: Infinity,
      repeatType: 'reverse',
      repeatDelay: 1,
      onUpdate: (v) => setProgressValue(v),
    });

    return () => controls.stop();
  }, [progress]);

  return (
    <section
      id="kinetic-reversal-hero"
      style={{
        position: 'relative',
        width: '100%',
        minHeight: '100vh',
        overflow: 'hidden',
        background: `linear-gradient(170deg, ${TOKENS.bgGradientStart} 0%, ${TOKENS.bgGradientEnd} 100%)`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Background grid pattern */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `
            linear-gradient(${TOKENS.vectorLine} 1px, transparent 1px),
            linear-gradient(90deg, ${TOKENS.vectorLine} 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
          opacity: 0.15,
          maskImage: 'radial-gradient(ellipse 70% 60% at 50% 50%, black, transparent)',
        }}
      />

      {/* The animation stage */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: 900,
          aspectRatio: '16 / 9',
          margin: '0 auto',
        }}
      >
        <VectorLine progress={progressValue} />

        {DATA_NODES.map((node) => (
          <FloatingParticle
            key={node.id}
            node={node}
            sphereProgress={progressValue}
          />
        ))}

        <FrostedSphere progress={progressValue} />
      </div>

      {/* Text overlay */}
      <div
        style={{
          position: 'absolute',
          bottom: '12%',
          left: '50%',
          transform: 'translateX(-50%)',
          textAlign: 'center',
          zIndex: 20,
          maxWidth: 640,
          padding: '0 24px',
        }}
      >
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.5 }}
          style={{
            fontFamily: "'Inter', 'SF Pro Display', -apple-system, sans-serif",
            fontSize: 'clamp(2rem, 5vw, 3.5rem)',
            fontWeight: 800,
            letterSpacing: '-0.03em',
            lineHeight: 1.1,
            color: TOKENS.textPrimary,
            margin: 0,
          }}
        >
          Reverse{' '}
          <span style={{ color: TOKENS.textAccent }}>Entropy</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.8 }}
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 'clamp(0.9rem, 2vw, 1.15rem)',
            color: TOKENS.textSecondary,
            lineHeight: 1.6,
            marginTop: 16,
            maxWidth: 480,
            marginLeft: 'auto',
            marginRight: 'auto',
          }}
        >
          Physics-defying compounding momentum.
          Every data point absorbed makes the next acquisition inevitable.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.2 }}
          style={{ marginTop: 28 }}
        >
          <button
            type="button"
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 14,
              fontWeight: 600,
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              padding: '14px 36px',
              borderRadius: 8,
              border: `1px solid ${TOKENS.vectorGlow}`,
              background: 'rgba(0, 229, 255, 0.08)',
              color: TOKENS.textAccent,
              cursor: 'pointer',
              backdropFilter: 'blur(12px)',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(0, 229, 255, 0.18)';
              e.currentTarget.style.boxShadow = `0 0 24px ${TOKENS.emissionPulse}`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(0, 229, 255, 0.08)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            Enter the Engine
          </button>
        </motion.div>
      </div>

      {/* Top-left brand mark */}
      <div
        style={{
          position: 'absolute',
          top: 32,
          left: 32,
          zIndex: 20,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
        }}
      >
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: '50%',
            border: `1.5px solid ${TOKENS.vectorGlow}`,
            background: 'rgba(0, 229, 255, 0.06)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: TOKENS.vectorGlow,
              boxShadow: `0 0 8px ${TOKENS.vectorGlow}`,
            }}
          />
        </div>
        <span
          style={{
            fontFamily: "'JetBrains Mono', 'SF Mono', monospace",
            fontSize: 13,
            fontWeight: 500,
            color: TOKENS.textSecondary,
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
          }}
        >
          Uphill Snowball
        </span>
      </div>
    </section>
  );
}
