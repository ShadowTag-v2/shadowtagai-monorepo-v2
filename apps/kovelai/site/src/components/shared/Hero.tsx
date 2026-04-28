'use client';

import Image from 'next/image';

interface HeroProps {
  onOpenModal?: () => void;
}

export default function Hero({ onOpenModal }: HeroProps) {
  return (
    <header className="relative min-h-[100dvh] flex items-center overflow-hidden" id="hero">
      {/* Layer 0: Vault interior hero (Flow-generated, Nano Banana 2) */}
      <Image
        src="/images/hero-vault-optimized.webp"
        alt="Abstract vault interior with scales of justice — representing privileged legal protection"
        fill
        priority
        quality={80}
        className="object-cover opacity-40"
        sizes="(max-width: 640px) 640px, (max-width: 1024px) 1024px, 1408px"
      />

      {/* Layer 0b: Deep navy overlay for text contrast */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#071325]/80 via-[#0a1a30]/60 to-[#071325]/90" />

      {/* Layer 0.5: Bottom fade */}
      <div className="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-t from-[#071325] to-transparent" />

      {/* Layer 1: Aura blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="aura-blob aura-blob--1" />
        <div className="aura-blob aura-blob--2" />
        <div className="aura-blob aura-blob--3" />
      </div>

      {/* Layer 1.5: Grain texture */}
      <div className="hero-grain" />

      {/* Layer 2: CSS Shield */}
      <div className="css-shield">
        <div className="shield-glow" />
        <div className="shield-outline" />
        <div className="shield-inner" />
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16 scroll-entrance">
        <div className="text-[0.6875rem] font-medium uppercase tracking-[0.15em] text-gold mb-6">
          PRIVILEGE-PROTECTED INFRASTRUCTURE · ATTORNEY-MONITORED · HEPPNER-COMPLIANT
        </div>
        <h1 className="text-[clamp(1.75rem,5vw,3.5rem)] font-extrabold leading-[1.05] tracking-[-0.02em] max-w-[800px] mb-6">
          Every Search. Every Chat.
          <br />
          <span className="text-gold">Discoverable.</span>
        </h1>
        <h2 className="text-[clamp(1rem,2.5vw,1.5rem)] font-semibold text-secondary-text max-w-[700px] mb-6 leading-snug">
          Deploy the privileged research portal that shields your clients&mdash;and your firm.
        </h2>
        <p className="text-[0.9375rem] leading-relaxed text-secondary-text max-w-[640px] mb-4">
          After <em>In re Heppner</em> (S.D.N.Y., Feb. 2026), every web search and AI conversation
          your client conducts outside your firm&apos;s umbrella is fair game for opposing counsel.
          KovelAI is the turnkey infrastructure you deploy to close that gap.
        </p>
        <p className="text-[0.9375rem] leading-relaxed text-secondary-text max-w-[640px] mb-8">
          Your clients search at will under your privilege umbrella. You monitor every session,
          deliver the first legal opinion, and bill their credit card automatically. The pitch is
          one sentence:{' '}
          <strong className="text-primary-text">
            &ldquo;Either you do it through our firm&apos;s KovelAI, or proceed at your
            peril.&rdquo;
          </strong>
        </p>
        <div className="flex flex-wrap gap-4 mb-4">
          <button
            type="button"
            onClick={onOpenModal}
            className="btn-gold text-sm"
            id="ctaFreeTrial"
          >
            Deploy Your Firm&apos;s Portal
          </button>
          <a href="#how-it-works" className="btn-ghost text-sm">
            See How Privilege Works →
          </a>
        </div>
        <p className="text-xs text-[#998f81]">
          Clients log in · You monitor all sessions · You give the first opinion · Automatic billing
          · Opposing counsel gets nothing
        </p>
      </div>
    </header>
  );
}
