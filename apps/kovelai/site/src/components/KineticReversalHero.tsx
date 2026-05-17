"use client";
import { motion, useScroll, useSpring, useTransform } from "framer-motion";
import Link from "next/link";
import { useRef } from "react";

interface KineticReversalHeroProps {
  onOpenModal: () => void;
}

export default function KineticReversalHero({ onOpenModal }: KineticReversalHeroProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Track scroll progress
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  // Smooth out the scroll physics
  const springProgress = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  });

  // Reversal effects based on scroll
  // Background moves down while content moves up (parallax)
  const bgY = useTransform(springProgress, [0, 1], ["0%", "30%"]);

  // Center blob expands and reverses its rotation
  const blobScale = useTransform(springProgress, [0, 1], [1, 2.5]);
  const blobRotate = useTransform(springProgress, [0, 1], [0, -180]);
  const blobOpacity = useTransform(springProgress, [0, 0.5, 1], [0.3, 0.1, 0]);

  // Main text gets "reversed" (spreads out and blurs out)
  const textY = useTransform(springProgress, [0, 1], ["0%", "-50%"]);
  const textScale = useTransform(springProgress, [0, 1], [1, 0.9]);
  const textOpacity = useTransform(springProgress, [0, 0.6], [1, 0]);
  const letterSpacing = useTransform(springProgress, [0, 1], ["-0.04em", "0.1em"]);

  return (
    <div ref={containerRef} className="relative h-[150vh] bg-surface w-full overflow-hidden">
      {/* Sticky container that holds the visual hero */}
      <div className="sticky top-0 h-screen w-full flex flex-col items-center justify-center overflow-hidden">
        {/* Parallax Background Grid */}
        <motion.div style={{ y: bgY }} className="absolute inset-0 pointer-events-none opacity-20">
          <div
            className="absolute inset-0"
            style={{
              backgroundImage:
                "linear-gradient(rgba(230,196,135,0.2) 1px, transparent 1px), linear-gradient(90deg, rgba(230,196,135,0.2) 1px, transparent 1px)",
              backgroundSize: "40px 40px",
              transform: "perspective(500px) rotateX(60deg) translateY(-100px) scale(3)",
            }}
          />
        </motion.div>

        {/* Kinetic Reversal Center Blob */}
        <motion.div
          style={{ scale: blobScale, rotate: blobRotate, opacity: blobOpacity }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[40vw] h-[40vw] rounded-full pointer-events-none mix-blend-screen"
        >
          <div className="w-full h-full rounded-full bg-gradient-to-r from-gold via-blue to-lavender blur-[80px]" />
        </motion.div>

        {/* Hero Content */}
        <motion.div
          style={{ y: textY, scale: textScale, opacity: textOpacity }}
          className="relative z-10 text-center px-6 max-w-5xl"
        >
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className="inline-block px-4 py-1.5 mb-8 rounded-full border border-gold/30 bg-surface-highest/50 backdrop-blur-md text-gold text-xs font-bold uppercase tracking-[0.2em]">
              The Law Demands Precision
            </span>
          </motion.div>

          <motion.h1
            style={{ letterSpacing }}
            className="text-[clamp(3rem,8vw,6rem)] font-black text-foreground leading-[1.05] mb-8"
          >
            Sovereign Architecture <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-gold to-gold-container">
              For Legal AI
            </span>
          </motion.h1>

          <p className="text-xl text-secondary-text max-w-2xl mx-auto leading-relaxed mb-10">
            A privilege-preserving intelligence layer designed to ensure your firm's data never
            leaks into public models.
          </p>

          <div className="flex items-center justify-center gap-6">
            <button
              onClick={onOpenModal}
              type="button"
              className="glass-card !bg-gold/10 hover:!bg-gold/20 border-gold/30 text-gold font-bold px-8 py-4 rounded-xl transition-all shadow-[0_0_30px_rgba(230,196,135,0.15)] hover:shadow-[0_0_50px_rgba(230,196,135,0.3)]"
            >
              Enter The Platform
            </button>
            <Link
              href="/trust"
              className="text-foreground hover:text-gold font-medium transition-colors px-6 py-4 flex items-center gap-2"
            >
              Read the Manifesto
              <svg
                aria-hidden="true"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </motion.div>

        {/* Foreground glass framing */}
        <div className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-background to-transparent pointer-events-none" />
      </div>
    </div>
  );
}
