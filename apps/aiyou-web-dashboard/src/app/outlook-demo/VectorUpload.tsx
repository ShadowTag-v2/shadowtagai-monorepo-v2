import React, { useState } from 'react';

export default function VectorUpload() {
  const [status, setStatus] = useState('Idle');

  const shadowDrop = () => {
    setStatus('Ingesting...');
    setTimeout(() => setStatus('SUCCESS_VECTORIZED'), 2000);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0b] flex items-center justify-center p-6 text-neutral-300 font-sans">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_60%_at_50%_0%,rgba(120,119,198,0.1),rgba(255,255,255,0))]" />
      
      <div className="relative z-10 w-full max-w-lg p-8 rounded-3xl border border-white/10 backdrop-blur-3xl bg-white/[0.02] shadow-2xl overflow-hidden group">
        <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
        
        <h2 className="text-2xl font-extrabold tracking-tight text-white mb-2">LanceDB Matrix Drop</h2>
        <p className="text-sm font-medium text-neutral-500 mb-8 tracking-wide">Secure Temporal Ingestion Pipeline</p>

        <div 
          onClick={shadowDrop}
          className="cursor-pointer border-2 border-dashed border-white/20 rounded-2xl p-12 text-center hover:bg-white/5 transition-all duration-300 hover:border-emerald-500/50"
        >
          <div className="mb-4 inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/5">
             <span className="text-2xl">⚡</span>
          </div>
          <h3 className="text-lg text-white font-semibold mb-1">Click to Drop Sovereign Assets</h3>
          <p className="text-xs text-neutral-500">Zero-Trust Endpoints Only (.pdf, .txt, .docx)</p>
        </div>

        <div className="mt-8 flex items-center justify-between px-4 py-3 bg-white/5 rounded-xl border border-white/5">
          <span className="text-xs font-semibold tracking-widest uppercase text-neutral-400">Queue Status</span>
          <span className={`text-xs font-bold uppercase tracking-wider ${status.includes('SUCCESS') ? 'text-emerald-400' : 'text-indigo-400'}`}>
            {status}
          </span>
        </div>
      </div>
    </div>
  );
}
