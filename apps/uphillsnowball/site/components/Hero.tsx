"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

/**
 * UphillSnowball Hero - Kinetic Reversal
 * Concept: "Physics-defying compounding momentum."
 * A frosted-glass sphere rolling upward along a diagonal vector, absorbing data.
 */
export default function Hero() {
  const containerRef = useRef<HTMLDivElement>(null);

  // Track scroll progress within the container for physics-based parallax
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  // Calculate the sphere's upward trajectory along the vector
  // As user scrolls down, sphere moves UP and to the RIGHT
  const sphereX = useTransform(scrollYProgress, [0, 1], ["0%", "150%"]);
  const sphereY = useTransform(scrollYProgress, [0, 1], ["0%", "-150%"]);
  const sphereRotation = useTransform(scrollYProgress, [0, 1], [0, 720]);

  // Compounding mass effect
  const sphereScale = useTransform(scrollYProgress, [0, 1], [1, 1.8]);

  return (
    <section
      ref={containerRef}
      className="relative w-full h-[150vh] bg-[#050505] overflow-hidden flex flex-col text-[#FAFAFA]"
    >
      {/* Sticky viewport to keep hero visible while scrolling triggers physics */}
      <div className="sticky top-0 h-screen w-full flex items-center justify-center overflow-hidden">
        {/* Background ambient lighting */}
        <div className="absolute inset-0 z-0">
          <div className="absolute top-1/4 right-1/4 w-[600px] h-[600px] bg-[#3B82F6]/10 rounded-full blur-[120px] opacity-50" />
          <div className="absolute bottom-1/4 left-1/4 w-[400px] h-[400px] bg-[#8B5CF6]/10 rounded-full blur-[100px] opacity-40" />
        </div>

        {/* Sharp Glowing Diagonal Vector Line */}
        <div className="absolute z-10 w-[200%] h-[2px] bg-gradient-to-r from-transparent via-[#FAFAFA]/40 to-transparent rotate-[-25deg] shadow-[0_0_15px_rgba(250,250,250,0.3)]" />

        {/* The Kinetic Sphere */}
        <motion.div
          className="absolute z-20 w-32 h-32 md:w-48 md:h-48 rounded-full"
          style={{
            x: sphereX,
            y: sphereY,
            rotate: sphereRotation,
            scale: sphereScale,
          }}
          initial={{ x: "-20vw", y: "20vh" }}
        >
          {/* Frosted Glass Effect using atmospheric-glass hex tokens */}
          <div className="w-full h-full rounded-full backdrop-blur-xl bg-[#FAFAFA]/10 border border-[#FAFAFA]/20 shadow-[0_0_40px_rgba(250,250,250,0.1),inset_0_0_20px_rgba(250,250,250,0.2)] flex items-center justify-center overflow-hidden relative">
            {/* Internal core glow */}
            <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-[#FAFAFA]/5 to-[#FAFAFA]/30" />
            <motion.div
              className="w-1/2 h-1/2 rounded-full bg-gradient-to-br from-[#FAFAFA] to-transparent opacity-30 blur-md"
              animate={{ rotate: 360 }}
              transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
            />
          </div>
        </motion.div>

        {/* Floating Data Nodes (Absorbed by the sphere) */}
        <motion.div
          className="absolute z-10 top-1/3 left-1/2 w-4 h-4 bg-[#3B82F6] rounded-sm shadow-[0_0_10px_#3B82F6] opacity-70"
          animate={{ y: [0, -20, 0], opacity: [0.3, 0.8, 0.3] }}
          transition={{ duration: 3, repeat: Infinity }}
        />
        <motion.div
          className="absolute z-10 bottom-1/3 right-1/4 w-3 h-3 bg-[#8B5CF6] rounded-full shadow-[0_0_10px_#8B5CF6] opacity-60"
          animate={{ x: [0, 15, 0], opacity: [0.4, 0.9, 0.4] }}
          transition={{ duration: 4, repeat: Infinity, delay: 1 }}
        />
        <motion.div
          className="absolute z-10 top-1/4 right-1/3 w-2 h-12 bg-[#FAFAFA]/50 rotate-45 shadow-[0_0_8px_rgba(250,250,250,0.5)]"
          animate={{ opacity: [0.1, 0.5, 0.1] }}
          transition={{ duration: 2.5, repeat: Infinity }}
        />

        {/* Typography Content */}
        <div className="relative z-30 flex flex-col items-start px-6 md:px-24 w-full max-w-7xl pointer-events-none mt-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <h1 className="text-5xl md:text-8xl font-black tracking-tighter uppercase leading-[0.9] text-transparent bg-clip-text bg-gradient-to-br from-[#FAFAFA] via-[#A1A1AA] to-[#3F3F46]">
              Kinetic <br /> Reversal
            </h1>
            <p className="mt-6 text-xl md:text-2xl font-light text-[#A1A1AA] max-w-xl">
              Physics-defying momentum. Compounding data gravity against the incline.
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
