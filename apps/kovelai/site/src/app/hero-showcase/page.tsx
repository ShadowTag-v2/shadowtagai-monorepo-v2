'use client';

import { useState } from 'react';
import FallingGavelHero from '@/components/FallingGavelHero';
import UphillSnowballHero from '@/components/UphillSnowballHero';

type HeroVariant = 'gavel' | 'snowball';

export default function HeroShowcase() {
  const [active, setActive] = useState<HeroVariant>('gavel');

  return (
    <div className="min-h-screen" style={{ background: '#071325' }}>
      {/* Switcher Bar */}
      <div
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-center gap-4 py-3"
        style={{ background: 'rgba(7,19,37,0.85)', backdropFilter: 'blur(20px)' }}
      >
        <span
          className="text-[0.6875rem] font-medium uppercase tracking-[0.15em] mr-4"
          style={{ color: '#d0c5b5' }}
        >
          Hero Variants
        </span>
        <button
          type="button"
          onClick={() => setActive('gavel')}
          className="px-4 py-1.5 rounded text-xs font-bold uppercase tracking-wider transition-all"
          style={{
            color: active === 'gavel' ? '#412d00' : '#e6c487',
            background:
              active === 'gavel'
                ? 'linear-gradient(135deg, #e6c487, #c9a96e)'
                : 'rgba(230,196,135,0.08)',
            border: `1px solid ${active === 'gavel' ? 'transparent' : 'rgba(230,196,135,0.2)'}`,
          }}
        >
          Falling Gavel
        </button>
        <button
          type="button"
          onClick={() => setActive('snowball')}
          className="px-4 py-1.5 rounded text-xs font-bold uppercase tracking-wider transition-all"
          style={{
            color: active === 'snowball' ? '#003064' : '#aac7ff',
            background:
              active === 'snowball'
                ? 'linear-gradient(135deg, #aac7ff, #3e90ff)'
                : 'rgba(170,199,255,0.08)',
            border: `1px solid ${active === 'snowball' ? 'transparent' : 'rgba(170,199,255,0.2)'}`,
          }}
        >
          Uphill Snowball
        </button>
      </div>

      {/* Hero viewport */}
      <div className="relative w-full h-screen">
        {active === 'gavel' ? <FallingGavelHero /> : <UphillSnowballHero />}
      </div>
    </div>
  );
}
