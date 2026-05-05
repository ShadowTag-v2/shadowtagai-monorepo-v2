import type React from 'react';

/**
 * UnusualChassis - Structural Layout Component
 * Extracted structural bones (DOM/CSS Grid/responsive pacing) from target reference.
 * Includes the "Kovelai Overlay (Falling Gavel)" full-bleed video placeholder.
 */
export default function UnusualChassis({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative min-h-screen bg-[#050505] text-[#FAFAFA] font-sans selection:bg-[#FAFAFA] selection:text-[#050505]">
      {/*
        HERO PROTOTYPE: Kovelai Overlay (Falling Gavel)
        Full-bleed background video placeholder with z-index layering
      */}
      <div className="absolute inset-0 z-0 overflow-hidden bg-black">
        {/* Placeholder for Cinematic Gavel Falling Downward */}
        <video
          className="w-full h-full object-cover opacity-40 mix-blend-screen"
          autoPlay
          loop
          muted
          playsInline
        >
          {/* <source src="/videos/falling-gavel-cinematic.mp4" type="video/mp4" /> */}
        </video>
        {/* Deep dark gradient overlay to ensure text legibility */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#050505]/80 via-transparent to-[#050505]" />
      </div>

      {/*
        Atmospheric Glass UI Layer
        z-index 10 floats over the impact zone
      */}
      <div className="relative z-10 flex flex-col min-h-screen backdrop-blur-[2px]">
        {/* Header / Navigation Chassis */}
        <header className="w-full sticky top-0 z-50 px-6 py-4 flex justify-between items-center bg-[#050505]/40 backdrop-blur-md border-b border-[#FFFFFF]/10">
          <div className="text-xl font-medium tracking-tight">KovelAI</div>
          <nav className="hidden md:flex gap-8 text-sm font-medium text-[#A1A1AA]">
            <a href="#features" className="hover:text-white transition-colors">
              Platform
            </a>
            <a href="#solutions" className="hover:text-white transition-colors">
              Solutions
            </a>
            <a href="#pricing" className="hover:text-white transition-colors">
              Pricing
            </a>
          </nav>
          <button
            type="button"
            className="px-5 py-2 text-sm font-semibold bg-[#FAFAFA] text-[#050505] rounded-full hover:bg-white/90 transition-colors"
          >
            Get Started
          </button>
        </header>

        {/* Main Content Area (Children Injection) */}
        <main className="flex-grow flex flex-col items-center justify-center px-6">
          {children || (
            <div className="max-w-4xl w-full mx-auto py-32 text-center">
              <h1 className="text-6xl md:text-8xl font-bold tracking-tighter mb-8 bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60">
                Automate the <br />
                Unprecedented.
              </h1>
              <p className="text-xl md:text-2xl text-[#A1A1AA] max-w-2xl mx-auto mb-12 font-light">
                Structural chassis extracted and established. Awaiting injection of dynamic content
                and logic modules.
              </p>
            </div>
          )}
        </main>

        {/* CSS Grid Section Pacing Chassis */}
        <section className="w-full max-w-7xl mx-auto px-6 py-24 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 border-t border-[#FFFFFF]/5">
          <div className="h-64 bg-[#111111] rounded-2xl border border-[#FFFFFF]/5 p-8">
            <div className="w-12 h-12 rounded-full bg-[#FFFFFF]/10 mb-6" />
            <div className="h-6 w-3/4 bg-[#FFFFFF]/10 rounded mb-4" />
            <div className="h-4 w-full bg-[#FFFFFF]/5 rounded" />
          </div>
          <div className="h-64 bg-[#111111] rounded-2xl border border-[#FFFFFF]/5 p-8">
            <div className="w-12 h-12 rounded-full bg-[#FFFFFF]/10 mb-6" />
            <div className="h-6 w-3/4 bg-[#FFFFFF]/10 rounded mb-4" />
            <div className="h-4 w-full bg-[#FFFFFF]/5 rounded" />
          </div>
          <div className="h-64 bg-[#111111] rounded-2xl border border-[#FFFFFF]/5 p-8">
            <div className="w-12 h-12 rounded-full bg-[#FFFFFF]/10 mb-6" />
            <div className="h-6 w-3/4 bg-[#FFFFFF]/10 rounded mb-4" />
            <div className="h-4 w-full bg-[#FFFFFF]/5 rounded" />
          </div>
        </section>

        {/* Footer Chassis */}
        <footer className="w-full px-6 py-12 border-t border-[#FFFFFF]/10 text-center text-sm text-[#71717A]">
          <p>&copy; {new Date().getFullYear()} KovelAI. Zero-Trust Architecture.</p>
        </footer>
      </div>
    </div>
  );
}
