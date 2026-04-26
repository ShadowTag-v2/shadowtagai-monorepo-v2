'use client';

export default function Hero() {
  return (
    <header className="relative min-h-screen flex items-center overflow-hidden" id="hero">
      {/* Layer 0: Video background (desktop) */}
      <video
        className="absolute inset-0 w-full h-full object-cover opacity-30"
        autoPlay
        loop
        muted
        playsInline
        preload="none"
        poster="/images/supercar-poster.png"
      >
        <source src="/videos/supercar-peelout.mp4" type="video/mp4" />
        <source src="/videos/hero-bg.mp4" type="video/mp4" />
      </video>

      {/* Layer 0b: Static fallback gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#071325] via-[#0a1a30] to-[#071325] opacity-70" />

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
          POST-HEPPNER · PRIVILEGED · REVENUE-FIRST
        </div>
        <h1 className="text-[clamp(1.75rem,5vw,3.5rem)] font-extrabold leading-[1.05] tracking-[-0.02em] max-w-[800px] mb-6">
          Every Google Search Your Client Makes Is a Loaded Gun Pointed at Your Case.
          <br />
          <span className="text-gold">KovelAI Disarms It — And Bills For the Protection.</span>
        </h1>
        <p className="text-[0.9375rem] leading-relaxed text-secondary-text max-w-[640px] mb-8">
          Since <em>In re Heppner</em> (S.D.N.Y., Feb. 2026), every unprotected client web search,
          every ChatGPT query, every 2 AM panic-Google is discoverable. Opposing counsel is already
          subpoenaing browser histories. KovelAI wraps all of it under attorney-client privilege —
          and your firm gets paid for every session.
        </p>
        <div className="flex flex-wrap gap-4 mb-4">
          <a
            href="https://buy.stripe.com/test_aEU5nR1Jy9Mg8zS000"
            className="btn-gold text-sm"
            id="ctaFreeTrial"
          >
            Start Free Trial
          </a>
          <a href="#discovery" className="btn-ghost text-sm">
            See the Risk →
          </a>
        </div>
        <p className="text-xs text-[#998f81]">
          No credit card required · 10,000 tokens free · SOC 2 audit-ready
        </p>
      </div>
    </header>
  );
}
