'use client';

import React, { useState, useEffect } from 'react';
import { useInView } from 'react-intersection-observer';
import { Tile } from '@/components/Tile';

const initialThreads = [
  {
    title: "United States v. Heppner – Full Risk Analysis & Mitigation Strategy",
    author: "Headfade Legal",
    views: "142.8k",
    time: "2h ago",
    thumbnail: "https://picsum.photos/id/1015/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=headfade1",
    hoverVideo: "https://www.w3schools.com/html/mov_bbb.mp4",
    type: "thread" as const,
    accent: true
  },
  {
    title: "How Top Law Firms Cut Legal Review Time by 87% Using AI",
    author: "Sarah Chen, Esq.",
    views: "89.4k",
    time: "4h ago",
    thumbnail: "https://picsum.photos/id/106/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=sarahchen",
    hoverVideo: "https://www.w3schools.com/html/mov_bbb.mp4",
    type: "insight" as const
  },
  {
    title: "Live Demo: Headfade AI Intake Portal in Action",
    author: "Headfade Product",
    views: "67.2k",
    time: "6h ago",
    thumbnail: "https://picsum.photos/id/1074/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=headfade2",
    type: "video" as const
  },
  {
    title: "The New Standard: Why 50+ AmLaw 200 Firms Switched to Headfade",
    author: "Michael Torres",
    views: "54.9k",
    time: "yesterday",
    thumbnail: "https://picsum.photos/id/1033/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=michaeltorres",
    type: "thread" as const
  },
  {
    title: "Gamified Turing Test Results – Week 47 Breakdown",
    author: "Headfade Research",
    views: "41.3k",
    time: "yesterday",
    thumbnail: "https://picsum.photos/id/160/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=headfade3",
    type: "insight" as const
  },
  {
    title: "Case Study: How We Helped a 340-Attorney Firm Achieve 340% ROI",
    author: "Headfade Enterprise",
    views: "38.7k",
    time: "2d ago",
    thumbnail: "https://picsum.photos/id/201/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=headfade4",
    type: "thread" as const
  },
  {
    title: "Real-time Clause Risk Heatmap – Now Available",
    author: "Product Updates",
    views: "29.1k",
    time: "2d ago",
    thumbnail: "https://picsum.photos/id/107/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=productupdates1",
    type: "video" as const
  },
  {
    title: "B2B SaaS Legal Risk Mitigation Masterclass (Recording)",
    author: "Headfade Academy",
    views: "24.6k",
    time: "3d ago",
    thumbnail: "https://picsum.photos/id/102/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=headfadeacademy",
    type: "video" as const
  },
  {
    title: "47 Red Flags We Caught This Month – Thread",
    author: "Headfade Risk Team",
    views: "19.8k",
    time: "3d ago",
    thumbnail: "https://picsum.photos/id/1060/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=riskteam",
    type: "thread" as const
  },
  {
    title: "How Headfade Passed SOC 2 Type II + HIPAA in Record Time",
    author: "Compliance Team",
    views: "17.4k",
    time: "4d ago",
    thumbnail: "https://picsum.photos/id/180/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=compliance",
    type: "insight" as const
  },
  {
    title: "The Future of AI in Legal Ethics – Panel Discussion",
    author: "Headfade Events",
    views: "15.2k",
    time: "5d ago",
    thumbnail: "https://picsum.photos/id/1036/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=events",
    type: "video" as const
  },
  {
    title: "Multi-Jurisdiction Shield: Now Live in All 50 States",
    author: "Product Updates",
    views: "13.9k",
    time: "5d ago",
    thumbnail: "https://picsum.photos/id/1071/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=productupdates2",
    type: "thread" as const,
    accent: true
  },
  {
    title: "Client Communications in the GenAI Era",
    author: "Communications Team",
    views: "11.1k",
    time: "1w ago",
    thumbnail: "https://picsum.photos/id/1005/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=comms",
    type: "video" as const
  },
  {
    title: "Automated Brief Generation: A Practitioner's Guide",
    author: "Legal Tech Review",
    views: "9.2k",
    time: "1w ago",
    thumbnail: "https://picsum.photos/id/1011/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=legaltech",
    type: "thread" as const
  },
  {
    title: "The Privacy Implications of LLM Log Retention",
    author: "Security Posture",
    views: "8.5k",
    time: "2w ago",
    thumbnail: "https://picsum.photos/id/1018/600/340",
    authorAvatar: "https://i.pravatar.cc/150?u=security",
    type: "insight" as const
  }
];

export default function HeadfadeHomepage() {
  const [threads, setThreads] = useState(initialThreads);
  const { ref, inView } = useInView({
    threshold: 0,
    rootMargin: '400px',
  });

  useEffect(() => {
    if (inView) {
      // Simulate loading more data
      const timeoutId = setTimeout(() => {
        const moreItems = initialThreads.map((t, i) => ({
          ...t,
          title: `${t.title} - Batch ${Math.floor(threads.length / initialThreads.length) + 1}`,
        }));
        setThreads((prev) => [...prev, ...moreItems]);
      }, 500);
      
      return () => clearTimeout(timeoutId);
    }
  }, [inView, threads.length]);

  return (
    <div className="min-h-screen bg-white text-[#0A2540]">
      {/* Sticky Header */}
      <header className="sticky top-0 z-50 bg-white border-b border-[#e5e5e5]">
        <div className="w-full px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-[#f2f2f2] rounded-full transition-colors md:hidden">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
            <div className="flex items-center gap-2 cursor-pointer">
              <div className="w-8 h-8 bg-[#cc0000] rounded flex items-center justify-center">
                <span className="text-white text-xl font-bold tracking-tighter">H</span>
              </div>
              <div>
                <div className="font-bold text-xl tracking-tighter">HeadFade</div>
              </div>
            </div>
          </div>

          <div className="hidden md:flex flex-1 max-w-2xl px-12">
            <div className="flex w-full items-center border border-[#cccccc] rounded-full overflow-hidden bg-white">
              <input type="text" placeholder="Search" className="w-full px-4 py-2 outline-none text-[#0A2540]" />
              <button className="px-5 py-2 bg-[#F7F9FC] border-l border-[#cccccc] hover:bg-[#e5e5e5] transition-colors">
                <svg className="w-5 h-5 text-[#606060]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              </button>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button 
              onClick={() => alert('Starting new thread...')}
              className="px-4 py-2 bg-[#F7F9FC] hover:bg-[#e5e5e5] text-[#0A2540] text-sm font-medium rounded-full transition-colors hidden sm:block"
            >
              Start New Thread
            </button>
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium cursor-pointer">
              A
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sticky Sidebar */}
        <aside className="hidden md:flex flex-col w-64 sticky top-14 h-[calc(100vh-3.5rem)] overflow-y-auto px-3 py-3 border-r border-[#e5e5e5]">
          <div className="flex flex-col gap-1 border-b border-[#e5e5e5] pb-3 mb-3">
            <button className="flex items-center gap-4 px-3 py-2.5 bg-[#f2f2f2] rounded-lg text-[14px] font-medium">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4l-8 8h3v8h10v-8h3l-8-8z" /></svg>
              Home
            </button>
            <button className="flex items-center gap-4 px-3 py-2.5 hover:bg-[#f2f2f2] rounded-lg text-[14px] transition-colors">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
              Shorts
            </button>
            <button className="flex items-center gap-4 px-3 py-2.5 hover:bg-[#f2f2f2] rounded-lg text-[14px] transition-colors">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" /></svg>
              Subscriptions
            </button>
          </div>
          
          <div className="flex flex-col gap-1 border-b border-[#e5e5e5] pb-3 mb-3">
            <h3 className="px-3 py-2 font-bold text-[16px]">You</h3>
            <button className="flex items-center gap-4 px-3 py-2.5 hover:bg-[#f2f2f2] rounded-lg text-[14px] transition-colors">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              History
            </button>
            <button className="flex items-center gap-4 px-3 py-2.5 hover:bg-[#f2f2f2] rounded-lg text-[14px] transition-colors">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              Your videos
            </button>
          </div>
        </aside>

        {/* Main Feed */}
        <main className="flex-1 px-4 sm:px-6 lg:px-8 pt-6 pb-24 overflow-x-hidden">
          {/* Responsive YouTube + TikTok Style Dense Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-x-4 gap-y-10">
            {threads.map((thread, index) => (
              <Tile 
                key={index} 
                {...thread} 
                onClick={() => console.log('Opening thread:', thread.title)}
              />
            ))}
          </div>

          {/* Infinite Scroll Trigger */}
          <div ref={ref} className="mt-12 flex justify-center py-8">
            <div className="w-8 h-8 border-4 border-[#F7F9FC] border-t-[#0A2540] rounded-full animate-spin"></div>
          </div>
        </main>
      </div>
    </div>
  );
}
