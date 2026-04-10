"use client";

import { useEffect, useState } from "react";
import { client } from "@/lib/api/client.gen";
import {
  healthHealthGet,
  getGcsMemoryMemoryGcsGet,
  getFirestoreMemoryMemoryFirestoreGet,
} from "@/lib/api/sdk.gen";
import type { MemoryResponse } from "@/lib/api/types.gen";

// Configure base URL for the client
client.setConfig({
  baseUrl: "http://localhost:8000",
});

export default function Home() {
  const [status, setStatus] = useState<string>("loading...");
  const [gcsData, setGcsData] = useState<MemoryResponse["data"] | null>(null);
  const [firestoreData, setFirestoreData] = useState<MemoryResponse["data"] | null>(null);

  useEffect(() => {
    // Check Health
    healthHealthGet()
      .then((res) => {
        // Health endpoint returns unknown, but we know it has status
        const data = res.data as { status: string };
        setStatus(data?.status || "error");
      })
      .catch(() => setStatus("offline"));

    // Fetch Memories
    getGcsMemoryMemoryGcsGet()
      .then((res) => {
        if (res.data) setGcsData(res.data.data);
      })
      .catch(console.error);

    getFirestoreMemoryMemoryFirestoreGet()
      .then((res) => {
        if (res.data) setFirestoreData(res.data.data);
      })
      .catch(console.error);
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <header className="flex items-center justify-between border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
              Antigravity Console
            </h1>
            <p className="text-slate-400 mt-1">Agentic Memory & Governance System</p>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${status === "healthy" ? "bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]" : "bg-red-500"}`}
            />
            <span className="text-sm font-medium uppercase tracking-wider text-slate-500">
              {status}
            </span>
          </div>
        </header>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* GCS Memory Card */}
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 backdrop-blur-sm hover:border-blue-500/30 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-blue-400">GCS Memory (Workbench)</h2>
              <span className="text-xs bg-blue-500/10 text-blue-400 px-2 py-1 rounded">Batch</span>
            </div>
            <pre className="bg-slate-950 rounded-lg p-4 text-xs font-mono overflow-auto max-h-60 text-slate-300 border border-slate-900">
              {gcsData ? JSON.stringify(gcsData, null, 2) : "Loading GCS data..."}
            </pre>
          </div>

          {/* Firestore Memory Card */}
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 backdrop-blur-sm hover:border-orange-500/30 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-orange-400">Firestore Memory</h2>
              <span className="text-xs bg-orange-500/10 text-orange-400 px-2 py-1 rounded">
                Real-time
              </span>
            </div>
            <pre className="bg-slate-950 rounded-lg p-4 text-xs font-mono overflow-auto max-h-60 text-slate-300 border border-slate-900">
              {firestoreData ? JSON.stringify(firestoreData, null, 2) : "Loading Firestore data..."}
            </pre>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-medium transition-colors">
            Refresh Data
          </button>
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors shadow-lg shadow-blue-900/20">
            Trigger Sync
          </button>
        </div>
      </div>
    </main>
  );
}
