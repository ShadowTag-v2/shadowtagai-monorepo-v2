'use client';

import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { useCallback, useEffect, useRef, useState } from 'react';

/* ── Design Token Constants (aligned with globals.css Sovereign Architect) ── */
const T = {
  ink: '#071325',
  inkLight: '#0a1a30',
  gold: '#e6c487',
  goldContainer: '#c9a96e',
  goldOn: '#412d00',
  blue: '#aac7ff',
  lavender: '#b8c8f2',
  primaryText: '#d7e3fc',
  secondaryText: '#d0c5b5',
  outline: '#998f81',
  surfaceHigh: '#1f2a3d',
} as const;

/* ── Kinetic Shield Geometry (SVG paths) ── */
const SHIELD_PATH = 'M50 2 C50 2 95 20 95 55 C95 80 75 98 50 98 C25 98 5 80 5 55 C5 20 50 2 50 2Z';

/* ── Particle System ── */
interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  opacity: number;
  speed: number;
  angle: number;
}

function generateParticles(count: number): Particle[] {
  return Array.from({ length: count }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 2 + 1,
    opacity: Math.random() * 0.4 + 0.1,
    speed: Math.random() * 20 + 10,
    angle: Math.random() * 360,
  }));
}

/* ── Typing Effect ── */
function useTypingEffect(text: string, speed = 40, delay = 800) {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    let i = 0;
    const timeout = setTimeout(() => {
      const interval = setInterval(() => {
        if (i < text.length) {
          setDisplayedText(text.slice(0, i + 1));
          i++;
        } else {
          clearInterval(interval);
          setIsComplete(true);
        }
      }, speed);
      return () => clearInterval(interval);
    }, delay);
    return () => clearTimeout(timeout);
  }, [text, speed, delay]);

  return { displayedText, isComplete };
}

/* ── Component ── */
interface KineticHeroProps {
  onOpenModal?: () => void;
}

export default function KineticHero({ onOpenModal }: KineticHeroProps) {
  const containerRef = useRef<HTMLElement>(null);
  const [particles] = useState(() => generateParticles(40));
  const [mounted, setMounted] = useState(false);

  // Mouse tracking for parallax
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springConfig = { stiffness: 50, damping: 30, mass: 1 };
  const smoothX = useSpring(mouseX, springConfig);
  const smoothY = useSpring(mouseY, springConfig);

  // Parallax transforms
  const shieldRotateX = useTransform(smoothY, [-0.5, 0.5], [8, -8]);
  const shieldRotateY = useTransform(smoothX, [-0.5, 0.5], [-8, 8]);
  const particleShiftX = useTransform(smoothX, [-0.5, 0.5], [-20, 20]);
  const particleShiftY = useTransform(smoothY, [-0.5, 0.5], [-20, 20]);
  const textShiftX = useTransform(smoothX, [-0.5, 0.5], [-5, 5]);
  const textShiftY = useTransform(smoothY, [-0.5, 0.5], [-5, 5]);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLElement>) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      mouseX.set(x);
      mouseY.set(y);
    },
    [mouseX, mouseY],
  );

  useEffect(() => setMounted(true), []);

  const { displayedText: typedTagline, isComplete: taglineComplete } = useTypingEffect(
    'Privilege-Protected Infrastructure',
    35,
    1200,
  );

  /* ── Stagger animation variants ── */
  const containerVariants = {
    hidden: {},
    visible: {
      transition: { staggerChildren: 0.12, delayChildren: 0.3 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30, filter: 'blur(8px)' },
    visible: {
      opacity: 1,
      y: 0,
      filter: 'blur(0px)',
      transition: { duration: 0.8, ease: [0.25, 0.4, 0.25, 1] as const },
    },
  };

  return (
    // biome-ignore lint/a11y/noStaticElementInteractions: onMouseMove is decorative parallax, not user interaction
    <header
      ref={containerRef}
      onMouseMove={handleMouseMove}
      style={{
        position: 'relative',
        minHeight: '100dvh',
        display: 'flex',
        alignItems: 'center',
        overflow: 'hidden',
        background: `linear-gradient(170deg, ${T.ink} 0%, ${T.inkLight} 40%, ${T.ink} 100%)`,
      }}
      id="hero"
    >
      {/* ── Layer 0: Radial Gradient Atmosphere ── */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `
            radial-gradient(ellipse 80% 60% at 70% 40%, rgba(230, 196, 135, 0.04) 0%, transparent 60%),
            radial-gradient(ellipse 60% 80% at 20% 60%, rgba(170, 199, 255, 0.03) 0%, transparent 60%)
          `,
          pointerEvents: 'none',
        }}
      />

      {/* ── Layer 1: Particle Field ── */}
      {mounted && (
        <motion.div
          style={{
            position: 'absolute',
            inset: 0,
            x: particleShiftX,
            y: particleShiftY,
            pointerEvents: 'none',
          }}
        >
          {particles.map((p) => (
            <motion.div
              key={p.id}
              style={{
                position: 'absolute',
                left: `${p.x}%`,
                top: `${p.y}%`,
                width: p.size,
                height: p.size,
                borderRadius: '50%',
                backgroundColor: p.id % 3 === 0 ? T.gold : T.blue,
                opacity: p.opacity,
              }}
              animate={{
                y: [0, -30, 0],
                opacity: [p.opacity, p.opacity * 1.5, p.opacity],
              }}
              transition={{
                duration: p.speed,
                repeat: Infinity,
                ease: 'easeInOut',
                delay: p.id * 0.1,
              }}
            />
          ))}
        </motion.div>
      )}

      {/* ── Layer 2: Kinetic Shield (3D Parallax) ── */}
      <motion.div
        style={{
          position: 'absolute',
          right: '8%',
          top: '50%',
          translateY: '-50%',
          width: 320,
          height: 380,
          rotateX: shieldRotateX,
          rotateY: shieldRotateY,
          perspective: 1000,
          pointerEvents: 'none',
        }}
      >
        {/* Outer glow */}
        <motion.div
          style={{
            position: 'absolute',
            inset: -60,
            borderRadius: '50%',
            background: `radial-gradient(circle, rgba(230, 196, 135, 0.06), transparent 70%)`,
          }}
          animate={{ scale: [1, 1.08, 1], opacity: [0.5, 0.8, 0.5] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Shield SVG */}
        <svg
          viewBox="0 0 100 100"
          role="img"
          aria-label="Protective shield emblem"
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
          }}
        >
          {/* Outer shield */}
          <motion.path
            d={SHIELD_PATH}
            fill="none"
            stroke={T.gold}
            strokeWidth={0.5}
            strokeOpacity={0.2}
            animate={{ strokeOpacity: [0.15, 0.3, 0.15] }}
            transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
          />
          {/* Inner shield */}
          <motion.path
            d={SHIELD_PATH}
            fill="none"
            stroke={T.blue}
            strokeWidth={0.3}
            strokeOpacity={0.1}
            style={{ transform: 'scale(0.85)', transformOrigin: 'center' }}
            animate={{ strokeOpacity: [0.08, 0.18, 0.08] }}
            transition={{
              duration: 3.5,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 0.5,
            }}
          />
          {/* Lock icon in center */}
          <motion.g
            style={{ transformOrigin: 'center' }}
            animate={{ scale: [1, 1.03, 1] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          >
            <rect
              x="40"
              y="48"
              width="20"
              height="16"
              rx="2"
              fill="none"
              stroke={T.gold}
              strokeWidth="0.8"
              opacity={0.25}
            />
            <path
              d="M44 48 L44 42 C44 38 56 38 56 42 L56 48"
              fill="none"
              stroke={T.gold}
              strokeWidth="0.8"
              opacity={0.25}
            />
            <circle cx="50" cy="55" r="2" fill={T.gold} opacity={0.3} />
          </motion.g>
        </svg>

        {/* Orbiting ring */}
        <motion.div
          style={{
            position: 'absolute',
            inset: -20,
            border: `1px solid rgba(230, 196, 135, 0.06)`,
            borderRadius: '50%',
          }}
          animate={{ rotate: 360 }}
          transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
        />
      </motion.div>

      {/* ── Layer 2.5: Grain Texture ── */}
      <div className="hero-grain" />

      {/* ── Layer 3: Content ── */}
      <motion.div
        style={{
          position: 'relative',
          zIndex: 10,
          maxWidth: 1140,
          margin: '0 auto',
          padding: '6rem 1rem 4rem',
          x: textShiftX,
          y: textShiftY,
        }}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Typing tagline */}
        <motion.div
          variants={itemVariants}
          style={{
            fontSize: '0.6875rem',
            fontWeight: 500,
            textTransform: 'uppercase' as const,
            letterSpacing: '0.15em',
            color: T.gold,
            marginBottom: '1.5rem',
            fontFamily: "'Inter', system-ui, sans-serif",
            minHeight: '1rem',
          }}
        >
          {typedTagline}
          {!taglineComplete && (
            <motion.span
              animate={{ opacity: [1, 0] }}
              transition={{ duration: 0.6, repeat: Infinity }}
              style={{ color: T.gold }}
            >
              |
            </motion.span>
          )}
          {taglineComplete && (
            <span style={{ color: T.outline, marginLeft: 8 }}>
              · ATTORNEY-MONITORED · HEPPNER-COMPLIANT
            </span>
          )}
        </motion.div>

        {/* Headline */}
        <motion.h1
          variants={itemVariants}
          style={{
            fontSize: 'clamp(1.75rem, 5vw, 3.5rem)',
            fontWeight: 800,
            lineHeight: 1.05,
            letterSpacing: '-0.02em',
            maxWidth: 800,
            marginBottom: '1.5rem',
            color: T.primaryText,
            fontFamily: "'Inter', system-ui, sans-serif",
          }}
        >
          Shield Your Client&apos;s Research
          <br />
          <motion.span
            style={{ color: T.gold }}
            animate={{
              textShadow: [
                '0 0 0px rgba(230, 196, 135, 0)',
                '0 0 20px rgba(230, 196, 135, 0.15)',
                '0 0 0px rgba(230, 196, 135, 0)',
              ],
            }}
            transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
          >
            From Discovery.
          </motion.span>
        </motion.h1>

        {/* Subheadline */}
        <motion.h2
          variants={itemVariants}
          style={{
            fontSize: 'clamp(1rem, 2.5vw, 1.5rem)',
            fontWeight: 600,
            color: T.secondaryText,
            maxWidth: 700,
            marginBottom: '1.5rem',
            lineHeight: 1.4,
            fontFamily: "'Inter', system-ui, sans-serif",
          }}
        >
          Deploy privileged search infrastructure your clients use under your oversight&mdash;so
          opposing counsel discovers nothing.
        </motion.h2>

        {/* Body copy */}
        <motion.p
          variants={itemVariants}
          style={{
            fontSize: '0.9375rem',
            lineHeight: 1.6,
            color: T.secondaryText,
            maxWidth: 640,
            marginBottom: '1rem',
            fontFamily: "'Inter', system-ui, sans-serif",
          }}
        >
          After <em>In re Heppner</em> (S.D.N.Y., Feb. 2026), every web search and AI conversation
          your client conducts outside your firm&apos;s umbrella is fair game for opposing counsel.
          KovelAI is the turnkey infrastructure you deploy to close that gap.
        </motion.p>

        <motion.p
          variants={itemVariants}
          style={{
            fontSize: '0.9375rem',
            lineHeight: 1.6,
            color: T.secondaryText,
            maxWidth: 640,
            marginBottom: '2rem',
            fontFamily: "'Inter', system-ui, sans-serif",
          }}
        >
          Your clients search at will under your privilege umbrella. You monitor every session,
          deliver the first legal opinion, and bill their credit card automatically.{' '}
          <strong style={{ color: T.primaryText }}>
            &ldquo;Either you do it through our firm&apos;s KovelAI, or proceed at your
            peril.&rdquo;
          </strong>
        </motion.p>

        {/* CTAs */}
        <motion.div
          variants={itemVariants}
          style={{ display: 'flex', flexWrap: 'wrap' as const, gap: '1rem', marginBottom: '1rem' }}
        >
          <motion.button
            type="button"
            onClick={onOpenModal}
            className="btn-gold"
            id="ctaFreeTrial"
            style={{ fontSize: '0.875rem' }}
            whileHover={{ scale: 1.03, boxShadow: '0 0 40px rgba(230, 196, 135, 0.3)' }}
            whileTap={{ scale: 0.98 }}
          >
            Deploy Your Firm&apos;s Portal
          </motion.button>
          <motion.a
            href="#how-it-works"
            className="btn-ghost"
            style={{ fontSize: '0.875rem' }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            See How Privilege Works →
          </motion.a>
        </motion.div>

        {/* Micro-copy */}
        <motion.p
          variants={itemVariants}
          style={{
            fontSize: '0.75rem',
            color: T.outline,
            fontFamily: "'Inter', system-ui, sans-serif",
          }}
        >
          Clients log in · You monitor all sessions · You give the first opinion · Automatic billing
          · Opposing counsel gets nothing
        </motion.p>
      </motion.div>

      {/* ── Layer 4: Bottom Fade ── */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 160,
          background: `linear-gradient(to top, ${T.ink}, transparent)`,
          pointerEvents: 'none',
        }}
      />

      {/* Hide shield on mobile via media query */}
      <style>{`
        @media (max-width: 768px) {
          [style*="right: 8%"][style*="width: 320"] {
            display: none !important;
          }
        }
      `}</style>
    </header>
  );
}
