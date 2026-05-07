'use client';
import React, { useRef, useEffect, useState } from 'react';
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
  onVote: (choice: 'ai' | 'human') => void;
  isBookmarked: boolean;
  onBookmark: () => void;
}

interface FeaturedCarouselProps {
  items: FeaturedItem[];
}

/**
 * HeadFade Featured Carousel
 *
 * UNIQUE DIFFERENTIATORS vs TikTok/YouTube:
 *   - Horizontal scroll-driven translate (NOT TikTok's vertical snap)
 *   - AI-vs-Human vote embedded directly in player chrome
 *   - "AI Presumed" cognitive uncertainty framing
 *   - Dot indicators show vote distribution, not likes/views
 *
 * TikTok protected: vertical snap, FYP algorithm, Duet, sound sync
 * YouTube protected: Subscribe button, thumbs up/down, chapters, chapters
 * HeadFade protectable: AI-presumed framing, vote bar mechanics, uncertainty UX
 */
export function FeaturedCarousel({ items }: FeaturedCarouselProps) {
  const trackRef = useRef<HTMLDivElement>(null);
  const sectionRef = useRef<HTMLDivElement>(null);
  const [activeIdx, setActiveIdx] = useState(0);
  const [translateX, setTranslateX] = useState(0);

  // Scroll-driven horizontal slide — scrolling down moves to next card
  useEffect(() => {
    const section = sectionRef.current;
    if (!section) return;
    const handleScroll = () => {
      const rect = section.getBoundingClientRect();
      const sectionTop = window.scrollY + rect.top;
      const scrolled = Math.max(0, window.scrollY - sectionTop);
      const cardW = section.offsetWidth;
      // Each 120px of scroll advances one card
      const idx = Math.min(Math.floor(scrolled / 120), items.length - 1);
      const frac = Math.min((scrolled % 120) / 120, 1);
      const raw = idx * cardW + frac * cardW;
      setTranslateX(raw);
      setActiveIdx(idx);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [items.length]);

  return (
    <section
      ref={sectionRef}
      className="relative w-full overflow-hidden"
      style={{ minHeight: '80vh', background: 'linear-gradient(135deg,#0A0A1A 0%,#1A0A2E 100%)' }}
      aria-label="Featured Videos"
    >
      {/* Scroll-driven track */}
      <div
        ref={trackRef}
        className="flex h-full"
        style={{ transform: `translateX(-${translateX}px)`, transition: 'transform 80ms linear', willChange: 'transform' }}
      >
        {items.map((item, i) => (
          <div
            key={item.id}
            className="flex-shrink-0 w-full flex flex-col lg:flex-row items-center justify-center gap-8 px-4 lg:px-16 py-10"
            style={{ minWidth: '100%' }}
          >
            {/* Player — left/center */}
            <div className="w-full max-w-[680px]">
              <HeadFadePlayer
                src={item.src}
                poster={item.thumbnail}
                title={item.title}
                voteAI={item.voteAI}
                voteHuman={item.voteHuman}
                userVote={item.userVote}
                onVoteAI={() => item.onVote('ai')}
                onVoteHuman={() => item.onVote('human')}
                isBookmarked={item.isBookmarked}
                onBookmark={item.onBookmark}
                autoplay={i === 0}
              />
            </div>
            {/* Meta — right */}
            <div className="flex flex-col gap-4 max-w-[340px] text-white">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold" style={{ background: 'rgba(124,58,237,0.7)' }}>
                  🤖 AI PRESUMED
                </span>
                <span className="text-white/50 text-[12px]">{item.views} views</span>
              </div>
              <h2 className="text-[22px] font-black leading-tight">{item.title}</h2>
              <p className="text-white/60 text-[14px]">by {item.author}</p>
              <p className="text-[13px] text-white/50 italic">
                Is this real or AI? Only you can tell. Cast your vote below.
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Dot nav */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 z-20">
        {items.map((_, i) => (
          <button
            key={i}
            aria-label={`Go to featured video ${i + 1}`}
            onClick={() => window.scrollTo({ top: i * 120, behavior: 'smooth' })}
            className="rounded-full transition-all duration-300"
            style={{
              width: i === activeIdx ? 24 : 8,
              height: 8,
              backgroundColor: i === activeIdx ? '#7C3AED' : 'rgba(255,255,255,0.35)',
            }}
          />
        ))}
      </div>

      {/* Scroll hint */}
      <div className="absolute bottom-14 right-6 flex flex-col items-center gap-1 text-white/40 text-[11px] animate-bounce">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
        scroll
      </div>
    </section>
  );
}
