import TeamSection from '../components/TeamSection';

export default function Home() {
  return (
    <main className="min-h-screen bg-void text-starlight selection:bg-accent selection:text-white">
      {/* HERO SECTION */}
      <section className="relative min-h-[90vh] flex flex-col justify-center items-center text-center px-4 overflow-hidden">
        {/* Background Grid */}
        <div className="absolute inset-0 bg-grid-pattern opacity-20 pointer-events-none" />
        <div className="absolute inset-0 bg-gradient-to-b from-void via-transparent to-void pointer-events-none" />

        <div className="relative z-10 max-w-4xl mx-auto space-y-8 animate-in fade-in zoom-in duration-1000">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-tension bg-surface/50 backdrop-blur">
            <span className="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
            <span className="text-xs font-mono text-ghost uppercase tracking-widest">System_Status: Sovereign</span>
          </div>
          
          <h1 className="text-6xl md:text-8xl font-sans font-medium tracking-tighter leading-none bg-gradient-to-br from-white to-gray-500 bg-clip-text text-transparent">
            Sovereignty is the <br/>
            <span className="text-white">New Supremacy.</span>
          </h1>
          
          <p className="text-lg md:text-xl text-ghost max-w-2xl mx-auto font-light leading-relaxed">
            Stop renting ephemeral thoughts. <strong className="text-starlight font-medium">Judge6</strong> is a sovereign AI architecture extracted from your Cloud Workstation. 
            <span className="block mt-2 font-mono text-xs text-accent">Owned by You. Running on Your Metal.</span>
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
            <button className="px-8 py-4 bg-starlight text-void font-mono text-sm font-bold uppercase tracking-widest hover:bg-white hover:shadow-[0_0_30px_rgba(255,255,255,0.3)] transition-all transform active:scale-95">
              Initialize_Reactor_
            </button>
            <button className="px-8 py-4 border border-tension text-ghost font-mono text-sm font-bold uppercase tracking-widest hover:text-starlight hover:border-gray-500 transition-all">
              Read_The_Doctrine
            </button>
          </div>
        </div>
      </section>

      {/* FEATURE GRID (The Bento Box) */}
      <section className="py-32 px-6">
        <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-6">
            {/* CELL 1 */}
            <div className="md:col-span-2 p-12 bg-surface border border-tension rounded-2xl relative overflow-hidden group hover:border-accent/50 transition-colors">
                <div className="absolute top-0 right-0 p-8 opacity-10 font-mono text-9xl font-bold group-hover:opacity-20 transition-opacity">01</div>
                <h3 className="text-2xl font-sans text-starlight mb-4">The Black Box</h3>
                <p className="text-ghost leading-relaxed max-w-md">
                    Your Data, Your Skull. No shared weights. No API leakage. Judge6 runs in your isolated VPC, strictly enforcing the <span className="text-accent">Antigravity Protocols</span>.
                </p>
            </div>

            {/* CELL 2 */}
            <div className="p-12 bg-surface border border-tension rounded-2xl relative group hover:border-burn/50 transition-colors">
                <div className="absolute top-4 right-4 w-2 h-2 rounded-full bg-burn"></div>
                <h3 className="text-2xl font-sans text-starlight mb-4">The Burn</h3>
                <p className="text-ghost text-sm leading-relaxed">
                    Real-time cost telemetry. Watch your GPU spend like a hawk.
                </p>
                <div className="mt-8 font-mono text-4xl text-starlight">$4.20<span className="text-sm text-ghost">/hr</span></div>
            </div>

            {/* CELL 3 */}
            <div className="p-12 bg-surface border border-tension rounded-2xl md:col-span-3 flex flex-col md:flex-row items-center justify-between gap-8">
                <div>
                    <h3 className="text-2xl font-sans text-starlight mb-2">The Google Extraction</h3>
                    <p className="text-ghost max-w-xl">
                        Re-engineered from the "Cloud Workstation" internal architecture. Enterprise-grade isolation, consumer-grade UX.
                    </p>
                </div>
                <div className="font-mono text-xs text-accent border border-accent/20 px-4 py-2 rounded bg-accent/5">
                    > SOURCE: MOUNTAIN_VIEW_CLASSIFIED
                </div>
            </div>
        </div>
      </section>

      {/* COMPLIANCE SECTION */}
      <TeamSection />
      
    </main>
  );
}
