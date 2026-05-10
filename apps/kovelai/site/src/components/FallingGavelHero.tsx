'use client';
import { motion, useAnimation } from 'framer-motion';
import { useCallback, useEffect, useMemo, useState } from 'react';

function GavelSVG({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 120 200"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      <rect x="55" y="80" width="10" height="110" rx="5" fill="url(#handleGrad)" />
      <rect x="10" y="40" width="100" height="45" rx="8" fill="url(#headGrad)" />
      <rect x="10" y="40" width="100" height="4" rx="2" fill="rgba(255,249,239,0.15)" />
      <rect x="25" y="55" width="70" height="3" rx="1.5" fill="rgba(65,45,0,0.3)" />
      <defs>
        <linearGradient
          id="headGrad"
          x1="10"
          y1="40"
          x2="110"
          y2="85"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#e6c487" />
          <stop offset="0.5" stopColor="#c9a96e" />
          <stop offset="1" stopColor="#a88b4e" />
        </linearGradient>
        <linearGradient
          id="handleGrad"
          x1="55"
          y1="80"
          x2="65"
          y2="190"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#8a7030" />
          <stop offset="1" stopColor="#553f08" />
        </linearGradient>
      </defs>
    </svg>
  );
}

function ImpactBurst({ visible }: { visible: boolean }) {
  const particles = useMemo(
    () =>
      Array.from({ length: 12 }, (_, i) => {
        const angle = (i / 12) * 360;
        const dist = 60 + Math.random() * 80;
        const rad = (angle * Math.PI) / 180;
        return {
          id: i,
          x: Math.cos(rad) * dist,
          y: Math.sin(rad) * dist * 0.5,
          size: 3 + Math.random() * 5,
          delay: Math.random() * 0.1,
        };
      }),
    [],
  );
  if (!visible) return null;
  return (
    <div className="absolute left-1/2 bottom-[18%] -translate-x-1/2 pointer-events-none">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full"
          style={{
            width: p.size,
            height: p.size,
            background: 'radial-gradient(circle, #e6c487 0%, rgba(230,196,135,0) 100%)',
            left: 0,
            top: 0,
          }}
          initial={{ x: 0, y: 0, opacity: 1, scale: 1 }}
          animate={{ x: p.x, y: p.y, opacity: 0, scale: 0.2 }}
          transition={{ duration: 0.8, delay: p.delay, ease: 'easeOut' }}
        />
      ))}
      <motion.div
        className="absolute -translate-x-1/2 -translate-y-1/2 rounded-full"
        style={{
          width: 20,
          height: 10,
          background: 'radial-gradient(ellipse, rgba(230,196,135,0.3) 0%, transparent 70%)',
          left: 0,
          top: 0,
        }}
        initial={{ scale: 1, opacity: 0.8 }}
        animate={{ scale: 12, opacity: 0 }}
        transition={{ duration: 1, ease: 'easeOut' }}
      />
    </div>
  );
}

export default function FallingGavelHero() {
  const [hasImpacted, setHasImpacted] = useState(false);
  const [showBurst, setShowBurst] = useState(false);
  const shakeControls = useAnimation();
  const floatControls = useAnimation();

  const handleImpact = useCallback(async () => {
    setHasImpacted(true);
    setShowBurst(true);
    await shakeControls.start({
      x: [0, -4, 6, -3, 4, -2, 0],
      y: [0, 2, -3, 1, -2, 1, 0],
      transition: { duration: 0.5, ease: 'easeOut' },
    });
    floatControls.start({
      y: [0, -8, 0],
      transition: {
        duration: 3,
        repeat: Infinity,
        repeatType: 'reverse' as const,
        ease: 'easeInOut',
      },
    });
  }, [shakeControls, floatControls]);

  useEffect(() => {
    const timer = setTimeout(() => handleImpact(), 1200);
    return () => clearTimeout(timer);
  }, [handleImpact]);

  return (
    <motion.div
      animate={shakeControls}
      className="absolute inset-0 flex flex-col items-center justify-center overflow-hidden"
      style={{ background: '#071325' }}
    >
      {/* Atmospheric Aura */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div
          className="absolute rounded-full"
          style={{
            width: '60vw',
            height: '60vw',
            top: '-15%',
            left: '-10%',
            background:
              'radial-gradient(ellipse at center, rgba(230,196,135,0.08) 0%, transparent 70%)',
            filter: 'blur(100px)',
            animation: 'aura-undulate-1 32s ease-in-out infinite',
          }}
        />
        <div
          className="absolute rounded-full"
          style={{
            width: '45vw',
            height: '45vw',
            bottom: '10%',
            right: '-5%',
            background:
              'radial-gradient(ellipse at center, rgba(170,199,255,0.06) 0%, transparent 70%)',
            filter: 'blur(80px)',
            animation: 'aura-undulate-2 38s ease-in-out infinite',
          }}
        />
      </div>

      {/* Dot Grid */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: 'radial-gradient(circle, rgba(230,196,135,0.4) 1px, transparent 1px)',
          backgroundSize: '24px 24px',
        }}
        aria-hidden="true"
      />

      {/* Impact Surface */}
      <div
        className="absolute left-0 right-0 bottom-[18%] h-[1px]"
        style={{
          background:
            'linear-gradient(90deg, transparent 0%, rgba(230,196,135,0.15) 30%, rgba(230,196,135,0.15) 70%, transparent 100%)',
        }}
        aria-hidden="true"
      />

      {/* Gavel */}
      <motion.div
        className="absolute z-10"
        style={{ top: '15%', width: 'clamp(80px, 10vw, 140px)' }}
        initial={{ y: '-120vh', rotate: -15 }}
        animate={hasImpacted ? undefined : { y: 0, rotate: 0 }}
        transition={{ type: 'spring', damping: 12, stiffness: 80, mass: 1.5, restDelta: 0.5 }}
      >
        <motion.div animate={floatControls}>
          <GavelSVG className="w-full h-auto drop-shadow-[0_0_40px_rgba(230,196,135,0.3)]" />
        </motion.div>
      </motion.div>

      <ImpactBurst visible={showBurst} />

      {/* Hero Content */}
      <div className="relative z-20 text-center px-8 max-w-[900px]">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.6, duration: 0.6 }}
          className="inline-block mb-6"
        >
          <span
            className="inline-block px-5 py-1.5 text-[0.7rem] font-bold tracking-[0.2em] uppercase"
            style={{
              color: '#e6c487',
              background: 'rgba(230,196,135,0.06)',
              border: '1px solid rgba(230,196,135,0.15)',
              borderRadius: '4px',
            }}
          >
            Privilege-Preserving AI
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.8, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="text-[clamp(1.75rem,3.5vw+0.5rem,4.5rem)] font-[800] leading-[0.95] tracking-[-0.04em] uppercase mb-6"
          style={{ color: '#ffffff' }}
        >
          The Law Demands <span style={{ color: '#e6c487' }}>Precision</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.0, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="text-lg leading-[1.7] max-w-[640px] mx-auto mb-8"
          style={{ color: '#d0c5b5' }}
        >
          KovelAI routes attorney work through{' '}
          <em className="font-semibold" style={{ color: '#ffffff', fontStyle: 'italic' }}>
            privilege-preserving channels
          </em>{' '}
          — so your AI never compromises the seal.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.2, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="flex items-center justify-center gap-4 flex-wrap"
        >
          <button type="button" className="btn btn-primary">
            Request Access
          </button>
          <button type="button" className="btn btn-ghost">
            See the Architecture →
          </button>
        </motion.div>
      </div>

      {/* Grain */}
      <div
        className="absolute inset-0 z-30 pointer-events-none opacity-[0.04] mix-blend-overlay"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'repeat',
        }}
        aria-hidden="true"
      />
    </motion.div>
  );
}
