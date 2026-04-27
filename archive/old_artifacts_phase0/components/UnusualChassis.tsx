export default function UnusualChassis() {
  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#020408] text-white">
      {/* Veo 3.1 Cinematic Video Background Placeholder */}
      <div className="absolute inset-0 z-0">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="h-full w-full object-cover opacity-60 mix-blend-screen"
        >
          <source
            src="https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
            type="video/mp4"
          />
          Your browser does not support the video tag.
        </video>
      </div>

      {/* Atmospheric Glass Overlay */}
      <div className="absolute inset-0 z-10 bg-[#050505]/90 backdrop-blur-sm"></div>

      {/* Main Chassis Content */}
      <div className="relative z-20 flex min-h-screen flex-col items-center justify-center px-6 md:px-12">
        <header className="absolute top-0 flex w-full items-center justify-between p-8">
          <div className="text-2xl font-bold tracking-tighter text-white">ShadowTag.AI</div>
          <nav className="hidden space-x-8 md:flex">
            <a
              href="#"
              className="text-sm uppercase tracking-widest text-gray-400 transition-colors hover:text-white"
            >
              Platform
            </a>
            <a
              href="#"
              className="text-sm uppercase tracking-widest text-gray-400 transition-colors hover:text-white"
            >
              Solutions
            </a>
            <a
              href="#"
              className="text-sm uppercase tracking-widest text-gray-400 transition-colors hover:text-white"
            >
              Security
            </a>
          </nav>
          <button className="rounded-full border border-white/20 bg-white/5 px-6 py-2 text-sm uppercase tracking-widest backdrop-blur-md transition-colors hover:bg-white/10">
            Client Portal
          </button>
        </header>

        <main className="max-w-4xl text-center">
          <h1 className="mb-6 text-5xl font-extrabold tracking-tight md:text-7xl">
            Elite Legal-Tech <br className="hidden md:block" /> Engineered for Precision.
          </h1>
          <p className="mx-auto mb-10 max-w-2xl text-lg text-gray-400 md:text-xl">
            Cognitive synthesis meets structural perfection. Experience the next generation of
            privilege-preserving LLM routing, secured by atmospheric glass architecture and powered
            by Veo 3.1 cinematic injection.
          </p>
          <div className="flex flex-col items-center justify-center space-y-4 sm:flex-row sm:space-x-6 sm:space-y-0">
            <button className="w-full rounded-none bg-white px-8 py-4 text-sm font-bold uppercase tracking-widest text-black transition-transform hover:scale-105 sm:w-auto">
              Initialize Heist
            </button>
            <button className="w-full rounded-none border border-white/30 bg-transparent px-8 py-4 text-sm font-bold uppercase tracking-widest text-white transition-colors hover:bg-white/10 sm:w-auto">
              View Architecture
            </button>
          </div>
        </main>

        <footer className="absolute bottom-0 w-full border-t border-white/10 p-8 text-center text-xs tracking-widest text-gray-600 uppercase">
          © 2026 ShadowTag Systems | Powered by Google Cognitive Suite
        </footer>
      </div>
    </div>
  );
}
