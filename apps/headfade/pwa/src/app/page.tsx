'use client';

import type { User } from 'firebase/auth';
import { onAuthStateChanged } from 'firebase/auth';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useInView } from 'react-intersection-observer';
import { AuthWallModal } from '@/components/AuthWallModal';
import { FeaturedCarousel } from '@/components/FeaturedCarousel';
import { Tile } from '@/components/Tile';
import { useForensicElo } from '@/hooks/useForensicElo';
import { useVotes } from '@/hooks/useVotes';
import { auth } from '@/lib/firebase';

const GCS = 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4';

const brand = {
  bg: '#FFFFFF',
  bgSubtle: '#F7F9FC',
  textPrimary: '#0A2540',
  textMuted: '#4D627A',
  accent: '#7C3AED',
  border: '#E5E8ED',
  chipDefault: '#F5F3FF',
} as const;

const categories = [
  { label: 'All', color: '#7C3AED', glyph: '🌐' },
  { label: 'Trending', color: '#DC2626', glyph: '🔥' },
  { label: 'Music', color: '#DB2777', glyph: '🎵' },
  { label: 'Gaming', color: '#059669', glyph: '🎮' },
  { label: 'News', color: '#0891B2', glyph: '📡' },
  { label: 'Comedy', color: '#D97706', glyph: '😂' },
  { label: 'Sports', color: '#2563EB', glyph: '⚡' },
  { label: 'Science', color: '#7C3AED', glyph: '🔬' },
  { label: 'Fashion', color: '#EC4899', glyph: '✨' },
  { label: 'Cooking', color: '#EA580C', glyph: '🍳' },
  { label: 'Film', color: '#6D28D9', glyph: '🎬' },
  { label: 'Education', color: '#0D9488', glyph: '📚' },
  { label: 'Saved', color: '#059669', glyph: '🔖' },
];

const SEED_VIDEOS = [
  {
    title: 'How AI Is Changing Music Creation Forever',
    author: 'TechVision',
    views: '2.4M',
    time: '3h ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&h=340&fit=crop',
    hoverVideo: GCS,
    accent: true,
    duration: '14:23',
  },
  {
    title: 'I Built a House Using Only AI Blueprints',
    author: 'Builder Mike',
    views: '1.8M',
    time: '5h ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&h=340&fit=crop',
    hoverVideo: GCS,
    duration: '22:17',
  },
  {
    title: 'The Science Behind Viral Videos',
    author: 'Veritasium',
    views: '4.1M',
    time: '1d ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600&h=340&fit=crop',
    duration: '18:05',
  },
  {
    title: 'Perfect Sourdough in Under 4 Hours',
    author: 'Joshua Weissman',
    views: '890K',
    time: '6h ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=340&fit=crop',
    hoverVideo: GCS,
    duration: '12:33',
  },
  {
    title: 'Why Studios Now Use AI Actors',
    author: 'Film Theory',
    views: '3.2M',
    time: '8h ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=600&h=340&fit=crop',
    accent: true,
    duration: '25:41',
  },
  {
    title: 'Day in My Life: Remote Dev in Tokyo',
    author: 'Joma Tech',
    views: '1.5M',
    time: '2d ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&h=340&fit=crop',
    hoverVideo: GCS,
    duration: '10:08',
  },
  {
    title: 'Biggest Startup Mistakes to Avoid',
    author: 'Graham Stephan',
    views: '2.1M',
    time: '12h ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&h=340&fit=crop',
    duration: '16:54',
  },
  {
    title: 'We Tested 50 AI Image Generators',
    author: 'MKBHD',
    views: '5.7M',
    time: '3d ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=600&h=340&fit=crop',
    hoverVideo: GCS,
    duration: '21:12',
  },
  {
    title: 'How to Actually Get Good at Chess',
    author: 'GothamChess',
    views: '1.3M',
    time: '1d ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1529699211952-734e80c4d42b?w=600&h=340&fit=crop',
    duration: '19:27',
  },
  {
    title: 'I Survived 100 Days in an AI Minecraft World',
    author: 'Luke TheNotable',
    views: '8.9M',
    time: '4d ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=600&h=340&fit=crop',
    hoverVideo: GCS,
    accent: true,
    duration: '34:56',
  },
  {
    title: 'Living on $1/Day in Different Countries',
    author: 'Nas Daily',
    views: '6.2M',
    time: '5d ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&h=340&fit=crop',
    duration: '8:17',
  },
  {
    title: 'Why Airlines Are Getting Worse',
    author: 'Wendover Productions',
    views: '2.8M',
    time: '6d ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=600&h=340&fit=crop',
    duration: '15:42',
  },
  {
    title: '10-Minute Full Body Workout — No Equipment',
    author: 'Chloe Ting',
    views: '14.2M',
    time: '1w ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=340&fit=crop',
    hoverVideo: GCS,
    duration: '10:00',
  },
  {
    title: 'How This 19-Year-Old Makes $50K/Month AI',
    author: 'Ali Abdaal',
    views: '3.4M',
    time: '2d ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=600&h=340&fit=crop',
    duration: '13:29',
  },
  {
    title: 'Every Fast Food Chicken Sandwich Ranked',
    author: 'Good Mythical Morning',
    views: '4.5M',
    time: '3d ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&h=340&fit=crop',
    hoverVideo: GCS,
    duration: '20:08',
  },
  {
    title: 'Learn Python in 1 Hour — 2026 Edition',
    author: 'Programming with Mosh',
    views: '9.1M',
    time: '1w ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600&h=340&fit=crop',
    duration: '1:02:14',
  },
  {
    title: 'I Let AI Control My Life for 30 Days',
    author: 'Yes Theory',
    views: '7.3M',
    time: '5d ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=600&h=340&fit=crop&q=80',
    hoverVideo: GCS,
    accent: true,
    duration: '28:33',
  },
  {
    title: 'The Most Satisfying Machines Ever Made',
    author: 'SmarterEveryDay',
    views: '11.6M',
    time: '2w ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600&h=340&fit=crop',
    duration: '17:45',
  },
  {
    title: 'Gordon Ramsay Reacts to AI Recipes',
    author: 'Gordon Ramsay',
    views: '15.8M',
    time: '4d ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=600&h=340&fit=crop',
    hoverVideo: GCS,
    duration: '11:22',
  },
  {
    title: 'Why Japan Is 10 Years Ahead of Your City',
    author: 'Abroad in Japan',
    views: '5.4M',
    time: '1w ago',
    // biome-ignore lint/security/noSecrets: Unsplash CDN URL — not a secret
    thumbnail: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&h=340&fit=crop&q=80',
    duration: '23:09',
  },
];

type Thread = (typeof SEED_VIDEOS)[number] & { type: 'video' };
const initialThreads: Thread[] = SEED_VIDEOS.map((v) => ({ ...v, type: 'video' as const }));

export default function HeadfadeHomepage() {
  const [threads, setThreads] = useState(initialThreads);
  const [activeCategory, setActiveCategory] = useState('All');
  const [batchCount, setBatchCount] = useState(1);
  const [authWallOpen, setAuthWallOpen] = useState(false);
  // Live Firebase Auth — subscribes to session changes
  const [firebaseUser, setFirebaseUser] = useState<User | null>(null);
  const isAuthenticated = firebaseUser !== null;
  const uid = firebaseUser?.uid ?? null;

  useEffect(() => {
    return onAuthStateChanged(auth, (user) => {
      setFirebaseUser(user);
    });
  }, []);

  const { ref, inView } = useInView({ threshold: 0, rootMargin: '600px' });
  const { votes, vote, filter, setFilter, saved, toggleSave, globalAI, globalHuman } = useVotes(
    threads.length,
  );
  const { elo } = useForensicElo(uid);

  const loadMore = useCallback(() => {
    const next = initialThreads.map((t) => ({ ...t }));
    void next;
    setThreads((prev) => [...prev, ...initialThreads.map((t) => ({ ...t }))]);
    setBatchCount((c) => c + 1);
  }, []);

  useEffect(() => {
    if (inView && batchCount < 20) {
      const id = setTimeout(loadMore, 400);
      return () => clearTimeout(id);
    }
  }, [inView, loadMore, batchCount]);

  const featuredItems = useMemo(
    () =>
      threads.slice(0, 5).map((t, i) => ({
        id: String(i),
        title: t.title,
        author: t.author,
        thumbnail: t.thumbnail,
        src: t.hoverVideo ?? GCS,
        views: t.views,
        actualType: (i % 2 === 0 ? 'ai' : 'human') as 'ai' | 'human',
        voteAI: votes[i]?.voteAI ?? 0,
        voteHuman: votes[i]?.voteHuman ?? 0,
        userVote: votes[i]?.userVote ?? null,
        onVote: (c: 'ai' | 'human') => vote(String(i), c),
        isBookmarked: saved.has(String(i)),
        onBookmark: () => toggleSave(String(i)),
      })),
    [threads, votes, vote, saved, toggleSave],
  );

  const visibleIndices = useMemo(
    () =>
      threads
        .map((_, i) => i)
        .filter((i) => {
          if (activeCategory === 'Saved') return saved.has(String(i));
          const v = votes[String(i)];
          if (!v) return true;
          if (filter === 'voted-ai') return v.userVote === 'ai';
          if (filter === 'voted-human') return v.userVote === 'human';
          if (filter === 'unvoted') return v.userVote === null;
          return true;
        }),
    [threads, votes, filter, saved, activeCategory],
  );

  const fmtCount = (n: number) => {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
    return String(n);
  };

  return (
    <>
      <style>{`
        @keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:0.6} }
        @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)} }
        @keyframes headfade-flash-in { from{opacity:0;transform:scale(1.04)} to{opacity:1;transform:scale(1)} }
        .cat-chip:hover .cat-glyph { animation: float 0.8s ease-in-out infinite; }
        .scrollbar-hide::-webkit-scrollbar { display:none; }
        .scrollbar-hide { -ms-overflow-style:none; scrollbar-width:none; }
      `}</style>

      {/* Auth Wall Modal */}
      <AuthWallModal
        isOpen={authWallOpen}
        onClose={() => setAuthWallOpen(false)}
      />

      <div className="min-h-screen" style={{ backgroundColor: brand.bg, color: brand.textPrimary }}>
        {/* ── Sticky Header ── */}
        <header
          className="sticky top-0 z-50"
          style={{ backgroundColor: brand.bg, borderBottom: `1px solid ${brand.border}` }}
        >
          <div className="w-full px-4 h-14 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                type="button"
                aria-label="Open menu"
                className="p-2 hover:bg-[#f2f2f2] rounded-full transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              </button>
              <div className="flex items-center gap-2 cursor-pointer select-none">
                <svg viewBox="0 0 32 32" className="w-8 h-8" fill="none" aria-label="HeadFade logo" role="img">
                  <title>HeadFade</title>
                  <rect width="32" height="32" rx="8" fill="#7C3AED" />
                  <path
                    d="M6 22 Q10 10 16 16 Q22 22 26 10"
                    stroke="white"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    fill="none"
                  />
                </svg>
                <span className="font-bold text-[20px] tracking-tight">HeadFade</span>
              </div>
            </div>

            <div className="hidden md:flex flex-1 max-w-[600px] px-8">
              <div
                className="flex w-full items-center rounded-full overflow-hidden"
                style={{ border: `1px solid ${brand.border}` }}
              >
                <input
                  type="text"
                  placeholder="Search AI-presumed videos..."
                  className="w-full px-4 py-2 outline-none text-[16px]"
                  style={{ backgroundColor: brand.bg }}
                />
                <button
                  type="button"
                  aria-label="Submit search"
                  className="px-5 py-2"
                  style={{
                    backgroundColor: brand.bgSubtle,
                    borderLeft: `1px solid ${brand.border}`,
                  }}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* Elo badge in header when signed in */}
              {isAuthenticated && (
                <div
                  className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full text-[12px] font-bold"
                  style={{ background: 'linear-gradient(90deg,#7C3AED,#0891B2)', color: 'white' }}
                >
                  ⚡ Elo {elo.eloRating.toLocaleString()}
                </div>
              )}
              <button
                type="button"
                aria-label="Upload your AI or non-AI videos — see who you can fake out"
                className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-[13px] font-bold text-white transition-all hover:scale-105"
                style={{ background: 'linear-gradient(90deg,#7C3AED,#0891B2)' }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <title>Upload icon</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                  />
                </svg>
                Upload &amp; Fake Us Out
              </button>
              <button
                type="button"
                onClick={() => !isAuthenticated && setAuthWallOpen(true)}
                className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium cursor-pointer"
                style={{ backgroundColor: brand.accent }}
                aria-label={isAuthenticated ? 'Your profile' : 'Sign in'}
              >
                {isAuthenticated ? 'U' : '?'}
              </button>
            </div>
          </div>

          {/* Vote campaign banner */}
          <div
            className="w-full px-4 py-2.5 flex flex-col sm:flex-row items-center justify-between gap-2"
            style={{ background: 'linear-gradient(90deg,#4C1D95 0%,#7C3AED 50%,#0891B2 100%)' }}
          >
            <div className="flex items-center gap-3 text-white">
              <span className="text-[20px] font-black tracking-tight">
                Is it <span style={{ color: '#C4B5FD' }}>AI</span>, or is it?
              </span>
              <span
                className="hidden sm:block text-[16px] font-bold px-3 py-0.5 rounded-full animate-pulse"
                style={{ backgroundColor: 'rgba(255,255,255,0.15)' }}
              >
                Vote Now ↓
              </span>
              <span className="text-[12px] opacity-75">AI Presumed Videos — Only You Can Tell</span>
            </div>
            <div className="flex items-center gap-4 text-[12px] text-white/80">
              <span>
                🤖 <strong>{fmtCount(globalAI)}</strong> AI votes
              </span>
              <span>
                👤 <strong>{fmtCount(globalHuman)}</strong> Human votes
              </span>
            </div>
          </div>
        </header>

        {/* ── FEATURED CAROUSEL with Cognitive Lock ── */}
        <FeaturedCarousel
          items={featuredItems}
          isAuthenticated={isAuthenticated}
          onAuthRequired={() => setAuthWallOpen(true)}
          eloRating={isAuthenticated ? elo.eloRating : undefined}
        />

        <div className="flex">
          {/* Sidebar */}
          <aside
            className="hidden lg:flex flex-col w-[240px] sticky top-[108px] h-[calc(100vh-6.75rem)] overflow-y-auto py-3 flex-shrink-0"
            style={{ borderRight: `1px solid ${brand.border}` }}
          >
            <nav
              className="flex flex-col gap-0.5 px-3 pb-3 mb-3"
              style={{ borderBottom: `1px solid ${brand.border}` }}
            >
              {[
                {
                  label: 'Home',
                  icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
                  active: true,
                },
                {
                  label: 'Discover',
                  icon: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z',
                  active: false,
                },
                {
                  label: 'Leaderboard',
                  icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
                  active: false,
                },
              ].map((item) => (
                <button
                  key={item.label}
                  type="button"
                  aria-label={item.label}
                  aria-current={item.active ? 'page' : undefined}
                  className="flex items-center gap-6 px-3 py-2.5 rounded-[10px] text-[14px] font-medium transition-colors"
                  style={{
                    backgroundColor: item.active ? '#EDE9FF' : 'transparent',
                    color: item.active ? brand.accent : brand.textPrimary,
                    fontWeight: item.active ? 700 : 400,
                  }}
                >
                  <svg
                    className="w-6 h-6 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <title>{`${item.label} icon`}</title>
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={item.active ? 2.5 : 1.5}
                      d={item.icon}
                    />
                  </svg>
                  {item.label}
                </button>
              ))}
            </nav>

            {/* Forensic Elo sidebar widget */}
            {isAuthenticated && (
              <div
                className="mx-3 mb-3 p-3 rounded-xl"
                style={{
                  background: 'linear-gradient(135deg,#4C1D95,#1A0A2E)',
                  border: '1px solid rgba(124,58,237,0.4)',
                }}
              >
                <p className="text-[11px] font-bold text-white/50 mb-1">YOUR FORENSIC ELO</p>
                <p className="text-[28px] font-black text-white">
                  {elo.eloRating.toLocaleString()}
                </p>
                <div className="flex gap-3 mt-1 text-[11px] text-white/60">
                  <span>✓ {elo.correctVotes} correct</span>
                  <span>📊 {elo.accuracy}% acc</span>
                </div>
                {elo.badges.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {elo.badges.map((b) => (
                      <span
                        key={b}
                        className="text-[10px] px-1.5 py-0.5 rounded-full bg-white/10 text-white/80"
                      >
                        {b}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            <div
              className="flex flex-col gap-0.5 px-3 pb-3 mb-3"
              style={{ borderBottom: `1px solid ${brand.border}` }}
            >
              <h3 className="px-3 py-2 font-bold text-[16px]">Your Votes</h3>
              {(
                [
                  { label: 'All Votes', value: 'all' },
                  { label: 'Voted AI', value: 'voted-ai' },
                  { label: 'Voted Human', value: 'voted-human' },
                  { label: 'Not Voted Yet', value: 'unvoted' },
                ] as const
              ).map(({ label, value }) => (
                <button
                  key={value}
                  type="button"
                  aria-pressed={filter === value}
                  onClick={() => setFilter(value)}
                  className="flex items-center gap-6 px-3 py-2 rounded-[10px] text-[14px] transition-colors"
                  style={{
                    backgroundColor: filter === value ? '#EDE9FF' : 'transparent',
                    color: filter === value ? '#7C3AED' : '#0A2540',
                    fontWeight: filter === value ? 700 : 400,
                  }}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="px-6 pt-4 pb-8">
              <p className="text-[12px] leading-relaxed" style={{ color: brand.textMuted }}>
                © 2026 HeadFade · Terms · Privacy
              </p>
            </div>
          </aside>

          {/* Main grid */}
          <main className="flex-1 overflow-x-hidden">
            <div
              className="sticky top-[108px] z-40 flex items-center gap-2 px-6 py-3 overflow-x-auto scrollbar-hide"
              style={{ backgroundColor: brand.bg, borderBottom: `1px solid ${brand.border}` }}
            >
              {categories.map((cat) => {
                const isActive = activeCategory === cat.label;
                return (
                  <button
                    key={cat.label}
                    type="button"
                    aria-label={`Filter by ${cat.label}`}
                    aria-pressed={isActive}
                    className="cat-chip flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[13px] font-medium transition-all duration-200 whitespace-nowrap hover:scale-105"
                    onClick={() => setActiveCategory(cat.label)}
                    style={{
                      background: isActive ? cat.color : brand.chipDefault,
                      color: isActive ? '#fff' : cat.color,
                      boxShadow: isActive ? `0 2px 12px ${cat.color}55` : 'none',
                    }}
                  >
                    <span className="cat-glyph text-[15px]" aria-hidden="true">{cat.glyph}</span>
                    {cat.label}
                  </button>
                );
              })}
            </div>

            <div className="px-4 sm:px-6 pt-6 pb-24">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-x-4 gap-y-10">
                {visibleIndices.length === 0 && (
                  <div className="col-span-full flex flex-col items-center gap-3 py-20 text-center">
                    <span className="text-5xl">🗳️</span>
                    <p className="text-[16px] font-semibold">No videos match this filter</p>
                    <button
                      type="button"
                      onClick={() => {
                        setFilter('all');
                        setActiveCategory('All');
                      }}
                      className="mt-2 px-4 py-2 rounded-lg text-white text-[13px] font-bold"
                      style={{ backgroundColor: '#7C3AED' }}
                    >
                      Show All
                    </button>
                  </div>
                )}
                {visibleIndices.map((index) => {
                  const thread = threads[index];
                  const key = String(index);
                  const v = votes[key] ?? { voteAI: 0, voteHuman: 0, userVote: null };
                  return (
                    <Tile
                      key={`tile-${index}`}
                      {...thread}
                      voteAI={v.voteAI}
                      voteHuman={v.voteHuman}
                      userVote={v.userVote}
                      onVote={(choice) => {
                        if (!isAuthenticated) {
                          setAuthWallOpen(true);
                          return;
                        }
                        vote(key, choice);
                      }}
                      onClick={() => {}}
                    />
                  );
                })}
              </div>

              {batchCount < 20 && (
                <div ref={ref} className="mt-12 flex justify-center py-8">
                  <div
                    className="w-8 h-8 border-[3px] rounded-full animate-spin"
                    style={{ borderColor: '#EDE9FF', borderTopColor: brand.accent }}
                  />
                </div>
              )}
            </div>
          </main>
        </div>
      </div>
    </>
  );
}
