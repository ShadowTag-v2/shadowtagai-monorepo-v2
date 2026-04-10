import React from "react";
import { VectorRetrieval } from "@/components/VectorRetrieval";

export default function OutlookDemo() {
  return (
    <div className="min-h-screen bg-[#0a0a0b] text-neutral-200 font-sans selection:bg-indigo-500/30">
      {/* Dynamic Background Mesh */}
      <div className="absolute inset-0 z-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.15),rgba(255,255,255,0))]" />
      
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-20">
        <header className="mb-16 border-b border-white/5 pb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-extrabold tracking-tight text-white mb-2">
                Unified Ingress
              </h1>
              <p className="text-sm font-medium text-neutral-500 tracking-wide uppercase">
                Temporal Worker Analytics • M1 ANE
              </p>
            </div>
            <div className="flex items-center gap-4">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
              <span className="text-xs font-semibold text-emerald-400/90 tracking-widest uppercase">
                Matrix Online
              </span>
            </div>
          </div>
        </header>

        {/* Luxury Glass Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { tag: "Swarm", val: "0.0.0.0:7233", act: "Active" },
            { tag: "VRAM Buffer", val: "16 GB ANE", act: "Stable" },
            { tag: "LanceDB Array", val: "Port 8080", act: "Ingesting" }
          ].map((node, i) => (
             <div 
               key={i} 
               className="group relative backdrop-blur-xl bg-white/[0.02] border border-white/[0.05] rounded-2xl p-6 transition-all duration-500 hover:bg-white/[0.04] hover:border-white/10 hover:-translate-y-1 shadow-2xl shadow-black/50 overflow-hidden"
             >
               <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
               <h3 className="text-xs font-bold text-neutral-500 uppercase tracking-widest mb-4">{node.tag}</h3>
               <p className="text-2xl font-light text-white mb-6 tabular-nums">{node.val}</p>
               <div className="flex items-center justify-between">
                 <button className="text-sm text-indigo-400 transition-colors hover:text-indigo-300 font-medium">Configure ↗</button>
                 <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-neutral-400">
                   {node.act}
                 </span>
               </div>
             </div>
          ))}
        </div>
        
        <VectorRetrieval />
      </div>
    </div>
  );
}
