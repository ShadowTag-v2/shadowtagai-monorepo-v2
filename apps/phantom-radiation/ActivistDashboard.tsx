import type React from 'react';
import { useEffect, useState } from 'react';

// Design Aesthetic: Glassmorphism per Vibe Coding Directive 2
// Variant 2 (Glassmorphism) as selected by Nano Banana 2 Vision Critic.

interface ActivistTargetData {
  ticker: string;
  fraudFlag: boolean;
  viabilityScore: number;
  satelliteProof: string;
  recommendedAction: string;
  evidenceHash: string;
}

const ActivistDashboard: React.FC = () => {
  const [targetData, setTargetData] = useState<ActivistTargetData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // This is a placeholder API endpoint. Replace with your actual API endpoint.
        const response = await fetch('/api/activist-target');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data: ActivistTargetData = await response.json();
        setTargetData(data);
      } catch (error: unknown) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black p-8 text-white font-sans">
        <div className="max-w-4xl mx-auto">
          <header className="mb-12">
            <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-teal-400 to-emerald-500">
              Omni-IPB Activist Oracle
            </h1>
            <p className="text-gray-400 mt-2 tracking-wide text-sm border-l-4 border-teal-500 pl-4 py-1">
              STATUS: GOD MODE ACTIVE. EX TOTO PREDATOR POSTURE.
            </p>
          </header>
          <main>
            <div className="animate-pulse flex space-x-4 p-8 backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl">
              <div className="flex-1 space-y-6 py-1">
                <div className="h-4 bg-white/10 rounded w-3/4"></div>
                <div className="space-y-3">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="h-4 bg-white/10 rounded col-span-2"></div>
                    <div className="h-4 bg-white/10 rounded col-span-1"></div>
                  </div>
                  <div className="h-4 bg-white/10 rounded w-5/6"></div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black p-8 text-white font-sans">
        <div className="max-w-4xl mx-auto">
          <div className="backdrop-blur-xl bg-red-500/20 border border-red-500/30 rounded-3xl p-8 shadow-2xl text-center">
            <h2 className="text-2xl font-bold text-red-400">Error</h2>
            <p className="text-red-300 mt-2">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black p-8 text-white font-sans">
      <div className="max-w-4xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-teal-400 to-emerald-500">
            Omni-IPB Activist Oracle
          </h1>
          <p className="text-gray-400 mt-2 tracking-wide text-sm border-l-4 border-teal-500 pl-4 py-1">
            STATUS: GOD MODE ACTIVE. EX TOTO PREDATOR POSTURE.
          </p>
        </header>

        <main>
          {targetData ? (
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
              {/* Glass reflection effect */}
              <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-white/5 to-transparent rounded-t-3xl pointer-events-none" />

              <div className="flex items-center justify-between mb-8 border-b border-white/10 pb-6 relative z-10">
                <div>
                  <h2 className="text-3xl font-bold font-mono tracking-widest">
                    {targetData.ticker}
                  </h2>
                  <span className="inline-block mt-2 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider bg-red-500/20 text-red-400 border border-red-500/30">
                    {targetData.fraudFlag ? 'Fraud Detected' : 'Clear'}
                  </span>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-400 uppercase tracking-widest mb-1">
                    Viability Score
                  </div>
                  <div
                    className={`text-5xl font-black ${targetData.viabilityScore < 60 ? 'text-red-500' : 'text-emerald-500'}`}
                  >
                    {targetData.viabilityScore}
                    <span className="text-xl text-gray-500 font-medium">/100</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8 relative z-10">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-xs text-gray-500 uppercase tracking-widest mb-1">
                      Physical Grounding (Nano Banana 2)
                    </h3>
                    <div className="p-4 bg-black/40 rounded-xl font-mono text-sm leading-relaxed text-amber-300 border border-amber-500/20 shadow-inner">
                      {targetData.satelliteProof}
                    </div>
                  </div>
                </div>

                <div className="space-y-4 flex flex-col justify-end">
                  <div>
                    <h3 className="text-xs text-gray-500 uppercase tracking-widest mb-1">
                      Recommended Action
                    </h3>
                    <div className="p-4 bg-rose-500/10 rounded-xl font-bold text-lg text-rose-400 border border-rose-500/30 uppercase tracking-wide">
                      {targetData.recommendedAction}
                    </div>
                  </div>
                </div>
              </div>

              <div className="border-t border-white/10 pt-6 mt-4 flex items-center justify-between relative z-10">
                <div className="flex items-center space-x-2 text-xs text-gray-500 font-mono">
                  <svg
                    aria-hidden="true"
                    className="w-4 h-4 text-emerald-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    ></path>
                  </svg>
                  <span>Immutable Evidence Hash: {targetData.evidenceHash}</span>
                </div>
                <button
                  type="button"
                  className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 transition-all rounded-full font-bold text-sm text-white shadow-[0_0_15px_rgba(6,182,212,0.5)]"
                >
                  Execute Trade Route
                </button>
              </div>
            </div>
          ) : (
            <div className="animate-pulse flex space-x-4 p-8 backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl">
              <div className="flex-1 space-y-6 py-1">
                <div className="h-4 bg-white/10 rounded w-3/4"></div>
                <div className="space-y-3">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="h-4 bg-white/10 rounded col-span-2"></div>
                    <div className="h-4 bg-white/10 rounded col-span-1"></div>
                  </div>
                  <div className="h-4 bg-white/10 rounded w-5/6"></div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default ActivistDashboard;
