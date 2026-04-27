import type React from 'react';

/**
 * UnusualChassis
 * Structural extraction from Unusual Machines homepage.
 * Strips specific IP, maintains CSS Grid, pacing, and responsive containers.
 */
export const UnusualChassis: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="unusual-chassis min-h-screen bg-neutral-950 text-white font-sans overflow-x-hidden">
      {/* Header Structure */}
      <header className="fixed top-0 w-full z-50 transition-colors duration-300 bg-neutral-950/80 backdrop-blur-md border-b border-white/10">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="header__logo w-32 h-10 bg-white/10 rounded animate-pulse" />
            <nav className="hidden lg:flex items-center space-x-8">
              <div className="h-4 w-20 bg-white/10 rounded" />
              <div className="h-4 w-24 bg-white/10 rounded" />
              <div className="h-4 w-16 bg-white/10 rounded" />
              <div className="h-4 w-28 bg-white/10 rounded" />
            </nav>
            <div className="lg:hidden w-8 h-8 flex flex-col justify-around cursor-pointer">
              <span className="block w-full h-0.5 bg-white" />
              <span className="block w-full h-0.5 bg-white" />
              <span className="block w-full h-0.5 bg-white" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Injection */}
      <main className="pt-20">{children}</main>

      {/* Highlights Grid Structure */}
      <section className="homeHighlights py-24 bg-neutral-900">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="h-64 bg-neutral-800 rounded-lg border border-white/5 p-6 flex flex-col justify-end transition-transform hover:-translate-y-1"
              >
                <div className="w-12 h-12 bg-white/10 rounded-full mb-4" />
                <div className="h-6 w-3/4 bg-white/10 rounded mb-2" />
                <div className="h-4 w-1/2 bg-white/10 rounded" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Quick Access Structure */}
      <section className="homeQuickAccess py-16 bg-neutral-950 border-t border-white/5">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="flex flex-col lg:flex-row items-center gap-8">
            <div className="lg:w-1/4">
              <div className="h-8 w-48 bg-white/10 rounded" />
            </div>
            <div className="lg:w-3/4 grid grid-cols-2 sm:grid-cols-4 gap-4 w-full">
              {Array.from({ length: 4 }).map((_, i) => (
                <div
                  key={i}
                  className="h-12 bg-white/5 rounded flex items-center justify-center hover:bg-white/10 transition-colors cursor-pointer"
                >
                  <div className="h-3 w-20 bg-white/20 rounded" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Footer Structure */}
      <footer className="py-12 bg-black border-t border-white/10">
        <div className="container mx-auto px-4 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="w-32 h-8 bg-white/10 rounded" />
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-white/10" />
            <div className="w-8 h-8 rounded-full bg-white/10" />
            <div className="w-8 h-8 rounded-full bg-white/10" />
          </div>
        </div>
      </footer>
    </div>
  );
};

export default UnusualChassis;
