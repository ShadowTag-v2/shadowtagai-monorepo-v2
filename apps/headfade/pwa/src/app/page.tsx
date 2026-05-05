'use client';
import { useState, useCallback, useRef, useEffect } from 'react';

/** Extract clean filename from local path or full URI */
function gcsVideoId(localPath: string): string {
  // '/media/genesis_clip_01.mp4' → 'genesis_clip_01.mp4'
  const basename = localPath.split('/').pop() || localPath;
  return basename;
}

export default function HeadFadeSwiper() {
  const [video, _setVideo] = useState('/media/genesis_clip_01.mp4');
  const [reveal, setReveal] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [userResult, setUserResult] = useState<'correct' | 'fooled' | null>(null);
  const terminalRef = useRef<HTMLDivElement>(null);

  // Auto-scroll terminal to bottom on new content
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [reveal]);

  const castVote = useCallback(
    async (vote: 'REAL' | 'AI') => {
      setReveal('> ■ INITIALIZING GEMINI 3.1 FLASH LITE FORENSICS...\n> ■ Loading multimodal video pipeline...\n');
      setIsAnalyzing(true);
      setUserResult(null);

      const startMs = performance.now();

      try {
        // Phase 1: Silent HDI telemetry — B2B data pipeline
        await fetch('/api/vote', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            video_id: gcsVideoId(video),
            user_vote: vote,
            actual_truth: 'AI',
            latency_ms: String(Math.round(performance.now() - startMs)),
          }),
        });

        setReveal((prev) => prev + '> ■ HDI telemetry logged.\n> ■ Requesting forensic teardown from Vertex AI...\n');

        // Phase 2: Forensic AI reveal via Gemini arbiter — FIXED GCS URI
        const res = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            video_uri: `gs://headfade-cdn-origin/${gcsVideoId(video)}`,
            actual_truth: 'AI',
            user_vote: vote,
          }),
        });

        const elapsed = Math.round(performance.now() - startMs);

        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
          setReveal(
            `> ✗ FORENSIC ENGINE STATUS: ${res.status}\n> ${err.detail || 'Service initializing — video analysis requires uploaded media in GCS.'}`,
          );
          return;
        }

        const data = await res.json();

        // Determine if user was correct
        const groundTruth = 'AI'; // Current video ground truth
        const wasCorrect = vote === groundTruth;
        setUserResult(wasCorrect ? 'correct' : 'fooled');

        setReveal(
          `> ■ ANALYSIS COMPLETE [${elapsed}ms]\n` +
            `> ■ YOUR VOTE: ${vote} | GROUND TRUTH: ${groundTruth}\n` +
            `> ${wasCorrect ? '✓ CORRECT — You detected the deception.' : '✗ FOOLED — The AI deceived you.'}\n` +
            `${'─'.repeat(48)}\n` +
            `> GEMINI INTERNAL REASONING:\n${data.gemini_thoughts || '[CLASSIFIED — No internal monologue exposed.]'}\n` +
            `${'─'.repeat(48)}\n` +
            `> ARBITER VERDICT:\n${data.gemini_verdict || '[PENDING ANALYSIS]'}\n`,
        );
      } catch (e) {
        setReveal(`> ✗ FATAL FORENSIC ARBITER ERROR: ${e}`);
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

        {/* Loading overlay */}
        {isAnalyzing && (
          <div className="absolute inset-0 bg-black/60 flex items-center justify-center z-20">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
              <p className="text-cyan-400 text-xs font-mono tracking-wider animate-pulse">
                FORENSIC ANALYSIS IN PROGRESS
              </p>
            </div>
          </div>
        )}

        {/* Result badge */}
        {userResult && !isAnalyzing && (
          <div className={`absolute top-6 left-1/2 -translate-x-1/2 z-20 px-6 py-2 rounded-full font-bold text-sm tracking-widest animate-fade-in ${
            userResult === 'correct'
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-400/30'
              : 'bg-red-500/20 text-red-400 border border-red-400/30'
          }`}>
            {userResult === 'correct' ? '✓ CORRECT' : '✗ FOOLED'}
          </div>
        )}

        {/* The Deception Controls */}
        <div className="absolute bottom-8 w-full flex justify-between px-6 z-10">
          <button
            type="button"
            onClick={() => castVote('REAL')}
            disabled={isAnalyzing}
            className="glass-card px-8 py-4 rounded-xl text-emerald-400 font-bold tracking-widest hover:bg-emerald-400/10 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed active:scale-95"
          >
            REAL
          </button>
          <button
            type="button"
            onClick={() => castVote('AI')}
            disabled={isAnalyzing}
            className="glass-card px-8 py-4 rounded-xl text-cyan-400 font-bold tracking-widest hover:bg-cyan-400/10 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed active:scale-95"
          >
            AI
          </button>
        </div>
      </div>

      {/* The Terminal: Exposing Gemini's Internal Monologue to the User */}
      <div
        ref={terminalRef}
        className="mt-6 w-full max-w-md p-6 glass-card font-mono text-xs md:text-sm h-48 overflow-y-auto leading-relaxed text-zinc-400 whitespace-pre-wrap scroll-smooth"
      >
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
