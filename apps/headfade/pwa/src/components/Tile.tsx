'use client';

import React, { useRef, useState } from 'react';

interface TileProps {
  title: string;
  author: string;
  views: string;
  time: string;
  thumbnail: string;
  authorAvatar?: string;
  hoverVideo?: string;
  content?: string;
  type?: 'thread' | 'video' | 'insight';
  accent?: boolean;
  duration?: string;
  onClick?: () => void;
}

export function Tile({
  title,
  author,
  views,
  time,
  thumbnail,
  authorAvatar,
  hoverVideo,
  type = 'thread',
  accent = false,
  duration,
  onClick,
}: TileProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isHovering, setIsHovering] = useState(false);
  const [progressPercent, setProgressPercent] = useState(0);

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
    if (videoRef.current && videoRef.current.duration) {
      setProgressPercent(
        (videoRef.current.currentTime / videoRef.current.duration) * 100,
      );
    }
  };

  return (
    <div
      onClick={onClick}
      className="group bg-transparent overflow-hidden cursor-pointer flex flex-col gap-3"
    >
      {/* Thumbnail Area */}
      <div
        className="relative aspect-video rounded-xl overflow-hidden transition-all duration-200 group-hover:rounded-none"
        style={{ backgroundColor: '#F7F9FC' }}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {hoverVideo ? (
          <>
            <img
              src={thumbnail}
              alt={title}
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
              onTimeUpdate={handleTimeUpdate}
            />
          </>
        ) : (
          <img
            src={thumbnail}
            alt={title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        )}

        {/* Hover overlay */}
        <div
          className="absolute inset-0 pointer-events-none transition-colors duration-200"
          style={{ backgroundColor: isHovering ? 'rgba(0,0,0,0.05)' : 'transparent' }}
        />

        {/* Video Progress Bar on Hover */}
        {isHovering && hoverVideo && (
          <div className="absolute bottom-0 left-0 right-0 h-[3px] z-20" style={{ backgroundColor: 'rgba(255,255,255,0.3)' }}>
            <div
              className="h-full transition-[width] duration-100"
              style={{ width: `${progressPercent}%`, backgroundColor: '#cc0000' }}
            />
          </div>
        )}

        {/* Duration Badge */}
        {duration && !isHovering && (
          <div className="absolute bottom-1 right-1 bg-black/80 text-white text-[12px] px-1.5 py-0.5 rounded font-medium z-10">
            {duration}
          </div>
        )}

        {/* Trending Badge */}
        {accent && (
          <div className="absolute top-2 left-2 text-white text-[10px] uppercase font-bold px-2 py-0.5 rounded-sm shadow-sm z-10" style={{ backgroundColor: '#cc0000' }}>
            TRENDING
          </div>
        )}

        {/* Watch Later + Add to Queue on Hover */}
        {isHovering && (
          <div className="absolute top-1 right-1 flex flex-col gap-1 z-20">
            <button
              className="w-7 h-7 rounded-sm flex items-center justify-center text-white transition-colors"
              style={{ backgroundColor: 'rgba(0,0,0,0.7)' }}
              onClick={(e) => { e.stopPropagation(); }}
              title="Watch later"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </button>
            <button
              className="w-7 h-7 rounded-sm flex items-center justify-center text-white transition-colors"
              style={{ backgroundColor: 'rgba(0,0,0,0.7)' }}
              onClick={(e) => { e.stopPropagation(); }}
              title="Add to queue"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" /></svg>
            </button>
          </div>
        )}
      </div>

      {/* Content — Avatar & Text (YouTube layout) */}
      <div className="flex gap-3">
        {authorAvatar ? (
          <img
            src={authorAvatar}
            alt={author}
            className="w-9 h-9 rounded-full object-cover flex-shrink-0 mt-0.5"
            loading="lazy"
          />
        ) : (
          <div
            className="w-9 h-9 rounded-full flex-shrink-0 mt-0.5 flex items-center justify-center text-xs font-bold uppercase"
            style={{ backgroundColor: '#E5E8ED', color: '#7A8FA6' }}
          >
            {author.charAt(0)}
          </div>
        )}

        <div className="flex flex-col min-w-0 flex-1">
          <h3
            className="font-semibold text-[14px] leading-[20px] line-clamp-2"
            style={{ color: '#0A2540' }}
          >
            {title}
          </h3>

          <div className="mt-0.5 flex flex-col text-[13px]" style={{ color: '#4D627A' }}>
            <span className="hover:text-[#0A2540] transition-colors truncate">{author}</span>
            <div className="flex items-center gap-1">
              <span>{views} views</span>
              <span className="text-[10px]">•</span>
              <span>{time}</span>
            </div>
          </div>
        </div>

        {/* 3-dot menu */}
        <button
          aria-label={`More options for ${title}`}
          className="self-start mt-1 p-1 rounded-full transition-colors opacity-0 group-hover:opacity-100"
          style={{ color: '#4D627A' }}
          onClick={(e) => { e.stopPropagation(); }}
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" /></svg>
        </button>
      </div>
    </div>
  );
}
