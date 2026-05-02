'use client';
import { motion, useAnimation } from 'framer-motion';
import { useEffect, useMemo } from 'react';

/* ─── Trail Particles ─── */
function SnowTrail({ count = 20 }: { count?: number }) {
  const dots = useMemo(
    () =>
      Array.from({ length: count }, (_, i) => ({
        id: i,
        x: 60 + Math.random() * 30,
        y: 60 + Math.random() * 20,
        size: 2 + Math.random() * 4,
        delay: i * 0.08,
        dur: 1.2 + Math.random() * 0.8,
      })),
    [count],
  );

  return (
    <>
      {dots.map((d) => (
        <motion.div
          key={d.id}
          className="absolute rounded-full pointer-events-none"
          style={{
            width: d.size,
            height: d.size,
            background: 'rgba(215,227,252,0.25)',
            left: `${d.x}%`,
            top: `${d.y}%`,
          }}
          initial={{ opacity: 0 }}
          animate={{
            opacity: [0, 0.6, 0],
            x: [0, 30 + Math.random() * 40],
            y: [0, 15 + Math.random() * 20],
            scale: [1, 0.3],
          }}
          transition={{ duration: d.dur, delay: 1.5 + d.delay, ease: 'easeOut' }}
        />
      ))}
    </>
  );
}

export default function UphillSnowballHero() {
  const rollControls = useAnimation();
  const growControls = useAnimation();

  useEffect(() => {
    const seq = async () => {
      // Wait for mount
      await new Promise((r) => setTimeout(r, 600));
      // Roll uphill: bottom-right → center-left
      rollControls.start({
        x: ['0vw', '-80vw'],
        y: ['0vh', '-55vh'],
        rotate: [0, -720],
        transition: { duration: 4, ease: [0.22, 1, 0.36, 1] },
      });
      // Grow as it accumulates
      growControls.start({
        scale: [1, 1.6],
        transition: { duration: 4, ease: [0.22, 1, 0.36, 1] },
      });
    };
    seq();
  }, [rollControls, growControls]);

  return (
    <div
      className="absolute inset-0 flex flex-col items-center justify-center overflow-hidden"
      style={{ background: '#071325' }}
    >
      {/* Atmospheric Aura */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div
          className="absolute rounded-full"
          style={{
            width: '55vw',
            height: '55vw',
            top: '-20%',
            right: '-10%',
            background:
              'radial-gradient(ellipse at center, rgba(170,199,255,0.07) 0%, transparent 70%)',
            filter: 'blur(100px)',
            animation: 'aura-undulate-2 38s ease-in-out infinite',
          }}
        />
        <div
          className="absolute rounded-full"
          style={{
            width: '50vw',
            height: '50vw',
            bottom: '-10%',
            left: '-15%',
            background:
              'radial-gradient(ellipse at center, rgba(230,196,135,0.06) 0%, transparent 70%)',
            filter: 'blur(90px)',
            animation: 'aura-undulate-3 28s ease-in-out infinite',
          }}
        />
      </div>

      {/* Incline Surface — diagonal line suggesting uphill */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <svg
          className="absolute inset-0 w-full h-full"
          viewBox="0 0 1000 600"
          preserveAspectRatio="none"
          aria-hidden="true"
        >
          <line
            x1="800"
            y1="480"
            x2="200"
            y2="280"
            stroke="rgba(230,196,135,0.1)"
            strokeWidth="1"
            strokeDasharray="8 6"
          />
          <line
            x1="820"
            y1="490"
            x2="180"
            y2="270"
            stroke="rgba(170,199,255,0.04)"
            strokeWidth="1"
          />
        </svg>
      </div>

      {/* Dot Grid */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: 'radial-gradient(circle, rgba(215,227,252,0.3) 1px, transparent 1px)',
          backgroundSize: '24px 24px',
        }}
        aria-hidden="true"
      />

      {/* Snowball */}
      <motion.div
        className="absolute z-[2]"
        style={{ bottom: '12%', right: '10%' }}
        animate={rollControls}
      >
        <motion.div animate={growControls} className="relative">
          {/* Outer glow */}
          <div
            className="absolute -inset-8 rounded-full"
            style={{
              background: 'radial-gradient(circle, rgba(170,199,255,0.12) 0%, transparent 70%)',
              filter: 'blur(20px)',
            }}
          />
          {/* Core sphere */}
          <div
            className="relative rounded-full"
            style={{
              width: 'clamp(48px, 6vw, 80px)',
              height: 'clamp(48px, 6vw, 80px)',
              background:
                'radial-gradient(circle at 35% 35%, rgba(215,227,252,0.95) 0%, rgba(184,200,242,0.7) 40%, rgba(170,199,255,0.5) 100%)',
              boxShadow:
                '0 0 40px rgba(170,199,255,0.2), inset -8px -8px 20px rgba(7,19,37,0.3), inset 4px 4px 12px rgba(255,255,255,0.15)',
            }}
          >
            {/* Specular highlight */}
            <div
              className="absolute top-[15%] left-[20%] w-[30%] h-[20%] rounded-full"
              style={{ background: 'rgba(255,255,255,0.3)', filter: 'blur(4px)' }}
            />
          </div>
        </motion.div>
      </motion.div>

      {/* Snow trail particles */}
      <SnowTrail />

      {/* Hero Content */}
      <div className="relative z-20 text-center px-8 max-w-[900px]">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="inline-block mb-6"
        >
          <span
            className="inline-block px-5 py-1.5 text-[0.7rem] font-bold tracking-[0.2em] uppercase"
            style={{
              color: '#aac7ff',
              background: 'rgba(170,199,255,0.06)',
              border: '1px solid rgba(170,199,255,0.15)',
              borderRadius: '4px',
            }}
          >
            Kinetic Reversal
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="text-[clamp(1.75rem,3.5vw+0.5rem,4.5rem)] font-[800] leading-[0.95] tracking-[-0.04em] uppercase mb-6"
          style={{ color: '#d7e3fc' }}
        >
          Momentum That <span style={{ color: '#aac7ff' }}>Defies Gravity</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="text-lg leading-[1.7] max-w-[640px] mx-auto mb-8"
          style={{ color: '#d0c5b5' }}
        >
          Like a snowball rolling uphill, our platform{' '}
          <em className="font-semibold" style={{ color: '#d7e3fc', fontStyle: 'italic' }}>
            accumulates advantage
          </em>{' '}
          with every interaction — compounding intelligence where others lose momentum.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.4, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="flex items-center justify-center gap-4 flex-wrap"
        >
          <button type="button" className="btn btn-primary">
            Start Building
          </button>
          <button type="button" className="btn btn-ghost">
            Explore the Monorepo →
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
    </div>
  );
}
