'use client';

import React from 'react';
import { Tile } from '@/components/Tile'; // we'll create this

export default function TrustPage() {
  const threads = [
  {
    title: "United States v. Heppner – Full Risk Analysis & Mitigation Strategy",
    author: "Headfade Legal",
    views: "142.8k",
    time: "2h ago",
    thumbnail: "https://picsum.photos/id/1015/600/340",
    type: "thread" as const,
    accent: true
  },
  {
    title: "How Top Law Firms Cut Legal Review Time by 87% Using AI",
    author: "Sarah Chen, Esq.",
    views: "89.4k",
    time: "4h ago",
    thumbnail: "https://picsum.photos/id/106/600/340",
    type: "insight" as const
  },
  {
    title: "Live Demo: Headfade AI Intake Portal in Action",
    author: "Headfade Product",
    views: "67.2k",
    time: "6h ago",
    thumbnail: "https://picsum.photos/id/1074/600/340",
    type: "video" as const
  },
  {
    title: "The New Standard: Why 50+ AmLaw 200 Firms Switched to Headfade",
    author: "Michael Torres",
    views: "54.9k",
    time: "yesterday",
    thumbnail: "https://picsum.photos/id/1033/600/340",
    type: "thread" as const
  },
  {
    title: "Gamified Turing Test Results – Week 47 Breakdown",
    author: "Headfade Research",
    views: "41.3k",
    time: "yesterday",
    thumbnail: "https://picsum.photos/id/160/600/340",
    type: "insight" as const
  },
  {
    title: "Case Study: How We Helped a 340-Attorney Firm Achieve 340% ROI",
    author: "Headfade Enterprise",
    views: "38.7k",
    time: "2d ago",
    thumbnail: "https://picsum.photos/id/201/600/340",
    type: "thread" as const
  },
  {
    title: "Real-time Clause Risk Heatmap – Now Available",
    author: "Product Updates",
    views: "29.1k",
    time: "2d ago",
    thumbnail: "https://picsum.photos/id/107/600/340",
    type: "video" as const
  },
  {
    title: "B2B SaaS Legal Risk Mitigation Masterclass (Recording)",
    author: "Headfade Academy",
    views: "24.6k",
    time: "3d ago",
    thumbnail: "https://picsum.photos/id/102/600/340",
    type: "video" as const
  },
  {
    title: "47 Red Flags We Caught This Month – Thread",
    author: "Headfade Risk Team",
    views: "19.8k",
    time: "3d ago",
    thumbnail: "https://picsum.photos/id/1060/600/340",
    type: "thread" as const
  },
  {
    title: "How Headfade Passed SOC 2 Type II + HIPAA in Record Time",
    author: "Compliance Team",
    views: "17.4k",
    time: "4d ago",
    thumbnail: "https://picsum.photos/id/180/600/340",
    type: "insight" as const
  },
  {
    title: "The Future of AI in Legal Ethics – Panel Discussion",
    author: "Headfade Events",
    views: "15.2k",
    time: "5d ago",
    thumbnail: "https://picsum.photos/id/1036/600/340",
    type: "video" as const
  },
  {
    title: "Multi-Jurisdiction Shield: Now Live in All 50 States",
    author: "Product Updates",
    views: "13.9k",
    time: "5d ago",
    thumbnail: "https://picsum.photos/id/1071/600/340",
    type: "thread" as const,
    accent: true
  }
  ];

  return (
    <div className="min-h-screen bg-white text-[#0A2540]">
      {/* Header */}
      <div className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-[#E0E5EE]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-[#0A2540] rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-xl">H</span>
            </div>
            <div>
              <div className="font-semibold text-2xl tracking-tight">Headfade</div>
              <div className="text-xs text-[#3B4C6B] -mt-1">Trust Center</div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="px-4 py-1.5 bg-[#F7F9FC] rounded-full text-sm">Live • 142k threads</div>
            <button type="button" className="px-6 py-2 bg-[#C9A227] hover:bg-[#B38B1F] text-white rounded-xl font-medium transition-all active:scale-[0.985]">
              Start New Thread
            </button>
          </div>
        </div>
      </div>

      {/* Hero */}
      <div className="max-w-7xl mx-auto px-6 pt-12 pb-8">
        <div className="max-w-2xl">
          <h1 className="text-6xl font-semibold tracking-tighter">The most trusted<br />legal AI platform.</h1>
          <p className="mt-4 text-xl text-[#3B4C6B]">Real-time risk mitigation for law firms. Built for the United States v. Heppner era.</p>
        </div>
      </div>

      {/* Main Feed — YouTube + TikTok Style */}
      <div className="max-w-7xl mx-auto px-6 pb-24">
        <div className="flex items-end justify-between mb-6">
          <div>
            <div className="text-sm font-medium text-[#C9A227]">TRENDING RIGHT NOW</div>
            <div className="text-3xl font-semibold tracking-tight">For You</div>
          </div>
          <div className="text-sm text-[#3B4C6B] hover:text-[#0A2540] cursor-pointer">See all →</div>
        </div>

        {/* Responsive Tile Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
          {threads.map((thread, index) => {
            const base = 800 + index * 213;
            const aiPct = 0.4 + (index % 5) * 0.06;
            return (
              <Tile
                key={index}
                {...thread}
                voteAI={Math.floor(base * aiPct)}
                voteHuman={Math.floor(base * (1 - aiPct))}
                userVote={null}
                onVote={() => {}}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
}
