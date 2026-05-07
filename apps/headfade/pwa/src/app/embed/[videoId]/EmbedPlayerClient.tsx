'use client';

import { useEffect, useState } from 'react';

/* =======================================================================
 * HeadFade Embed Player — The Zero-CAC Distribution Engine
 * -----------------------------------------------------------------------
 * Embeddable <iframe> forensic video player for publishers.
 * When major news outlets write about a viral deepfake, they embed this
 * player instead of a raw X/TikTok link.
 *
 * Usage (Publisher-facing):
 *   <iframe
 *     src="https://headfade.com/embed/{videoId}"
 *     width="560" height="400"
 *     frameborder="0" allowfullscreen
 *   ></iframe>
 *
 * Revenue funnel: Viewer → [View Forensics] → CTA → headfade.com signup
 * ======================================================================= */

interface EmbedVideoData {
  id: string;
  cdnUrl: string;
  models: string[];
  hdiScore: number;
  parentCreator: string;
  remixDepth: number;
  title: string;
}

/** Minimal API client for embed data — runs against Cloud Run */
async function fetchEmbedData(videoId: string): Promise<EmbedVideoData> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/embed/${videoId}`);
    if (!res.ok) throw new Error(`API ${res.status}`);
    return await res.json();
  } catch (_err: unknown) {
    // Fallback for demo / static export — API unavailable in static mode
    console.debug('[HeadFade Embed] API unreachable, using demo fallback', _err);
    return {
      id: videoId,
      cdnUrl: '/media/genesis_clip_01.mp4',
      models: ['Sora 2.0', 'Runway Gen-3', 'ElevenLabs'],
      hdiScore: 87,
      parentCreator: 'genesis_artist',
      remixDepth: 3,
      title: 'Synthetic Media Specimen',
    };
  }
}

export default function EmbedPlayerClient({ videoId }: { videoId: string }) {
  const [videoData, setVideoData] = useState<EmbedVideoData | null>(null);
  const [showMatrix, setShowMatrix] = useState(false);
  const [impressionLogged, setImpressionLogged] = useState(false);

  useEffect(() => {
    fetchEmbedData(videoId).then(setVideoData);
  }, [videoId]);

  // Silent impression telemetry — B2B data pipeline
  useEffect(() => {
    if (videoData && !impressionLogged) {
      fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/telemetry/embed-view`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          videoId: videoData.id,
          referrer: typeof document !== 'undefined' ? document.referrer : '',
          timestamp: new Date().toISOString(),
        }),
      }).catch(() => {}); // Fire-and-forget
      setImpressionLogged(true);
    }
  }, [videoData, impressionLogged]);

  if (!videoData) {
    return (
      <div className="flex items-center justify-center h-screen bg-black">
        <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="relative w-full h-screen bg-black font-mono overflow-hidden">
      {/* Cloud CDN Native Video Player */}
      <video
        className="w-full h-full object-contain"
        src={videoData.cdnUrl}
        controls
        controlsList="nodownload"
        playsInline
        autoPlay
        muted
        loop
        title="Embedded Video Player"
        aria-label="Embedded Video Player"
      />

      {/* HeadFade Branding & Toggle Bar */}
      <div className="absolute top-3 left-3 right-3 z-10 flex items-center justify-between">
        <div className="flex gap-2 items-center">
          <span className="bg-red-600 text-white text-[9px] font-bold px-2 py-0.5 rounded-sm tracking-[0.15em] uppercase">
            AI-Presumed
          </span>
          <span className="text-zinc-400 text-[9px] tracking-wider">{videoData.title}</span>
        </div>
        <button
          type="button"
          aria-label={showMatrix ? 'Hide forensics overlay' : 'View forensics overlay'}
          onClick={() => setShowMatrix(!showMatrix)}
          className="bg-black/80 text-[#00FF41] text-[9px] border border-[#00FF41]/40 px-2.5 py-1 rounded-sm hover:bg-[#00FF41] hover:text-black transition-all duration-200 tracking-wider"
        >
          {showMatrix ? '[Hide Data]' : '[View Forensics ▸]'}
        </button>
      </div>

      {/* The Forensics Overlay — The Traffic Funnel */}
      <div
        className={`absolute right-0 top-0 bottom-0 w-[280px] bg-black/95 border-l border-[#00FF41]/20 p-4 text-white overflow-y-auto shadow-2xl backdrop-blur-sm transition-transform duration-300 ease-out ${
          showMatrix ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Detected Stack */}
        <div className="mb-5">
          <h3 className="text-[10px] text-zinc-400 uppercase tracking-[0.2em] mb-1.5">
            Detected AI Stack
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {videoData.models.map((model) => (
              <span
                key={model}
                className="text-[10px] bg-cyan-400/10 text-cyan-400 border border-cyan-400/20 px-2 py-0.5 rounded-sm"
              >
                {model}
              </span>
            ))}
          </div>
        </div>

        {/* Human Deception Index */}
        <div className="mb-5">
          <h3 className="text-[10px] text-zinc-400 uppercase tracking-[0.2em] mb-1.5">
            Human Deception Index
          </h3>
          <div className="flex items-end gap-2">
            <span className="text-3xl font-bold text-red-500 leading-none">
              {videoData.hdiScore}%
            </span>
            <span className="text-[10px] text-zinc-400 pb-0.5">of humans fooled</span>
          </div>
          {/* HDI bar */}
          <div className="mt-2 h-1.5 bg-zinc-900 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-1000"
              style={{
                width: `${videoData.hdiScore}%`,
                background: `linear-gradient(90deg, #00FF41 0%, #ff4444 ${videoData.hdiScore}%)`,
              }}
            />
          </div>
        </div>

        {/* Remix Lineage */}
        <div className="mb-5">
          <h3 className="text-[10px] text-zinc-400 uppercase tracking-[0.2em] mb-1.5">
            Remix Lineage
          </h3>
          <p className="text-[11px] text-zinc-300">
            ↳ Forked from <span className="text-cyan-400">@{videoData.parentCreator}</span>
          </p>
          <p className="text-[10px] text-zinc-400 mt-1">
            Depth: {videoData.remixDepth} generations
          </p>
        </div>

        {/* Cognitive Telemetry Badge */}
        <div className="mb-5 p-3 border border-zinc-800 rounded-lg bg-zinc-900/50">
          <h3 className="text-[10px] text-zinc-400 uppercase tracking-[0.2em] mb-1.5">
            Cognitive Telemetry
          </h3>
          <p className="text-[10px] text-zinc-400 leading-relaxed">
            Clean RLHF behavioral data. Not algorithmically lobotomized. HeadFade demands active
            forensics — not passive consumption.
          </p>
        </div>

        {/* Core CTA — drives users back to main platform */}
        <a
          href={`https://headfade.com/v/${videoData.id}?ref=embed`}
          target="_blank"
          rel="noopener noreferrer"
          className="block w-full text-center bg-[#00FF41] text-black py-2.5 text-[11px] font-bold rounded-sm hover:bg-white transition-colors tracking-wider"
        >
          Unlock Full Prompt &amp; Lineage ↱
        </a>

        <p className="text-[9px] text-zinc-400 text-center mt-2">
          Free sandbox · $19.99/mo Premium Forensics
        </p>
      </div>

      {/* Bottom HeadFade branding bar */}
      <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-black/90 to-transparent flex items-end justify-between px-3 pb-1.5 z-10">
        <span className="text-[10px] font-bold tracking-[0.2em] text-gradient">HEADFADE</span>
        <a
          href={`https://headfade.com/v/${videoData.id}?ref=embed`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[9px] text-zinc-400 hover:text-white transition-colors"
        >
          headfade.com
        </a>
      </div>
    </div>
  );
}
