"use client";

import React, { useState } from "react";

export function VectorRetrieval() {
  const [documentId, setDocumentId] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!documentId.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    // Call the newly minted FastApi extraction endpoint natively
    try {
      // Pointing to proxy or localhost 8000 depending on dev setup
      const response = await fetch(`http://localhost:8000/transcript/retrieval/${documentId}`);
      if (!response.ok) throw new Error("Document vector matrix not found.");
      
      const data = await response.json();
      setResult(data.data);
    } catch (err: any) {
      setError(err.message || "Failed to retrieve from PyArrow matrix");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-12 backdrop-blur-xl bg-white/[0.02] border border-white/[0.05] rounded-2xl p-8 shadow-2xl shadow-black/50 overflow-hidden relative group">
      <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none" />
      
      <div className="flex items-center gap-4 mb-8 border-b border-white/5 pb-6">
        <div className="p-3 bg-white/5 rounded-xl border border-white/10">
          <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white/90">Sovereign Vector Retrieval</h2>
          <p className="text-sm font-medium text-neutral-500 mt-1">Extract PyArrow payload dimensions from LanceDB.</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="flex gap-4">
        <input 
          type="text" 
          placeholder="Enter Document ID (e.g. doc_contract.pdf)"
          value={documentId}
          onChange={(e) => setDocumentId(e.target.value)}
          className="flex-1 bg-black/20 border border-white/10 rounded-xl px-5 py-3 text-white placeholder-neutral-600 focus:outline-none focus:border-indigo-500/50 transition-colors font-mono text-sm"
        />
        <button 
          type="submit" 
          disabled={loading}
          className="bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 font-semibold px-8 py-3 rounded-xl transition-all duration-300 disabled:opacity-50"
        >
          {loading ? "Scanning..." : "Extract Node"}
        </button>
      </form>

      {error && (
        <div className="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-3">
           <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
           <p className="text-sm text-red-400 font-medium font-mono">{error}</p>
        </div>
      )}

      {result && (
        <div className="mt-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <h3 className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Extraction Payload</h3>
          </div>
          <div className="bg-black/40 border border-white/5 rounded-xl p-5 overflow-x-auto relative group/code">
            <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500/50" />
            <pre className="text-xs text-neutral-300 font-mono leading-relaxed">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
