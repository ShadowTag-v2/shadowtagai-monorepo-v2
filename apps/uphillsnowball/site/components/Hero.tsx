import { motion, useScroll, useTransform } from 'framer-motion';
import type React from 'react';
import { useRef } from 'react';

/**
 * UphillSnowballHero
 * Concept: "Kinetic Reversal"
 * A heavy frosted-glass sphere rolling UP a glowing diagonal vector line,
 * absorbing data nodes, demonstrating physics-defying compounding momentum.
 */
export const UphillSnowballHero: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end start'],
  });

  // Calculate the upward motion based on scroll (Kinetic Reversal)
  // As user scrolls down, the ball moves UP the line
  const ballY = useTransform(scrollYProgress, [0, 1], ['0%', '-400%']);
  const ballX = useTransform(scrollYProgress, [0, 1], ['0%', '200%']);
  const ballRotate = useTransform(scrollYProgress, [0, 1], [0, 360]);

  // Node absorption animation (nodes moving towards the vector line)
  const floatVariants = {
    initial: { y: 0, opacity: 0.2 },
    animate: {
      y: [-10, 10, -10],
      opacity: [0.2, 0.5, 0.2],
      transition: { repeat: Infinity, duration: 4, ease: 'easeInOut' },
    },
  };

  return (
    <section
      ref={containerRef}
      className="relative w-full h-[150vh] bg-[#050505] overflow-hidden flex flex-col items-center pt-32"
    >
      {/* Background ambient lighting */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-4xl opacity-30 pointer-events-none">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-indigo-600 rounded-full mix-blend-screen filter blur-[150px] animate-pulse" />
        <div
          className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-blue-600 rounded-full mix-blend-screen filter blur-[150px] animate-pulse"
          style={{ animationDelay: '2s' }}
        />
      </div>

      <div className="relative z-20 text-center max-w-4xl mx-auto px-4 mt-16 mb-32">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-6xl md:text-8xl font-black text-white tracking-tighter mb-6"
        >
          Reverse{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-500 to-purple-600">
            Entropy.
          </span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-xl md:text-2xl text-neutral-400 font-light max-w-2xl mx-auto"
        >
          Compounding algorithmic momentum that defies technical gravity.
        </motion.p>
      </div>

      {/* The Kinetic Reversal Physics Simulation */}
      <div className="relative w-full max-w-6xl mx-auto h-[800px] pointer-events-none">
        {/* The glowing diagonal vector line */}
        <div className="absolute top-1/2 left-0 w-full h-px bg-gradient-to-r from-transparent via-blue-500/50 to-purple-500 -rotate-12 origin-left shadow-[0_0_30px_rgba(59,130,246,0.5)]" />
        <div className="absolute top-1/2 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-white/20 to-white -rotate-12 origin-left" />

        {/* Floating Data Nodes being absorbed */}
        <motion.div
          variants={floatVariants}
          initial="initial"
          animate="animate"
          className="absolute top-[30%] left-[20%] w-4 h-4 rounded-sm bg-blue-400/30 border border-blue-400/50 backdrop-blur-sm shadow-[0_0_15px_rgba(96,165,250,0.5)]"
        />
        <motion.div
          variants={floatVariants}
          initial="initial"
          animate="animate"
          style={{ animationDelay: '1s' }}
          className="absolute top-[60%] left-[40%] w-6 h-6 rounded-full bg-indigo-500/20 border border-indigo-500/40 backdrop-blur-sm"
        />
        <motion.div
          variants={floatVariants}
          initial="initial"
          animate="animate"
          style={{ animationDelay: '2.5s' }}
          className="absolute top-[40%] left-[70%] w-3 h-3 rotate-45 bg-purple-400/40 border border-purple-400/60 shadow-[0_0_20px_rgba(192,132,252,0.6)]"
        />
        <motion.div
          variants={floatVariants}
          initial="initial"
          animate="animate"
          style={{ animationDelay: '0.5s' }}
          className="absolute top-[20%] left-[60%] w-8 h-2 bg-white/10 border border-white/20 rounded-full"
        />

        {/* The Heavy Frosted Glass Sphere */}
        <motion.div
          style={{ y: ballY, x: ballX, rotate: ballRotate }}
          className="absolute top-1/2 left-[10%] -translate-y-full -translate-x-1/2 z-30"
        >
          <div className="relative w-48 h-48 rounded-full backdrop-blur-2xl bg-gradient-to-tr from-white/5 to-white/20 border border-white/20 shadow-[inset_0_0_40px_rgba(255,255,255,0.1),0_0_50px_rgba(59,130,246,0.3)] flex items-center justify-center overflow-hidden">
            {/* Inner dynamic core */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10 mix-blend-overlay" />
            <div className="w-full h-full bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-white/40 via-transparent to-transparent opacity-60" />

            {/* "Absorbed" data particle effect inside sphere */}
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 10, repeat: Infinity, ease: 'linear' }}
              className="absolute w-[150%] h-[150%] border-[0.5px] border-white/10 rounded-full border-dashed"
            />
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default UphillSnowballHero;
