'use client';

import { useCallback, useEffect, useState } from 'react';

interface WorkflowListing {
  id: string;
  title: string;
  creator: string;
  price: number;
  models: string[];
  remixCount: number;
  category: string;
  earnings: number;
  purchaseCount: number;
}

const DEMO_LISTINGS: WorkflowListing[] = [
  {
    id: 'wf-001',
    title: 'Hyperreal Portrait — Flux + Gen-3 Alpha Pipeline',
    creator: 'synthwave_director',
    price: 2.99,
    models: ['Flux Pro', 'Runway Gen-3', 'ElevenLabs'],
    remixCount: 1247,
    category: 'full-pipeline',
    earnings: 2984,
    purchaseCount: 1243,
  },
  {
    id: 'wf-002',
    title: 'Uncanny Valley Detector — ComfyUI Node Map',
    creator: 'forensic_queen',
    price: 4.99,
    models: ['ComfyUI', 'Midjourney v7'],
    remixCount: 643,
    category: 'comfyui',
    earnings: 1605,
    purchaseCount: 401,
  },
  {
    id: 'wf-003',
    title: 'Political Deepfake Base — Sora 2.0 Seed Bundle',
    creator: 'truth_hunter',
    price: 1.99,
    models: ['Sora 2.0'],
    remixCount: 2891,
    category: 'seed',
    earnings: 4623,
    purchaseCount: 2901,
  },
  {
    id: 'wf-004',
    title: 'Glitch Aesthetic Master Prompt',
    creator: 'vaporwave_ai',
    price: 0.99,
    models: ['Midjourney v7', 'SDXL'],
    remixCount: 5412,
    category: 'prompt',
    earnings: 4299,
    purchaseCount: 5423,
  },
];

const CATS = ['all', 'prompt', 'comfyui', 'seed', 'full-pipeline'] as const;

export default function MarketplacePage() {
  const [listings, setListings] = useState<WorkflowListing[]>([]);
  const [cat, setCat] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => {
      setListings(DEMO_LISTINGS);
      setLoading(false);
    }, 400);
    return () => clearTimeout(t);
  }, []);

  const filtered = listings
    .filter((l) => cat === 'all' || l.category === cat)
    .sort((a, b) => b.remixCount - a.remixCount);

  const buy = useCallback(async (wfId: string) => {
    try {
      const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/marketplace/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ videoId: wfId, buyerId: 'anon' }),
      });
      const d = await r.json();
      if (d.checkoutUrl) window.location.href = d.checkoutUrl;
    } catch (_err: unknown) {
      void _err;
      alert('Stripe Connect checkout opens in production.');
    }
  }, []);

  return (
    <div className="min-h-screen bg-black text-white">
      <header className="border-b border-zinc-900 px-6 py-5">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tighter">
              <span className="text-gradient">HeadFade</span>{' '}
              <span className="text-zinc-400 font-normal">Marketplace</span>
            </h1>
            <p className="text-zinc-600 text-xs mt-1">
              The GitHub of AI — License workflows, earn passive income from every remix
            </p>
          </div>
          <div className="flex gap-3">
            <a
              href="/"
              className="text-xs text-zinc-500 border border-zinc-800 px-3 py-1.5 rounded-lg hover:text-white transition-colors"
            >
              ← Sandbox
            </a>
            <button
              type="button"
              className="text-xs bg-[#00FF41] text-black px-4 py-1.5 rounded-lg font-bold hover:bg-white transition-colors"
            >
              List Your Workflow
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-3 gap-4 mb-8">
          {[
            { l: 'Creator Earnings (30d)', v: '$143,291', s: '↑ 24% MoM' },
            { l: 'Workflows Listed', v: '12,847', s: '20% platform take-rate' },
            { l: 'Total Remixes', v: '2.4M', s: 'Network effect flywheel' },
          ].map((st) => (
            <div key={st.l} className="p-4 border border-zinc-900 rounded-xl bg-zinc-950/50">
              <p className="text-zinc-600 text-[10px] uppercase tracking-[0.2em]">{st.l}</p>
              <p className="text-xl font-bold text-white mt-1">{st.v}</p>
              <p className="text-[10px] text-emerald-500 mt-0.5">{st.s}</p>
            </div>
          ))}
        </div>

        <div className="flex gap-2 mb-6">
          {CATS.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setCat(c)}
              className={`text-[11px] px-3 py-1.5 rounded-lg border transition-all ${cat === c ? 'bg-[#00FF41]/10 text-[#00FF41] border-[#00FF41]/30' : 'text-zinc-500 border-zinc-800 hover:border-zinc-700'}`}
            >
              {c === 'all' ? 'All' : c}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filtered.map((l) => (
              <div
                key={l.id}
                className="border border-zinc-900 rounded-xl p-4 hover:border-zinc-700 transition-all"
              >
                <h3 className="text-sm font-bold mb-1">{l.title}</h3>
                <p className="text-[11px] text-zinc-500 mb-2">
                  by <span className="text-cyan-400">@{l.creator}</span>
                </p>
                <div className="flex flex-wrap gap-1 mb-2">
                  {l.models.map((m) => (
                    <span
                      key={m}
                      className="text-[9px] bg-zinc-900 text-zinc-400 px-1.5 py-0.5 rounded-sm"
                    >
                      {m}
                    </span>
                  ))}
                </div>
                <div className="flex justify-between text-[10px] text-zinc-600 mb-3">
                  <span>🔀 {l.remixCount.toLocaleString()} remixes</span>
                  <span>💰 ${l.earnings.toLocaleString()} earned</span>
                </div>
                <button
                  type="button"
                  onClick={() => buy(l.id)}
                  className="w-full bg-gradient-to-r from-cyan-500 to-emerald-500 text-black py-2 text-[11px] font-bold rounded-lg hover:opacity-90 transition-opacity"
                >
                  Fork Workflow — ${l.price.toFixed(2)}
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="mt-12 p-8 border border-[#00FF41]/20 rounded-2xl bg-[#00FF41]/5 text-center">
          <h2 className="text-xl font-bold mb-2">Your Workflows. Your Revenue.</h2>
          <p className="text-sm text-zinc-400 max-w-lg mx-auto mb-4">
            Upload prompts, ComfyUI nodes, or full pipelines. Every fork earns you 80% instantly via
            Stripe Connect.
          </p>
          <button
            type="button"
            className="bg-[#00FF41] text-black px-6 py-2.5 rounded-lg text-sm font-bold hover:bg-white transition-colors"
          >
            Start Selling
          </button>
        </div>
      </main>

      <footer className="border-t border-zinc-900 px-6 py-6 mt-12">
        <div className="max-w-6xl mx-auto flex justify-between text-[10px] text-zinc-700">
          <span>© 2026 ShadowTag AI · Stripe Connect</span>
          <span>20% platform · 80% to creators</span>
        </div>
      </footer>
    </div>
  );
}
