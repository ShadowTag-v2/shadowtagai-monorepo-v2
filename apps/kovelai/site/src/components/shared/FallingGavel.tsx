// Copyright (c) 2026 ShadowTag, Inc. All rights reserved. Dual-Licensed under CounselConduit Compliance.

"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";

/* ── Design Token Constants (aligned with globals.css Sovereign Architect) ── */
const T = {
  ink: "#071325",
  gold: "#e6c487",
  goldDim: "rgba(230, 196, 135, 0.15)",
  blue: "#aac7ff",
  primaryText: "#d7e3fc",
  secondaryText: "#d0c5b5",
  surfaceHigh: "#1f2a3d",
  outline: "#998f81",
} as const;

/* ── Gavel SVG (minimal, authoritative) ── */
function GavelSVG() {
  return (
    <svg
      viewBox="0 0 64 64"
      width="48"
      height="48"
      fill="none"
      stroke={T.gold}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      role="img"
      aria-label="Gavel icon representing legal authority"
    >
      {/* Handle */}
      <line x1="18" y1="46" x2="38" y2="26" />
      {/* Head */}
      <rect x="34" y="14" width="18" height="10" rx="2" transform="rotate(45 43 19)" />
      {/* Strike plate */}
      <rect x="8" y="52" width="24" height="4" rx="1" />
      {/* Impact ring */}
      <motion.circle
        cx="20"
        cy="52"
        r="6"
        fill="none"
        stroke={T.gold}
        strokeWidth="1"
        strokeOpacity={0.3}
        animate={{
          r: [6, 14, 20],
          strokeOpacity: [0.3, 0.1, 0],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "easeOut",
          repeatDelay: 2,
        }}
      />
    </svg>
  );
}

/* ── Component ── */
interface FallingGavelProps {
  onOpenModal?: () => void;
}

export default function FallingGavel({ onOpenModal }: FallingGavelProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  /* Spring-damper animation: gavel falls from above, bounces, settles */
  const gavelVariants = {
    hidden: { y: -80, opacity: 0, rotate: -25 },
    visible: {
      y: 0,
      opacity: 1,
      rotate: 0,
      transition: {
        type: "spring" as const,
        stiffness: 200,
        damping: 12,
        mass: 1.2,
        delay: 0.2,
      },
    },
  };

  /* Impact shockwave — triggers after gavel lands */
  const shockwaveVariants = {
    hidden: { scale: 0, opacity: 0 },
    visible: {
      scale: [0, 1.8, 2.5],
      opacity: [0.4, 0.15, 0],
      transition: {
        duration: 0.8,
        delay: 0.55,
        ease: "easeOut" as const,
      },
    },
  };

  /* Text stagger */
  const textContainerVariants = {
    hidden: {},
    visible: {
      transition: { staggerChildren: 0.1, delayChildren: 0.7 },
    },
  };

  const textItemVariants = {
    hidden: { opacity: 0, y: 20, filter: "blur(6px)" },
    visible: {
      opacity: 1,
      y: 0,
      filter: "blur(0px)",
      transition: { duration: 0.6, ease: [0.25, 0.4, 0.25, 1] as const },
    },
  };

  return (
    <section
      ref={ref}
      style={{
        position: "relative",
        padding: "5rem 1rem",
        overflow: "hidden",
        background: `linear-gradient(180deg, ${T.ink} 0%, #0c1e38 50%, ${T.ink} 100%)`,
        textAlign: "center",
      }}
      id="gavel-cta"
      aria-labelledby="gavel-headline"
    >
      {/* Atmospheric glow */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse 50% 40% at 50% 45%, ${T.goldDim}, transparent 70%)`,
          pointerEvents: "none",
        }}
      />

      {/* Gavel drop zone */}
      <div
        style={{
          position: "relative",
          zIndex: 2,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          maxWidth: 720,
          margin: "0 auto",
        }}
      >
        {/* Gavel animation */}
        <motion.div
          variants={gavelVariants}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          style={{
            marginBottom: "1.5rem",
            position: "relative",
          }}
        >
          <GavelSVG />
          {/* Shockwave ring behind gavel */}
          <motion.div
            variants={shockwaveVariants}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              width: 80,
              height: 80,
              marginTop: -40,
              marginLeft: -40,
              borderRadius: "50%",
              border: `1px solid ${T.gold}`,
              pointerEvents: "none",
            }}
          />
        </motion.div>

        {/* Copy */}
        <motion.div
          variants={textContainerVariants}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
        >
          <motion.p
            variants={textItemVariants}
            style={{
              fontSize: "0.6875rem",
              fontWeight: 500,
              textTransform: "uppercase",
              letterSpacing: "0.15em",
              color: T.gold,
              marginBottom: "1rem",
              fontFamily: "'Inter', system-ui, sans-serif",
            }}
          >
            The Ruling Is Clear
          </motion.p>

          <motion.h2
            variants={textItemVariants}
            id="gavel-headline"
            style={{
              fontSize: "clamp(1.5rem, 4vw, 2.5rem)",
              fontWeight: 800,
              lineHeight: 1.1,
              letterSpacing: "-0.02em",
              color: T.primaryText,
              marginBottom: "1rem",
              fontFamily: "'Inter', system-ui, sans-serif",
            }}
          >
            Stop Gambling With
            <br />
            <span style={{ color: T.gold }}>Client Privilege.</span>
          </motion.h2>

          <motion.p
            variants={textItemVariants}
            style={{
              fontSize: "1rem",
              lineHeight: 1.6,
              color: T.secondaryText,
              maxWidth: 560,
              margin: "0 auto 2rem",
              fontFamily: "'Inter', system-ui, sans-serif",
            }}
          >
            Every day your clients search without KovelAI is another day opposing counsel can
            subpoena their browser history. Deploy your firm&apos;s privileged portal today.
          </motion.p>

          {/* CTA buttons */}
          <motion.div
            variants={textItemVariants}
            style={{
              display: "flex",
              justifyContent: "center",
              flexWrap: "wrap",
              gap: "1rem",
            }}
          >
            <motion.button
              type="button"
              onClick={onOpenModal}
              className="btn-gold"
              id="ctaGavelDeploy"
              style={{ fontSize: "0.875rem" }}
              whileHover={{
                scale: 1.04,
                boxShadow: "0 0 50px rgba(230, 196, 135, 0.35)",
              }}
              whileTap={{ scale: 0.97 }}
            >
              Deploy Your Shield Now
            </motion.button>
            <motion.a
              href="#pricing"
              className="btn-ghost"
              style={{ fontSize: "0.875rem" }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              View Pricing →
            </motion.a>
          </motion.div>
        </motion.div>
      </div>

      {/* Decorative horizontal rule */}
      <motion.div
        initial={{ scaleX: 0 }}
        animate={isInView ? { scaleX: 1 } : { scaleX: 0 }}
        transition={{ duration: 1, delay: 1.2, ease: "easeOut" }}
        style={{
          position: "relative",
          zIndex: 2,
          maxWidth: 300,
          margin: "3rem auto 0",
          height: 1,
          background: `linear-gradient(90deg, transparent, ${T.gold}, transparent)`,
          opacity: 0.3,
          transformOrigin: "center",
        }}
      />
    </section>
  );
}
