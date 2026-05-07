'use client';

import React from 'react';

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
  content,
  type = 'thread',
  accent = false,
  onClick 
}: TileProps) {
  return (
    <div 
      onClick={onClick}
      className="group bg-transparent overflow-hidden cursor-pointer flex flex-col gap-3"
    >
      {/* Thumbnail Area - YouTube/TikTok edge-to-edge feel */}
      <div 
        className="relative aspect-video rounded-xl bg-[#F7F9FC] overflow-hidden group-hover:rounded-none transition-all duration-300"
        onMouseEnter={(e) => {
          if (hoverVideo) {
            const video = e.currentTarget.querySelector('video');
            if (video) video.play().catch(() => {});
          }
        }}
        onMouseLeave={(e) => {
          if (hoverVideo) {
            const video = e.currentTarget.querySelector('video');
            if (video) {
              video.pause();
              video.currentTime = 0;
            }
          }
        }}
      >
        {hoverVideo ? (
          <>
            <img 
              src={thumbnail} 
              alt={title} 
              className="w-full h-full object-cover absolute inset-0 group-hover:opacity-0 transition-opacity duration-300 z-10" 
            />
            <video 
              src={hoverVideo} 
              className="w-full h-full object-cover absolute inset-0 z-0" 
              muted 
              loop 
              playsInline
            />
          </>
        ) : (
          <img 
            src={thumbnail} 
            alt={title} 
            className="w-full h-full object-cover" 
          />
        )}
        
        {/* Google Tinting Trick */}
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors duration-200 pointer-events-none mix-blend-multiply" />

        {/* Duration / Type Badge */}
        {type === 'video' && (
          <div className="absolute bottom-1 right-1 bg-black/80 text-white text-[12px] px-1.5 py-0.5 rounded font-medium">
            12:41
          </div>
        )}

        {/* Trending Badge */}
        {accent && (
          <div className="absolute top-1 right-1 bg-[#cc0000] text-white text-[10px] uppercase font-bold px-1.5 py-0.5 rounded shadow-sm">
            TRENDING
          </div>
        )}
      </div>

      {/* Content - Avatar & Text side-by-side like YouTube */}
      <div className="flex gap-3">
        {/* Avatar Placeholder */}
        {authorAvatar ? (
          <img src={authorAvatar} alt={author} className="w-9 h-9 rounded-full object-cover flex-shrink-0 mt-0.5" />
        ) : (
          <div className="w-9 h-9 rounded-full bg-gray-200 flex-shrink-0 mt-0.5 flex items-center justify-center text-xs font-bold text-gray-500 uppercase">
            {author.charAt(0)}
          </div>
        )}
        
        <div className="flex flex-col">
          <h3 className="font-semibold text-[16px] leading-tight text-[#0A2540] line-clamp-2">
            {title}
          </h3>
          
          <div className="mt-1 flex flex-col text-[14px] text-[#4D627A]">
            <span className="hover:text-[#0A2540] transition-colors">{author}</span>
            <div className="flex items-center gap-1">
              <span>{views}</span>
              <span className="text-[10px]">•</span>
              <span>{time}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
