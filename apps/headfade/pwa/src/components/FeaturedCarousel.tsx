'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import type { RevealState } from '@/hooks/useTuringFeed';
import { useTuringFeed } from '@/hooks/useTuringFeed';
import { HeadFadePlayer } from './HeadFadePlayer';

interface FeaturedItem {
  id: string;
  title: string;
  author: string;
  thumbnail: string;
  src: string;
  views: string;
  voteAI: number;
  voteHuman: number;
  userVote: 'ai' | 'human' | null;
  /**
   * Ground-truth type of the video. In production this would come from
   * the creator's upload metadata (verified server-side). For now
   * we cycle deterministically so every other featured card is 'ai'.
   */
  actualType?: 'ai' | 'human';
  onVote: (choice: 'ai' | 'human') => void;
  isBookmarked: boolean;
  onBookmark: () => void;
}

interface FeaturedCarouselProps {
  items: FeaturedItem[];
  /** True when the user is signed in — gates the Cognitive Lock. */
  isAuthenticated?: boolean;
  /** Called when an unauthenticated user tries to vote. */
  onAuthRequired?: () => void;
  /** Forensic Elo rating to display in the HUD. */
  eloRating?: number;
}

/**
 * HeadFade Featured Carousel — Cognitive Lock Scroll Architecture
 *
 * TURING FEED MECHANICS:
 *   - Video loops infinitely until user casts a vote (Cognitive Lock).
 *   - After voting: green/red reveal flash for 800ms.
 *   - If Auto-Scroll is ON: advances to the next card automatically.
 *   - Visible "⚡ Auto-Scroll" toggle lets users disable this à la TikTok.
 *
 * SCROLL ARCHITECTURE (unchanged from v1):
 *   - Outer container is `items × SCROLL_PER_CARD` px tall → creates scroll space.
 *   - Inner panel is `position: sticky; top: HEADER_H` → stays pinned.
 *   - Dot nav + scroll-driven horizontal translate (not TikTok vertical snap).
 */
const SCROLL_PER_CARD = 700; // px of outer scroll per card transition
const HEADER_H = 108; // px — header + campaign banner combined height

export function FeaturedCarousel({
  items,
  isAuthenticated = false,
  onAuthRequired,
  eloRating,
}: FeaturedCarouselProps) {
  const outerRef = useRef<HTMLDivElement>(null);
  const [scrollProgress, setScrollProgress] = useState(0); // 0–1 across ALL cards
  const [scrollDrivenIdx, setScrollDrivenIdx] = useState(0); // index from scroll position

  /* ── Turing Feed state machine ── */
  const { autoScroll, revealState, setAutoScroll, handleVote, goToIndex } =
    useTuringFeed({
      count: items.length,
      isAuthenticated,
      onAuthRequired: onAuthRequired ?? (() => {}),
      onVoteAccepted: (index, choice) => {
        // Delegate to the item's own vote handler
        items[index]?.onVote(choice);
      },
      onAdvance: (nextIdx) => {
        // Programmatically scroll the outer container to the next card
        const outer = outerRef.current;
        if (!outer) return;
        const outerTop = outer.getBoundingClientRect().top + window.scrollY;
        window.scrollTo({ top: outerTop + nextIdx * SCROLL_PER_CARD, behavior: 'smooth' });
      },
    });

  /* ── Scroll listener — keeps scrollDrivenIdx in sync ── */
  useEffect(() => {
    const outer = outerRef.current;
    if (!outer) return;

    const handleScroll = () => {
      const rect = outer.getBoundingClientRect();
      const scrolled = Math.max(0, -rect.top);
      const totalScroll = SCROLL_PER_CARD * (items.length - 1);
      const p = Math.min(scrolled / totalScroll, 1);
      setScrollProgress(p);
      setScrollDrivenIdx(Math.min(Math.floor(scrolled / SCROLL_PER_CARD), items.length - 1));
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, [items.length]);

  /* Scroll position is the canonical display index.
   * TuringFeed's onAdvance callback programmatically scrolls the outer
   * container, which updates scrollDrivenIdx via the scroll listener.
   * Using Math.max previously prevented backward scrolling past the
   * TuringFeed-advanced index — this desync is now eliminated. */
  const activeIdx = scrollDrivenIdx;
  // Each card occupies (100 / items.length)% of the track's full width.
  // To place card N flush at the left edge we translateX by N × (100 / items.length)%.
  // Interpolating over [0,1] progress: progress × (N_cards - 1) × cardSlotPct.
  const translatePct = scrollProgress * (items.length - 1) * (100 / items.length);

  const jumpToCard = useCallback(
    (i: number) => {
      const outer = outerRef.current;
      if (!outer) return;
      const outerTop = outer.getBoundingClientRect().top + window.scrollY;
      window.scrollTo({ top: outerTop + i * SCROLL_PER_CARD, behavior: 'smooth' });
      goToIndex(i);
    },
    [goToIndex],
  );

  /* Derive ground-truth for reveal (alternating pattern for demo) */
  const getActualType = useCallback(
    (i: number): 'ai' | 'human' => items[i]?.actualType ?? (i % 2 === 0 ? 'ai' : 'human'),
    [items],
  );

  return (
    <section
      ref={outerRef}
      aria-label="Featured Videos Carousel"
      style={{ height: `${SCROLL_PER_CARD * items.length + HEADER_H + 100}px` }}
    >
      {/* Inner sticky panel */}
      <div
        className="sticky w-full overflow-hidden"
        style={{
          top: HEADER_H,
          height: `calc(100vh - ${HEADER_H}px)`,
          background: 'linear-gradient(160deg,#F8F7FF 0%,#F0EDFF 50%,#EAF4FF 100%)',
          borderBottom: '1px solid #E5E0FF',
          zIndex: 10,
        }}
      >
        {/* ── Elo HUD + AutoScroll Toggle (top-right overlay) ── */}
        <div className="absolute top-3 right-4 z-30 flex items-center gap-2">
          {/* Forensic Elo badge */}
          {eloRating !== undefined && (
            <div
              className="flex items-center gap-1.5 px-3 py-1 rounded-full text-[12px] font-bold"
              style={{
                background: 'linear-gradient(90deg,#7C3AED,#0891B2)',
                color: 'white',
                boxShadow: '0 2px 10px rgba(124,58,237,0.3)',
              }}
            >
              ⚡ Elo {eloRating.toLocaleString()}
            </div>
          )}

          {/* Auto-Scroll toggle */}
          <button
            type="button"
            aria-label={autoScroll ? 'Disable auto-scroll' : 'Enable auto-scroll'}
            aria-pressed={autoScroll}
            data-testid="autoscroll-toggle"
            onClick={() => setAutoScroll(!autoScroll)}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full text-[12px] font-bold transition-all duration-200 hover:scale-105"
            style={{
              background: autoScroll ? '#0891B2' : 'white',
              border: `1px solid ${autoScroll ? '#0891B2' : '#D1D5DB'}`,
              color: autoScroll ? 'white' : '#4B5563',
              boxShadow: '0 1px 6px rgba(0,0,0,0.08)',
            }}
          >
            <span style={{ fontSize: 14 }}>{autoScroll ? '⚡' : '✋'}</span>
            Auto-Scroll: {autoScroll ? 'ON' : 'OFF'}
          </button>
        </div>

        {/* Scroll-driven horizontal track */}
        <div
          className="flex h-full"
          style={{
            transform: `translateX(-${translatePct}%)`,
            transition: 'transform 60ms linear',
            willChange: 'transform',
            width: `${items.length * 100}%`,
          }}
        >
          {items.map((item, i) => {
            const isActive = i === activeIdx;
            /* revealState only applies to the active card */
            const cardReveal: RevealState = isActive ? revealState : null;

            return (
              <div
                key={item.id}
                className="flex-shrink-0 flex flex-col lg:flex-row items-center justify-center gap-8 px-4 lg:px-16 py-10"
                style={{ width: `${100 / items.length}%`, height: `calc(100vh - ${HEADER_H}px)` }}
              >
                {/* Player */}
                <div
                  className="w-full max-w-[680px]"
                  style={{ filter: 'drop-shadow(0 8px 32px rgba(124,58,237,0.12))' }}
                >
                  <HeadFadePlayer
                    src={item.src}
                    poster={item.thumbnail}
                    title={item.title}
                    voteAI={item.voteAI}
                    voteHuman={item.voteHuman}
                    userVote={item.userVote}
                    onVoteAI={() => handleVote('ai', getActualType(i))}
                    onVoteHuman={() => handleVote('human', getActualType(i))}
                    isBookmarked={item.isBookmarked}
                    onBookmark={item.onBookmark}
                    autoplay={i === 0}
                    revealState={cardReveal}
                  />
                </div>

                {/* Meta — right side (now light-mode) */}
                <div className="flex flex-col gap-4 max-w-[340px]" style={{ color: '#0A2540' }}>
                  <div className="flex items-center gap-2">
                    <span
                      className="px-2.5 py-1 rounded-full text-[11px] font-bold"
                      style={{
                        background: 'linear-gradient(90deg,#7C3AED,#0891B2)',
                        color: 'white',
                        animation: 'pulse 2s infinite',
                      }}
                    >
                      🤖 AI PRESUMED
                    </span>
                    <span className="text-[12px]" style={{ color: '#4D627A' }}>
                      {item.views} views
                    </span>
                  </div>
                  <h2 className="text-[24px] font-black leading-tight" style={{ color: '#0A2540' }}>
                    {item.title}
                  </h2>
                  <p className="text-[14px]" style={{ color: '#4D627A' }}>
                    by {item.author}
                  </p>

                  {/* Cognitive Lock hint — only show when not yet voted */}
                  {item.userVote === null && (
                    <div
                      className="flex items-center gap-2 px-4 py-3 rounded-xl text-[13px] font-medium"
                      style={{
                        background: 'rgba(124,58,237,0.08)',
                        border: '1px solid rgba(124,58,237,0.2)',
                        color: '#5B21B6',
                      }}
                    >
                      🔒 Vote to advance — the truth is locked until you decide.
                    </div>
                  )}
                  {item.userVote !== null && (
                    <div
                      className="flex items-center gap-2 px-4 py-3 rounded-xl text-[13px] font-bold"
                      style={{
                        background: 'rgba(5,150,105,0.08)',
                        border: '1px solid rgba(5,150,105,0.25)',
                        color: '#047857',
                      }}
                    >
                      ✓ You voted: {item.userVote === 'ai' ? '🤖 AI-Made' : '👤 Human'}
                    </div>
                  )}

                  {/* Card progress dots */}
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[11px] font-medium" style={{ color: '#9CA3AF' }}>
                      {i + 1} / {items.length}
                    </span>
                    <span className="text-[11px]" style={{ color: '#D1D5DB' }}>
                      · vote or scroll to explore
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* ── Dot nav ── */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2 z-20">
          {items.map((item, i) => (
            <button
              type="button"
              key={item.id ?? `dot-${i}`}
              aria-label={`Jump to featured video ${i + 1}`}
              onClick={() => jumpToCard(i)}
              className="rounded-full transition-all duration-300"
              style={{
                width: i === activeIdx ? 24 : 8,
                height: 8,
                backgroundColor: i === activeIdx ? '#7C3AED' : 'rgba(124,58,237,0.2)',
                boxShadow: i === activeIdx ? '0 0 8px rgba(124,58,237,0.4)' : 'none',
              }}
            />
          ))}
        </div>

        {/* ── Scroll progress bar (top) ── */}
        <div
          className="absolute top-0 left-0 h-[3px] transition-[width] duration-100"
          style={{
            width: `${scrollProgress * 100}%`,
            background: 'linear-gradient(90deg,#7C3AED,#0891B2)',
            borderRadius: '0 2px 2px 0',
          }}
        />

        {/* ── Scroll hint arrow ── */}
        <div
          className="absolute bottom-16 right-8 flex flex-col items-center gap-1 text-[11px] font-medium"
          style={{
            color: '#9CA3AF',
            animation: scrollProgress > 0.05 ? 'none' : 'bounce 1.5s infinite',
          }}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <title>Scroll down</title>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
          scroll
        </div>
      </div>
    </section>
  );
}
