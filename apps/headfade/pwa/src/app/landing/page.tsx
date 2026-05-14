'use client';

import { useEffect, useRef, useState } from 'react';

/* ─────────────────────────────────────────────────────────────
   HeadFade Landing Page — "The Truth Layer for the Synthetic Internet"
   Premium glassmorphism + gradient + dark-luxury aesthetic
   ───────────────────────────────────────────────────────────── */

// Animated counter hook
function useCounter(target: number, duration = 2000, start = false) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!start) return;
    let raf: number;
    const startTime = performance.now();
    const tick = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - (1 - progress) ** 3;
      setCount(Math.round(target * eased));
      if (progress < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, duration, start]);
  return count;
}

// Intersection observer hook
function useIntersect(threshold = 0.3) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          obs.disconnect();
        }
      },
      { threshold },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);
  return { ref, visible };
}

const NAV_LINKS = ['How It Works', 'For Publishers', 'For Creators', 'API Docs'];

const STATS = [
  { label: 'Videos Analyzed', value: 2_400_000, suffix: '+', prefix: '' },
  { label: 'Human Votes Cast', value: 18_700_000, suffix: '+', prefix: '' },
  { label: 'Average Accuracy', value: 73, suffix: '%', prefix: '' },
  { label: 'API Latency', value: 280, suffix: 'ms', prefix: '<' },
];

const HOW_IT_WORKS = [
  {
    step: '01',
    title: 'Upload or Ingest',
    description:
      'Creators upload media. Publishers connect feeds. Every asset enters the forensic pipeline automatically.',
    icon: '⬆️',
    gradient: 'from-sky-600 to-blue-600',
  },
  {
    step: '02',
    title: 'Forensic Analysis',
    description:
      'Four AI agents — Temporal, Physics, Audio-Visual, Metadata — analyze every frame in parallel under 300ms.',
    icon: '🔬',
    gradient: 'from-cyan-600 to-blue-600',
  },
  {
    step: '03',
    title: 'Human Turing Test',
    description:
      "The crowd votes: AI or Real? Every vote feeds the Human Deception Index — the world's most granular authenticity dataset.",
    icon: '🗳️',
    gradient: 'from-emerald-600 to-teal-600',
  },
  {
    step: '04',
    title: 'Trust Score & License',
    description:
      'Content earns a forensic trust score. Publishers embed it. Creators monetize it. Everyone knows the truth.',
    icon: '🛡️',
    gradient: 'from-amber-500 to-orange-600',
  },
];

const USE_CASES = [
  {
    title: 'Newsrooms',
    description:
      'Verify every video before publication. Embed forensic trust badges directly in your CMS.',
    icon: '📰',
    stat: '94% faster verification',
  },
  {
    title: 'Social Platforms',
    description:
      'Integrate the Arbiter API to flag synthetic content at upload, before it goes viral.',
    icon: '📱',
    stat: '12M+ daily scans',
  },
  {
    title: 'AI Studios',
    description:
      'Prove your content is AI-generated. Get higher CPMs from publishers who value transparency.',
    icon: '🎬',
    stat: '3x creator revenue',
  },
  {
    title: 'Legal & Insurance',
    description:
      'Forensic verdicts with provenance chains. Court-admissible evidence grade analysis.',
    icon: '⚖️',
    stat: 'ISO 27001 compliant',
  },
];

export default function LandingPage() {
  const [scrollY, setScrollY] = useState(0);
  const statsSection = useIntersect(0.2);
  const howSection = useIntersect(0.15);
  const ctaSection = useIntersect(0.2);

  const statValues = STATS.map((s) => useCounter(s.value, 2200, statsSection.visible));

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const fmtNum = (n: number) => {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
    return n.toLocaleString();
  };

  return (
    <main className="relative min-h-screen bg-[#030712] text-white overflow-x-hidden">
      {/* ── Animated background mesh ── */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div
          className="absolute w-[800px] h-[800px] rounded-full opacity-20"
          style={{
            background: 'radial-gradient(circle, #0891B2 0%, transparent 70%)',
            top: '-200px',
            right: '-200px',
            transform: `translateY(${scrollY * 0.1}px)`,
          }}
        />
        <div
          className="absolute w-[600px] h-[600px] rounded-full opacity-15"
          style={{
            background: 'radial-gradient(circle, #0891B2 0%, transparent 70%)',
            bottom: '10%',
            left: '-150px',
            transform: `translateY(${scrollY * -0.08}px)`,
          }}
        />
        <div
          className="absolute w-[400px] h-[400px] rounded-full opacity-10"
          style={{
            background: 'radial-gradient(circle, #F59E0B 0%, transparent 70%)',
            top: '50%',
            right: '20%',
            transform: `translateY(${scrollY * 0.05}px)`,
          }}
        />
      </div>

      {/* ── Nav ── */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-[#030712]/60 border-b border-white/[0.06]">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <svg
              viewBox="0 0 32 32"
              className="w-9 h-9"
              fill="none"
              aria-label="HeadFade logo"
              role="img"
            >
              <title>HeadFade</title>
              <rect width="32" height="32" rx="8" fill="#0891B2" />
              <path
                d="M6 22 Q10 10 16 16 Q22 22 26 10"
                stroke="white"
                strokeWidth="2.5"
                strokeLinecap="round"
                fill="none"
              />
            </svg>
            <span className="text-xl font-bold tracking-tight">HeadFade</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            {NAV_LINKS.map((link) => (
              <a
                key={link}
                href={`#${link.toLowerCase().replace(/\s+/g, '-')}`}
                className="text-sm text-white/60 hover:text-white transition-colors duration-200"
              >
                {link}
              </a>
            ))}
          </div>
          <div className="flex items-center gap-3">
            <a
              href="/"
              className="hidden sm:inline-flex px-4 py-2 text-sm font-medium text-white/70 hover:text-white border border-white/10 rounded-full hover:border-white/25 transition-all duration-200"
            >
              Sign In
            </a>
            <a
              href="/"
              className="px-5 py-2.5 text-sm font-bold rounded-full text-white transition-all duration-300 hover:scale-105 hover:shadow-[0_0_30px_rgba(8,145,178,0.4)]"
              style={{ background: 'linear-gradient(135deg, #0891B2 0%, #06B6D4 100%)' }}
            >
              Try the Test →
            </a>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative z-10 pt-32 pb-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          {/* Trust badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium mb-8 border border-cyan-500/30 bg-cyan-500/10 text-cyan-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Judge6 Trust & Safety — Always On
          </div>

          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tight leading-[0.95] mb-6">
            <span className="block">The Truth Layer</span>
            <span
              className="block mt-2"
              style={{
                background: 'linear-gradient(135deg, #0891B2 0%, #06B6D4 50%, #F59E0B 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              for the Synthetic Internet
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-lg sm:text-xl text-white/55 leading-relaxed mb-10">
            AI-generated media is indistinguishable from reality.
            <br className="hidden sm:block" />
            HeadFade is the forensic infrastructure that tells you the difference —{' '}
            <span className="text-white/80 font-medium">and turns that data into revenue.</span>
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="/"
              className="group relative px-8 py-4 text-lg font-bold rounded-2xl text-white overflow-hidden transition-all duration-300 hover:scale-105"
              style={{ background: 'linear-gradient(135deg, #0891B2, #06B6D4)' }}
            >
              <span className="relative z-10">Take the Turing Test</span>
              <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
            </a>
            <a
              href="#how-it-works"
              className="px-8 py-4 text-lg font-medium rounded-2xl text-white/70 border border-white/10 hover:border-white/25 hover:text-white transition-all duration-200"
            >
              How It Works
            </a>
          </div>

          {/* Floating UI preview */}
          <div className="relative mt-16 max-w-4xl mx-auto">
            <div className="absolute -inset-4 bg-gradient-to-r from-cyan-600/20 via-sky-500/20 to-amber-500/20 rounded-3xl blur-xl" />
            <div className="relative rounded-2xl border border-white/10 bg-[#0a0a1a]/80 backdrop-blur-xl p-1 overflow-hidden shadow-2xl">
              {/* Mock browser chrome */}
              <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06]">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/60" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
                  <div className="w-3 h-3 rounded-full bg-green-500/60" />
                </div>
                <div className="flex-1 mx-4">
                  <div className="bg-white/5 rounded-lg px-4 py-1.5 text-xs text-white/50 text-center">
                    headfade.com
                  </div>
                </div>
              </div>
              {/* Simulated feed */}
              <div className="grid grid-cols-3 gap-2 p-4">
                {[
                  { label: 'Deepfake Speech', verdict: 'AI', confidence: 97, color: '#EF4444' },
                  { label: 'Street Interview', verdict: 'REAL', confidence: 91, color: '#22C55E' },
                  { label: 'Generated Actor', verdict: 'AI', confidence: 88, color: '#EF4444' },
                ].map((item) => (
                  <div
                    key={item.label}
                    className="rounded-xl bg-white/[0.03] border border-white/[0.06] p-3"
                  >
                    <div className="aspect-video rounded-lg bg-gradient-to-br from-white/5 to-white/[0.02] flex items-center justify-center mb-2">
                      <div
                        className="px-3 py-1 rounded-full text-xs font-bold"
                        style={{ backgroundColor: `${item.color}22`, color: item.color }}
                      >
                        {item.verdict}
                      </div>
                    </div>
                    <p className="text-xs text-white/50 truncate">{item.label}</p>
                    <div className="mt-1 h-1 rounded-full bg-white/5 overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-1000"
                        style={{
                          width: `${item.confidence}%`,
                          backgroundColor: item.color,
                          opacity: 0.6,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats Bar ── */}
      <section
        ref={statsSection.ref}
        className="relative z-10 py-16 px-6 border-y border-white/[0.06]"
      >
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {STATS.map((stat, i) => (
            <div
              key={stat.label}
              className="text-center transition-all duration-700"
              style={{
                opacity: statsSection.visible ? 1 : 0,
                transform: statsSection.visible ? 'translateY(0)' : 'translateY(20px)',
                transitionDelay: `${i * 100}ms`,
              }}
            >
              <p className="text-3xl sm:text-4xl font-black tracking-tight">
                {stat.prefix}
                {fmtNum(statValues[i])}
                {stat.suffix}
              </p>
              <p className="text-sm text-white/55 mt-1">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How It Works ── */}
      <section ref={howSection.ref} id="how-it-works" className="relative z-10 py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-sm font-bold tracking-widest text-cyan-400/80 uppercase mb-3">
              The Pipeline
            </p>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight">
              From Upload to{' '}
              <span
                style={{
                  background: 'linear-gradient(135deg, #0891B2, #06B6D4)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}
              >
                Truth Score
              </span>
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {HOW_IT_WORKS.map((item, i) => (
              <div
                key={item.step}
                className="group relative rounded-2xl border border-white/[0.06] bg-white/[0.02] p-6 hover:border-white/[0.12] hover:bg-white/[0.04] transition-all duration-300"
                style={{
                  opacity: howSection.visible ? 1 : 0,
                  transform: howSection.visible ? 'translateY(0)' : 'translateY(30px)',
                  transitionDelay: `${i * 150}ms`,
                  transitionDuration: '600ms',
                }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-2xl">{item.icon}</span>
                  <span className="text-xs font-bold text-white/20 tracking-widest">
                    {item.step}
                  </span>
                </div>
                <h3 className="text-lg font-bold mb-2 group-hover:text-cyan-300 transition-colors">
                  {item.title}
                </h3>
                <p className="text-sm text-white/55 leading-relaxed">{item.description}</p>
                <div
                  className="absolute bottom-0 left-0 right-0 h-[2px] rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  style={{
                    background: `linear-gradient(90deg, transparent, ${
                      ['#0891B2', '#0EA5E9', '#10B981', '#F59E0B'][i]
                    }, transparent)`,
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── For Publishers Section ── */}
      <section
        id="for-publishers"
        className="relative z-10 py-24 px-6 border-t border-white/[0.06]"
      >
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-sm font-bold tracking-widest text-cyan-400/80 uppercase mb-3">
              Use Cases
            </p>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight">
              Built for{' '}
              <span
                style={{
                  background: 'linear-gradient(135deg, #06B6D4, #F59E0B)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}
              >
                Every Stakeholder
              </span>
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {USE_CASES.map((uc) => (
              <div
                key={uc.title}
                className="group rounded-2xl border border-white/[0.06] bg-white/[0.02] p-6 hover:border-cyan-500/20 hover:bg-cyan-500/[0.03] transition-all duration-300"
              >
                <span className="text-3xl block mb-4">{uc.icon}</span>
                <h3 className="text-lg font-bold mb-2">{uc.title}</h3>
                <p className="text-sm text-white/55 leading-relaxed mb-4">{uc.description}</p>
                <p className="text-xs font-bold text-cyan-400/80">{uc.stat}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── API / Developer Section ── */}
      <section id="api-docs" className="relative z-10 py-24 px-6 border-t border-white/[0.06]">
        <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <p className="text-sm font-bold tracking-widest text-amber-400/80 uppercase mb-3">
              Developer-First
            </p>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight mb-6">
              One API.{' '}
              <span
                style={{
                  background: 'linear-gradient(135deg, #F59E0B, #0891B2)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}
              >
                Infinite Trust.
              </span>
            </h2>
            <p className="text-white/55 leading-relaxed mb-8">
              The Arbiter Engine API returns forensic verdicts in real-time via SSE. Four
              specialized agents analyze temporal coherence, physics simulation fidelity,
              audio-visual sync, and metadata provenance — all in parallel under 300ms.
            </p>
            <div className="flex flex-wrap gap-3">
              {['SSE Streaming', 'REST + gRPC', 'Webhook Callbacks', 'OpenAPI 3.1'].map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1.5 rounded-full text-xs font-medium border border-white/10 text-white/50"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
          <div className="relative">
            <div className="rounded-2xl border border-white/[0.06] bg-[#0a0a1a]/80 backdrop-blur-xl overflow-hidden">
              <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06] bg-white/[0.02]">
                <span className="text-xs text-white/50 font-mono">arbiter_engine.py</span>
              </div>
              <pre className="p-4 text-sm font-mono text-white/60 overflow-x-auto leading-relaxed">
                <code>{`POST /api/arbiter-engine/analyze
Content-Type: application/json
Accept: text/event-stream

{
  "media_uri": "gs://headfade-cdn/clip.mp4",
  "agents": ["temporal", "physics",
             "audio_visual", "metadata"]
}

→ data: {"agent": "temporal",
          "verdict": "AI_GENERATED",
          "confidence": 0.94,
          "latency_ms": 87}

→ data: {"agent": "physics",
          "verdict": "AI_GENERATED",
          "confidence": 0.91,
          "latency_ms": 112}

→ data: {"fusion": "AI_GENERATED",
          "hdi_score": 0.73,
          "trust_level": "LOW"}`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA Section ── */}
      <section ref={ctaSection.ref} className="relative z-10 py-32 px-6">
        <div
          className="max-w-4xl mx-auto text-center rounded-3xl p-12 sm:p-16 border border-white/[0.08] overflow-hidden relative"
          style={{ background: 'linear-gradient(135deg, #0a1a28 0%, #0a1628 50%, #0a1a14 100%)' }}
        >
          <div
            className="absolute inset-0 opacity-30"
            style={{
              background:
                'radial-gradient(circle at 30% 50%, #0891B233 0%, transparent 50%), radial-gradient(circle at 70% 50%, #06B6D433 0%, transparent 50%)',
            }}
          />
          <div className="relative z-10">
            <h2
              className="text-4xl sm:text-5xl font-black tracking-tight mb-6"
              style={{
                opacity: ctaSection.visible ? 1 : 0,
                transform: ctaSection.visible ? 'translateY(0)' : 'translateY(20px)',
                transition: 'all 0.6s ease',
              }}
            >
              Can You Tell
              <br />
              What&apos;s Real?
            </h2>
            <p className="text-white/55 text-lg mb-10 max-w-xl mx-auto">
              Join millions of humans training the world&apos;s most advanced deepfake detection
              engine. Your vote matters.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href="/"
                className="px-10 py-4 text-lg font-bold rounded-2xl text-white transition-all duration-300 hover:scale-105 hover:shadow-[0_0_40px_rgba(8,145,178,0.5)]"
                style={{ background: 'linear-gradient(135deg, #0891B2, #06B6D4)' }}
              >
                Start Voting — It&apos;s Free
              </a>
              <a
                href="#api-docs"
                className="px-10 py-4 text-lg font-medium rounded-2xl text-white/50 border border-white/10 hover:border-white/25 hover:text-white transition-all duration-200"
              >
                View API Docs
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="relative z-10 border-t border-white/[0.06] py-12 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <svg viewBox="0 0 32 32" className="w-7 h-7" fill="none">
              <rect width="32" height="32" rx="8" fill="#0891B2" />
              <path
                d="M6 22 Q10 10 16 16 Q22 22 26 10"
                stroke="white"
                strokeWidth="2.5"
                strokeLinecap="round"
                fill="none"
              />
            </svg>
            <span className="text-sm text-white/50">
              © 2026 HeadFade — Synthetic Media Infrastructure
            </span>
          </div>
          <div className="flex items-center gap-6 text-sm text-white/50">
            <a href="/trust" className="hover:text-white/60 transition-colors">
              Trust & Safety
            </a>
            <a href="#" className="hover:text-white/60 transition-colors">
              Privacy
            </a>
            <a href="#" className="hover:text-white/60 transition-colors">
              Terms
            </a>
            <a href="#" className="hover:text-white/60 transition-colors">
              Status
            </a>
          </div>
        </div>
      </footer>
    </main>
  );
}
