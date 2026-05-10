'use client';

import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

interface EmbedPlayerProps {
  videoId: string;
  autoPlay?: boolean;
}

export default function EmbedPlayer({ videoId, autoPlay = false }: EmbedPlayerProps) {
  const [showForensics, setShowForensics] = useState(true);
  const [isPlaying, setIsPlaying] = useState(autoPlay);

  // Fetch live forensics data via MCP
  const { data: forensics, isLoading } = useQuery({
    queryKey: ['forensics', videoId],
    queryFn: async () => {
      const res = await fetch('/api/mcp/verify_synthetic_video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ videoId }),
      });
      return res.json();
    },
  });

  const togglePlay = () => setIsPlaying(!isPlaying);

  return (
    <div className="relative w-full max-w-[640px] mx-auto rounded-2xl overflow-hidden shadow-2xl bg-black">
      {/* Video Container */}
      <div className="relative aspect-video bg-zinc-950 flex items-center justify-center">
        {/* Placeholder for actual video (in production: use HLS or signed GCS URL) */}
        <div className="text-white text-center">
          <div className="text-6xl mb-4">🎥</div>
          <p className="text-sm opacity-70">HeadFade Synthetic Video</p>
          <p className="text-xs text-zinc-500 mt-1">ID: {videoId}</p>
        </div>

        {/* Play Overlay */}
        {!isPlaying && (
          <button
            onClick={togglePlay}
            className="absolute inset-0 flex items-center justify-center bg-black/40 hover:bg-black/60 transition-all"
          >
            <div className="w-20 h-20 rounded-full bg-white/90 flex items-center justify-center">
              <div className="w-0 h-0 border-l-[18px] border-l-black border-y-[12px] border-y-transparent ml-1" />
            </div>
          </button>
        )}

        {/* Live Forensics Badge */}
        <div className="absolute top-4 right-4 bg-black/80 text-white text-xs px-3 py-1 rounded-full flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          LIVE FORENSICS
        </div>
      </div>

      {/* Forensics Panel */}
      {showForensics && (
        <div className="bg-zinc-950 border-t border-zinc-800 p-4 text-sm text-white">
          <div className="flex justify-between items-center mb-3">
            <div className="font-semibold">TRUTH LAYER</div>
            <button
              onClick={() => setShowForensics(false)}
              className="text-xs opacity-60 hover:opacity-100"
            >
              HIDE
            </button>
          </div>

          {isLoading ? (
            <div className="text-zinc-500">Analyzing video stack...</div>
          ) : forensics ? (
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-zinc-400">Human Deception Index</span>
                <span className="font-mono text-emerald-400">{forensics.hdiScore}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Foundational Models</span>
                <span className="font-mono text-xs">{forensics.modelsUsed?.join(' + ')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Remix Parent</span>
                <span className="font-mono text-xs">{forensics.parentCreatorId}</span>
              </div>
            </div>
          ) : (
            <div className="text-red-400">Failed to load forensics data</div>
          )}
        </div>
      )}

      {/* Bottom Bar */}
      <div className="bg-black px-4 py-2 text-xs text-white/60 flex justify-between items-center">
        <div>HeadFade • Zero Filter Bubbles</div>
        <button
          onClick={() => setShowForensics(!showForensics)}
          className="hover:text-white transition-colors"
        >
          {showForensics ? 'Hide Forensics' : 'Show Forensics'}
        </button>
      </div>
    </div>
  );
}
