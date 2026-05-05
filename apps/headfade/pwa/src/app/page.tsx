'use client';
import { useState, useCallback } from 'react';

export default function HeadFadeSwiper() {
  const [video, _setVideo] = useState('/media/genesis_clip_01.mp4');
  const [reveal, setReveal] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const castVote = useCallback(
    async (vote: 'REAL' | 'AI') => {
      setReveal('> Initializing Gemini 3.1 Flash Lite Forensics...\n');
      setIsAnalyzing(true);
      try {
        // Phase 1: Silent HDI telemetry — B2B data pipeline
        await fetch('/api/vote', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            video_id: video,
            user_vote: vote,
            actual_truth: 'AI',
            latency_ms: '104',
          }),
        });

        // Phase 2: Forensic AI reveal via Gemini arbiter
        const res = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            video_uri: `gs://headfade-cdn-origin/${video}`,
            actual_truth: 'AI',
            user_vote: vote,
          }),
        });

        if (!res.ok) {
          const err = await res.json();
          setReveal(
            `> FORENSIC ENGINE STATUS: ${res.status}\n> ${err.detail || 'Service initializing — video analysis requires uploaded media in GCS.'}`,
          );
          return;
        }

        const data = await res.json();
        setReveal(
          `> STATUS: ${data.status}\n\n` +
            `> GEMINI INTERNAL THOUGHTS:\n${data.gemini_thoughts || '[CLASSIFIED]'}\n\n` +
            `> VERDICT:\n${data.gemini_verdict || '[PENDING ANALYSIS]'}`,
        );
      } catch (e) {
        setReveal(`> FATAL FORENSIC ARBITER ERROR: ${e}`);
      } finally {
        setIsAnalyzing(false);
      }
    },
    [video],
  );

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white p-4">
      <h1 className="text-4xl font-bold text-gradient mb-2 tracking-tighter shadow-sm">
        HeadFadeAi
      </h1>
      <p className="text-zinc-500 text-sm mb-6 tracking-wide">
        The Global Turing Test — Can You Tell What Is Real?
      </p>

      {/* The Central Artifact Viewer (TikTok/Tinder Swiper) */}
      <div className="glass-panel w-full max-w-md h-[550px] rounded-3xl overflow-hidden relative shadow-2xl border border-white/5">
        <video className="w-full h-full object-cover" src={video} autoPlay loop muted playsInline />

        {/* The Deception Controls */}
        <div className="absolute bottom-8 w-full flex justify-between px-6 z-10">
          <button
            type="button"
            onClick={() => castVote('REAL')}
            disabled={isAnalyzing}
            className="glass-card px-8 py-4 rounded-xl text-emerald-400 font-bold tracking-widest hover:bg-emerald-400/10 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            REAL
          </button>
          <button
            type="button"
            onClick={() => castVote('AI')}
            disabled={isAnalyzing}
            className="glass-card px-8 py-4 rounded-xl text-cyan-400 font-bold tracking-widest hover:bg-cyan-400/10 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            AI
          </button>
        </div>
      </div>

      {/* The Terminal: Exposing Gemini's Internal Monologue to the User */}
      <div className="mt-6 w-full max-w-md p-6 glass-card font-mono text-xs md:text-sm h-40 overflow-y-auto leading-relaxed text-zinc-400 whitespace-pre-wrap">
        {reveal || '> SECURE TERMINAL: Awaiting Human Deception Input...'}
      </div>

      {/* Stripe Pro Upgrade CTA */}
      <div className="mt-8 w-full max-w-md flex flex-col items-center gap-3">
        <a
          href="https://buy.stripe.com/headfade_pro"
          target="_blank"
          rel="noopener noreferrer"
          className="w-full text-center px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 text-black font-bold tracking-wide hover:opacity-90 transition-opacity text-sm"
        >
          Upgrade to Pro — Unlimited Forensic Analysis
        </a>
        <p className="text-zinc-600 text-xs">
          Enterprise deepfake detection API access · Bulk HDI analytics · Priority support
        </p>
      </div>

      {/* Footer */}
      <footer className="mt-12 text-zinc-700 text-xs text-center">
        <p>
          &copy; 2026 ShadowTag AI · Powered by Gemini 3.1 Flash Lite ·{' '}
          <a
            href="https://shadowtagai.web.app"
            className="text-zinc-500 hover:text-white transition-colors"
          >
            ShadowTagAI
          </a>
        </p>
      </footer>
    </div>
  );
}
