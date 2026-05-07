'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useInView } from 'react-intersection-observer';
import { Tile } from '@/components/Tile';

/* ─── Brand Palette (Google tinting trick) ─── */
const brand = {
  bg: '#FFFFFF',
  bgSubtle: '#F7F9FC',
  bgHover: '#EEF1F6',
  textPrimary: '#0A2540',
  textSecondary: '#4D627A',
  textMuted: '#7A8FA6',
  accent: '#cc0000',
  border: '#E5E8ED',
  chipActive: '#0A2540',
  chipDefault: '#F2F4F7',
} as const;

/* ─── Category Chips ─── */
const categories = [
  'All',
  'Trending',
  'AI Generated',
  'Music',
  'Gaming',
  'Live',
  'News',
  'Comedy',
  'Sports',
  'Science',
  'Fashion',
  'Cooking',
  'Podcasts',
  'Film',
  'Education',
  'Recently uploaded',
];

/* ─── Large Initial Dataset — 24 tiles for dense grid ─── */
const initialThreads = [
  {
    title: 'How AI Is Changing the Way We Create Music Forever',
    author: 'TechVision',
    views: '2.4M',
    time: '3h ago',
    thumbnail: 'https://picsum.photos/id/1015/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=techvision',
    hoverVideo: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    type: 'video' as const,
    accent: true,
    duration: '14:23',
  },
  {
    title: 'I Built a House Using Only AI-Generated Blueprints',
    author: 'Builder Mike',
    views: '1.8M',
    time: '5h ago',
    thumbnail: 'https://picsum.photos/id/1029/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=buildermike',
    hoverVideo: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    type: 'video' as const,
    duration: '22:17',
  },
  {
    title: 'The Science Behind Why Viral Videos Go Viral',
    author: 'Veritasium',
    views: '4.1M',
    time: '1d ago',
    thumbnail: 'https://picsum.photos/id/1036/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=veritasium',
    type: 'video' as const,
    duration: '18:05',
  },
  {
    title: 'Making the Perfect Sourdough in Under 4 Hours',
    author: 'Joshua Weissman',
    views: '890K',
    time: '6h ago',
    thumbnail: 'https://picsum.photos/id/292/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=joshuaw',
    hoverVideo: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    type: 'video' as const,
    duration: '12:33',
  },
  {
    title: 'Why Every Major Studio Is Now Using AI Actors',
    author: 'Film Theory',
    views: '3.2M',
    time: '8h ago',
    thumbnail: 'https://picsum.photos/id/1074/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=filmtheory',
    type: 'video' as const,
    accent: true,
    duration: '25:41',
  },
  {
    title: 'Day in My Life: Remote Developer in Tokyo',
    author: 'Joma Tech',
    views: '1.5M',
    time: '2d ago',
    thumbnail: 'https://picsum.photos/id/1005/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=jomatech',
    hoverVideo: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    type: 'video' as const,
    duration: '10:08',
  },
  {
    title: 'The Biggest Mistakes People Make When Starting a Business',
    author: 'Graham Stephan',
    views: '2.1M',
    time: '12h ago',
    thumbnail: 'https://picsum.photos/id/106/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=grahamstephan',
    type: 'video' as const,
    duration: '16:54',
  },
  {
    title: 'We Tested 50 AI Image Generators — Here Are the Results',
    author: 'MKBHD',
    views: '5.7M',
    time: '3d ago',
    thumbnail: 'https://picsum.photos/id/160/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=mkbhd',
    hoverVideo: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    type: 'video' as const,
    duration: '21:12',
  },
  {
    title: 'How to Actually Get Good at Chess (No BS Guide)',
    author: 'GothamChess',
    views: '1.3M',
    time: '1d ago',
    thumbnail: 'https://picsum.photos/id/1033/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=gothamchess',
    type: 'video' as const,
    duration: '19:27',
  },
  {
    title: 'I Survived 100 Days in a Minecraft AI World',
    author: 'Luke TheNotable',
    views: '8.9M',
    time: '4d ago',
    thumbnail: 'https://picsum.photos/id/201/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=lukenotable',
    hoverVideo: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    type: 'video' as const,
    accent: true,
    duration: '34:56',
  },
  {
    title: 'What Living on $1/Day Looks Like in Different Countries',
    author: 'Nas Daily',
    views: '6.2M',
    time: '5d ago',
    thumbnail: 'https://picsum.photos/id/107/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=nasdaily',
    type: 'video' as const,
    duration: '8:17',
  },
  {
    title: 'The Real Reason Airlines Are Getting Worse',
    author: 'Wendover Productions',
    views: '2.8M',
    time: '6d ago',
    thumbnail: 'https://picsum.photos/id/102/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=wendover',
    type: 'video' as const,
    duration: '15:42',
  },
  {
    title: '10-Minute Full Body Workout No Equipment Needed',
    author: 'Chloe Ting',
    views: '14.2M',
    time: '1w ago',
    thumbnail: 'https://picsum.photos/id/1060/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=chloeting',
    hoverVideo: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    type: 'video' as const,
    duration: '10:00',
  },
  {
    title: 'How This 19-Year-Old Makes $50K/Month with AI',
    author: 'Ali Abdaal',
    views: '3.4M',
    time: '2d ago',
    thumbnail: 'https://picsum.photos/id/180/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=aliabdaal',
    type: 'video' as const,
    duration: '13:29',
  },
  {
    title: 'We Ranked Every Fast Food Chicken Sandwich',
    author: 'Good Mythical Morning',
    views: '4.5M',
    time: '3d ago',
    thumbnail: 'https://picsum.photos/id/1011/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=gmm',
    hoverVideo: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    type: 'video' as const,
    duration: '20:08',
  },
  {
    title: 'Learn Python in 1 Hour — Full Beginner Course 2026',
    author: 'Programming with Mosh',
    views: '9.1M',
    time: '1w ago',
    thumbnail: 'https://picsum.photos/id/1018/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=mosh',
    type: 'video' as const,
    duration: '1:02:14',
  },
  {
    title: 'I Let AI Control My Life for 30 Days',
    author: 'Yes Theory',
    views: '7.3M',
    time: '5d ago',
    thumbnail: 'https://picsum.photos/id/1020/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=yestheory',
    hoverVideo: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    type: 'video' as const,
    accent: true,
    duration: '28:33',
  },
  {
    title: 'The Most Satisfying Machines Ever Created',
    author: 'SmarterEveryDay',
    views: '11.6M',
    time: '2w ago',
    thumbnail: 'https://picsum.photos/id/1025/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=smartereveryday',
    type: 'video' as const,
    duration: '17:45',
  },
  {
    title: 'Gordon Ramsay Reacts to AI-Generated Recipes',
    author: 'Gordon Ramsay',
    views: '15.8M',
    time: '4d ago',
    thumbnail: 'https://picsum.photos/id/1040/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=gordonramsay',
    hoverVideo: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    type: 'video' as const,
    duration: '11:22',
  },
  {
    title: 'Why Japan Is 10 Years Ahead of Your City',
    author: 'Abroad in Japan',
    views: '5.4M',
    time: '1w ago',
    thumbnail: 'https://picsum.photos/id/1042/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=abroadinjapan',
    type: 'video' as const,
    duration: '23:09',
  },
  {
    title: 'This AI Can Read Your Mind (And It Scared Me)',
    author: 'Linus Tech Tips',
    views: '6.8M',
    time: '3d ago',
    thumbnail: 'https://picsum.photos/id/1050/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=linustechtips',
    hoverVideo: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    type: 'video' as const,
    duration: '19:14',
  },
  {
    title: 'How to Style Outfits Like a Celebrity Stylist',
    author: 'Lydia Tomlinson',
    views: '2.9M',
    time: '6d ago',
    thumbnail: 'https://picsum.photos/id/1055/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=lydiatomlinson',
    type: 'video' as const,
    duration: '14:51',
  },
  {
    title: 'The Hidden Math Behind Every Hit Song',
    author: 'Vox',
    views: '8.3M',
    time: '2w ago',
    thumbnail: 'https://picsum.photos/id/1062/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=vox',
    hoverVideo: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    type: 'video' as const,
    duration: '12:07',
  },
  {
    title: 'My $500 Budget Gaming Setup — Full Tour',
    author: 'Setup Wars',
    views: '4.7M',
    time: '1w ago',
    thumbnail: 'https://picsum.photos/id/1071/600/340',
    authorAvatar: 'https://i.pravatar.cc/150?u=setupwars',
    type: 'video' as const,
    duration: '16:38',
  },
];

export default function HeadfadeHomepage() {
  const [threads, setThreads] = useState(initialThreads);
  const [activeCategory, setActiveCategory] = useState('All');
  const [batchCount, setBatchCount] = useState(1);
  const { ref, inView } = useInView({
    threshold: 0,
    rootMargin: '600px',
  });

  const loadMore = useCallback(() => {
    const nextBatch = initialThreads.map((t) => ({
      ...t,
      title: `${t.title}`,
      views: `${(parseFloat(t.views) * (0.5 + Math.random())).toFixed(1)}${t.views.replace(/[\d.]/g, '')}`,
      time: `${batchCount + 1}d ago`,
    }));
    setThreads((prev) => [...prev, ...nextBatch]);
    setBatchCount((prev) => prev + 1);
  }, [batchCount]);

  useEffect(() => {
    if (inView && batchCount < 20) {
      const timeoutId = setTimeout(loadMore, 400);
      return () => clearTimeout(timeoutId);
    }
  }, [inView, loadMore, batchCount]);

  return (
    <div className="min-h-screen" style={{ backgroundColor: brand.bg, color: brand.textPrimary }}>

      {/* ──────── Sticky Header ──────── */}
      <header
        className="sticky top-0 z-50"
        style={{ backgroundColor: brand.bg, borderBottom: `1px solid ${brand.border}` }}
      >
        <div className="w-full px-4 h-14 flex items-center justify-between">
          {/* Left: Logo + Menu */}
          <div className="flex items-center gap-4">
            <button aria-label="Open menu" className="p-2 hover:bg-[#f2f2f2] rounded-full transition-colors">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
            <div className="flex items-center gap-1 cursor-pointer select-none">
              <div className="w-8 h-8 rounded flex items-center justify-center" style={{ backgroundColor: brand.accent }}>
                <svg viewBox="0 0 24 24" className="w-5 h-5 text-white" fill="currentColor">
                  <path d="M8 5v14l11-7z" />
                </svg>
              </div>
              <span className="font-bold text-[20px] tracking-tight" style={{ color: brand.textPrimary }}>
                HeadFade
              </span>
            </div>
          </div>

          {/* Center: Search */}
          <div className="hidden md:flex flex-1 max-w-[600px] px-8">
            <div className="flex w-full items-center rounded-full overflow-hidden" style={{ border: `1px solid ${brand.border}` }}>
              <input
                type="text"
                placeholder="Search"
                className="w-full px-4 py-2 outline-none text-[16px]"
                style={{ backgroundColor: brand.bg, color: brand.textPrimary }}
              />
              <button
                aria-label="Submit search"
                className="px-5 py-2 transition-colors"
                style={{ backgroundColor: brand.bgSubtle, borderLeft: `1px solid ${brand.border}` }}
              >
                <svg className="w-5 h-5" style={{ color: brand.textMuted }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              </button>
            </div>
            <button aria-label="Search with voice" className="ml-2 p-2 rounded-full transition-colors" style={{ backgroundColor: brand.bgSubtle }}>
              <svg className="w-5 h-5" style={{ color: brand.textMuted }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
            </button>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => alert('Starting new thread...')}
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-colors"
              style={{ backgroundColor: brand.bgSubtle, color: brand.textPrimary }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
              Create
            </button>
            <button aria-label="Notifications" className="p-2 rounded-full transition-colors hover:bg-[#f2f2f2] relative">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full" style={{ backgroundColor: brand.accent }}></span>
            </button>
            <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium cursor-pointer" style={{ backgroundColor: '#6366F1' }}>
              A
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* ──────── Sticky Sidebar ──────── */}
        <aside
          className="hidden lg:flex flex-col w-[240px] sticky top-14 h-[calc(100vh-3.5rem)] overflow-y-auto overflow-x-hidden py-3 flex-shrink-0"
          style={{ borderRight: `1px solid ${brand.border}` }}
        >
          <nav className="flex flex-col gap-0.5 px-3 pb-3 mb-3" style={{ borderBottom: `1px solid ${brand.border}` }}>
            {[
              { label: 'Home', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6', active: true },
              { label: 'Shorts', icon: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z', active: false },
              { label: 'Subscriptions', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10', active: false },
            ].map((item) => (
              <button
                key={item.label}
                className="flex items-center gap-6 px-3 py-2.5 rounded-[10px] text-[14px] font-medium transition-colors"
                style={{
                  backgroundColor: item.active ? brand.bgSubtle : 'transparent',
                  fontWeight: item.active ? 700 : 400,
                }}
              >
                <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={item.active ? 2.5 : 1.5} d={item.icon} />
                </svg>
                {item.label}
              </button>
            ))}
          </nav>

          <div className="flex flex-col gap-0.5 px-3 pb-3 mb-3" style={{ borderBottom: `1px solid ${brand.border}` }}>
            <h3 className="px-3 py-2 font-bold text-[16px]">You</h3>
            {['History', 'Watch later', 'Liked videos', 'Your clips'].map((label) => (
              <button
                key={label}
                className="flex items-center gap-6 px-3 py-2 rounded-[10px] text-[14px] transition-colors hover:bg-[#f2f2f2]"
              >
                {label}
              </button>
            ))}
          </div>

          <div className="flex flex-col gap-0.5 px-3 pb-3 mb-3" style={{ borderBottom: `1px solid ${brand.border}` }}>
            <h3 className="px-3 py-2 font-bold text-[16px]">Explore</h3>
            {['Trending', 'Music', 'Gaming', 'News', 'Sports', 'Learning'].map((label) => (
              <button
                key={label}
                className="flex items-center gap-6 px-3 py-2 rounded-[10px] text-[14px] transition-colors hover:bg-[#f2f2f2]"
              >
                {label}
              </button>
            ))}
          </div>

          {/* Footer */}
          <div className="px-6 pt-4 pb-8">
            <p className="text-[12px] leading-relaxed" style={{ color: brand.textMuted }}>
              © 2026 HeadFade · Terms · Privacy · Safety
            </p>
          </div>
        </aside>

        {/* ──────── Main Feed ──────── */}
        <main className="flex-1 overflow-x-hidden">
          {/* Category Chip Bar — scrollable like YouTube */}
          <div
            className="sticky top-14 z-40 flex items-center gap-3 px-6 py-3 overflow-x-auto scrollbar-hide"
            style={{ backgroundColor: brand.bg, borderBottom: `1px solid ${brand.border}` }}
          >
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className="flex-shrink-0 px-3 py-1.5 rounded-lg text-[14px] font-medium transition-colors whitespace-nowrap"
                style={{
                  backgroundColor: activeCategory === cat ? brand.chipActive : brand.chipDefault,
                  color: activeCategory === cat ? '#FFFFFF' : brand.textPrimary,
                }}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Dense Video Grid */}
          <div className="px-4 sm:px-6 pt-6 pb-24">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 4xl:grid-cols-7 gap-x-4 gap-y-10">
              {threads.map((thread, index) => (
                <Tile
                  key={`tile-${index}`}
                  {...thread}
                  onClick={() => console.log('Opening thread:', thread.title)}
                />
              ))}
            </div>

            {/* Infinite Scroll Trigger */}
            {batchCount < 20 && (
              <div ref={ref} className="mt-12 flex justify-center py-8">
                <div className="flex flex-col items-center gap-3">
                  <div
                    className="w-8 h-8 border-[3px] rounded-full animate-spin"
                    style={{ borderColor: brand.bgSubtle, borderTopColor: brand.textPrimary }}
                  ></div>
                  <span className="text-[13px]" style={{ color: brand.textMuted }}>Loading more...</span>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
