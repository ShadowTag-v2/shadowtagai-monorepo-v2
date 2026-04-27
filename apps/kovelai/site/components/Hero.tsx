import type React from 'react';

/**
 * KovelaiOverlay
 * Hero Component: The Falling Gavel
 * Features full-bleed cinematic video background placeholder and atmospheric-glass UI
 */
export const KovelaiOverlay: React.FC = () => {
  return (
    <section className="relative w-full h-[85vh] flex items-center justify-center overflow-hidden bg-black">
      {/* Cinematic Video Background Placeholder */}
      <div className="absolute inset-0 w-full h-full">
        {/* Placeholder for Gavel Video */}
        <div className="absolute inset-0 bg-neutral-900 animate-pulse flex items-center justify-center">
          <span className="text-white/20 uppercase tracking-widest text-sm font-semibold">
            [ Cinematic Gavel Video Region ]
          </span>
        </div>

        {/* Gradient overlays to ensure text readability */}
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent z-10" />
        <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-transparent to-black/80 z-10" />
      </div>

      {/* Floating UI Layer (Atmospheric Glass) */}
      <div className="relative z-20 container mx-auto px-4 lg:px-8 flex flex-col lg:flex-row items-center justify-between">
        {/* Left Content */}
        <div className="max-w-2xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-md mb-6">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            <span className="text-xs text-white/70 uppercase tracking-wider font-medium">
              Justice Modernized
            </span>
          </div>

          <h1 className="text-5xl md:text-7xl font-extrabold text-white tracking-tight leading-[1.1] mb-6">
            The weight of truth,
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-600">
              without the friction.
            </span>
          </h1>

          <p className="text-lg md:text-xl text-white/60 font-light mb-10 max-w-xl leading-relaxed">
            Kovel AI reconstructs evidence processing through an immutable, autonomous pipeline.
          </p>

          <div className="flex flex-wrap items-center gap-4">
            <button className="px-8 py-4 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition-colors shadow-[0_0_20px_rgba(255,255,255,0.3)]">
              Initiate Pipeline
            </button>
            <button className="px-8 py-4 bg-white/5 text-white font-medium rounded border border-white/10 backdrop-blur-md hover:bg-white/10 transition-all">
              View Architecture
            </button>
          </div>
        </div>

        {/* Right Atmospheric Glass Floating Panel */}
        <div className="hidden lg:flex flex-col gap-4 mt-12 lg:mt-0 relative">
          <div className="absolute -inset-10 bg-blue-500/10 blur-[100px] rounded-full z-0 pointer-events-none" />

          <div className="relative z-10 w-80 p-6 rounded-2xl bg-[#0a0a0c]/40 backdrop-blur-xl border border-white/10 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <span className="text-white/50 text-xs font-mono uppercase tracking-widest">
                Live Inference
              </span>
              <span className="text-emerald-400 text-xs font-mono flex items-center gap-2">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                Active
              </span>
            </div>

            <div className="space-y-3 pt-2">
              <div className="flex justify-between items-center">
                <span className="text-white/70 text-sm">Case Density</span>
                <span className="text-white font-mono text-sm">84.2%</span>
              </div>
              <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 w-[84.2%]" />
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <div className="flex justify-between items-center">
                <span className="text-white/70 text-sm">Latency</span>
                <span className="text-white font-mono text-sm">12ms</span>
              </div>
              <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 w-[12%]" />
              </div>
            </div>
          </div>

          {/* Secondary smaller floating card */}
          <div className="relative z-10 w-64 p-4 rounded-xl bg-[#0a0a0c]/40 backdrop-blur-md border border-white/5 shadow-xl self-end transform translate-x-8 -translate-y-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/50 flex items-center justify-center">
                <svg
                  className="w-4 h-4 text-blue-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <div>
                <div className="text-white text-sm font-medium">Verified Cryptography</div>
                <div className="text-white/40 text-xs font-mono">SHA-256 Hash Locked</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default KovelaiOverlay;
