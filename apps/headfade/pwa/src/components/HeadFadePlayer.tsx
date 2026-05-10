'use client';

import type React from 'react';
import { useCallback, useEffect, useRef, useState } from 'react';
import type { RevealState } from '@/hooks/useTuringFeed';

export interface AdSlot {
  /** 'preroll' fires before play, 'midroll' fires at midpointSec */
  type: 'preroll' | 'midroll';
  midpointSec?: number;
  onAdRequest: (type: AdSlot['type']) => Promise<{ src: string; durationSec: number } | undefined>;
}

interface HeadFadePlayerProps {
  src: string;
  poster?: string;
  title?: string;
  adSlots?: AdSlot[];
  onVoteAI?: () => void;
  onVoteHuman?: () => void;
  userVote?: 'ai' | 'human' | null;
  voteAI?: number;
  voteHuman?: number;
  onBookmark?: () => void;
  isBookmarked?: boolean;
  autoplay?: boolean;
  /** Fired whenever the player crosses a quartile (25/50/75/100) */
  onQuartile?: (pct: 25 | 50 | 75 | 100) => void;
  /**
   * Cognitive Lock: when set, the player renders a full-screen reveal flash
   * overlay. 'correct' = green, 'incorrect' = red.
   * Parent clears this after REVEAL_DURATION_MS (handled by useTuringFeed).
   */
  revealState?: RevealState;
}

// biome-ignore lint/complexity/noExcessiveCognitiveComplexity: Video player coordinates ads, quartiles, preroll, midroll, and cognitive-lock — complexity is load-bearing.
export function HeadFadePlayer({
  src,
  poster,
  title,
  adSlots = [],
  onVoteAI,
  onVoteHuman,
  userVote = null,
  voteAI = 0,
  voteHuman = 0,
  onBookmark,
  isBookmarked = false,
  autoplay = false,
  onQuartile,
  revealState = null,
}: HeadFadePlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const adVideoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [playing, setPlaying] = useState(false);
  const [muted, setMuted] = useState(true);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [showControls, setShowControls] = useState(true);
  const [adActive, setAdActive] = useState(false);
  const [adSrc, setAdSrc] = useState<string | null>(null);
  const [adCountdown, setAdCountdown] = useState(0);
  const [prerollFired, setPrerollFired] = useState(false);
  const [midrollFired, setMidrollFired] = useState(false);
  const [quartilesFired, setQuartilesFired] = useState(new Set<number>());
  const controlsTimerRef = useRef<ReturnType<typeof setTimeout>>();

  const totalVotes = voteAI + voteHuman;
  const aiPct = totalVotes > 0 ? Math.round((voteAI / totalVotes) * 100) : 50;
  const humanPct = 100 - aiPct;

  /* ── Auto-hide controls ── */
  const resetControlsTimer = useCallback(() => {
    setShowControls(true);
    clearTimeout(controlsTimerRef.current);
    controlsTimerRef.current = setTimeout(() => {
      if (playing) setShowControls(false);
    }, 2500);
  }, [playing]);

  /* ── Ad injection ── */
  const fireAd = useCallback(
    async (type: AdSlot['type']) => {
      const slot = adSlots.find((s) => s.type === type);
      if (!slot) return;
      const ad = await slot.onAdRequest(type);
      if (!ad) return;
      videoRef.current?.pause();
      setAdSrc(ad.src);
      setAdActive(true);
      setAdCountdown(ad.durationSec);
      const interval = setInterval(() => {
        setAdCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            setAdActive(false);
            setAdSrc(null);
            videoRef.current?.play().catch(() => {});
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    },
    [adSlots],
  );

  /* ── Preroll on first play ── */
  const handlePlay = useCallback(async () => {
    if (!prerollFired) {
      setPrerollFired(true);
      await fireAd('preroll');
    }
    videoRef.current?.play().catch(() => {});
    setPlaying(true);
    resetControlsTimer();
  }, [fireAd, prerollFired, resetControlsTimer]);

  const handlePause = useCallback(() => {
    videoRef.current?.pause();
    setPlaying(false);
    setShowControls(true);
  }, []);

  const togglePlay = useCallback(() => {
    if (playing) handlePause();
    else handlePlay();
  }, [playing, handlePause, handlePlay]);

  /* ── Progress + midroll + quartiles ── */
  const handleTimeUpdate = useCallback(() => {
    const vid = videoRef.current;
    if (!vid?.duration) return;
    const pct = (vid.currentTime / vid.duration) * 100;
    setProgress(pct);
    setCurrentTime(vid.currentTime);

    // Midroll
    const midSlot = adSlots.find((s) => s.type === 'midroll');
    if (midSlot && !midrollFired && midSlot.midpointSec && vid.currentTime >= midSlot.midpointSec) {
      setMidrollFired(true);
      fireAd('midroll');
    }

    // Quartiles
    for (const q of [25, 50, 75, 100] as const) {
      if (!quartilesFired.has(q) && pct >= q) {
        setQuartilesFired((prev) => new Set(Array.from(prev).concat([q])));
        onQuartile?.(q);
      }
    }
  }, [adSlots, midrollFired, fireAd, quartilesFired, onQuartile]);

  /**
   * Cognitive Lock: on ended, loop the video instead of advancing.
   * The video loops until the user casts a vote. The parent's useTuringFeed
   * handles the actual advance after reveal flash completes.
   */
  const handleEnded = useCallback(() => {
    const vid = videoRef.current;
    if (vid) {
      vid.currentTime = 0;
      vid.play().catch(() => {});
      // Reset quartiles so they can fire again on next loop
      setQuartilesFired(new Set());
    }
  }, []);

  /* ── Autoplay ── */
  useEffect(() => {
    if (autoplay) handlePlay();
  }, [handlePlay, autoplay]); // eslint-disable-line react-hooks/exhaustive-deps

  const fmt = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, '0')}`;
  };

  const seek = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = (e.clientX - rect.left) / rect.width;
    if (videoRef.current) videoRef.current.currentTime = ratio * videoRef.current.duration;
  };

  /* Reveal flash colours */
  const revealBg =
    revealState === 'correct'
      ? 'rgba(16,185,129,0.35)' // emerald-500
      : revealState === 'incorrect'
        ? 'rgba(239,68,68,0.35)' // red-500
        : null;

  return (
    <section
      ref={containerRef}
      id="headfade-player"
      aria-label="Video player"
      className="relative w-full aspect-video bg-black rounded-2xl overflow-hidden group select-none"
      onMouseMove={resetControlsTimer}
      onMouseLeave={() => {
        if (playing) setShowControls(false);
      }}
    >
      {/* Main video */}
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        muted={muted}
        playsInline
        preload="metadata"
        className="w-full h-full object-cover"
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={() => setDuration(videoRef.current?.duration ?? 0)}
        onEnded={handleEnded}
        onClick={togglePlay}
      />

      {/* ── Cognitive Lock Reveal Flash ── */}
      {revealBg && (
        <div
          role="status"
          aria-live="polite"
          className="absolute inset-0 z-40 flex flex-col items-center justify-center gap-3 pointer-events-none"
          style={{
            backgroundColor: revealBg,
            backdropFilter: 'blur(2px)',
            animation: 'headfade-flash-in 200ms ease-out',
          }}
        >
          <span className="text-5xl" aria-hidden="true">
            {revealState === 'correct' ? '✅' : '❌'}
          </span>
          <span
            className="text-[18px] font-black text-white"
            style={{ textShadow: '0 2px 8px rgba(0,0,0,0.5)' }}
          >
            {revealState === 'correct' ? 'You spotted it!' : 'You were fooled!'}
          </span>
        </div>
      )}

      {/* Ad overlay */}
      {adActive && adSrc && (
        <div className="absolute inset-0 z-50 bg-black">
          <video
            ref={adVideoRef}
            src={adSrc}
            autoPlay
            muted={muted}
            playsInline
            className="w-full h-full object-cover"
          />
          <div
            className="absolute top-3 right-3 px-2 py-1 rounded text-white text-[11px] font-bold"
            style={{ backgroundColor: 'rgba(0,0,0,0.6)' }}
          >
            Ad · {adCountdown}s
          </div>
        </div>
      )}

      {/* Controls */}
      <div
        className="absolute inset-0 flex flex-col justify-between transition-opacity duration-300 pointer-events-none"
        style={{ opacity: showControls || !playing ? 1 : 0 }}
      >
        {/* Top bar */}
        <div className="pointer-events-auto flex items-start justify-between p-3">
          {title && (
            <span
              className="text-white text-[13px] font-semibold drop-shadow line-clamp-2 max-w-[60%]"
              style={{ textShadow: '0 1px 4px rgba(0,0,0,0.6)' }}
            >
              {title}
            </span>
          )}
          <div className="flex items-center gap-2 ml-auto">
            {/* Bookmark */}
            {onBookmark && (
              <button
                type="button"
                aria-label={isBookmarked ? 'Remove bookmark' : 'Bookmark video'}
                onClick={onBookmark}
                className="p-2.5 rounded-full transition-colors"
                style={{ backgroundColor: isBookmarked ? '#7C3AED' : 'rgba(0,0,0,0.45)' }}
              >
                <svg
                  className="w-4 h-4 text-white"
                  fill={isBookmarked ? 'currentColor' : 'none'}
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <title>{isBookmarked ? 'Remove bookmark' : 'Bookmark'}</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
                  />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Center play/pause */}
        <button
          type="button"
          aria-label={playing ? 'Pause video' : 'Play video'}
          onClick={togglePlay}
          className="pointer-events-auto absolute inset-0 flex items-center justify-center"
        >
          {!playing && (
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center"
              style={{ backgroundColor: 'rgba(124,58,237,0.85)' }}
            >
              <svg
                className="w-7 h-7 text-white ml-1"
                fill="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <title>Play</title>
                <path d="M8 5v14l11-7z" />
              </svg>
            </div>
          )}
        </button>

        {/* Bottom bar: vote + scrub + mute */}
        <div
          className="pointer-events-auto flex flex-col gap-2 p-3"
          style={{ background: 'linear-gradient(to top, rgba(0,0,0,0.75) 0%, transparent 100%)' }}
        >
          {/* Vote buttons — ghost opacity until voted */}
          <div className="flex gap-2">
            <button
              type="button"
              aria-label="AI-Made"
              aria-pressed={userVote === 'ai'}
              data-testid="vote-ai-btn"
              onClick={onVoteAI}
              className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg text-[11px] font-bold transition-all duration-200"
              style={{
                backgroundColor: userVote === 'ai' ? '#7C3AED' : 'rgba(124,58,237,0.18)',
                color: '#fff',
                border: `1px solid ${userVote === 'ai' ? '#7C3AED' : 'rgba(167,139,250,0.45)'}`,
                backdropFilter: 'blur(4px)',
                opacity: userVote === null ? 0.7 : 1,
              }}
            >
              🤖 AI-Made {userVote === 'ai' && '✓'}
            </button>
            <button
              type="button"
              aria-label="Human"
              aria-pressed={userVote === 'human'}
              data-testid="vote-human-btn"
              onClick={onVoteHuman}
              className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg text-[11px] font-bold transition-all duration-200"
              style={{
                backgroundColor: userVote === 'human' ? '#0891B2' : 'rgba(8,145,178,0.18)',
                color: '#fff',
                border: `1px solid ${userVote === 'human' ? '#0891B2' : 'rgba(103,232,249,0.4)'}`,
                backdropFilter: 'blur(4px)',
                opacity: userVote === null ? 0.7 : 1,
              }}
            >
              👤 Human {userVote === 'human' && '✓'}
            </button>
          </div>

          {/* Vote result bar — only shown after voting */}
          {userVote && (
            <div className="flex flex-col gap-0.5">
              <div
                className="flex w-full h-[4px] rounded-full overflow-hidden"
                style={{ backgroundColor: 'rgba(255,255,255,0.2)' }}
              >
                <div
                  className="h-full transition-[width] duration-500 rounded-full"
                  style={{ width: `${aiPct}%`, backgroundColor: '#A78BFA' }}
                />
              </div>
              <div className="flex justify-between text-[10px] text-white/80">
                <span>
                  🤖 {aiPct}% · {voteAI.toLocaleString()}
                </span>
                <span>
                  👤 {humanPct}% · {voteHuman.toLocaleString()}
                </span>
              </div>
            </div>
          )}

          {/* Scrub + time + mute */}
          <div className="flex items-center gap-2">
            <span className="text-white text-[10px] tabular-nums">{fmt(currentTime)}</span>
            <button
              type="button"
              aria-label="Seek video"
              className="flex-1 h-[28px] rounded-full cursor-pointer relative flex items-center"
              style={{ backgroundColor: 'transparent', padding: '12px 0', border: 'none' }}
              onClick={seek as unknown as React.MouseEventHandler<HTMLButtonElement>}
              onKeyDown={(e) => {
                if (e.key === 'ArrowRight' && videoRef.current)
                  videoRef.current.currentTime = Math.min(
                    videoRef.current.duration,
                    videoRef.current.currentTime + 5,
                  );
                if (e.key === 'ArrowLeft' && videoRef.current)
                  videoRef.current.currentTime = Math.max(0, videoRef.current.currentTime - 5);
              }}
            >
              <div
                className="absolute left-0 right-0 h-[4px] rounded-full"
                style={{
                  backgroundColor: 'rgba(255,255,255,0.3)',
                  top: '50%',
                  transform: 'translateY(-50%)',
                }}
              >
                <div
                  className="h-full rounded-full transition-[width] duration-100"
                  style={{ width: `${progress}%`, backgroundColor: '#7C3AED' }}
                />
              </div>
            </button>
            <span className="text-white text-[10px] tabular-nums">{fmt(duration)}</span>
            <button
              type="button"
              aria-label={muted ? 'Unmute' : 'Mute'}
              onClick={() => setMuted((m) => !m)}
              className="p-2 rounded-full"
              style={{ backgroundColor: 'rgba(0,0,0,0.4)' }}
            >
              <svg
                className="w-3.5 h-3.5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <title>{muted ? 'Unmute' : 'Mute'}</title>
                {muted ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15.536 8.464a5 5 0 010 7.072M12 6v12m-5.657-5.657A4 4 0 016.343 12M9 9l6 6"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
