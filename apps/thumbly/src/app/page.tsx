'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, Image as ImageIcon, Sparkles, Zap } from 'lucide-react';
import Link from 'next/link';

export default function ThumblyLanding() {
  return (
    <div className="min-h-screen relative overflow-hidden flex flex-col items-center justify-center selection:bg-emerald-500/30">
      {/* Background Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/20 rounded-full blur-[120px] -z-10" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-[120px] -z-10" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-emerald-400/5 rounded-full blur-[150px] -z-10" />

      {/* Main Container */}
      <main className="w-full max-w-6xl mx-auto px-6 py-24 flex flex-col items-center text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-8"
        >
          <Sparkles className="w-4 h-4 text-emerald-400" />
          <span className="text-sm font-medium text-emerald-100 tracking-wide uppercase">
            Vibe Coding 2026
          </span>
        </motion.div>

        {/* Hero Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-6xl md:text-8xl font-black tracking-tight mb-8"
        >
          Generate High-Conversion <br />
          <span className="text-gradient">YouTube Thumbnails.</span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-xl md:text-2xl text-zinc-400 max-w-2xl mb-12 leading-relaxed font-light"
        >
          Stop guessing what works. Thumbly uses NPU-accelerated intelligence to craft CTR-optimized
          imagery in seconds.
        </motion.p>

        {/* CTA Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Link
            href="/dashboard"
            className="group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-white text-black rounded-full text-lg font-bold hover:scale-105 active:scale-95 transition-all shadow-[0_0_40px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_rgba(255,255,255,0.5)]"
          >
            <Zap className="w-5 h-5 group-hover:fill-current" />
            Start Generating Now
            <div className="absolute inset-0 rounded-full ring-2 ring-white/20 ring-offset-2 ring-offset-black scale-110 opacity-0 group-hover:scale-100 group-hover:opacity-100 transition-all duration-300" />
          </Link>
        </motion.div>

        {/* Features Glass Grid */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-32 w-full"
        >
          {/* Feature 1 */}
          <div className="glass-panel p-8 rounded-3xl text-left flex flex-col gap-4 group hover:-translate-y-2 transition-transform duration-300">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">
              <ImageIcon className="w-6 h-6 text-emerald-400" />
            </div>
            <h3 className="text-xl font-bold text-white">Pixel-Perfect Canvas</h3>
            <p className="text-zinc-400 leading-relaxed">
              Generated strictly at 1280x720. Ready to upload immediately to YouTube Studio.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="glass-panel p-8 rounded-3xl text-left flex flex-col gap-4 group hover:-translate-y-2 transition-transform duration-300">
            <div className="w-12 h-12 rounded-2xl bg-cyan-500/20 flex items-center justify-center border border-cyan-500/30">
              <CheckCircle2 className="w-6 h-6 text-cyan-400" />
            </div>
            <h3 className="text-xl font-bold text-white">Stripe Lifecycle</h3>
            <p className="text-zinc-400 leading-relaxed">
              Deterministic credit ledgers powered by Supabase Edge webhooks and Stripe.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="glass-panel p-8 rounded-3xl text-left flex flex-col gap-4 group hover:-translate-y-2 transition-transform duration-300">
            <div className="w-12 h-12 rounded-2xl bg-purple-500/20 flex items-center justify-center border border-purple-500/30">
              <Zap className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-xl font-bold text-white">Instant Generations</h3>
            <p className="text-zinc-400 leading-relaxed">
              No queue times. NPU execution guarantees your asset is ready in under 3 seconds.
            </p>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
