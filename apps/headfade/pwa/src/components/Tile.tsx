'use client';

import Image from 'next/image';
import { useRef, useState } from 'react';

interface TileProps {
  title: string;
  author: string;
  views: string;
  time: string;
  thumbnail: string;
  authorAvatar?: string;
  hoverVideo?: string;
  accent?: boolean;
  duration?: string;
  onClick?: () => void;
  /* Voting */
  voteAI: number;
  voteHuman: number;
  userVote: 'ai' | 'human' | null;
  onVote: (choice: 'ai' | 'human') => void;
}

export function Tile({
  title,
  author,
  views,
  time,
  thumbnail,
  authorAvatar,
  hoverVideo,
  accent = false,
  duration,
  onClick,
  voteAI,
  voteHuman,
  userVote,
  onVote,
}: TileProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isHovering, setIsHovering] = useState(false);
  const [progressPercent, setProgressPercent] = useState(0);

  const totalVotes = voteAI + voteHuman;
  const aiPct = totalVotes > 0 ? Math.round((voteAI / totalVotes) * 100) : 50;
  const humanPct = 100 - aiPct;

  const handleMouseEnter = () => {
    setIsHovering(true);
    if (hoverVideo && videoRef.current) {
      videoRef.current.play().catch(() => {});
    }
  };

  const handleMouseLeave = () => {
    setIsHovering(false);
    setProgressPercent(0);
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.currentTime = 0;
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current?.duration) {
      setProgressPercent((videoRef.current.currentTime / videoRef.current.duration) * 100);
    }
  };

  return (
    <div className="group bg-transparent overflow-hidden cursor-pointer flex flex-col gap-0">
      {/* ── Thumbnail + overlays ── */}
      <button
        type="button"
        aria-label={title}
        className="relative aspect-video rounded-xl overflow-hidden transition-all duration-200 group-hover:rounded-t-xl group-hover:rounded-b-none w-full p-0 border-0"
        style={{ backgroundColor: '#F0F0FF' }}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={onClick}
      >
        {/* Thumbnail / video */}
        {hoverVideo ? (
          <>
            <Image
              src={thumbnail}
              alt={title}
              fill
              unoptimized
              className="w-full h-full object-cover absolute inset-0 transition-opacity duration-300 z-10"
              style={{ opacity: isHovering ? 0 : 1 }}
              loading="lazy"
            />
            <video
              ref={videoRef}
              src={hoverVideo}
              className="w-full h-full object-cover absolute inset-0 z-0"
              muted
              loop
              playsInline
              crossOrigin="anonymous"
              onTimeUpdate={handleTimeUpdate}
            />
          </>
        ) : (
          <Image
            src={thumbnail}
            alt={title}
            fill
            unoptimized
            className="w-full h-full object-cover"
            loading="lazy"
          />
        )}

        {/* Hover overlay tint */}
        <div
          className="absolute inset-0 pointer-events-none transition-colors duration-200"
          style={{ backgroundColor: isHovering ? 'rgba(0,0,0,0.05)' : 'transparent' }}
        />

        {/* Video scrub progress bar */}
        {isHovering && hoverVideo && (
          <div
            className="absolute bottom-0 left-0 right-0 h-[3px] z-20"
            style={{ backgroundColor: 'rgba(255,255,255,0.3)' }}
          >
            <div
              className="h-full transition-[width] duration-100"
              style={{ width: `${progressPercent}%`, backgroundColor: '#7C3AED' }}
            />
          </div>
        )}

        {/* Duration badge */}
        {duration && !isHovering && (
          <div
            aria-hidden="true"
            className="absolute bottom-2 right-2 bg-black/80 text-white text-[12px] px-1.5 py-0.5 rounded font-medium z-10"
          >
            {duration}
          </div>
        )}

        {/* Trending badge */}
        {accent && (
          <span
            aria-hidden="true"
            className="absolute top-2 left-2 text-white text-[10px] uppercase font-bold px-2 py-0.5 rounded-sm shadow-sm z-10"
            style={{ backgroundColor: '#7C3AED' }}
          >
            TRENDING
          </span>
        )}

        {/* AI Presumed badge — top right */}
        <div
          aria-hidden="true"
          className="absolute top-2 right-2 z-20 flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold text-white"
          style={{ backgroundColor: 'rgba(124,58,237,0.85)' }}
        >
          <span>🤖</span> AI Presumed
        </div>
      </button>

      {/* ── VOTE SECTION — always visible below thumbnail ── */}
      <div
        className="px-2 pt-2 pb-2.5 flex flex-col gap-1.5 rounded-b-xl"
        style={{
          backgroundColor: 'rgba(10,15,30,0.06)',
          borderTop: '1px solid rgba(124,58,237,0.15)',
        }}
      >
        {/* Vote distribution bar — always shown */}
        <div className="flex flex-col gap-0.5">
          <div
            className="flex w-full h-[5px] rounded-full overflow-hidden"
            style={{ backgroundColor: 'rgba(124,58,237,0.15)' }}
            title={`${aiPct}% think AI · ${humanPct}% think Human`}
          >
            <div
              className="h-full transition-[width] duration-500 rounded-full"
              style={{
                width: `${aiPct}%`,
                backgroundColor: userVote ? '#A78BFA' : 'rgba(167,139,250,0.45)',
              }}
            />
          </div>
          <div className="flex justify-between text-[10px]" style={{ color: '#4D627A' }}>
            <span>
              🤖 {aiPct}% AI{userVote ? ` (${voteAI.toLocaleString()})` : ''}
            </span>
            <span>
              👤 {humanPct}% Human{userVote ? ` (${voteHuman.toLocaleString()})` : ''}
            </span>
          </div>
        </div>

        {/* Vote buttons — always visible */}
        <div className="flex gap-1.5">
          <button
            type="button"
            id={`vote-ai-${title.replace(/\s+/g, '-').toLowerCase().slice(0, 20)}`}
            aria-label="AI-Made"
            aria-pressed={userVote === 'ai'}
            onClick={(e) => {
              e.stopPropagation();
              onVote('ai');
            }}
            className="flex-1 flex items-center justify-center gap-1 py-1 rounded-lg text-[11px] font-bold transition-all active:scale-95"
            style={{
              backgroundColor: userVote === 'ai' ? '#7C3AED' : 'rgba(124,58,237,0.12)',
              color: userVote === 'ai' ? '#fff' : '#5B21B6',
              border: `1.5px solid ${userVote === 'ai' ? '#7C3AED' : 'rgba(167,139,250,0.5)'}`,
            }}
          >
            🤖 AI-Made {userVote === 'ai' && '✓'}
          </button>
          <button
            type="button"
            id={`vote-human-${title.replace(/\s+/g, '-').toLowerCase().slice(0, 20)}`}
            aria-label="Human"
            aria-pressed={userVote === 'human'}
            onClick={(e) => {
              e.stopPropagation();
              onVote('human');
            }}
            className="flex-1 flex items-center justify-center gap-1 py-1 rounded-lg text-[11px] font-bold transition-all active:scale-95"
            style={{
              backgroundColor: userVote === 'human' ? '#0891B2' : 'rgba(8,145,178,0.12)',
              color: userVote === 'human' ? '#fff' : '#164E63',
              border: `1.5px solid ${userVote === 'human' ? '#0891B2' : 'rgba(103,232,249,0.45)'}`,
            }}
          >
            👤 Human {userVote === 'human' && '✓'}
          </button>
        </div>
      </div>

      {/* ── Meta row ── */}
      <div className="flex gap-3 px-0.5 pt-2">
        {authorAvatar ? (
          <Image
            src={authorAvatar}
            alt={author}
            width={32}
            height={32}
            unoptimized
            className="w-8 h-8 rounded-full object-cover flex-shrink-0 mt-0.5"
            loading="lazy"
          />
        ) : (
          <div
            className="w-8 h-8 rounded-full flex-shrink-0 mt-0.5 flex items-center justify-center text-xs font-bold uppercase"
            style={{ backgroundColor: '#EDE9FF', color: '#7C3AED' }}
          >
            {author.charAt(0)}
          </div>
        )}

        <div className="flex flex-col min-w-0 flex-1">
          <h3
            className="font-semibold text-[13px] leading-[18px] line-clamp-2"
            style={{ color: '#0A2540' }}
          >
            {title}
          </h3>
          <div className="mt-0.5 flex flex-col text-[12px]" style={{ color: '#4D627A' }}>
            <span className="hover:text-[#0A2540] transition-colors truncate">{author}</span>
            <div className="flex items-center gap-1">
              <span>{views} views</span>
              <span className="text-[10px]">•</span>
              <span>{time}</span>
            </div>
          </div>
        </div>

        <button
          type="button"
          aria-label={`More options for ${title}`}
          className="self-start mt-0.5 p-2 rounded-full transition-colors opacity-0 group-hover:opacity-100"
          style={{ color: '#4D627A' }}
          onClick={(e) => {
            e.stopPropagation();
          }}
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <title>More options</title>
            <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
          </svg>
        </button>
      </div>
    </div>
  );
}
